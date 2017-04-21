# Extracts frames to png
# Usage: frame_extractor.py <inputfile> <outputdir>

import cv2
import os

class App:
	def __init__(self, inputfile, outputdir):
		self.outputdir = outputdir
		self.inputfile = inputfile
		self.resize_ratio = 1
		

	def run(self):
		if not os.path.exists(self.outputdir):
			os.makedirs(self.outputdir)
		
		cap = cv2.VideoCapture(self.inputfile)
		
		count = 1
		while(cap.isOpened()):
			ret, frame = cap.read()
			if(not ret):
				break
			print('Writing frame %d' % count)
			frame = cv2.resize(frame, None, fx=self.resize_ratio, fy=self.resize_ratio, interpolation=cv2.INTER_CUBIC)
			cv2.imwrite("%s/%05d.png" % (self.outputdir, count), frame)
			count += 1
	
		print('Finished writing frames to %s' % self.outputdir)
		cap.release()
		cv2.destroyAllWindows()
	
def main():
	import sys
	try:
		inputfile = sys.argv[1]
		outputdir = sys.argv[2]
	except:
		inputfile = "./testdata/testclip1.mp4"
		outputdir = "./output_frames/"
		print('No args given, using defaults inputfile: %s and outputdir %s' % (inputfile, outputdir))
	
	print(__doc__)
	App(inputfile, outputdir).run()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()