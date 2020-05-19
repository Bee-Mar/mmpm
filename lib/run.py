#!/usr/bin/env python3
from ctypes import cdll, c_char_p, c_int, POINTER, c_bool

libmmpm = cdll.LoadLibrary('./libmmpm.so')
modules = [
    [b'category', b'title'],
    [b'health', b'stuff']
]
display_table = libmmpm.display_table
rows, columns = len(modules), len(modules[0])

display_table.argtypes = [POINTER(POINTER(c_char_p)), c_int, c_int]
display_table.restype = None

allocate_table_memory = libmmpm.allocate_table_memory
allocate_table_memory.argtypes = [c_int, c_int]
allocate_table_memory.restype = POINTER(POINTER(c_char_p))
matrix = allocate_table_memory(rows, columns)

for i, row in enumerate(modules):
    for j, column in enumerate(modules[i]):
        matrix[i][j] = modules[i][j]

display_table(matrix, rows, columns)
