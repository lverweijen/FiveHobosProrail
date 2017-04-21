import os
import cv2
import json
import sys
import tensorflow as tf

# Wagon segmentation with the help of Tensorflow
class App:
    def __init__(self):
        # Config
        self.debug = False

        # Global variables
        self.tf_files_dir = './tf_files'
        self.frames_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "frames"))
        self.crop = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "crop"))
        self.output_dir_stitched = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "output", "stiched"))

    def run(self):
        self.print_debug('Loading tensorflow')
        self.create_output_dirs()

        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line
                       in tf.gfile.GFile(self.tf_files_dir + '/retrained_labels.txt')]

        # Unpersists graph from file
        with tf.gfile.FastGFile(self.tf_files_dir + '/retrained_graph.pb', 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

            count = 1
            data = self.read_input()
            previous_buffer_score = [0, 0]
            previous_left_edge = [0, 0]
            previous_buffer_left_edge = 0
            buffers_left_edges = []

            while (data):
                frame_nr = data["frameNr"]
                frame_path = os.path.join(self.frames_dir, '%05d.png' % frame_nr)
                leftedge = data["leftEdge"]
                if(leftedge != previous_left_edge[-1]):
                    #Read frame
                    frame = cv2.imread(frame_path, cv2.IMREAD_COLOR)  # trainImage

                    self.print_debug('Processing frame %d' % frame_nr)

                    #Create crop
                    p1 = (290, 200)
                    p2 = (390, 440)
                    crop = frame[p1[0]:p2[0], p1[1]:p2[1]]
                    outputpath = "%s/%s_%05d.jpg" % (self.crop, frame_nr, count)
                    cv2.imwrite(outputpath, crop)

                    # Read in the image_data
                    image_data = tf.gfile.FastGFile(outputpath, 'rb').read()
                    #Feed the image to tensorflow
                    predictions = sess.run(softmax_tensor, \
                                           {'DecodeJpeg/contents:0': image_data})

                    #Fill the bufferscore with the prediction of the crop being a buffer
                    buffer_score = predictions[0][0]
                    threshold = 0.90

                    if (buffer_score < previous_buffer_score[1] and previous_buffer_score[0] < previous_buffer_score[1] and
                                previous_buffer_score[1] > threshold):
                        buffer_left_edge = self.calculate_buffer_left_edge(p1, p2, previous_left_edge)
                        self.write_output(previous_buffer_left_edge, buffer_left_edge)
                        buffers_left_edges.append(buffer_left_edge)
                        previous_buffer_left_edge = buffer_left_edge

                    #Update the buffer scores and left edges
                    self.update_buffer_scores(buffer_score, leftedge, previous_buffer_score, previous_left_edge)

                    if (self.debug):
                        self.write_classified_images(count, frame_nr, label_lines, predictions, crop)
                    count += 1
                data = self.read_input()

        #self.draw_separation_lines(buffers_left_edges)
        self.print_debug('Finished writing frames to')

    def update_buffer_scores(self, buffer_score, leftedge, previous_buffer_score, previous_left_edge):
        del previous_buffer_score[0]
        previous_buffer_score.append(buffer_score)
        del previous_left_edge[0]
        previous_left_edge.append(leftedge)

    def calculate_buffer_left_edge(self, p1, p2, previous_left_edge):
        return int(previous_left_edge[1] + round(p1[0] + (p2[0] - p1[0]) / 2))

    def write_classified_images(self, count, frame_nr, label_lines, predictions, crop):
        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        outputfile = "%s/%s_%05d_%03f.jpg" % (
            os.path.join(self.crop, label_lines[top_k[0]]), frame_nr, count, predictions[0][top_k[0]])
        cv2.imwrite(outputfile, crop)

    def draw_separation_lines(self, buffers_left_edges):
        stitched_image = cv2.imread(self.output_dir_stitched + '\stitched.jpg', cv2.IMREAD_COLOR)  # trainImage
        for buffer_left_edge in buffers_left_edges:
            if(buffer_left_edge > 0):
                cv2.line(stitched_image, (buffer_left_edge, 0), (buffer_left_edge, stitched_image.shape[1]), (255, 0, 0), 5)
            else:
                cv2.line(stitched_image, ( stitched_image.shape[0] + buffer_left_edge, 0), ( stitched_image.shape[0] + buffer_left_edge, stitched_image.shape[1]), (255, 0, 0), 5)
        cv2.imwrite(self.output_dir_stitched + '/stitched_wagons.jpg', stitched_image)

    def create_output_dirs(self):
        if not os.path.exists(self.crop):
            os.makedirs(self.crop)
        if(self.debug):
            if not os.path.exists(self.crop + '/buffer'):
                os.makedirs(self.crop + '/buffer')
            if not os.path.exists(self.crop + '/non buffer'):
                os.makedirs(self.crop + '/non buffer')

    def read_input(self):
        line = sys.stdin.readline()
        if not line:
            return
        return json.loads(line)

    def write_output(self, wagonStart, wagonEnd):
        outData = {"wagonStart": wagonStart, "wagonEnd": wagonEnd}
        outLine = json.dumps(outData)
        print(outLine)

    def print_debug(self, message):
        if (self.debug):
            sys.stderr.write(message)


def main():
    App().run()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
