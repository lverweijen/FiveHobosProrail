#include "dumpJson.hpp"

using namespace std;
using namespace cv;

void dumpJson(std::ostream& out, cv::FileStorage& storage)
{
	// We can't read from a memory storage that is still open for writing,
	// so we close it and open the resulting string for reading.
	FileStorage reader(storage.releaseAndGetString(), FileStorage::READ | FileStorage::MEMORY);
	dumpJson(out, reader.root());
	out << endl;
}

void dumpJson(std::ostream& out, const cv::FileNode& node)
{
	if (node.isNamed()) out << '"' << node.name() << "\": ";
	if (node.isSeq() || node.isMap())
	{
		char closeChar;
		if (node.isMap())
		{
			out << '{';
			closeChar = '}';
		}
		else
		{
			out << '[';
			closeChar = ']';
		}
		bool firstOne = true;
		for (const cv::FileNode& subNode : node)
		{
			if (firstOne) firstOne = false;
			else out << ", ";
			dumpJson(out, subNode);
		}
		out << closeChar;
	}
	else
	{
		if (node.isString()) out << '"' << node.string() << '"';
		else if (node.isInt() || node.isReal()) out << node.real();
		else if (node.isNone()) out << "null";
		else out << "\"Oops! Forgot about type " << node.type() << '"';
	}
}