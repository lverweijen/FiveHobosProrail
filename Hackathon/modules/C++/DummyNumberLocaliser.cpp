#include <iostream>
#include <string>
#include <vector>
#include "opencv2/core.hpp"
#include "dumpJson.hpp"

using namespace std;
using namespace cv;

Point2f prototype[] =
{
	Point2f(0.1f, 0.3f),
	Point2f(0.2f, 0.3f),
	Point2f(0.2f, 0.4f),
	Point2f(0.5f, 0.4f),
	Point2f(0.5f, 0.5f),
	Point2f(0.1f, 0.5f)
};

vector<Point> makeLocalPolygon(int offset, Size size)
{
	vector<Point> result;
	for (const Point2f& point : prototype)
	{
		result.push_back(
			Point(
				point.x * size.width + offset,
				point.y * size.height
			)
		);
	}
	return result;
}

bool isInFrame(const vector<Point>& polygon, Size size)
{
	for (const Point& point : polygon)
	{
		if (point.x >= 0 && point.x < size.width &&
			point.y >= 0 && point.y < size.height )
		{
			return true;
		}
	}
	return false;
}

int main()
{
	while (!cin.eof())
	{
		string line;
		getline(cin, line);
		if (cin.fail()) break;
	
		FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);
		FileStorage outDta(line, FileStorage::WRITE | FileStorage::MEMORY);
		int wagonStart = data["wagonStart"].real();
		int wagonEnd = data["wagonEnd"].real();
		int wagonWidth = wagonEnd - wagonStart;
		FileNode frames = data["frames"];
		int height = frames[0]["height"].real();
		Size wagonSize(wagonWidth, height);
		Size frameSize(frames[0]["width"].real(), height);

		outDta << "wagonStart" << wagonStart;
		outDta << "numberLocations" << "[:";
		for (const FileNode& frame : frames)
		{
			int leftEdge = frame["leftEdge"].real();
			vector<Point> localPolygon = makeLocalPolygon(wagonStart - leftEdge, wagonSize);
			if (isInFrame(localPolygon, frameSize))
			{
				outDta << "{:";
				outDta << "frameNr" << static_cast<int>(frame["frameNr"].real());
				outDta << "polygons" << "[:";
				// Here you could make a loop to add multiple polygons. For now we just add one
				// The block is just for indentation :-)
				{
					outDta << "{:";
					outDta << "points" << "[:";
					for (const Point& point : localPolygon)
					{
						outDta << "[:" << point.x << point.y << "]";
					}
					outDta << "]"; // Close point list
					outDta << "score" << 0.95;
					outDta << "}"; // Close our single polygon
				}
				outDta << "]"; // Close the polygon array
				outDta << "}"; // Close the frame
			}
		}
		outDta << "]";
		dumpJson(cout, outDta);
	}

	cerr << "NumberLocaliser C++ has finished!" << endl;
}