#!/usr/bin/python

try:
	import cv2
except:
	print("\nOpencv for python is not installed. Try pip install opencv-python")
	quit()
import subprocess
import linktype
import datasource as ds
import os
import sys

if sys.version_info < (3, 0):
	print("You are using Python 2. Please invoke again using Python3 instead.")
	sys.exit()

def makeProcess(config, name):
	command = config.getNode(name).getNode("command").string()
	return subprocess.Popen(command, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)

def log(config, isInput, name):
	"""Returns the logging options for the given module if logging is requested"""
	logOptions = {}
	node = config.getNode(name).getNode("showInput" if isInput else "showOutput")
	if node and node.string().lower() == "true":
		logOptions["consoleTag"] = name
	logName = "_".join([config.getNode("teamName").string(), name, ("input" if isInput else "output") + ".txt"])
	logOptions["filename"] = os.path.join(config.getNode("cache").string(), logName)
	return logOptions

MOD_RM = "regionMatcher"
MOD_WS = "wagonSegmenter"
MOD_NL = "numberLocaliser"
MOD_NR = "numberRecogniser"

links = [] # Links read output from one module and feed input to the next

config = None
try:
	config = cv2.FileStorage("configuration.yml", 0)
	matcher = makeProcess(config, MOD_RM)
	segmenter = makeProcess(config, MOD_WS)
	localiser = makeProcess(config, MOD_NL)
	recogniser = makeProcess(config, MOD_NR)

	frameCache = {}
	wagonCache = {}

	links.append(linktype.Feeder            (config,                                                       ds.JsonStream(matcher.stdin,    log(config, True, MOD_RM)), frameCache))
	links.append(linktype.Region2Segment    (ds.JsonStream(matcher.stdout,    log(config, False, MOD_RM)), ds.JsonStream(segmenter.stdin,  log(config, True, MOD_WS)), frameCache))
	links.append(linktype.Segment2Localise  (ds.JsonStream(segmenter.stdout,  log(config, False, MOD_WS)), ds.JsonStream(localiser.stdin,  log(config, True, MOD_NL)), frameCache, wagonCache))
	links.append(linktype.Localise2Recognise(ds.JsonStream(localiser.stdout,  log(config, False, MOD_NL)), ds.JsonStream(recogniser.stdin, log(config, True, MOD_NR)),             wagonCache))
	links.append(linktype.Link              (ds.TextStream(recogniser.stdout, log(config, False, MOD_NR)), ds.DummySource()))

	for link in links:
		link.start()
	for link in links:
		link.join()

finally:
	if config:
		config.release()
print("Processing complete")
