/*
 * CanSocket.h
 *
 *  Created on: Dec 6, 2017
 *      Author: jucom
 */

#ifndef SRC_CANSOCKET_HPP_
#define SRC_CANSOCKET_HPP_

#include <net/if.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>

#include <linux/can.h>
#include <linux/can/raw.h>

#include <string>

class CanSocket
{
public:

	CanSocket();
	~CanSocket();

	void open(const std::string& ifname);

	void close();

	ssize_t write(const can_frame& frame);

	ssize_t read(can_frame& frame);

	int fd() const;

private:

	int m_socket;
};

#endif /* SRC_CANSOCKET_HPP_ */
