/*
 * CanSocket.cpp
 *
 *  Created on: Dec 6, 2017
 *      Author: jucom
 */

#include "CanSocket.hpp"

#include <cstring>
#include <cstdio>
#include <unistd.h>

CanSocket::CanSocket() :
	m_socket(-1)
{

}

CanSocket::~CanSocket()
{
	close();
}

void CanSocket::open(const std::string& ifname)
{
	sockaddr_can addr;
	ifreq ifr;

	if((m_socket = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0)
	{
		fprintf(stderr, "Failed to create CAN socket\n");
		close();
	}

	strcpy(ifr.ifr_name, ifname.c_str());
	ioctl(m_socket, SIOCGIFINDEX, &ifr);

	addr.can_family  = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;

	printf("%s at index %d\n", ifname.c_str(), ifr.ifr_ifindex);

	if(bind(m_socket, (sockaddr*)&addr, sizeof(addr)) < 0)
	{
		fprintf(stderr, "Failed to bind CAN socket\n");
		close();
	}
}

void CanSocket::close()
{
	::close(m_socket);
}

ssize_t CanSocket::write(const can_frame& frame)
{
	return ::write(m_socket, &frame, sizeof(frame));
}

ssize_t CanSocket::read(can_frame& frame)
{
	ssize_t nbytes = ::read(m_socket, &frame, sizeof(frame));

	if(nbytes < 0)
	{
		fprintf(stderr, "Failed to read CAN socket\n");
		return nbytes;
	}

	if(nbytes < (decltype(nbytes))sizeof(struct can_frame))
	{
		fprintf(stderr, "Incomplete CAN frame readed\n") ;
		return nbytes;
	}

	return nbytes;
}

int CanSocket::fd() const
{
	return m_socket;
}
