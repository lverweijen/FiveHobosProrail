#!/usr/bin/python

import sys
import json

while True:
	line = sys.stdin.readline()
	if not line:
		break
	data = json.loads(line)
	offset = int(data["frameNr"] * 0.2 * data["width"])
	outData = {"leftEdge": offset, "frameNr": data["frameNr"], "xtra": data["width"]}
	outLine = json.dumps(outData)
	print(outLine)

sys.stderr.write("Dummy region matcher python is done!\n")