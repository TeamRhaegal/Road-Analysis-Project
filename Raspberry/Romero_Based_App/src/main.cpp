/*
 * main.cpp
 *
 *  Created on: Dec 6, 2017
 *      Author: jucom
 */
#include "common-defs.h"
#include "AcmApplication.hpp"

int main()
{
	acm::Application app("time.log","test.csv");
	return app.run();
}
