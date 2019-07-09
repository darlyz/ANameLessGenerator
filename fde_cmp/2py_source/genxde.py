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

def prepare(gesname, coortype, ges_info):
    ges_shap_type = regx.search(r'[ltqwc][1-9][0-9]*',gesname,regx.I).group()
    ges_gaus_type = regx.search(r'g[1-9][0-9]*',gesname,regx.I)
    if ges_gaus_type != None:
        ges_gaus_type = ges_gaus_type.group()
    else: ges_gaus_type = ges_shap_type

    ges_shap_nodn = regx.search(r'[1-9][0-9]*',ges_shap_type,regx.I).group()
    ges_shap_form = ges_shap_type[0]

    dim = regx.search(r'[1-9]+', coortype, regx.I).group()
    axi = coortype.split('d')[1]
    ges_info['shap_nodn'] = ges_shap_nodn
    ges_info['shap_form'] = ges_shap_form
    ges_info['gaus_type'] = ges_gaus_type
    ges_info['dim'] = dim
    ges_info['axi'] = axi

    from felac_data import get_operator_data, \
                           get_gaussian_data, \
                           get_shapfunc_data
    get_operator_data()
    get_gaussian_data()
    get_shapfunc_data()

def genxde(xdename, gesname, coortype):

    # start parsing
    start = time()

    # xde elements and their line number
    xde_lists, list_addr, ges_info = {}, {}, {}

    prepare(gesname, coortype, ges_info)

    # parse xde
    from parse_xde import parse_xde
    xdefile = open('../0xde_source/'+xdename, mode='r')
    error = parse_xde(ges_info, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    # generate ges by xde element
    from xde2ges import xde2ges
    gesfile = open('../1ges_target/'+gesname+'.ges1', mode='w')
    error = xde2ges(ges_info, xde_lists, list_addr, gesfile)
    gesfile.close()
    if error: return

    # export xde element
    import json
    file = open('../1ges_target/'+gesname+'.json',mode='w')
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
    
    genxde(argvs[1], argvs[2], argvs[3])

if __name__ == "__main__":
    exit(main())