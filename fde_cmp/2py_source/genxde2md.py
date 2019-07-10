'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-26
 Author: Zhang_Licheng
 Title: main func of generate xde file to markdown
 All rights reserved
'''
from sys import argv,exit
from time import time
import re as regx

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

    from felac_data import get_operator_data, \
                           get_gaussian_data, \
                           get_shapfunc_data
    get_operator_data()
    get_gaussian_data()
    get_shapfunc_data()

# ...$python genfde.py filename elemtype
def main(argvs=None):
    if argvs is None:
        argvs = argv

    if argvs[1] == '-h' \
    or argvs[1] == '--h' \
    or argvs[1] == '-H' \
    or argvs[1] == '--H':
        print('type as: python genxde.py delxyz aec27g3 3dxyz')
        return

    start = time()

    xdename, gesname, coortype = argvs[1], argvs[2], argvs[3]

    # xde elements and their line number
    xde_lists, list_addr, ges_info = {}, {}, {}

    prepare(gesname, coortype, ges_info)


    from parse_xde import parse_xde
    xdefile = open('../0xde_source/'+xdename, mode='r')
    error = parse_xde(ges_info, xde_lists, list_addr, xdefile)
    xdefile.close()
    if error: return

    from xde2md import xde2md
    mdfile = open('../1ges_target/'+argvs[1]+'.md', mode='w')
    xde2md(gesname, coortype, xde_lists, list_addr, mdfile)
    mdfile.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

if __name__ == "__main__":
    exit(main())