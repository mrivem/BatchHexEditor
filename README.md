# BatchHexEditor

Batch Hex Editor v1.2
Author: Matías Rivera Maldonado @mrivem

Small and to-the-point utility to make quick hex modifications to many files via an instructions file

Usage:
python BatchHex.py path_to_instruction_file
BatchHex.exe path_to_instruction_file

Example of a instruction file line:
file_name="path\to\file.ini",offset=0,data=FEFEFE

file_name: Full path to file to modify
offset: Byte offset from which changes will be made
data: Raw block of hex data to insert in the file
