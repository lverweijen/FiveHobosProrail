#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <cmath>
#include "opencv2/core.hpp"
#include "dumpJson.hpp"

using namespace std;
using namespace cv;

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

int main()
{
	while (!cin.eof())
	{
		string line;
		getline(cin, line);
		if (cin.fail()) break;
	
		FileStorage data(line, FileStorage::READ | FileStorage::MEMORY);
		int frameSum = 0;
		FileNode numberLocations = data["numberLocations"];
		for (const FileNode& numberLocation : numberLocations)
		{
			frameSum += numberLocation["frameNr"].real();
		}
		float averageFrame = frameSum / static_cast<float>(numberLocations.size());
		int digits = static_cast<int>(averageFrame * 218); // Just some random multiplication to get more digits
		int checkSum = generateUICChecksum(digits);
		stringstream uic;
		uic << setfill('0') << setw(11) << digits << '-' << checkSum;

		FileStorage outData(".yml", FileStorage::WRITE | FileStorage::MEMORY);
		outData << "wagonStart" << data["wagonStart"].real();
		outData << "number" << uic.str();
		dumpJson(cout, outData);
	}

	cerr << "NumberRecogniser C++ has finished!" << endl;
}