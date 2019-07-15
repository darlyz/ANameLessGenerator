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
import re as regx

xde_folder = '../0xde_source/'
ges_folder = '../2ges_target/'
ifo_folder = '../4other_gen_file/'

def genxde(xdename, gesname, coortype):

    # start parsing
    start = time()

    # xde elements and their line number
    xde_lists, list_addr, ges_info = {}, {}, {}

    # get shap, gaus, dim and axis information into ges_info
    from felac_data import prepare_to_genxde
    prepare_to_genxde(gesname, coortype, ges_info)

    # parse xde
    from parse_xde import parse_xde
    xdefile = open(xde_folder + xdename, mode='r')
    error = parse_xde(ges_info, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    # generate ges by xde element
    from xde2ges import xde2ges
    gesfile = open(ges_folder + gesname+'.ges', mode='w')
    error = xde2ges(ges_info, xde_lists, list_addr, gesfile)
    gesfile.close()
    if error: return

    # export xde element
    import json
    file = open(ifo_folder + gesname+'.json', mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

# ...$python genfde.py filename elemtype axis
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

    from felac_data import get_felac_data
    get_felac_data()

    genxde(argvs[1], argvs[2], argvs[3])

if __name__ == "__main__":
    exit(main())