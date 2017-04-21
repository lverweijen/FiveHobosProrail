cmake_minimum_required(VERSION 2.8)

project(kijfhoek_cpp_modules)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11")

if (NOT DEFINED ENV{OpenCV_DIR})
	if (WIN32)
		set(OpenCV_DIR "C:/OpenCVgitBuild")
	else(WIN32)
		set(OpenCV_DIR "/usr/lib/opencv")
	endif(WIN32)
endif()
MESSAGE("Using OpenCV from location: " $ENV{OpenCV_DIR} " (Override by exporting OpenCV_DIR)")
find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(DummyRegionMatcher DummyRegionMatcher.cpp dumpJson.cpp)
add_executable(DummyWagonSegmenter DummyWagonSegmenter.cpp dumpJson.cpp)
add_executable(DummyNumberLocaliser DummyNumberLocaliser.cpp dumpJson.cpp)
add_executable(DummyNumberRecogniser DummyNumberRecogniser.cpp dumpJson.cpp)
add_executable(NumberRecogniser NumberRecogniser.cpp dumpJson.cpp)

target_link_libraries(DummyRegionMatcher ${OpenCV_LIBS})
target_link_libraries(DummyWagonSegmenter ${OpenCV_LIBS})
target_link_libraries(DummyNumberLocaliser ${OpenCV_LIBS})
target_link_libraries(DummyNumberRecogniser ${OpenCV_LIBS})
target_link_libraries(NumberRecogniser ${OpenCV_LIBS})
