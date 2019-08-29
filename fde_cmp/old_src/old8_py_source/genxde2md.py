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

# ...$python genfde.py filename elemtype
def main(argvs=None):
    if argvs is None:
        argvs = argv

    start = time()

    from felac_data import get_felac_data
    get_felac_data()

    xdename, gesname, coortype = argvs[1], argvs[2], argvs[3]

    # xde elements and their line number
    xde_lists, list_addr, ges_info = {}, {}, {}

    # get shap, gaus, dim and axis information into ges_info
    from felac_data import prepare_to_genxde
    prepare_to_genxde(gesname, coortype, ges_info)

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