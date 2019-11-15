/*
 * Timerfd.hpp
 *
 *  Created on: Dec 9, 2017
 *      Author: jucom
 */

#ifndef SRC_TIMERFD_HPP_
#define SRC_TIMERFD_HPP_

#include <sys/timerfd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <cstring>
#include <cstdint>
#include <cstdio>
#include <functional>

extern "C" {
#include <mainloop.h>
}

class Timerfd
{
public:

	Timerfd() : m_duration_ms(0), m_userData(nullptr)
	{
		m_fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
	}

	Timerfd(unsigned int msec) : m_duration_ms(msec)
	{
		m_fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
		setDuration(msec);
	}

	~Timerfd()
	{
		::close(m_fd);
	}

	int setDuration(unsigned int msec)
	{
		m_duration_ms = msec;

		struct itimerspec itimer;
		unsigned int sec = msec / 1000;

		memset(&itimer, 0, sizeof(itimer));
		itimer.it_interval.tv_sec = 0;
		itimer.it_interval.tv_nsec = 0;
		itimer.it_value.tv_sec = sec;
		itimer.it_value.tv_nsec = (msec - (sec * 1000)) * 1000 * 1000;

		return timerfd_settime(m_fd, 0, &itimer, nullptr);
	}

	int fd() const { return m_fd; }

	template<typename TFunc>
	int mainloopAttach(TFunc&& callback, void* user_data)
	{
		m_callback = callback;
		m_userData = user_data;
		return mainloop_add_fd(m_fd, EPOLLIN | EPOLLET, onTimeout, this, nullptr);
	}

private:

	static void onTimeout(int fd, uint32_t events, void *user_data)
	{
		Timerfd* self = (decltype(self))user_data;
		uint64_t expired;
		ssize_t result;

		result = read(fd, &expired, sizeof(expired));
		if (result != sizeof(expired))
		{
			fprintf(stderr,"Timer callback error reading\n");
			return;
		}

		if(self->m_callback)
			self->m_callback(self->m_userData);

		self->setDuration(self->m_duration_ms);
	}

	int m_fd;
	unsigned int m_duration_ms;
	std::function<void(void*)> m_callback;
	void* m_userData;
};

#endif /* SRC_TIMERFD_HPP_ */

