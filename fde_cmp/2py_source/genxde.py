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

    # xde help system
    if argvs[1] in ['-h', '--h', '-H', '--H', '-help', '--help']:
        if len(argvs) == 2 or len(argvs) > 3 :
            print('type as: python genxde.py xdename gesname coortype')
        else:
            from xde_help import xde_help
            xde_help(argvs[2])
        return

    elif len(argvs) != 4:
        print('type as: python genxde.py xdename gesname coortype')
        return
    # help system to be improve

    # start parsing
    start = time()

    xdename, gesname, coortype = argvs[1], argvs[2], argvs[3]

    # xde elements and their line number
    xde_lists, list_addr = {}, {}

    # parse xde
    from parse_xde import parse_xde
    xdefile = open('../0xde_source/'+xdename, mode='r')
    error = parse_xde(gesname, coortype, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    # export xde element
    import json
    file = open('../1ges_target/'+gesname+'.json',mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()

    # generate ges by xde element
    from xde2ges import xde2ges
    gesfile = open('../1ges_target/'+gesname+'.ges1', mode='w')
    error = xde2ges(gesname, coortype, xde_lists, list_addr, gesfile)
    gesfile.close()
    if error: return

    end   = time()
    print ('parsing time: {}s'.format(end-start))

if __name__ == "__main__":
    exit(main())