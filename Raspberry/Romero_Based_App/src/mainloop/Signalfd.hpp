/*
 * Signalfd.hpp
 *
 *  Created on: Dec 9, 2017
 *      Author: jucom
 */

#ifndef SRC_SIGNALFD_HPP_
#define SRC_SIGNALFD_HPP_

#include <signal.h>

extern "C" {
#include <mainloop.h>
}

class Signalfd
{
public:

	Signalfd() : m_callback(nullptr)
	{
		sigemptyset(&m_mask);
	}

	int add(int signum)
	{
		return sigaddset(&m_mask, signum);
	}

	template<typename TFunc>
	int mainloopAttach(TFunc&& callback, void* user_data)
	{
		m_callback = callback;
		return mainloop_set_signal(&m_mask, m_callback, user_data, NULL);
	}

private:

	sigset_t m_mask;
	mainloop_signal_func m_callback;
};



#endif /* SRC_SIGNALFD_HPP_ */
