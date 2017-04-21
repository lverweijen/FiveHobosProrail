# FiveHobosProrail
Five hobos on a hackaton
Ruben is up and running!

# Code contributed #

- VisualNumberLocaliser
A tool to output the image with a box around the location of the numbers.

- VisualizeWagonSegmenter
A tool to output the images with a bounding box around the location of the numbers.

- edgeFilterWagon
A tool to visualize the edges in the whole wagon (as taken from the stitched image). A heatmap is made of the edges, and where there are a lot of edges, there probably is some text. The highest areas of the heatmap are shown in the screenshots. Lot's of text, not always the uic code (probably due to illumination).

- Number Recogniser using tessorflow
Recognise the UIC number using tessorflow. It's based on the input for Have fun with graffity.
The approach is simple. The image is cropped to a bounding box containing the estimated locations of the individual digits.
Then tessorflow is used on that. All the non-numbers are removed from it and the remaining number is padded with zeros to get it in the UIC format.

- Hazardous materials by heatmap
We had different ideas about doing this.
It was decided to calculate the distance to the orange colour.
The L2-distance to the colour is calculated.


