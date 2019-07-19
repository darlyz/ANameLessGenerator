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

    comb = set()

    if len(fparam) == 1 :
        comb.add(fparam)

    elif len(fparam) >1 :
        for i in range(len(fparam)-1):
            for j in range(i+1,len(fparam)):
                comb.add(fparam[i]+'\\w*'+fparam[j])

    param_pattern = re.compile('|'.join(comb))

    match_keys = set()
    for keys in gen_obj.keys():
        if param_pattern.search(keys) != None:
            match_keys.add('-'+keys)

    if   len(match_keys) == 1:
        print(f"Do you want to input '{list(match_keys)[0]}' " \
            + f"insteed of -{parameter}?\n")

    elif len(match_keys) > 1:
        print(f"Do you want to input one of " \
            + f"'{', '.join(match_keys)}' insteed of -{parameter}?\n")

    else:
        print(f"Do you want to input one of " \
            + f"'{', '.join(map(lambda x: '-'+x, gen_obj.keys()))}'" \
            + f" insteed of -{parameter}?\n")
# end find_similar_paramater()

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
    if gen_obj['ges'] > 0:
        from xde2ges import xde2ges
        gesfile = open(ges_folder + gesname+'.ges', mode='w')
        error = xde2ges(ges_info, xde_lists, list_addr, gesfile)
        gesfile.close()
        if error: return

    # generate html by xde element
    if gen_obj['html'] > 0:
        from xde2html import xde2html
        htmlfile = open(xdename+'.html', mode='w')
        xde2html(ges_info, xde_lists, list_addr, htmlfile)
        htmlfile.close()

    # ...

    # export xde element
    import json
    file = open(ifo_folder + gesname+'.json', mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

def main(argvs=None):
    if argvs is None:
        argvs = argv

    if len(argvs) == 1:
        print('to fill')
        return

    # xde help system
    if argvs[1] in ['-h', '--h', '-H', '--H', '-help', '--help']:

        if len(argvs) == 2 or len(argvs) > 3 :
            print(f"type as: python generate_xde.py " \
                + f"{argvs[1]} [key of xde].\n")

        else:
            from xde_help import xde_help
            xde_help(argvs[2])
        return
    
    else:
        nonfunc_params = []

        for parameter in argvs[1:] :

            if  parameter[0] == '-':
                if parameter.count('=') == 1:

                    parameter, val = parameter[1:].split('=')

                    if parameter in gen_obj.keys():
                        try:
                            gen_obj[parameter] = int(val)
                        except ValueError:
                            print(f"Please input as '-{parameter}=[int]'.\n")
                            return

                    else:
                        find_similar_paramater(parameter)
                        return


                else:
                    if parameter[1:] in gen_obj.keys():
                        gen_obj[parameter[1:]] = 1

                    else:
                        find_similar_paramater(parameter[1:])
                        return

            else:
                nonfunc_params.append(parameter)

        if   len(nonfunc_params) == 3:
            xdename  = nonfunc_params[0]
            gesname  = nonfunc_params[1]
            coortype = nonfunc_params[2]

        elif len(nonfunc_params) == 2:
            
            xdename = nonfunc_params[1].replace('\\','/').rstrip('/')
            xdename = xdename.split('/')[-1]
            xdename, xdetype = xdename.split('.')[:2]

            mdifile = open(nonfunc_params[0]+'.mdi', mode='r')

            for strings in mdifile.readlines():

                fieldSN = re.search(r'#[a-z]', strings, re.I)
                if fieldSN != None:
                    fieldnum = fieldSN.group().lstrip('#')

                axi = re.search(r'[123]d[xyzrozs]{1,3}', strings, re.I)
                if axi != None:
                    coortype = axi.group()

                if  re.search(xdename, strings, re.I) != None \
                and re.search(xdetype, strings, re.I) != None :
                    ges_list = re.findall(r'[ltqwc]\d+(?:g\d+)?', strings, re.I)
                    gesname = f'{fieldnum}e{ges_list[0]}'

            xdename = nonfunc_params[1]

        else:
            print('type as: python genxde.py [xdename] [gesname] [coortype]')
            print('      or python genxde.py [mdiname] [xdename]')
            return

    from felac_data import get_felac_data
    get_felac_data()

    genxde(argvs[1], argvs[2], argvs[3])


if __name__ == "__main__":
    exit(main())
        
