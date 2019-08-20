'''
 Copyright: Copyright (c) 2019
 Created: 2019-3-30
 Author: Zhang_Licheng
 Title: parse the sch file and check it
 All rights reserved
'''
from colorama import init, Fore, Back, Style
init(autoreset=True)
Error_color = Fore.MAGENTA
Warnn_color = Fore.CYAN
Empha_color = Fore.GREEN

import re
import json
from gensch import gen_obj, ifo_folder

dict_check = {'pre':1, 'sec':1, 'fnl':1}
addr_check = {'pre':1, 'sec':1, 'fnl':1}

def parse_sch(sch_dict, sch_addr, schfile):

    # parse xde to features and workflow features
    # just push the sentence into dict
    # report the meaningless sentence and paragraph declaration error
    pre_parse(sch_dict, sch_addr, schfile)

    # a simple parsing feature sentence to list
    # and check the duplicated of some feature declaration
    #sec_parse(sch_dict, sch_addr)
    
    # fully check all features 
    #if gen_obj['check'] > 0:
    #    if check_xde(sch_dict, sch_addr):
    #        return True
 
    # parse features into a readable and transable style
    #fnl_parse(sch_dict, sch_addr)

    return False

def pre_parse(sch_dict, sch_addr, schfile):

    # all the sch keys
    key_pattern = r'DEFI|STIF|MASS|DAMP|LOAD|TYPE|MDTY|INIT|COEF|' \
                + r'EQUATION|SOLUTION|@SUBET|@head|@NBDE|END'

    keywd_tag = {'paragraph': 'DEFI'}

    line_i = 0
    stitchline = ''

    # parsing while read sch to sch_dict
    for line in schfile.readlines():
        line_i += 1

        # skip comment line and blank line
        if re.match(r'\s*(\$c[c6])?\s*((\\|//).*)?\s*\n',line,re.I) != None:
            continue

        # deal with valid sentence with comment
        # identify comment and stitch the next line begin with '\'
        line = stitchline + line
        if line.find('\\') != -1 :
            stitchline = line.split('\\')[0]
            continue
        else: stitchline = ''

        # identify comment begin with '//'
        if line.find('//') != -1:
            line = line.split('//')[0]

        # pop the space from head and tail
        line = line.strip()

        # retrieve the keywords
        matched_key = re.match(key_pattern, line, re.I)

        # find the keyword at the head
        if matched_key != None:

            key_match = matched_key.group()
            key_lower = key_match.lower()

            if key_lower in ['equation', 'solution', '@subet', '@head', '@nbde']:

                keywd_tag['paragraph'] = key_lower

                if key_lower not in sch_dict:
                    sch_dict[key_lower] = []
                    sch_addr[key_lower] = []

                continue

            elif key_lower in ['stif', 'mass', 'damp', 'load', 'type', 'mdty', 'init']:

                if 'defi' not in sch_dict:
                    sch_dict['defi'] = {}
                    sch_addr['defi'] = {}

                sch_dict['defi'][key_lower] = line.replace(key_match,'').lstrip()
                sch_addr['defi'][key_lower] = line_i

            elif key_lower == 'coef':

                sch_dict['coef'] = line.replace(key_match,'').lstrip()
                sch_addr['coef'] = line_i


        # find the non-keyword-head line in 'EQUATION' 'SOLUTION' '@SUBET', '@head' and '@NBDE' paragraph
        else:
            para_key = keywd_tag['paragraph']

            sch_dict[para_key].append( line )
            sch_addr[para_key].append( line_i )

    export_parsing_result('pre', sch_dict, sch_addr)
# end pre_parse()


def export_parsing_result(stage, xde_dict, xde_addr):
    if dict_check[stage] != 0:
        file = open(ifo_folder + stage + '_check.json', mode='w')
        file.write(json.dumps(xde_dict,indent=4))
        file.close()
    if addr_check[stage] != 0:
        file = open(ifo_folder + stage + '_addr.json',  mode='w')
        file.write(json.dumps(xde_addr,indent=4))
        file.close()
# end export_parsing_result()