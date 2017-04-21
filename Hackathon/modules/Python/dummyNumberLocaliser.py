#!/usr/bin/python

import sys
import json
import numpy as np

# The polygon is inside the frame if any point is inside the frame
def frameContains(frame, polygon):
	width = frame["width"]
	height = frame["height"]
	for point in polygon:
		if point[0] >= 0 and point[0] <= width and point[1] >= 0 and point[1] <= height:
		   return True
	return False

# define a big ulgy L shape
prototype = [(0.1, 0.3), (0.2, 0.3), (0.2, 0.4), (0.5, 0.4), (0.5, 0.5), (0.1, 0.5)]

while True:
	line = sys.stdin.readline()
	if not line:
		break
	data = json.loads(line)

	wagonStart = data["wagonStart"]
	wagonEnd = data["wagonEnd"]
	wagonWidth = wagonEnd - wagonStart
	height = data["frames"][0]["height"]

	# In this example we define one polygon in train coordinates. Then we see if this polygon
	# intersects with any of the frames. If it does we put this one polygon as a single element
	# in the output array, but you can put more polygons in there if you like.
	numberLocations = []
	for frame in data["frames"]:
		leftEdge = frame["leftEdge"]
		polygon = [(wagonStart - leftEdge + x * wagonWidth, y * height) for (x, y) in prototype]
		if frameContains(frame, polygon):
			polygons = []
			polygons.append({"points": polygon, "score": 0.95})
			numberLocations.append({"frameNr": frame["frameNr"], "polygons": polygons})

	outData = {"wagonStart": wagonStart, "numberLocations": numberLocations}
	outLine = json.dumps(outData)
	print(outLine)

sys.stderr.write("Dummy number localiser python is done!\n")