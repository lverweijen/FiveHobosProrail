#ifndef JSON_OUTPUT_HPP
#define JSON_OUTPUT_HPP

#include <ostream>
#include <string>
#include <vector>
#include <map>
#include "opencv2/core.hpp"

void dumpJson(std::ostream& out, cv::FileStorage& storage);
void dumpJson(std::ostream& out, const cv::FileNode& node);

#endif