#!/usr/bin/python

import sys
import json
import math
import tensorflow as tf
import numpy as np
# import scipy as sc
import cv2
import os.path
import subprocess
import pytesseract
import PIL.Image as pil

def generateUICChecksum(digits):
	digits = int(digits)
	evenPosition = False
	sum = 0
	while digits > 0:
		factor = 1 if evenPosition else 2
		digit = (digits % 10) * factor
		while digit > 0:
			sum += digit % 10
			digit = int(digit / 10)
		digits = int(digits / 10)
		evenPosition = not evenPosition
	roundUp = math.ceil(sum / 10.0) * 10
	return roundUp - sum


def recogniseImage(img):
	text = pytesseract.image_to_string(img)
	text = "".join([char for char in text if char.isdigit()])
	text = text[:12]
	if len(text) < 11:
		text += "0" * (11 - len(text))
	if len(text) < 12:
		text += str(generateUICChecksum(text))
	text = text[:11] + "-" + text[11]
	return text


def polygon_to_image(frames, location, polygon):
	"""Given json objects, return numpy.array by taking a bounding box that contains the polygon."""

	# Find bounding box (meh)
	xs = [point[0] for point in polygon["points"]]
	ys = [point[1] for point in polygon["points"]]

	min_x, max_x = int(min(xs)), int(max(xs))
	min_y, max_y = int(min(ys)), int(max(ys))
	frame_nr = location["frameNr"]

	# Find filename
	for frame in frames:
		if frame["frameNr"] == frame_nr:
			filename = frame["filename"]
			break

	img = cv2.imread(filename)
	return img[min_y:max_y, min_x:max_x]

def number_to_image(frames, number_locations):
	"""Given json objects, return an image containing all digits."""
	xs = []
	ys = []

	for location in number_locations:
		polygons = location["polygons"]
		polygon = max(polygons, key=lambda polygon: polygon["score"])

		# Find bounding box (meh)
		xs.extend([point[0] for point in polygon["points"]])
		ys.extend([point[1] for point in polygon["points"]])
		frame_nr = location["frameNr"]

	min_x, max_x = int(min(xs)), int(max(xs))
	min_y, max_y = int(min(ys)), int(max(ys))
	# print("(min_x, max_x, min_y, max_y", (min_x, max_x, min_y, max_y))


	# Find filename
	for frame in frames:
		if frame["frameNr"] == frame_nr:
			filename = frame["filename"]
			break

	img = cv2.imread(filename)
	return img[min_y:max_y, min_x:max_x]


def run():
	c = 0

	while True:
		c+= 1
		line = sys.stdin.readline()
		if not line:
			break
		data = json.loads(line)

		# if c == 5:
		# 	break

		# begin stitched image through tesserflow)
		img = number_to_image(data["frames"], data["numberLocations"])

		uic = recogniseImage(pil.fromarray(img))
		# print(digits)

		outData = {"wagonStart": data["wagonStart"], "number": uic}
		outLine = json.dumps(outData)
		print(outLine)
		sys.stderr.write("Dummy number recogniser python is done!\n")

run()

		# Test data
		# print(os.path.join("/home/testdigits", "image_{}.png".format(c)))
		# cv2.imwrite("testdigits/image_{}.png".format(c), img)

		# Begin code per digit
		# for index, location in zip(stringetje, data["numberLocations"]):
		# 	polygons = location["polygons"]
		# 	polygon = max(polygons, key=lambda polygon: polygon["score"])
		# 	img = polygon_to_image(data["frames"], location, polygon)
		# 	cv2.imshow("useful {} ({})".format(index, c), img)
	    # Code per digit

	    # Given code
		# frameSum = 0
		# for numberLocation in data["numberLocations"]:
		# 	frameSum = frameSum + int(numberLocation["frameNr"])
		# averageFrame = frameSum / float(len(data["numberLocations"]))
		# digits = averageFrame * 218 # This is just to get some interesting digits
		# checksum = generateUICChecksum(digits)
		# uic = "%011d-%d" % (digits, checksum)
		# outData = {"wagonStart": data["wagonStart"], "number": uic}
		# outLine = json.dumps(outData)
		# print(outLine)



		# for frame in data["frames"]:
		# 	# frame has width, frameNr, height, channels, timestamp, leftEdge and filename
		# 	width = int(frame["width"])
		# 	frameNr = frame["frameNr"]
		# 	height = frame["height"]
		# 	channels = frame["channels"]
		# 	timestamp = frame["timestamp"]
		# 	leftEdge = int(frame["leftEdge"])
		# 	filename = frame["filename"]

		# 	img = cv2.imread(filename)
		# 	cv2.imshow("whole_image", img)
		# 	img = img[:, leftEdge:leftEdge + width]
		# 	cv2.imshow("part_image", img)
		# 	cv2.waitKey(0)
		# 	input()
		# 	cv2.destroyAllWindows()
		# 	exit(1)

	# first_part = ""
	# control_part = ""
	# if "-" in text:
	# 	parts = text.split("-")
	# 	first_part += parts[0]
	# 	control_part += parts[1]

	# 	if control_part:
	# 		control_part = control_part[0]
	# else:
	# 	first_part = text[:12]
	# 	if len(text) > 12:
	# 		control_part = text[12]

	# first_part += "0" * (11 - len(first_part))
	# if not control_part:
	# 	control_part = generateUICChecksum(first_part)

	# return first_part + "-" + str(control_part)
