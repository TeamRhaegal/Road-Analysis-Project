/*
 * prompt.c
 *
 *  Created on: Dec 4, 2017
 *      Author: jucom
 */

#include "prompt.h"

#include <stdio.h>

void print_prompt(void)
{
	printf(COLOR_BLUE "[GATT server]" COLOR_OFF "# ");
	fflush(stdout);
}
