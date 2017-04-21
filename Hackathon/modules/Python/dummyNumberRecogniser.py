#!/usr/bin/python

import sys
import json
import math

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

while True:
	line = sys.stdin.readline()
	if not line:
		break
	data = json.loads(line)

	frameSum = 0
	for numberLocation in data["numberLocations"]:
		frameSum = frameSum + int(numberLocation["frameNr"])
	averageFrame = frameSum / float(len(data["numberLocations"]))
	digits = averageFrame * 218 # This is just to get some interesting digits
	checksum = generateUICChecksum(digits)
	uic = "%011d-%d" % (digits, checksum)

	outData = {"wagonStart": data["wagonStart"], "number": uic}
	outLine = json.dumps(outData)
	print(outLine)

sys.stderr.write("Dummy number recogniser python is done!\n")