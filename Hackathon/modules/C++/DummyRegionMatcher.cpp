#include <iostream>
#include <string>
#include "opencv2/core.hpp"
#include "dumpJson.hpp"

using namespace std;
using namespace cv;

int main()
{
	while (!cin.eof())
	{
		string line;
		getline(cin, line);
		if (cin.fail()) break;
	
		FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);
		int frameNr;
		data["frameNr"] >> frameNr;
		int offset = static_cast<int>(frameNr * 0.2 * data["width"].real());

		FileStorage outData(".yml", FileStorage::WRITE | FileStorage::MEMORY);
		outData << "leftEdge" << offset;
		outData << "frameNr" << frameNr;
		dumpJson(cout, outData);
	}

	cerr << "RegionMatcher C++ has finished!" << endl;
}