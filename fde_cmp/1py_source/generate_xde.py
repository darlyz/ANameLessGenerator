#!/usr/bin/python3
'''
 Copyright: Copyright (c) 2019
 Created: 2019-7-18
 Author: Zhang_Licheng
 Title: main func of generate xde file to ges, html, md, xml, c or fortran
 All rights reserved
'''
from sys import argv,exit
from time import time
import re

# default folder
xde_folder = '../0xde_source'
ges_folder = '../2ges_target'
ifo_folder = '../4other_gen_file'

gen_obj = { 'ges'  : 1, \
            'Ccode': 0, \
            'Fcode': 0, \
            'xml'  : 0, \
            'html' : 0, \
            'md'   : 0, \
            'check': 1, }

def find_similar_paramater(parameter):

    fparam = ''
    for char in parameter:
        if char.isalpha():
            fparam += char

    comp = set()

    if len(fparam) == 1 :
        comp.add(fparam)

    elif len(fparam) >1 :
        for i in range(len(fparam)-1):
            for j in range(i+1,len(fparam)):
                comp.add(fparam[i]+'\\w*'+fparam[j])

    param_pattern = re.compile('|'.join(comp))

    match_keys = set()
    for keys in gen_obj.keys():
        if param_pattern.search(keys) != None:
            match_keys.add('-'+keys)

    if   len(match_keys) == 1:
        output  = f"Do you want to input '{list(match_keys)[0]}' " \
                + f"insteed of -{parameter}?\n"
        print(output)

    elif len(match_keys) > 1:
        output  = f"Do you want to input one of " \
                + f"'{', '.join(match_keys)}' insteed of -{parameter}?\n"
        print(output)

    else:
        output  = f"Do you want to input one of " \
                + f"'{', '.join(map(lambda x: '-'+x, gen_obj.keys()))}'" \
                + f" insteed of -{parameter}?\n"
        print(output)
# end find_similar_paramater()

def main(argvs=None):
    if argvs is None:
        argvs = argv

    for parameter in argvs[1:] :

        if  parameter[0] == '-':
            if parameter.count('=') == 1:

                parameter, val = parameter[1:].split('=')

                if parameter in gen_obj.keys():
                    try:
                        gen_obj[parameter] = int(val)
                    except ValueError:
                        print(f"Please input as '-{parameter}=[int]'.\n")

                else:
                    find_similar_paramater(parameter)


            else:
                if parameter[1:] in gen_obj.keys():
                    gen_obj[parameter[1:]] = 1

                else:
                    find_similar_paramater(parameter[1:])

        else:
            

if __name__ == "__main__":
    exit(main())
        
