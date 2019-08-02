#!/usr/bin/python3
'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: main func of generate xde file to ges, html, md, xml, c or fortran
 All rights reserved
'''
from sys import argv,exit
from time import time
import re

# default folder
xde_folder = '../0xde_source/'
ges_folder = '../2ges_target/'
c_folder   = '../3c_target/'
ifo_folder = '../4other_gen_file/'

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
    xde_dict = {}
    xde_addr = {}
    ges_info = {}
    ges_dict = {}

    # get shap, gaus, dim and axis information into ges_info
    from felac_data import prepare_to_genxde
    prepare_to_genxde(gesname, coortype, ges_info)

    # parse xde
    from parse_xde import parse_xde
    xdefile = open(xde_folder + xdename, mode='r')
    error = parse_xde(ges_info, xde_dict, xde_addr, xdefile)
    xdefile.close()
    if error: return

    # parse ges
    from xde2ges import xde2ges_dict
    error = xde2ges_dict(ges_info, xde_dict, xde_addr, ges_dict)
    if error: return

    # ----------------------------------------------------------

    # generate ges by ges_dict
    if gen_obj['ges'] > 0:
        from xde2ges import xde2ges
        gesfile = open(ges_folder + gesname + '.ges', mode='w')
        xde2ges(ges_info, xde_dict, ges_dict, gesfile)
        gesfile.close()

    # generate c by ges_dict
    if gen_obj['Ccode'] > 0:
        from ges2c import ges2c
        cfile = open(c_folder + gesname + '.c', mode = 'w')
        ges2c(ges_info, ges_dict, cfile)
        cfile.close()

    # generate html by xde element to preview
    if gen_obj['html'] > 0:
        from xde2html import xde2html
        htmlfile = open(ls + xdename + '.html', mode='w')
        xde2html(ges_info, xde_dict, xde_addr, htmlfile)
        htmlfile.close()

    # generate markdown by xde element to preview
    #if gen_obj['md'] > 0:
    #    from xde2md import xde2md
    #    mdfile = open('../1ges_target/'+argvs[1]+'.md', mode='w')
    #    xde2md(ges_info xde_dict, xde_addr, mdfile)
    #    mdfile.close()

    # ...

    # export xde element
    import json
    file = open(ifo_folder + gesname+'.json', mode='w')
    file.write(json.dumps(xde_dict,indent=4))
    file.close()

    end   = time()
    print ('parsing time: {}s'.format(end-start))

def command_help():
    from xde_help import auto_line_break_print
    from os import get_terminal_size
    maxcol = get_terminal_size().columns - 10

    print("* command as \n  'genxde (parameter) (address)[xdename] (address)[gesname] [coortype]',")
    print(               "  'genxde (parameter) (address)[mdiname] (address)[xdename]',")
    print("  where 'address' is file address if necessary, and 'parameter' is optional as:\n")

    auto_line_break_print(maxcol, 10, '-ges[=1]', \
        "generate ges file when '-ges=1' or '-ges', no ges output when '-ges=0', and default by '-ges=1'.")

    auto_line_break_print(maxcol, 10, '-Ccode[=1]', \
        "generate c code file when '-Ccode=1' or '-Ccode', and default by '-Ccode=0'.")

    auto_line_break_print(maxcol, 10, '-Fcode[=1]', \
        "generate c code file when '-Fcode=1' or '-Fcode', and default by '-Fcode=0'.")

    auto_line_break_print(maxcol, 10, '-xml[=1]', \
        "generate xml file when '-xml=1' or '-xml', and default by '-xml=0'.")

    auto_line_break_print(maxcol, 10, '-html[=1]', \
        "generate html file to preview when '-html=1' or '-html', and default by '-html=0'.")

    auto_line_break_print(maxcol, 10, '-md[=1]', \
        "generate html file to preview when '-md=1' or '-md', and default by '-md=0'.")

    auto_line_break_print(maxcol, 10, '-check[=1]', \
        "check xde file when '-check=1' or '-check', and default by '-check=1'.")

    print("\n* and it could get help of xde key type as\n  'genxde -h [key]'\n")

    auto_line_break_print(maxcol, 10, '-h [key]', \
        "help of xde key, also it could use '--h', '-H', '--H', '-help', " \
        +"'--help' insteed of '-h', and use '-h all' could print all of key help.")

def main(argvs=None):
    if argvs is None:
        argvs = argv

    if len(argvs) == 1:

        command_help()  
        return

    # xde help system
    if argvs[1] in ['-h', '--h', '-H', '--H', '-help', '--help']:

        if len(argvs) == 2 :
            command_help()  
        
        elif len(argvs) > 3 :
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

            if xdename.find('/')  != -1 \
            or xdename.find('\\') != -1 :
                xdename = re.split(r'/|\\', nonfunc_params[0])[-1]
                global xde_folder
                xde_folder = nonfunc_params[0].replace(xdename, '')

            if gesname.find('/')  != -1 \
            or gesname.find('\\') != -1 :
                gesname = re.split(r'/|\\', nonfunc_params[1])[-1]
                global ges_folder, ifo_folder, c_folder
                ges_folder = nonfunc_params[1].replace(gesname, '')
                ifo_folder = nonfunc_params[1].replace(gesname, '')
                c_folder   = nonfunc_params[1].replace(gesname, '')

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

    genxde(xdename, gesname, coortype)

if __name__ == "__main__":
    exit(main())
