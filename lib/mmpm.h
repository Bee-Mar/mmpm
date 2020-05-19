#ifndef MMPM_H
#define MMPM_H

#include "fort.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

void display_table(const char ***modules, const int rows, const int columns);
char ***allocate_table_memory(const int rows, const int columns);

#endif
