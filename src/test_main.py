#!/usr/bin/env python3

import os
import sys
import shutil
import getopt


def need(param_name):
    while True:
        res = input('Need ' + param_name + '? (y/n): ')
        if res == 'y':
            return True
        if res == 'n':
            return False


files_dirs = os.listdir(os.path.relpath('../templates/test_template'))

for file_name in files_dirs:
    if '?' in file_name:
        arr = file_name.split('?')
        params = arr[:-1]
        new_name = arr[-1]
        print(params)
        print(new_name)


print('Argument List:', str(sys.argv))



