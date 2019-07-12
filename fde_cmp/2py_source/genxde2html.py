'''
 Copyright: Copyright (c) 2019
 Created: 2019-7-12
 Author: Zhang_Licheng
 Title: main func of generate xde file to html
 All rights reserved
'''
from sys import argv,exit
from time import time
import re as regx
import os

def prepare(gesname, coortype, ges_info):
    ges_shap_type = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
    ges_gaus_type = regx.search(r'g[1-9]+',gesname,regx.I)
    if ges_gaus_type != None:
        ges_gaus_type = ges_gaus_type.group()
    else: ges_gaus_type = ges_shap_type

    ges_shap_nodn = regx.search(r'[1-9]+',ges_shap_type,regx.I).group()
    ges_shap_form = ges_shap_type[0]

    dim = regx.search(r'[1-9]+',coortype,regx.I).group()
    axi = coortype.split('d')[1]
    ges_info['name'] = gesname
    ges_info['shap_nodn'] = ges_shap_nodn
    ges_info['shap_form'] = ges_shap_form
    ges_info['gaus_type'] = ges_gaus_type
    ges_info['dim'] = dim
    ges_info['axi'] = axi

def main(argvs=None):
    if argvs is None:
        argvs = argv

    start = time()

    from felac_data import get_felac_data
    get_felac_data()

    xdename, gesname, coortype, fieldnum= 'nl', 'nl', 'nl', 'nl'

    if len(argvs) == 4:
        xdename, gesname, coortype = argvs[1], argvs[2], argvs[3]
    elif len(argvs) == 3:
        xdename = argvs[2].replace('\\','/').rstrip('/')
        xdename = xdename.split('/')[-1]
        xdename, xdetype = xdename.split('.')[:2]
        mdifile = open(argv[1]+'.mdi', mode='r')
        for strings in mdifile.readlines():
            fieldSN = regx.search(r'#[a-z]', strings, regx.I)
            if fieldSN != None: fieldnum = fieldSN.group().lstrip('#')

            axi = regx.search(r'[123]d[xyzrozs]{1,3}', strings, regx.I)
            if axi != None: coortype = axi.group()

            if  regx.search(xdename, strings, regx.I) != None \
            and regx.search(xdetype, strings, regx.I) != None :
                ges_list = regx.findall(r'[ltqwc]\d+(?:g\d+)?', strings, regx.I)
                gesname = f'{fieldnum}e{ges_list[0]}'

        xdename = argvs[2]

    # xde elements and their line number
    xde_lists, list_addr, ges_info = {}, {}, {}

    prepare(gesname, coortype, ges_info)


    from parse_xde import parse_xde
    xdefile = open(xdename, mode='r')
    error = parse_xde(ges_info, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    from xde2html import xde2html
    htmlfile = open(xdename+'.html', mode='w')
    xde2html(ges_info, xde_lists, list_addr, htmlfile)
    htmlfile.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

if __name__ == "__main__":
    exit(main())