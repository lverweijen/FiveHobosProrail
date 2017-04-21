#!/usr/bin/python

import sys
import json

import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

class App:
	def __init__(self):
		self.data = []
		self.images = {}

	def run(self):
		self.read_stdin()
		self.read_imgs()
		self.show_numbers()
		

	def read_stdin(self):
		data = []

		with open('Hackathon/output/cache/Dummies_numberLocaliser_output.txt','r') as file:
			for line in file.readlines():
				data_json = json.loads(line)

				for loc in data_json["numberLocations"][0:5]:
					polygons = map(lambda x: x["points"], loc["polygons"])
					self.data.append({
						"frame_nr": loc["frameNr"],
						"paths": polygons
						})

	def read_imgs(self):
		for frame in self.data:
			frame_nr = frame["frame_nr"]
			self.images[frame_nr] = mpimg.imread('Hackathon/output/frames/%05d.png' % frame_nr)


	def show_numbers(self):
		for loc in self.data[0:5]:
			img = self.images[loc["frame_nr"]]
			paths = loc["paths"]
			
			for path in paths:
				ys = list(map(lambda x: x[1], path))
				xs = list(map(lambda x: x[0], path))

				if (max(xs)-min(xs) > 5 and max(ys)-min(ys) > 8):
					fix, ax = plt.subplots(1,1)
					ax.imshow(img[min(ys):max(ys), min(xs):max(xs)])
					plt.show()




if __name__ == '__main__':
    App().run()