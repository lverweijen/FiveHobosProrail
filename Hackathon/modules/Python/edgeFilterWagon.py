import sys
import json

import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2
import pytesseract as pt
import PIL.Image as pil
import PIL.ImageOps

class App:
	def __init__(self):
		self.wagons = []
		self.image = None
		self.myhome = '/media/sf_hackathon/'
	def run(self):
		self.read_stdin()
		self.read_img()
		self.show_wagons()

	def read_stdin(self):
		with open(self.myhome + 'Hackathon/output/cache/Dummies_wagonSegmenter_output.txt','r') as file:
			for line in file.readlines():
				self.wagons.append(json.loads(line))

		self.offset = self.wagons[0]["wagonEnd"]
		self.wagons = self.wagons[1:]

	def read_img(self):
		self.image = cv2.imread(self.myhome + 'Hackathon/output/stiched/stitched.jpg')
		b,g,r = cv2.split(self.image)       # get b,g,r
		self.image = cv2.merge([r,g,b])     # switch it to rgb
		kernel = np.ones((5,5),np.float32)/25
		heat_kernel = np.ones((15,15), np.float32)
		#sheat_kernel[1,1] = 1

		dst = cv2.filter2D(self.image,-1,kernel)
		self.edges = cv2.Canny(dst,100,200).astype('float')
		self.heatmap_edges = cv2.filter2D(self.edges, -1, heat_kernel).astype('float')

	def show_wagons(self):
		for wagon in self.wagons[5:15]:
			start = wagon["wagonStart"] #+ self.offset
			end = wagon["wagonEnd"] #+ self.offset
			f, ax = plt.subplots(3,1, sharex = True, sharey= True)
			ax[0].imshow(self.image[:, start:end], cmap = 'gray')
			ax[1].imshow(self.edges[:, start:end], cmap = 'gray')
			ax[2].imshow(self.heatmap_edges[:, start:end], cmap = 'plasma')
			ax[0].set_title(str(start))
			
			orig_max = np.max(self.heatmap_edges[:, start:end])
			while np.max(self.heatmap_edges[:, start:end]) > 0.95 * orig_max:
				i = 1
				index = np.argmax(self.heatmap_edges[:, start:end].astype('float'))
				yi, xi = np.unravel_index(index,self.heatmap_edges[:, start:end].shape)
				interesting_patch = self.image[yi-50:yi+50, start+xi-250:start+xi+250]
				f2, ax2 = plt.subplots(2,1)
				interesting_pict = pil.fromarray(interesting_patch)
				ax2[0].set_title(pt.image_to_string(interesting_pict, config='outputbase digits'))
				ax2[0].imshow(interesting_patch)
				inverted = PIL.ImageOps.invert(interesting_pict)
				ax2[1].imshow(inverted)
				ax2[1].set_title(pt.image_to_string(inverted, config='outputbase digits'))
				f2.savefig("wagon" + str(start) + "_patch_" + str(i) + ".png")
				plt.close(f2)
				self.heatmap_edges[yi-30:yi+30, start+xi-150:start+xi+150] = 0.0
			
			f.savefig("wagon_" + str(start)) + "_complete.png")
			plt.close(f)
if __name__ == '__main__':
    App().run()