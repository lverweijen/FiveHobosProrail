import threading
import os
import io
import sys
import cv2
import json
import numbers
import datasource

class Link:
	def __init__(self, moduleOutput, moduleInput, outModuleName = None, inModuleName = None):
		self.moduleOutput = moduleOutput
		self.moduleInput = moduleInput
		self.outModuleName = outModuleName
		self.inModuleName = inModuleName
		self.thread = None

	def start(self):
		if self.thread:
			print("Already running")
			return
		self.thread = threading.Thread(target = self.run)
		self.thread.start()

	def run(self):
		try:
			with (self.moduleOutput):
				with (self.moduleInput):
					while True:
						data = self.moduleOutput.read()
						# We use is None instead of not data because the truth value of an array is ambiguous
						if data is None or not self.validate(data):
							break
						if self.outModuleName:
							self.showModuleOutput(data)
						output = self.transformData(data)
						if output is None:
							break
						if self.inModuleName:
							self.showModuleInput(output)
						self.moduleInput.write(output)
		except Exception as e:
			print(self.__class__.__name__ + " encountered an error: ")
			print(e)

	def join(self):
		if not self.thread:
			print("Not started")
			return
		self.thread.join()
		self.thread = None

	def showModuleOutput(self, data):
		print(self.outModuleName + " output: " + json.dumps(data))

	def validate(self, data):
		return True

	def transformData(self, data):
		return data

	def showModuleInput(self, data):
		print(self.inModuleName + " input:  " + json.dumps(data))

	def hasAllKeys(self, keys, data):
		hasAll = True
		for key in keys:
			if not key in data:
				hasAll = False
				print(self.__class__.__name__ + " received data that does not have key '" + key + "': " + str(data))
		return hasAll

class Feeder(Link):
	def __init__(self, config, moduleInput, frameCache, inModuleName = None):
		videoNode = config.getNode("video")
		filename = videoNode.getNode("input").string()
		super(Feeder, self).__init__(datasource.VideoReader(filename), moduleInput, None, inModuleName)
		self.frameCache = frameCache
		self.framePath = videoNode.getNode("output").string()
		self.scale = videoNode.getNode("scale").real()
		dirs = os.path.dirname(self.framePath)
		if dirs and not os.path.exists(dirs):
			os.makedirs(dirs)

	def transformData(self, data):
		frameNr = self.moduleOutput.frameNr
		filename = self.framePath % frameNr
		if not os.path.exists(filename):
			scaledData = cv2.resize(data, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_CUBIC)
			cv2.imwrite(filename, scaledData)
		(rows, cols, nchannels) = data.shape
		result = {
			"frameNr": frameNr,
			"filename": filename,
			"timestamp": self.moduleOutput.time,
			"width": int(cols * self.scale),
			"height": int(rows * self.scale),
			"channels": nchannels
		}
		self.frameCache[frameNr] = result
		return result

class Region2Segment(Link):
	def __init__(self, moduleOutput, moduleInput, frameCache, outModuleName = None, inModuleName = None):
		super(Region2Segment, self).__init__(moduleOutput, moduleInput, outModuleName, inModuleName)
		self.frameCache = frameCache

	def validate(self, data):
		return self.hasAllKeys(["frameNr", "leftEdge"], data)

	def transformData(self, data):
		frameNr = data["frameNr"]
		if not frameNr in self.frameCache:
			print("Received data for frame " + frameNr + " but this frame is not in the cache")
			return None
		cacheData = self.frameCache[frameNr]
		cacheData.update(data)
		return cacheData

class Segment2Localise(Link):
	OBLIGATORY = ["wagonStart", "wagonEnd"]

	def __init__(self, moduleOutput, moduleInput, frameCache, wagonCache, outModuleName = None, inModuleName = None):
		super(Segment2Localise, self).__init__(moduleOutput, moduleInput, outModuleName, inModuleName)
		self.frameCache = frameCache
		self.wagonCache = wagonCache

	def validate(self, data):
		if "frames" in data:
			print("Output data contains a field named 'frames'. This field will be overwritten.")
		return self.hasAllKeys(self.OBLIGATORY, data)

	def transformData(self, data):
		start = data["wagonStart"]
		end = data["wagonEnd"]
		# Find all frames that display part of the wagon
		frames = []
		leftEdgeKey = "leftEdge"
		for frame in self.frameCache.values():
			if not leftEdgeKey in frame:
				continue
			leftEdge = frame[leftEdgeKey]
			rightEdge = leftEdge + frame["width"]
			if leftEdge <= start and rightEdge >= start \
			or leftEdge <= end   and rightEdge >= end   \
			or leftEdge >= start and rightEdge <= end   :
				frames.append(frame)
		data["frames"] = frames
		# We only need the full wagon data once. Only store the "extra" data to pass on to other modules.
		self.wagonCache[start] = {key: value for (key, value) in data.items() if not key in self.OBLIGATORY}
		return data

class Localise2Recognise(Link):
	def __init__(self, moduleOutput, moduleInput, wagonCache, outModuleName = None, inModuleName = None):
		super(Localise2Recognise, self).__init__(moduleOutput, moduleInput, outModuleName, inModuleName)
		self.wagonCache = wagonCache

	def validate(self, data):
		if not self.hasAllKeys(["wagonStart", "numberLocations"], data):
			return False
		numberLocations = data["numberLocations"]
		if not type(numberLocations) is list:
			print("numberLocations must be a list: " + str(numberLocations))
			return False
		for numberLocation in numberLocations:
			if not self.hasAllKeys(["frameNr", "polygons"], numberLocation):
				return False
			polygons = numberLocation["polygons"]
			if not type(polygons) is list:
				print("polygons must be a list: " + str(polygons))
				return False
			for polygon in polygons:
				if not self.hasAllKeys(["points", "score"], polygon):
					return False
				points = polygon["points"]
				if not type(points) is list:
					print("points must be a list: " + str(polygon))
					return False
				for point in points:
					if len(point) != 2 or not isinstance(point[0], numbers.Number) or not isinstance(point[1], numbers.Number):
						print("point must be a tuple of 2 coordinates: " + str(point))
						return False
		return True

	def transformData(self, data):
		start = data["wagonStart"]
		if not start in self.wagonCache:
			print("Received data for wagon that starts at " + start + " but this wagon is not in the cache")
			return None
		cacheData = self.wagonCache[start]
		cacheData.update(data)
		return cacheData