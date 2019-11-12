#ifndef SRC_GATEWAY_HPP_
#define SRC_GATEWAY_HPP_

#include <Logger.hpp>
#include <cstdint>

#include "mainloop/Timerfd.hpp"
#include "mainloop/Signalfd.hpp"
#include "can/CanController.hpp"
#include "gatt/GattServer.hpp"
#include "CarParam.hpp"
#include "ObstacleDetector.hpp"
#include "Camera.hpp"

namespace acm
{

class Application
{
public:

	enum CanId : uint16_t
	{
		CanId_UltrasoundData 	= 1,
		CanId_DirectionCmd 		= 2,
		CanId_SpeedCmd 			= 3,
		CanId_DirectionData 	= 4,
		CanId_SpeedData 		= 5,
		CanId_BatteryData 		= 6
	};

	enum BleUuid : uint16_t
	{
		BleUuid_AcmService 		= 0x7db9,
		BleUuid_AcmCharState 	= 0xd288,	// Write without resp
		BleUuid_AcmCharFeedb 	= 0xc15b,	// Read and Notify
		BleUuid_AcmCharAlert 	= 0xdcb1 	// Read and Notify
	};

	enum UsSensorId : uint16_t
	{
		UsSensorId_SideLeft 		= 0,
		UsSensorId_FrontLeft 		= 1,
		UsSensorId_FrontSideLeft 	= 2,
		UsSensorId_FrontSideRight 	= 3,
		UsSensorId_FrontRight 		= 4,
		UsSensorId_SideRight 		= 5,
	};

	static constexpr unsigned int CAN_WRITE_PERIOD_MS 		= 25;
	static constexpr unsigned int AUTO_PROCESS_PERIOD_MS 	= 50; // TODO: choose wisely =)
	static constexpr unsigned int CAMERA_PROCESS_PERIOD_MS  = 200 ;

	static constexpr float SPEED_THRESHOLD_NORMAL_TURBO = 1.5f;

	struct UsSensorData
	{
		int detectionDistanceNormal_cm;
		int detectionDistanceTurbo_cm;
		float speedThresholdNormalTurbo_dmps;
	};

	inline static const std::map<UsSensorId, UsSensorData> usSensorParams
	{
		{UsSensorId_FrontLeft,		{40, 80,	SPEED_THRESHOLD_NORMAL_TURBO}},
		{UsSensorId_FrontRight,		{40, 80,	SPEED_THRESHOLD_NORMAL_TURBO}},
		{UsSensorId_FrontSideLeft, 	{20, 40,	SPEED_THRESHOLD_NORMAL_TURBO}},
		{UsSensorId_FrontSideRight, {20, 40,	SPEED_THRESHOLD_NORMAL_TURBO}},
		{UsSensorId_SideLeft, 		{5,  10,	SPEED_THRESHOLD_NORMAL_TURBO}},
		{UsSensorId_SideRight, 		{5,  10,	SPEED_THRESHOLD_NORMAL_TURBO}}
	};

	Application(const std::string& timeFilename, const std::string& csvFilename) :
		m_csvLogger(csvFilename), m_timeLogger(timeFilename) {}
	~Application() = default;

	void bleAdvertise();

	int run();

private:

	///////////////////////////////////////////////////////////////////////////
	//// Callbacks
	///////////////////////////////////////////////////////////////////////////
	void signalCallback(int signum);
	void autonomousControl();
	void systemControl();
	void cameraProcess();
	void canOnTimeToSend();
	void canOnDataReceived(int fd, uint32_t events);
	void bleOnTimeToSend(void* user_data);
	void bleOnDataReceived(struct gatt_db_attribute *attrib,
			unsigned int id, uint16_t offset, const uint8_t *value, size_t len,
			uint8_t opcode, struct bt_att *att);

	//Timerfd timer;
	Timerfd m_timerCanSend;
	Timerfd m_timerAutonomousProcess;
	Timerfd m_timerCameraProcess;
	Signalfd m_signal;

	CanController m_canController;
	GattServer m_gattServer;
	CarParamOut m_carParamOut;
	CarParamIn m_carParamIn ;
	ObstacleDetector m_obstacleDetector;
	Camera m_camera;
	CsvLogger m_csvLogger;
	TimeLogger m_timeLogger;
};

} // namespace acm

#endif /* SRC_GATEWAY_HPP_ */
