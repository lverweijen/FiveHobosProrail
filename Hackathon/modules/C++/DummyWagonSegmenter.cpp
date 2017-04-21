#include <cmath>
#include <iostream>
#include <string>
#include <map>
#include "opencv2/core.hpp"
#include "dumpJson.hpp"

using namespace std;
using namespace cv;

int main()
{
	int wagonStart = 0;

	while (!cin.eof())
	{
		string line;
		getline(cin, line);
		if (cin.fail()) break;
	
		FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);
		int leftEdge;
		data["leftEdge"] >> leftEdge;
		if (abs(leftEdge - wagonStart) > 3300)
		{
			int wagonEnd = wagonStart + 3300;
			FileStorage outData(".yml", FileStorage::WRITE | FileStorage::MEMORY);
			outData << "wagonStart" << wagonStart;
			outData << "wagonEnd" << wagonEnd;
			dumpJson(cout, outData);

			wagonStart = wagonEnd;
		}
	}

	cerr << "WagonSegmenter C++ has finished!" << endl;
}