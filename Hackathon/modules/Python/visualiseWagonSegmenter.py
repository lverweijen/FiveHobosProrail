#!/usr/bin/python

import sys
import json

import numpy as np
#import PIL.image as pil
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

class App:
	def __init__(self):
		self.wagons = []
		self.image = None

	def run(self):
		self.read_stdin()
		self.read_img()
		self.show_wagons()

	def read_stdin(self):
		for line in sys.stdin:
			self.wagons.append(json.loads(line))

		self.offset = self.wagons[0]["wagonEnd"]
		self.wagons = self.wagons[1:]

	def read_img(self):
		self.image = plt.imread('Hackathon/output/stiched/stitched.jpg')

	def show_wagons(self):
		for wagon in self.wagons[0:5]:
			start = wagon["wagonStart"] + self.offset
			end = wagon["wagonEnd"] + self.offset
			f, ax = plt.subplots(1,1)
			ax.imshow(self.image[:, start:end])

		plt.show()

if __name__ == '__main__':
    App().run()