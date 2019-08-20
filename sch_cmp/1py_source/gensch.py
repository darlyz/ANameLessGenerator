#!/usr/bin/python3
'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: main func of generate sch file to html, md, xml, c or fortran
 All rights reserved
'''
from sys import argv,exit
from time import time
import re

# default folder
sch_folder = '../0sch_source/'
c_folder   = '../2c_target/'
ifo_folder = '../3other_gen_file/'

gen_obj = { 'Ccode': 1, \
            'Fcode': 0, \
            'xml'  : 0, \
            'html' : 0, \
            'md'   : 0, \
            'check': 1, }

def gensch(schname, fieldSN):

    # start parsing
    start = time()

    # sch element and their line number
    sch_dict = {}
    sch_addr = {}

    # parse sch
    from parse_sch import parse_sch
    schfile = open(sch_folder + schname + '.sch', mode='r',encoding='gb18030', errors='ignore')
    error = parse_sch(sch_dict, sch_addr, schfile)
    schfile.close()
    if error: return

    # generate c by ges_dict
    #if gen_obj['Ccode'] > 0:
    #    from sch2c import sch2c
    #    cfile = open(c_folder + schname + '.c', mode = 'w')
    #    ges2c(sch_dict, cfile)
    #    cfile.close()

    # generate html by xde element to preview
    #if gen_obj['html'] > 0:
    #    from sch2html import sch2html
    #    htmlfile = open(ifo_folder + schname + '.html', mode='w')
    #    xde2html(sch_dict, htmlfile)
    #    htmlfile.close()

    # generate markdown by xde element to preview
    #if gen_obj['md'] > 0:
    #    from sch2md import sch2md
    #    mdfile = open('ifo_folder + schname +'.md', mode='w')
    #    xde2md(sch_dict, mdfile)
    #    mdfile.close()

    # ...

    # export xde element
    #import json
    #file = open(ifo_folder + schname+'.json', mode='w')
    #file.write(json.dumps(sch_dict,indent=4))
    #file.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

def main(argvs=None):
    if argvs is None:
        argvs = argv

    #if len(argvs) == 1:
    #
    #    command_help()  
    #    return

    schname = argvs[1].replace('\\','/').rstrip('/')
    fieldSN = argvs[2]

    gensch(schname, fieldSN)

if __name__ == "__main__":
    exit(main())