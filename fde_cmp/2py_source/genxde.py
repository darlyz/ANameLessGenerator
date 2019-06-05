#!/usr/bin/python3
'''
 Copyright: Copyright (c) 2019
 Created: 2019-3-30
 Author: Zhang_Licheng
 Title: main func of generate xde file to ges
 All rights reserved
'''
from sys import argv,exit
from time import time

# ...$python genfde.py filename elemtype
def main(argvs=None):
    if argvs is None:
        argvs = argv

    if argvs[1] == '-h' or argvs[1] == '--h' \
    or argvs[1] == '-H' or argvs[1] == '--H' \
    or len(argvs) != 4:
        print('type as: python genxde.py xdename gesname coortype')
        return

    start = time()

    xdename  = argvs[1]
    gesname  = argvs[2]
    coortype = argvs[3]

    list_addr = {}
    xde_lists = {}

    from parse_xde import parse_xde
    xdefile = open('../0xde_source/'+xdename, mode='r')
    error = parse_xde(gesname, coortype, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    import json
    file = open('../1ges_target/'+gesname+'.json',mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()

    file = open('../1ges_target/'+gesname+'.json1',mode='w')
    file.write(json.dumps(list_addr,indent=4))
    file.close()

    from xde2ges import xde2ges
    gesfile = open('../1ges_target/'+gesname+'.ges1', mode='w')
    error = xde2ges(gesname, coortype, xde_lists, list_addr, gesfile)
    gesfile.close()
    if error: return

    end   = time()
    print ('parsing time: {}s'.format(end-start))

if __name__ == "__main__":
    exit(main())