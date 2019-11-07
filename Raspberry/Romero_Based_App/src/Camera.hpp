#ifndef SRC_CAMERA_HPP_
#define SRC_CAMERA_HPP_

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/core/core.hpp"
#include "opencv2/videoio/videoio.hpp"
#include "CarParam.hpp"
#include <iostream>

using namespace cv;

namespace acm
{

class Camera
{

private:
	VideoCapture cap;
	Mat img, hsv, val[3], hue, sat;

public:

	Camera() :
			cap(0)
	{
		if (!cap.isOpened())
		{  // check if we succeeded
			//std::cout << "Could not open camera" << std::endl;
			throw std::runtime_error("Unable to open the camera");
		}
	}

	int countLeft(Mat img)
	{
		int h = img.rows;
		int w = img.cols;
		int count = 0;
		for (int y = h / 4; y < h; y++)
		{
			for (int x = 0; x < w / 2; x++)
			{
				if (y >= (-h * x / (2 * w)) + (h / 2))
				{
					int pixel = img.at<int>(y, x, 0);
					if (pixel == 0)
					{
						count++;
					}
				}
			}
		}
		return count;
	}

	int countRight(Mat img)
	{
		int h = img.rows;
		int w = img.cols;
		int count = 0;
		for (int y = h / 4; y < h; y++)
		{
			for (int x = w / 2; x < w; x++)
			{
				if (y >= h * x / (2 * w))
				{
					int pixel = img.at<int>(y, x, 0);
					if (pixel == 0)
					{
						count++;
					}
				}
			}
		}
		return count;
	}

	RoadDetection_t placement(Mat img)
	{
		const int surface = (img.rows * img.cols * 5) / 16;

		const int low = surface * 0.25;
		const int critical = surface * 0.35;
		const int filled = surface * 0.6;
		//const int side = surface * 0.6;

		int l = countLeft(img);
		int r = countRight(img);
		if (r < low && l < low)
		{
			return RoadDetection_t::middle;
		}
		else if (r < low)
		{
			if (l < critical)
			{
				return RoadDetection_t::middle;
			}
			else if (l < filled)
			{
				return RoadDetection_t::left;
			}
			else
			{
				return RoadDetection_t::leftcrit;
			}
		}
		else if (l < low)
		{
			if (r < critical)
			{
				return RoadDetection_t::middle;
			}
			else if (r < filled)
			{
				return RoadDetection_t::right;
			}
			else
			{
				return RoadDetection_t::rightcrit;
			}
		}
		/*else if (r > critical && l > side){
		 return leftCrit;
		 }
		 else if (l > critical && r > side){
		 return rightCrit;
		 }*/
		/*else if (r < critical && l < critical){
		 return front;
		 }*/
		else
		{
			if (r > l)
			{
				return RoadDetection_t::rightcrit;
			}
			else
			{
				return RoadDetection_t::leftcrit;
			}
		}
	}

	RoadDetection_t process()
	{
		cap >> img; // get a new frame from camera
		/* Convert from Red-Green-Blue to Hue-Saturation-Value */
		cvtColor(img, hsv, CV_BGR2HSV);

		/* Split hue, saturation and value of hsv in val, get hue*/
		split(hsv, val);
		hue = val[0];

		inRange(hue, 60, 255, hue);


		return placement(hue);
	}

};

} // namespace acm

#endif /* SRC_CAMERA_HPP_ */
