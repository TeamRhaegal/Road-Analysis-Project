/*
 * Timing.hpp
 *
 *  Created on: Jan 16, 2018
 *      Author: jucom
 */

#ifndef UTILS_TIMING_HPP_
#define UTILS_TIMING_HPP_

#include <chrono>

template<typename TCallable, typename... Args>
double getDuration(TCallable&& callable, Args&&... args)
{
	auto start = std::chrono::steady_clock::now();

	callable(std::forward(args)...);

	auto end = std::chrono::steady_clock::now();

	return std::chrono::duration <double, std::milli>(end-start).count();
}

#endif /* UTILS_TIMING_HPP_ */


