#!/usr/bin/python

import sys
import json

wagonStart = 0

while True:
	line = sys.stdin.readline()
	if not line:
		break
	data = json.loads(line)
	leftEdge = data["leftEdge"]
	if abs(leftEdge - wagonStart) > 3300:
		wagonEnd = wagonStart + 3300
		outData = {"wagonStart": wagonStart, "wagonEnd": wagonEnd, "xtradata": leftEdge}
		outLine = json.dumps(outData)
		print(outLine)
		wagonStart = wagonEnd

sys.stderr.write("Dummy wagon segmenter python is done!\n")