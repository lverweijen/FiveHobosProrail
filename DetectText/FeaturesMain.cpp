
/*
    Copyright 2012 Andrew Perrault and Saurav Kumar.

    This file is part of DetectText.

    DetectText is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DetectText is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DetectText.  If not, see <http://www.gnu.org/licenses/>.
*/
#include <cassert>
#include <fstream>
#include <exception>
#include <iostream>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "TextDetection.h"

using namespace std;
using namespace cv;
using namespace DetectText;
RNG rng(12345);

void convertToFloatImage ( Mat& byteImage, Mat& floatImage )
{
    byteImage.convertTo(floatImage, CV_32FC1, 1 / 255.);
}

class FeatureError: public std::exception {
    std::string message;
public:
    FeatureError(const std::string & msg, const std::string & file) {
        std::stringstream ss;

        ss << msg << " " << file;
        message = msg.c_str();
    }
    ~FeatureError() throw () {
    }
};

Mat loadByteImage(const char * name) {
    Mat image = imread(name);

    if (image.empty()) {
        return Mat();
    }
    cvtColor(image, image, CV_BGR2RGB);
    return image;
}

Mat loadFloatImage(const char * name) {
    Mat image = imread(name);

    if (image.empty()) {
        return Mat();
    }
    cvtColor(image, image, CV_BGR2RGB);
    Mat floatingImage(image.size(), CV_32FC3);
    image.convertTo(floatingImage, CV_32F, 1 / 255.);
    return floatingImage;
}

string Type2Str(int type)
{
  string r;

  uchar depth = type & CV_MAT_DEPTH_MASK;
  uchar chans = 1 + (type >> CV_CN_SHIFT);

  switch ( depth ) {
    case CV_8U:  r = "8U"; break;
    case CV_8S:  r = "8S"; break;
    case CV_16U: r = "16U"; break;
    case CV_16S: r = "16S"; break;
    case CV_32S: r = "32S"; break;
    case CV_32F: r = "32F"; break;
    case CV_64F: r = "64F"; break;
    default:     r = "User"; break;
  }

  r += "C";
  r += (chans+'0');

  return r;
}

string ContourToPolygons(std::vector<std::vector<Point> >& contours)
{
    ostringstream ss;

    ss << "\"polygons\":[";
    for(int i = 0; i < contours.size(); i++)
    {
        if(i != 0)
        {
            ss << ",";
        }

        ss << "{\"score\":1.0," << "\"points\":[";
        for(int j = 0; j < contours[i].size(); j++)
        {
           if(j != 0)
           {
                ss << ",";
           }

           ss << "[" << contours[i][j].x << "," << contours[i][j].y << "]";
        }
        ss << "]}";
    }
    ss << "]";
    
    return ss.str();
}

void GetImageFrameNumbers(const FileNode& input, std::vector<int>& frameNumbers)
{
    FileNodeIterator it = input.begin(), it_end = input.end();
    for (; it != it_end; ++it)
    {
        frameNumbers.push_back((int)(*it)["frameNr"] );
    }
}

void GetFilenames(const FileNode& input, std::vector<string>& fileNames)
{
    FileNodeIterator it = input.begin(), it_end = input.end();
    for (; it != it_end; ++it)
    {
        fileNames.push_back( (string)(*it)["filename"] );
    }
}

string GetOutputFilename(int frameNr)
{
    string baseDir = "output/frames/"; 

    std::ostringstream ss;
    ss << baseDir << "swt_" << frameNr << ".png";
    return ss.str();
}

void GetOutputFilenames(const FileNode& input, std::vector<string>& fileNames)
{
    std::vector<int> frameNumbers;

    GetImageFrameNumbers(input, frameNumbers);

    for(int frameNr: frameNumbers)
    {
        fileNames.push_back(GetOutputFilename(frameNr));
    }
}

void GetContours(cv::Mat& image, std::vector<vector<Point> >& contours)
{
    std::vector<Vec4i> hierarchy;
    
    cv::Mat greyImage(image.size(), CV_8UC1);
    cvtColor(image, greyImage, CV_BGR2GRAY);

    findContours(greyImage, contours, hierarchy, CV_RETR_LIST, CHAIN_APPROX_SIMPLE, Point(0, 0) );
    
    /// Draw contours
    Mat drawing = Mat::zeros( image.size(), CV_8UC3 );
      
    for( int i = 0; i < contours.size(); i++)
    {
       Scalar color = Scalar( rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255) );
       drawContours( drawing, contours, i, color, 2, 8, hierarchy, 0, Point() );
    }
}  

void TextDetection(string inputFile, Mat& outputCombined) {
    Mat byteQueryImage = loadByteImage(inputFile.c_str());
    if (byteQueryImage.empty()) {
        cerr << "couldn't load query image" << endl;
        return;
    }

    // Detect text in the image
    Mat outputLightOnDark = textDetection(byteQueryImage, true);
    Mat outputDarkOnLight = textDetection(byteQueryImage, false);

    Mat outputLightOnDarkInv; 
    Mat outputDarkOnLightInv;

    cv::bitwise_not(outputLightOnDark, outputLightOnDarkInv);
    cv::bitwise_not(outputDarkOnLight, outputDarkOnLightInv);

    outputCombined = outputDarkOnLightInv + outputLightOnDarkInv;
}

int HandleModuleInput()
{
	while (!cin.eof())
	{
		string line;
		getline(cin, line);

		if (cin.fail())
		{
			return -1;
		}

        FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);
	
		try
		{
            ostringstream out;
            out << "{\"numberLocations\":[";

            std::vector<string> fileNames;
            GetFilenames(data["frames"], fileNames);

            std::vector<string> outputFileNames;
            GetOutputFilenames(data["frames"], outputFileNames);

            std::vector<int> frameNumbers;
            GetImageFrameNumbers(data["frames"], frameNumbers);

            // TODO: processes image multiple times if image contains multiple wagons
            for(int i = 0; i < fileNames.size(); i++)
            {                
                Mat outputCombined;
                TextDetection(fileNames[i], outputCombined);
                
                std::vector<vector<Point> > contours;
                GetContours(outputCombined, contours);

                if(i != 0)
                {
                    out << ",";
                }

                out << "{\"frameNr\":" << frameNumbers[i] << ","
                    << "\"swtMask\":" << "\"" << outputFileNames[i] <<  "\"" <<","
                    << ContourToPolygons(contours) << "}";

                cv::imwrite(outputFileNames[i], outputCombined);
            }

			FileStorage memoryReader(line, FileStorage::READ | FileStorage::MEMORY);
			int wagonStart = (int)memoryReader["wagonStart"]; 
            out << "],\"wagonStart\":" << wagonStart << "}";

            cout << out.str() << endl;
		}
		catch( cv::Exception& e )
		{
            return -1;
		}
	}
}

int main(int argc, char** argv)
{
    return HandleModuleInput();
}
