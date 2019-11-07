/*
 * CanController.h
 *
 *  Created on: 9 d�c. 2017
 *      Author: JulienCombattelli
 */

#ifndef SRC_CANCONTROLLER_HPP_
#define SRC_CANCONTROLLER_HPP_

#include <cstdint>
#include <string>
#include <cstring>
#include <map>
#include "CanSocket.hpp"
extern "C" {
#include "mainloop.h"
}

class CanController
{
public:
	CanController() :
		m_callbackWrite(nullptr),
		m_callbackRead(nullptr)
	{

	}

	void open(const std::string& ifname)
	{
		m_can_socket.open(ifname);
	}

	int registerMessageType(uint16_t id, size_t size)
	{
		if (size > CAN_MAX_DLEN)
		{
			return -1;
		}
		m_message_size[id] = size;
		return 0;
	}

	int sendMessage(uint16_t id, uint8_t* data)
	{
		if (m_message_size.find(id) == m_message_size.end())
		{
			return -1;
		}
		size_t size = m_message_size[id];

		struct can_frame frame;
		frame.can_id = id;
		frame.can_dlc = size;
		memcpy(frame.data, data, size);

		return m_can_socket.write(frame);
 	}

	// TODO: read operation

	int fd() const { return m_can_socket.fd(); }

	template<typename TFunc>
	int mainloopAttachWrite(TFunc&& callback, void* user_data)
	{
		m_callbackWrite = callback;
		return mainloop_add_fd(m_can_socket.fd(), EPOLLOUT, m_callbackWrite, user_data, NULL);
	}

	template<typename TFunc>
	int mainloopAttachRead(TFunc&& callback, void* user_data)
	{
		m_callbackRead = callback;
		return mainloop_add_fd(m_can_socket.fd(), EPOLLIN, m_callbackRead, user_data, NULL);
	}

private:

	std::map<uint16_t,size_t> m_message_size;

	CanSocket m_can_socket;

	mainloop_event_func m_callbackWrite;
	mainloop_event_func m_callbackRead;
};

#endif /* SRC_CANCONTROLLER_HPP_ */
