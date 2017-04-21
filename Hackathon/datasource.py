import json
import cv2
import io
import os

class DummySource:
	def __init__(self):
		pass

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		return type == None

	def read(self):
		return None

	def write(self, data):
		pass

class VideoReader:
	def __init__(self, filename):
		self.filename = filename
		self.cap = None

	def __enter__(self):
		if self.cap:
			print("Video reader already open")
			return self
		self.cap = cv2.VideoCapture(self.filename)
		self.frameNr = 0
		self.time = 0
		return self

	def __exit__(self, type, value, traceback):
		if self.cap:
			self.cap.release()
		return type == None

	def read(self):
		if not self.cap or not self.cap.isOpened():
			return None
		ret, frame = self.cap.read()
		if ret:
			self.frameNr += 1
			self.time = self.cap.get(cv2.CAP_PROP_POS_MSEC)
			return frame
		else:
			return None

class TextStream:
	def __init__(self, stream, logOptions):
		self.stream = stream
		self.textStream = None
		self.logOptions = logOptions
		self.logFile = None

	def __enter__(self):
		if self.textStream:
			print("Text Stream already open")
			return self
		self.textStream = io.TextIOWrapper(self.stream)
		if "filename" in self.logOptions:
			self.logFile = File(self.logOptions["filename"], "w")
			self.logFile.__enter__()
		return self

	def __exit__(self, type, value, traceback):
		if self.textStream:
			self.textStream.close();
		if self.logFile:
			self.logFile.__exit__(None, None, None)
		return type == None

	def read(self):
		line = self.textStream.readline()
		if "consoleTag" in self.logOptions:
			print(self.logOptions["consoleTag"] + " output: " + line.strip())
		if self.logFile:
			self.logFile.write(line)
		return line if line else None

	def write(self, data):
		line = str(data)
		if line[-1] != '\n':
			line += '\n'
		if "consoleTag" in self.logOptions:
			print(self.logOptions["consoleTag"] + " input: " + line.strip())
		if self.logFile:
			self.logFile.write(line)
		self.textStream.write(line)
		self.textStream.flush()

class JsonStream(TextStream):
	def __init__(self, stream, logTag):
		super(JsonStream, self).__init__(stream, logTag)

	def read(self):
		line = super(JsonStream, self).read()
		return json.loads(line) if line else None

	def write(self, data):
		super(JsonStream, self).write(json.dumps(data))

class File:
	def __init__(self, filename, mode):
		dirname = os.path.dirname(filename)
		if dirname and not os.path.exists(dirname):
			os.makedirs(dirname)
		self.filename = filename
		self.mode = mode
		self.file = None

	def __enter__(self):
		if self.file:
			print("File already open")
			return self
		self.file = open(self.filename, self.mode)
		return self

	def __exit__(self, type, value, traceback):
		self.file.close()
		self.file = None
		return type == None

	def read(self):
		return self.file.readline()

	def write(self, data):
		if len(data) == 0:
			return
		self.file.write(str(data))