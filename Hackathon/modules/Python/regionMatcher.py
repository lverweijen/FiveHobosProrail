import cv2
import sys
import json
import numpy as np
import os


class App:
    def __init__(self):
        #Config

        self.create_stiched_output = False
        # Toggle to show debug message
        self.debug = False
        self.pause_after_each_frame = False

        #Global vars
        self.leftedge = 0
        self.continu = True
        self.frames_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "frames"))
        self.stitched_image = np.zeros((1, 1, 3))
        self.train_detected = 0
        self.previous_frame = np.zeros((1, 1, 3))
        self.output_dir_stitched = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "stiched"))
        self.stitch_completed = False


    def run(self):
        """Run for complete train.

        Measure by orb.DetectAndCompute
        Call determine_flow to update model

        Laurent
        """
        self.create_output_dirs()
        data = self.read_input()
        while (data):
           # Initiate ORB detector
            orb = cv2.ORB_create()

            if (self.continu):
                current_frame_nr = data["frameNr"]
                if(current_frame_nr > 1):
                    self.determine_flow(orb, current_frame_nr)
                else:
                  #Read first image
                  self.previous_frame_path = os.path.join(self.frames_dir, '%05d.png' % 1)
                  self.previous_frame = cv2.imread(self.previous_frame_path, 0)  # queryImage
                  # Find the keypoints and descriptors with ORB
                  self.kp_previous_frame, self.des_previous_frame = orb.detectAndCompute(self.previous_frame, None)
            elif(self.stitch_completed):
                self.write_stitched_image()
                self.continu = False
                self.stitch_completed = True
                return
            data = self.read_input()



    def determine_flow(self, orb, current_frame_nr):
        """Update model.

        Update model
        Write movement to log file

        Laurent
        """

        current_frame_path = os.path.join(self.frames_dir, '%05d.png' % current_frame_nr)

        average_horizontal_distance = self.determine_average_horizontal_distance(current_frame_path, orb)

        self.write_debug('Train detected: %d average_horizontal_distance: %d' % (self.train_detected, average_horizontal_distance))

        # Laurent: I think here they detect end of train
        if(self.train_detected > 2 and average_horizontal_distance == 0 ):
            self.write_stitched_image()
            self.write_output(current_frame_nr)
            self.continu = False
            return


        elif(average_horizontal_distance != 0):
            self.create_stitched_image(average_horizontal_distance, current_frame_path)
            self.write_output(current_frame_nr)

    def write_stitched_image(self):
        """Write image with end of train.

        Laurent"""

        self.write_debug("End of train detected. Writing stitched image.")
        cv2.imwrite(os.path.join(self.output_dir_stitched, 'stitched.jpg'), self.stitched_image)

    def create_stitched_image(self, average_horizontal_distance, current_frame_path):
        query_image = cv2.imread(self.previous_frame_path, cv2.IMREAD_COLOR)  # queryImage
        train_image = cv2.imread(current_frame_path, cv2.IMREAD_COLOR)  # trainImage
        query_image_with_border = cv2.copyMakeBorder(query_image, 0, 0, 0, abs(average_horizontal_distance),
                                                     cv2.BORDER_CONSTANT,
                                                     value=(255, 255, 255))
        train_image_with_border = cv2.copyMakeBorder(train_image, 0, 0, abs(average_horizontal_distance), 0,
                                                     cv2.BORDER_CONSTANT,
                                                     value=(255, 255, 255))
        if(average_horizontal_distance > 0):
            overlayed_image = cv2.addWeighted(query_image_with_border, 0.5, train_image_with_border, 0.5, 0)
        else:
            overlayed_image = cv2.addWeighted(train_image_with_border, 0.5,query_image_with_border , 0.5, 0)
        if (self.stitched_image.shape[0] == 1):
            self.stitched_image = query_image

        (hA, wA) = self.stitched_image.shape[:2]

        # Find center of image
        center = int(round(train_image.shape[1] / 2))

        # Create empty image
        stiched = np.zeros((hA, wA + abs(average_horizontal_distance), 3), dtype="uint8")


        if(average_horizontal_distance > 0):
            # Create stitched image RTL
            stiched[:, :wA] = self.stitched_image
            stiched[:, wA - center:] = train_image[:, center - average_horizontal_distance:stiched.shape[1]]
        else:
            # Create stitched image LTR
            stiched[:, center:] = self.stitched_image[:,center-abs(average_horizontal_distance):]
            stiched[:, :center] = train_image[:, :center]
        self.stitched_image = stiched

        if (self.pause_after_each_frame):
            cv2.imshow('im1', query_image)
            cv2.imshow('im2', train_image)
            cv2.imshow('overlayed_image', overlayed_image)
            cv2.imshow('stitched', stiched)
            cv2.waitKey(0)

            self.write_debug('average distance %d' % average_horizontal_distance)
            self.write_debug('leftedge = %d' % self.leftedge)
            self.write_debug('Train detected:%d' % self.train_detected)
        self.train_detected += 1

    def determine_average_horizontal_distance(self, current_frame_path, orb):
        """Measure shift.

        Laurent"""

        current_frame = cv2.imread(current_frame_path, 0)  # trainImage

        # find the keypoints and descriptors with ORB
        kp_current_frame, des_current_frame = orb.detectAndCompute(current_frame, None)

        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match descriptors.
        matches = bf.match(self.des_previous_frame, des_current_frame)

        # Sort them in the order of their distance.
        matches = sorted(matches, key=lambda x: x.distance)
        self.write_debug('#matches: %d' % len(matches))

        nr_of_matches_to_use = 200
        trainId = [m.trainIdx for m in matches[:nr_of_matches_to_use]]
        queryId = [m.queryIdx for m in matches[:nr_of_matches_to_use]]

        total_horizontal_distance = 0
        horizontal_distance_list = []
        nr_of_valid_distances = 0
        for i in range(1, len(trainId)):
            horizontal_distance = (self.kp_previous_frame[queryId[i]].pt[0] - kp_current_frame[trainId[i]].pt[0])

            # Only considder matches with a small vertical distance and a large horizontal distance
            if ((abs(self.kp_previous_frame[queryId[i]].pt[1] - kp_current_frame[trainId[i]].pt[1]) < 50) and (
                abs(horizontal_distance) > 40 and abs(horizontal_distance) < 110)):
                self.write_debug('Distance: %d' % horizontal_distance)
                nr_of_valid_distances += 1
                total_horizontal_distance += horizontal_distance
                horizontal_distance_list.append(horizontal_distance)


        positive_distances = [item for item in horizontal_distance_list if item > 0]
        negative_distances = [item for item in horizontal_distance_list if item < 0]
        if (len(horizontal_distance_list) == 0):
            median_horizontal_distance = 0
        elif(len(positive_distances) > len(negative_distances)):
            median_horizontal_distance = round(np.median(positive_distances))
        else:
            median_horizontal_distance = round(np.median(negative_distances))

        self.leftedge += median_horizontal_distance

        self.set_current_to_previous(current_frame, current_frame_path, des_current_frame, kp_current_frame)

        return int(median_horizontal_distance)

    def set_current_to_previous(self, current_frame, current_frame_path, des_current_frame, kp_current_frame):
        self.previous_frame_path = current_frame_path
        self.previous_frame = current_frame
        self.kp_previous_frame = kp_current_frame
        self.des_previous_frame = des_current_frame

    def write_debug(self, message):
        if (self.debug):
            sys.stderr.write(message + '\n')

    def read_input(self):
        line = sys.stdin.readline()
        if not line:
            return
        return json.loads(line)

    def write_output(self, frame_nr):
        outData = {"leftEdge": self.leftedge, "frameNr": frame_nr}
        outLine = json.dumps(outData)
        print(outLine)

    def create_output_dirs(self):
        if not os.path.exists(self.output_dir_stitched):
            os.makedirs(self.output_dir_stitched)

def main():
    App().run()


if __name__ == '__main__':
    main()
