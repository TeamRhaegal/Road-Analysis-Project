/*
 * acm.h
 *
 *  Created on: 27 nov. 2017
 *      Author: JulienCombattelli
 */

#ifndef ACM_H_
#define ACM_H_

#include <cstring>

#include "ObstacleDetector.hpp"

namespace acm
{

enum class AcmMode_t : uint8_t
{
	manual 			= 0,
	autonomous		= 1,
	obstAvoiding	= 2,
	emergencyStop	= 3
};

enum class RoadDetection_t : uint8_t
{
	middle = 0,
	right,
	rightcrit,
	left,
	leftcrit
};

enum class Direction_t : uint8_t
{
	middle = 0,
	leftCrit,
	rightCrit,
	left,
	right
};

enum class Speed_t : uint8_t
{
	stop = 0,
	normal,
	turbo
};


struct CarParamOut
{
	CarParamOut()
	{
		dir = Direction_t::middle;
		requestedDir = Direction_t::middle;
		speed = Speed_t::stop;
		sonar = 0;
		requestedMode = AcmMode_t::manual;
		mode = AcmMode_t::manual;

		requestedTurbo = false;
		turbo = false;
		moving = false;
		idle = true;

		autonomousLocked=0 ;
	}

	Direction_t dir;
	Direction_t requestedDir;
	Speed_t speed;
	uint8_t sonar;
	AcmMode_t requestedMode;
	AcmMode_t mode;
	bool requestedTurbo;
	bool turbo;
	bool moving;
	bool idle;

	int autonomousLocked;
};

struct CarParamIn
{
	CarParamIn()
	{
		obst = 0;
		speedMeasure = 0;
		dir = Direction_t::middle;
		bat = 0;
		roadDetection = RoadDetection_t::middle;
		prev_roadDetection = roadDetection ;
		memset(obstacles, 0, sizeof(obstacles));
	}

	uint8_t obst;
	obstacle obstacles[6];
	uint8_t speedMeasure;
	Direction_t dir;
	uint8_t bat;
	RoadDetection_t roadDetection ;
	RoadDetection_t prev_roadDetection ;
};

} // namespace acm

#endif /* ACM_H_ */
