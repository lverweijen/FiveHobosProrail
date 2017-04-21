#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include "dumpJson.hpp"
#include "opencv2/core.hpp"
#include "opencv2/text.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"

using namespace std;
using namespace cv;
using namespace cv::text;

int generateUICChecksum(long digits)
{
	bool evenPosition = false;
	int sum = 0;
	while (digits > 0)
	{
		int factor = evenPosition ? 1 : 2;
		int digit = (digits % 10) * factor;
		while (digit > 0)
		{
			sum += digit % 10;
			digit /= 10;
		}
		digits /= 10;
		evenPosition = !evenPosition;
	}
	int roundUp = 10 * static_cast<int>(ceil(sum / 10.0f));
	return roundUp - sum;
}

string makeSenseOfIt(const vector<string>& options)
{
	const int idealLength = 12;
	string bestOption = "";
	int bestAmount = 0;
	bool bestCorrectUIC = false;
	for (string option : options)
	{
		int lastSub = max(0, static_cast<int>(option.size() - idealLength));
		for (int sub = 0; sub <= lastSub; sub++)
		{
			string candidate = option.substr(sub, idealLength);
			long number = stol(candidate);
			int numDigits = log10(number) + 1;
			int checksum = number % 10;
			number /= 10;
			stringstream formatted;
			formatted << setfill('0') << setw(11) << number << '-' << checksum;
			bool thisCorrectUIC = generateUICChecksum(number) == checksum;

			bool newBest = false;
			if (thisCorrectUIC)
			{
				if (numDigits == idealLength) return formatted.str();
				else newBest = true;
			}
			else newBest = !bestCorrectUIC && abs(idealLength - numDigits) < abs(idealLength - bestAmount);
			if (newBest)
			{
				bestOption = formatted.str();
				bestAmount = numDigits;
				bestCorrectUIC = thisCorrectUIC;
			}
		}
	}
	return bestOption;
}

// This is the only frame info we'll need so we just ignore the other fields
typedef struct FrameInfo
{
	int leftEdge;
	string filename;
} FrameInfo;

map<int, FrameInfo> buildFrameLookup(const FileNode& frames)
{
	map<int, FrameInfo> result;
	for (const FileNode& frame : frames)
	{
		FrameInfo newFrame;
		newFrame.leftEdge = frame["leftEdge"].real();
		newFrame.filename = frame["filename"].string();
		result[static_cast<int>(frame["frameNr"].real())] = newFrame;
	}
	return result;
}

vector<Point> getPolygon(const FileNode& points)
{
	vector<Point> result;
	for (const FileNode& point : points)
	{
		result.push_back(Point(point[0].real(), point[1].real()));
	}
	return result;
}

int main(int argc, const char * argv[])
{
	bool debug = argc > 1; // Too lazy to actually parse it. Pass any argument at all to enable debug.

	string wanted = "01234567890";
	string speckles = ".'`-";
	string whitespace = " \n\t";
	string whitelist = wanted + speckles; // We allow speckles to give tesseract something to assign noise to
	string unwanted = speckles + whitespace;

	vector<Mat> kernels;
	kernels.push_back((Mat_<float>(3,3) << -1,  0, -1,  0,  4,  0, -1,  0, -1)); // Bright text on dark background
	kernels.push_back((Mat_<float>(3,3) <<  1,  0,  1,  0, -4,  0,  1,  0,  1)); // Dark text on bright background
	Mat dilateKernel = getStructuringElement(MORPH_RECT, Size(5, 5));

	Ptr<OCRTesseract> ocr = OCRTesseract::create(NULL, NULL, whitelist.c_str());
	while (!cin.eof())
	{
		string line;
		getline(cin, line);
		if (cin.fail()) break;

		FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);

		vector<string> possibleNumbers;
		map<int, FrameInfo> frameLookup = buildFrameLookup(data["frames"]);
		FileNode numberLocations = data["numberLocations"];
		for (const FileNode& numberLocation : numberLocations)
		{
			int frameNr = numberLocation["frameNr"].real();
			Mat image = imread(frameLookup[frameNr].filename);
			Mat mask(image.rows, image.cols, CV_8UC1, Scalar(0, 0, 0));
			Mat gray;
			cvtColor(image, gray, COLOR_BGR2GRAY);

			// We combine all polygons into one big mask and do one detection per frame
			vector<vector<Point> > polygons;
			for (const FileNode& polygonNode : numberLocation["polygons"])
			{
				polygons.push_back(getPolygon(polygonNode["points"]));
			}
			fillPoly(mask, polygons, Scalar(255));
			dilate(mask, mask, dilateKernel);

			for (const Mat& kernel : kernels)
			{
				Mat edges, masked;
				filter2D(gray, edges, -1, kernel);
				edges.copyTo(masked, mask);

				string output;
				vector<Rect>   boxes;
				vector<string> words;
				vector<float>  confidences;
				ocr->run(masked, output, &boxes, &words, &confidences, OCR_LEVEL_WORD);
				for (char c : unwanted)
				{
					output.erase(remove(output.begin(), output.end(), c), output.end());
				}
				if (output.size() > 0) possibleNumbers.push_back(output);

				if (debug)
				{
					cerr << "output: _" << output << "_" << endl;
					vector<Mat> layers;
					layers.push_back(gray);
					layers.push_back(masked);
					layers.push_back(mask);
					Mat annotated;
					merge(layers, annotated);
					for (int index = 0; index < boxes.size(); index++)
					{
						rectangle(annotated, boxes[index], Scalar(128, 50 + 2 * confidences[index], 0));
						Point origin = boxes[index].tl()-Point(1,1);
						if (origin.y < 10) origin.y = boxes[index].br().y + 10;
						putText(annotated, "\"" + words[index] + "\"", origin, FONT_HERSHEY_SIMPLEX, 0.45f, Scalar(255,255,0));
					}
					if (debug) imshow("Red: mask Yellow: Text", annotated);

					if (waitKey(0) == 27) return 0;
				}
			}
		}

		FileStorage outData(".yml", FileStorage::WRITE | FileStorage::MEMORY);
		outData << "wagonStart" << data["wagonStart"].real();
		outData << "number" << makeSenseOfIt(possibleNumbers);
		dumpJson(cout, outData);
	}

	cerr << "NumberRecogniser C++ has finished!" << endl;
}