/*
 * ObstacleDetector.hpp
 *
 *  Created on: Dec 10, 2017
 *      Author: jucom
 */

#ifndef SRC_OBSTACLEDETECTOR_HPP_
#define SRC_OBSTACLEDETECTOR_HPP_

#include <cstdio>
#include <cstdint>

#include "utils/prompt.h"

namespace acm
{

struct obstacle
{
	int detected;  //1 if obstacle detected else 0
	int mobile;    //1 if mobile ; 0 if static
	int dist;      //distance from the detected object
};

class ObstacleDetector
{
public:

	void detect(uint8_t data[6], obstacle obst[6])
	{
		for (int i = 0; i < 6; i++)
		{
			obst[i].detected = (data[i]) & 0x01;
			obst[i].mobile = ((data[i]) & 0x02) >> 1;
			obst[i].dist = ((data[i]) & 0xFC) >> 1;
		}
	}

	void print(obstacle obst[6])
	{
		for (int i = 0; i < 6; i++)
		{
			if (obst[i].detected)
			{
				/*printf("||=============================||\n");
				switch (i)
				{
				case 0:
					printf("OBASTACLE DETECTED ON || SIDE LEFT || (SL)\n");
					break;
				case 1:
					printf(
							"OBASTACLE DETECTED ON || FRONT SIDE LEFT || (FSL)\n");
					break;
				case 2:
					printf("OBASTACLE DETECTED ON || FRONT LEFT || (FL)\n");
					break;
				case 3:
					printf("OBASTACLE DETECTED ON || FRONT RIGHT || (FR)\n");
					break;
				case 4:
					printf(
							"OBASTACLE DETECTED ON || FRONT SIDE RIGHT || (FSR)\n");
					break;
				default:
					printf("OBASTACLE DETECTED ON || SIDE RIGHT || (SR)\n");
					break;
				}*/
				if (obst[i].mobile)
				{
					printf(COLOR_RED "Mobile 		   " COLOR_OFF);
				}
				else
				{
					printf(COLOR_GREEN "Static 		   " COLOR_OFF);
				}
				printf("Dist : %d cm\n", obst[i].dist);
			}
		}
	}
};

}  // namespace acm

#endif /* SRC_OBSTACLEDETECTOR_HPP_ */
