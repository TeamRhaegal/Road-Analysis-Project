/*
 * Csv.hpp
 *
 *  Created on: Jan 11, 2018
 *      Author: coegre
 */

#ifndef LOGGER_HPP_
#define LOGGER_HPP_

#include "CarParam.hpp"
#include "fstream"

namespace acm
{

class CsvLogger
{
public:

	CsvLogger(const std::string &fileName)
	{
		m_fileName = fileName;
		m_file = fopen(m_fileName.c_str(), "w");
	}
	~CsvLogger()
	{
		fclose(m_file);
	}

	void generate_csv(const CarParamOut &m_carParamOut, const CarParamIn &m_carParamIn)
	{
		uint8_t speed;
		AcmMode_t currentMode;
		int obst_detected = 0;
		int obst_mobile = 0;
		int obst_min_dist = 0;

		speed =  m_carParamIn.speedMeasure * 0.36; // Speed conversion from dm/s to km/h

		if (m_carParamOut.mode == AcmMode_t::obstAvoiding or m_carParamOut.mode == AcmMode_t::manual)
			currentMode = AcmMode_t::manual;

		else if (m_carParamOut.mode == AcmMode_t::emergencyStop or m_carParamOut.mode == AcmMode_t::autonomous)
			currentMode = AcmMode_t::autonomous;


		fprintf(m_file, "%d;%d;%d;%d;%d;%d;%d;", (int)currentMode, (int)m_carParamOut.requestedMode, speed, m_carParamOut.turbo,
											   (int)m_carParamIn.dir, (int)m_carParamOut.dir, (int)m_carParamIn.roadDetection);

		for (int i = 0 ; i < 6 ; i++)
		{
			if (m_carParamIn.obstacles[i].detected == 1 and obst_detected == 0)
				obst_detected = 1;
			if (m_carParamIn.obstacles[i].mobile == 1 and obst_mobile == 0)
				obst_mobile = 1;
			if (m_carParamIn.obstacles[i].detected == 1)
			{
				if(obst_min_dist == 0)
					obst_min_dist = m_carParamIn.obstacles[i].dist;
				else if (m_carParamIn.obstacles[i].dist < obst_min_dist)
					obst_min_dist = m_carParamIn.obstacles[i].dist;
			}
		}
		fprintf(m_file, "%d;%d;%d;",obst_detected,obst_mobile,obst_min_dist);
		fprintf(m_file,"\n");
	}

private:

	std::string m_fileName;
	FILE *m_file;
};

class TimeLogger
{
public:

	TimeLogger(const std::string &fileName)
	{
		m_fileName = fileName;
		m_file.open(m_fileName);
	}
	~TimeLogger() = default;

	void write(const std::string& header, double time)
	{
		m_file << header << time << std::endl;
	}

private:

	std::string m_fileName;
	std::ofstream m_file;
};

} // namespace acm

#endif /* LOGGER_HPP_ */
