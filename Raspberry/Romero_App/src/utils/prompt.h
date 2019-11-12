/*
 * prompt.h
 *
 *  Created on: Dec 4, 2017
 *      Author: jucom
 */

#ifndef SRC_BLE_PROMPT_H_
#define SRC_BLE_PROMPT_H_

#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PRLOG(...) \
	do { \
		printf(__VA_ARGS__); \
		print_prompt(); \
	} while (0)

#define COLOR_OFF	"\x1B[0m"
#define COLOR_RED	"\x1B[0;91m"
#define COLOR_GREEN	"\x1B[0;92m"
#define COLOR_YELLOW	"\x1B[0;93m"
#define COLOR_BLUE	"\x1B[0;94m"
#define COLOR_MAGENTA	"\x1B[0;95m"
#define COLOR_BOLDGRAY	"\x1B[1;30m"
#define COLOR_BOLDWHITE	"\x1B[1;37m"

void print_prompt(void);

#ifdef __cplusplus
}
#endif

#endif /* SRC_BLE_PROMPT_H_ */
