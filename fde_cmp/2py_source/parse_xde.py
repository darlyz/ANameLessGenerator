'''
 Copyright: Copyright (c) 2019
 Created: 2019-3-30
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''
import re as regx

def parse_xde(gesname, coortype, keywd_tag, xde_lists, list_addr, keyws_reg,file):

    # 0 prepare
    shap_tag = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
    gaus_tag = regx.search(r'g[1-9]+',gesname,regx.I)
    if gaus_tag != None:
        gaus_tag = gaus_tag.group()

    dim = regx.search(r'[1-9]+',coortype,regx.I).group()
    axi = coortype.split('d')[1]

    shap_nodn = regx.search(r'[1-9]+',shap_tag,regx.I).group()
    shap_form = shap_tag[0]

    i = 0
    stitchline = ''
    keywd_tag['paragraph'] = 'BFmate'
    keywd_tag['matrixtag'] = 0
    keywd_tag['complex'] = 0
    xde_lists['code'] = {}
    list_addr['code'] = {}
    matrixname = ''

    # 1 fist step parsing while read xde to xde_lists
    for line in file.readlines():
        i += 1

        # 1.1 identify comment and stitch the next line begin with '\'
        line = stitchline + line
        if line.find('\\') != -1 :
            stitchline = line.split('\\')[0]
            continue
        else:
            stitchline = ''

        # 1.2 skip comment line and blank line
        if regx.match(r'\s*[\\(//)]*\n',line,regx.I) != None:
            continue

        # 1.3 identify commentbegin with '//'
        if line.find('//') != -1:
            line = line.split('//')[0]+'\n'
            if regx.match(r'\$CC \n',line,regx.I) != None: continue

        # 1.4 retrieve the keywords
        regxrp = regx.search(keyws_reg,line,regx.I)
        if regxrp == None:

            # 1.4.1 find complex tag
            if line.find('|') != -1:
                keywd_tag['complex'] = 1

            # 1.4.2 find weak form and disp var deform in non-keyword-head line
            if line.find('[')!= -1 and line.find(']')!= -1:
                if   keywd_tag['paragraph'] == 'mass' \
                     and 'mass' in xde_lists:
                     
                    xde_lists['mass'].append(line.strip())
                    list_addr['mass'].append(i)

                elif keywd_tag['paragraph'] == 'damp' \
                     and 'damp' in xde_lists:
                     
                    xde_lists['damp'].append(line.strip())
                    list_addr['damp'].append(i)

                elif keywd_tag['paragraph'] == 'stif' \
                     and 'stif' in xde_lists:
                     
                    xde_lists['stif'].append(line.strip())
                    list_addr['stif'].append(i)

                elif keywd_tag['paragraph'] == 'load' \
                     and 'load' in xde_lists:
                     
                    xde_lists['load'].append(line.strip())
                    list_addr['load'].append(i)

                elif keywd_tag['paragraph'] == 'func' \
                     and 'func' in xde_lists['code']:
                     
                    xde_lists['code']['func'].append(line.strip()+'\n')
                    list_addr['code']['func'].append(i)

                elif keywd_tag['matrixtag'] != 0 :
                    xde_lists['matrix'][matrixname].append(line.strip())
                    list_addr['matrix'][matrixname].append(i)

            # 1.4.3 find maxtrix declaration
            elif keywd_tag['matrixtag'] != 0 :
                xde_lists['matrix'][matrixname].append(line.strip())
                list_addr['matrix'][matrixname].append(i)
            else:
                print('redundant information or wrong declare, line {}: '.format(i)+line)
        elif regxrp.span()[0] != 0:
            keywd_tag['matrixtag'] = 0
            print('error: line {0}, keyword {1} must be at the head of line.'.format(i,regxrp.group()))

        else:
            # 1.4.4 find keywords
            keywd_tag['matrixtag'] = 0
            if   regxrp.group().lower() == 'disp':
                pushkeydeclar('disp', i, line, xde_lists, list_addr)

            elif regxrp.group().lower() == 'coef':
                pushkeydeclar('coef', i, line, xde_lists, list_addr)

            elif regxrp.group().lower() == 'coor':
                pushkeydeclar('coor', i, line, xde_lists, list_addr)

            elif regxrp.group().lower() == 'gaus':
                pushkeydeclar('gaus', i, line, xde_lists, list_addr)

            elif regxrp.group().lower() == 'mate':
                pushkeydeclar('mate', i, line, xde_lists, list_addr)
                keywd_tag['paragraph'] = 'AFmate'

            elif regxrp.group().lower() == 'vect':
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1
                pushcomdeclar('vect', i, line, xde_lists, list_addr)

            elif regxrp.group().lower() == 'fmatr':
                pushcomdeclar('fmatr',i, line, xde_lists, list_addr)
                line_list = line.strip().split()
                if len(line_list) == 2:
                    xde_lists['fvect'][line_list[1]].append('1')
                    xde_lists['fvect'][line_list[1]].append('1')

            elif regxrp.group().lower() == 'fvect':
                pushcomdeclar('fvect',i, line, xde_lists, list_addr)
                line_list = line.strip().split()
                if len(line_list) == 2:
                    xde_lists['fvect'][line_list[1]].append('1')

            elif regxrp.group().find('$')!= -1 or regxrp.group().find('@')!= -1:
                if regxrp.group().lower() == '$cp':
                    keywd_tag['complex'] = 1
                line = line.replace('%1',shap_form).replace('%2',shap_nodn)
                pushcodeline (i, line, keywd_tag, xde_lists, list_addr)

            elif regxrp.group().lower() == 'common':
                line = line.replace('%1',shap_form).replace('%2',shap_nodn)
                pushcodeline (i, line, keywd_tag, xde_lists, list_addr)
            
            elif regxrp.group().lower() == 'array':
                line = line.replace('%1',shap_form).replace('%2',shap_nodn)
                pushcodeline (i, line, keywd_tag, xde_lists, list_addr)

            elif regxrp.group().lower() == 'mass':
                pushwekdeclar('mass', i, line, keywd_tag, xde_lists, list_addr)

            elif regxrp.group().lower() == 'damp':
                pushwekdeclar('damp', i, line, keywd_tag, xde_lists, list_addr)

            elif regxrp.group().lower() == 'stif':
                pushwekdeclar('stif', i, line, keywd_tag, xde_lists, list_addr)

            elif regxrp.group().lower() == 'shap':
                if not 'shap' in xde_lists:
                    list_addr['shap'] = []
                    xde_lists['shap'] = []
                list_addr['shap'].append(i)
                wordlist = line.strip().split()
                wordlist.pop(0)
                xde_lists['shap'].append(wordlist)

            elif regxrp.group().lower() == 'dist':
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1
                for strs in ['mass','damp','stif']:
                    if keywd_tag['paragraph'] == strs:
                        xde_lists[strs].append('dist')
                        xde_lists[strs].append(line.split('=')[1].strip())
                        list_addr[strs].append(i)

            elif regxrp.group().lower() == 'load':
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1
                if not 'load' in xde_lists:
                    xde_lists['load'] = []
                    list_addr['load'] = []
                xde_lists['load'].append(line.split('=')[1].strip())
                list_addr['load'].append(i)
                keywd_tag['paragraph'] = 'load'

            elif regxrp.group().lower() == 'func':
                wordlist = line.strip().split()
                if len(wordlist) != 1:
                    if not 'func' in xde_lists:
                        xde_lists['func'] = []
                    keywd_tag['func'] = 1
                    for j in range(2,len(wordlist)+1):
                        xde_lists['func'].append(wordlist[j-1])
                else:
                    keywd_tag['paragraph'] = 'func'

            elif regxrp.group().lower() == 'matrix':
                pushcomdeclar('matrix', i, line, xde_lists, list_addr)
                matrnam = line.strip().split()[1]
                linenum = list_addr['matrix'][matrnam]
                list_addr['matrix'][matrnam] = []
                list_addr['matrix'][matrnam].append(linenum)

                wordlist = line.strip().split()
                matrixname = wordlist[1]
                #if len(wordlist) == 4:
                #    xde_lists['matrix'][matrixname].append(wordlist[2])
                #    xde_lists['matrix'][matrixname].append(wordlist[3])
                keywd_tag['matrixtag'] = 1

            elif regxrp.group().lower() == 'userc':
                pass

            elif regxrp.group().lower() == 'end':
                pass

            elif regxrp.group().lower() == 'defi':
                pass

            else: print(str(line))

    import json
    file = open('../1ges_target/xde_lists.json',mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()

    file = open('../1ges_target/list_addr.json',mode='w')
    file.write(json.dumps(list_addr,indent=4))
    file.close()


    # 2 checking
    from check_xde import check_xde
    error = check_xde(xde_lists,list_addr,shap_tag,gaus_tag)
    if error == True:
        return error

    # 3 second step parsing
    # 3.1 parsing shap
    if 'shap' in xde_lists:
        shap_type = shap_tag
        shap_dict = {}
        shap_list = xde_lists['shap'].copy()

        # 3.1.1 common shap (maybe user declare twice or more, so the last active)
        shap_i = 0
        for shp_list in shap_list:
            if len(shp_list) == 2:
                if  shp_list[0] == '%1':
                    shp_list[0] = shap_form
                if  shp_list[1] == '%2':
                    shp_list[1] = shap_nodn
                shap_type = shp_list[0]+shp_list[1]

                shap_dict[shap_type] = []
                for disp_var in xde_lists['disp']:
                    shap_dict[shap_type].append(disp_var)

                if 'coef' in xde_lists:
                    xde_lists['coef_shap'] = {}
                    xde_lists['coef_shap'][shap_type] = []
                    for coef_var in xde_lists['coef']:
                        xde_lists['coef_shap'][shap_type].append(coef_var)
            shap_i += 1

        # 3.1.2 penalty or mix shap
        shap_i = 0
        comm_shap = shap_type
        for shp_list in shap_list:
            if len(shp_list) >= 3:
                if shp_list[0] == '%1':
                    shp_list[0] = shap_form

                if shp_list[1] == '%4' or shp_list[1].isnumeric():

                    var_list  = shp_list[2:len(shp_list)]
                    disp_find_n = len(set(var_list)&set(xde_lists['disp']))

                    coef_find_n = 0
                    if 'coef' in xde_lists:
                        coef_find_n = len(set(var_list)&set(xde_lists['coef']))

                    shap_type = shp_list[0] + shap_nodn

                    for var_name in var_list:
                        if var_name.isnumeric(): continue

                        if 'coef' not in xde_lists:
                            if var_name not in xde_lists['disp'] :
                                continue
                        else:
                            if  var_name not in xde_lists['disp'] \
                            and var_name not in xde_lists['coef'] :
                                continue

                        if disp_find_n > 0 and coef_find_n == 0:
                            if   shap_type == 't6':  shp_list[1] = '3'
                            elif shap_type == 'q9':  shp_list[1] = '4'
                            elif shap_type == 'w10': shp_list[1] = '4'
                            elif shap_type == 'c27': shp_list[1] = '8'
                            else:
                                print('error: line {}, mix element should to be used in 2nd shap function'.format(list_addr['shap'][shap_i]))
                            sub_shap_type = shp_list[0]+shp_list[1]
                            if var_name in shap_dict[comm_shap]:
                                shap_dict[comm_shap].remove(var_name)

                            if not sub_shap_type in shap_dict:
                                shap_dict[sub_shap_type] = []
                            shap_dict[sub_shap_type].append(var_name)

                        elif disp_find_n == 0 and coef_find_n > 0:
                            if   shap_tag == 't6':  shp_list[1] = '3'
                            elif shap_tag == 'q9':  shp_list[1] = '4'
                            elif shap_tag == 'w10': shp_list[1] = '4'
                            elif shap_tag == 'c27': shp_list[1] = '8'
                            else:
                                print('error: line {}, mix element should to be used in 2nd shap function'.format(list_addr['shap'][shap_i]))
                            sub_shap_type = shp_list[0]+shp_list[1]
                            xde_lists['coef_shap'][comm_shap].remove(var_name)

                            if not sub_shap_type in xde_lists['coef_shap']:
                                xde_lists['coef_shap'][sub_shap_type] = []
                            xde_lists['coef_shap'][sub_shap_type].append(var_name)
                        else:
                            print('error: line {}, disp or coef declaration fault.'.format(list_addr['shap'][shap_i]))

                elif shp_list[1] == '%2c' \
                or  (shp_list[1][-1] == 'c' \
                and  shp_list[1][:-1].isnumeric) :

                    var_list = shp_list[2:len(shp_list)]
                    pena_var_list = []
                    for var in var_list:
                        if var.isnumeric(): continue
                        if shp_list[2].find('_'):
                            pena_var_list.append(shp_list[2].split('_')[0])
                        else: pena_var_list.append(shp_list[2])

                    pena_var_list = set(pena_var_list)&set(xde_lists['disp'])

                    shp_list[1]   = shp_list[1].replace('%2',shap_nodn)
                    sub_shap_type = shp_list[0]+shp_list[1]

                    if shp_list[1] not in shap_dict:
                        shap_dict[sub_shap_type] = []

                    for pena_var in pena_var_list :
                        if pena_var in xde_lists['disp']:
                            shap_dict[comm_shap].remove(pena_var)
                            shap_dict[sub_shap_type].append(pena_var)

            shap_i += 1
        xde_lists['shap'] = shap_dict

    # 3.2 parsing gaus
    if gaus_tag != None:
        xde_lists['gaus'] = gaus_tag
    else:
        xde_lists['gaus'] = shap_tag

    # 3.3 parsing mate
    mate_dict = {}
    mate_dict['default'] = {}
    mate_var = []
    mate_val = []
    is_var = r'[a-z]\w*'

    for strs in xde_lists['mate']:
        if regx.match(is_var,strs,regx.I) == None :
            mate_val.append(strs)
        else:
            mate_var.append(strs)

    var_i = 0
    for var in mate_var:
        if var_i < len(mate_val):
            mate_dict['default'][var] = mate_val[var_i]
        else:
            mate_dict['default'][var] = 0.0
        var_i += 1
    xde_lists['mate'] = mate_dict

    # 3.4 parsing mass and damp
    if 'mass' in xde_lists:
        if xde_lists['mass'][0] == '%1':
            xde_lists['mass'][0] = 'lump'
    if 'damp' in xde_lists:
        if xde_lists['damp'][0] == '%1':
            xde_lists['damp'][0] = 'lump'

    # 3.5 parsing fvect, fmatr, vect, matrix
    if 'fvect' in xde_lists:
        for lists in xde_lists['fvect'].values():
            if len(lists) == 1:
                for ii in range(int(lists[0])):
                    lists.append('')
    if 'fmatr' in xde_lists:
        for lists in xde_lists['fmatr'].values():
            if len(lists) == 2:
                for ii in range(int(lists[0])):
                    lists.append([])
                    for jj in range(int(lists[1])):
                        lists[ii+2].append('')
    if 'vect' in xde_lists:
        for lists in xde_lists['vect'].values():
            if not lists[0].isnumeric():
                lists.insert(0,str(len(lists)))
    if 'matrix' in xde_lists:
        for lists in xde_lists['matrix'].values():
            if  not lists[0].isnumeric() \
            and not lists[1].isnumeric() :
                row = len(lists)
                clm = len(lists[0].split())
                lists.insert(0,str(clm))
                lists.insert(0,str(row))
            for ii in range(2,len(lists)):
                lists[ii] = lists[ii].split()

    # 3.6 parsing code
    code = {}
    code_key = r'\$C[CPV]|@[LAWSR]|ARRAY'
    for code_place in xde_lists['code'].keys():
        code_i = 0
        for code_strs in xde_lists['code'][code_place]:
            code_i += 1
            regxrp = regx.search(code_key,code_strs,regx.I)

            if regxrp != None:
                if regxrp.group().lower() == '$cc':
                    xde_lists['code'][code_place][code_i-1] \
                        = code_strs.replace(regxrp.group(),'Insr_C:')
                elif regxrp.group().lower() == '$cv':
                    xde_lists['code'][code_place][code_i-1] \
                        = code_strs.replace(regxrp.group(),'Tnsr_Asgn:')
                elif regxrp.group().lower() == '$cp':
                    xde_lists['code'][code_place][code_i-1] \
                        = code_strs.replace(regxrp.group(),'Cplx_Asgn:')

                # 3.6.1 parsing operator
                elif regxrp.group().lower() == '@l':
                    opr_list = code_strs.split()
                    operator_expr = opr_list[1]
                    operator_name = operator_expr.split('.')[0]

                    if opr_list[2].lower() == 'n':
                        if operator_name.lower() == 'singular':
                            xde_lists['code'][code_place][code_i-1] \
                                = 'Oprt_Asgn: '+operator_expr
                        elif operator_name.lower() == 'vol':
                            xde_lists['code'][code_place][code_i-1] \
                                = 'Oprt_Asgn: '+operator_expr
                    else:
                        var_prefix = ['', '',   '',     '[']
                        var_posfix = ['', '_i', '_i_j', ']']
                        kk = 0
                        for strs in ['c','v','m','f']:
                            if opr_list[2].lower() == strs:
                                if strs == 'f':
                                    if 'fvect' in xde_lists and \
                                    opr_list[3] in xde_lists['fvect']:
                                        var_posfix[kk] = '_i'+var_posfix[kk]
                                    elif 'fmatr' in xde_lists and \
                                    opr_list[3] in xde_lists['fmatr']:
                                        var_posfix[kk] = '_i_j'+var_posfix[kk]
                                temp_str  = 'Oprt_Asgn: '+var_prefix[kk]+opr_list[3]+var_posfix[kk]
                                temp_str += '='+operator_expr+'('
                                for ii in range(4,len(opr_list)):
                                    temp_str += opr_list[ii]+','
                                xde_lists['code'][code_place][code_i-1] = temp_str.rstrip(',')+')'
                            kk += 1

                # 3.6.2 parsing assignment
                elif regxrp.group().lower() == '@a':
                    code_strs = code_strs[3:len(code_strs)]
                    expr = code_strs.split('=')
                    xde_lists['code'][code_place][code_i-1] \
                    = 'Func_Asgn: ['+ expr[0].rstrip()+']='+expr[1].lstrip()

                elif regxrp.group().lower() == '@w':
                    opr_list = code_strs.split()
                    temp_str = 'Func_Asgn: '+opr_list[1]
                    for strs,idxs in zip(['vect','matrix'],['_i=','_i_j=']):
                        if  strs in xde_lists and opr_list[1] in xde_lists[strs]:
                            temp_str += idxs+opr_list[2]+'['
                            for ii in range(3,len(opr_list)):
                                temp_str += opr_list[ii]+','
                            xde_lists['code'][code_place][code_i-1] = temp_str.rstrip(',')+']'

                elif regxrp.group().lower() == '@s':
                    opr_list = code_strs.split()
                    temp_str = 'Func_Asgn: ['+opr_list[1]
                    for strs,idxs in zip(['fvect','fmatr'],['_i]=','_i_j]=']):
                        if  strs in xde_lists and opr_list[1] in xde_lists[strs]:
                            temp_str += idxs+opr_list[2]+'['
                            for ii in range(3,len(opr_list)):
                                temp_str += opr_list[ii]+','
                            xde_lists['code'][code_place][code_i-1] = temp_str.rstrip(',')+']'

                elif regxrp.group().lower() == '@r':
                    code_strs = code_strs[3:len(code_strs)]
                    expr = code_strs.split('=')
                    xde_lists['code'][code_place][code_i-1] \
                    = 'Func_Asgn: ['+ expr[0].rstrip()+']='+expr[1].lstrip().replace('[','').replace(']','')

                elif regxrp.group().lower() == 'array':
                    code_strs = code_strs.split()[1]
                    var_list = code_strs.split(',')
                    xde_lists['code'][code_place][code_i-1] = 'Insr_C: double '
                    for var_str in var_list:
                        var = var_str.strip().split('[')[0]
                        idx_list = regx.findall(r'\[\d+\]',var_str,regx.I)
                        if len(idx_list) == 1:
                            if 'vect' not in xde_lists: 
                                xde_lists['vect'] = {}
                            xde_lists['vect'][var] = []
                            for idx in idx_list:
                                xde_lists['vect'][var].append(idx.lstrip('[').rstrip(']'))
                            for ii in range(int(xde_lists['vect'][var][0])):
                                xde_lists['vect'][var].append(var+'['+str(ii+1)+']')
                            var_str = var + '[' + str(int(idx_list[0].lstrip('[').rstrip(']'))+1) +']'
                        elif len(idx_list) == 2:
                            if 'matrix' not in xde_lists: 
                                xde_lists['matrix'] = {}
                            xde_lists['matrix'][var] = []
                            for idx in idx_list:
                                xde_lists['matrix'][var].append(idx.lstrip('[').rstrip(']'))
                            for ii in range(int(xde_lists['matrix'][var][0])):
                                xde_lists['matrix'][var].append([])
                                for jj in range(int(xde_lists['matrix'][var][1])):
                                    xde_lists['matrix'][var][ii+2].append(var+'['+str(ii+1)+']['+str(jj+1)+']')

                        xde_lists['code'][code_place][code_i-1] += var_str + ','
                    xde_lists['code'][code_place][code_i-1] = xde_lists['code'][code_place][code_i-1].rstrip(',') +';'
    #print(code)

    return False

# key declare type1: DISP, COEF, COOR, GAUS, MATE
def pushkeydeclar (strs, linenum, line, xde_lists, list_addr):
    if strs in xde_lists:
        print('warn: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,list_addr[strs]))
    else:
        list_addr[strs] = linenum
        xde_lists[strs] = []
        line = line.replace(',',' ').replace(';',' ')
        wordlist = line.strip().split()
        for j in range(2,len(wordlist)+1): xde_lists[strs].append(wordlist[j-1])

# common declare type: VECT, FMATR
def pushcomdeclar (strs, linenum, line, xde_lists, list_addr):
    if strs not in xde_lists: 
        xde_lists[strs] = {}
        list_addr[strs] = {}
    wordlist = line.strip().split()
    for j in range(2,len(wordlist)+1):
        if j == 2:
            xde_lists[strs][wordlist[1]]=[]
            list_addr[strs][wordlist[1]]=linenum
        else:
            xde_lists[strs][wordlist[1]].append(wordlist[j-1])

# common code line : @x, $Cx
def pushcodeline (linenum, line, keywd_tag, xde_lists, list_addr):
    code_find = 0
    for strs in ['BFmate','AFmate','func','stif','mass','damp']:
        if keywd_tag['paragraph'] == strs:
            code_find = 1
            if not strs in xde_lists['code']:
                xde_lists['code'][strs] = []
                list_addr['code'][strs] = []
            xde_lists['code'][strs].append(line.strip())
            list_addr['code'][strs].append(linenum)
    if code_find == 0:
        print('error: line {}, wrong position inserted'.format(linenum))

# stif, mass, damp declare
def pushwekdeclar (strs, linenum, line, keywd_tag, xde_lists, list_addr):
    if strs in xde_lists:
        print('error: line {0}, duplicated declare, {1} has been declared at line {2}'.format(linenum,strs,list_addr[strs][0]))
    else:
        list_addr[strs] = []
        xde_lists[strs] = []
        wordlist = line.strip().split()
        if len(wordlist) > 1:
            list_addr[strs].append(linenum)
            for j in range(2,len(wordlist)+1):
                xde_lists[strs].append(wordlist[j-1])
        else:
            keywd_tag['paragraph'] = strs