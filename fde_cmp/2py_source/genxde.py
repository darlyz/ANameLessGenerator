'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
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
    
    if argvs[1] == '-h' \
    or argvs[1] == '--h' \
    or argvs[1] == '-H' \
    or argvs[1] == '--H':
        print('type as: python genxde.py delxyz aec27g3 3dxyz')
        return
    
    start = time()
    
    keyws_reg  = r'DEFI|DISP|COEF|COOR|SHAP|GAUS|MATE|MASS|DAMP|STIF|'
    keyws_reg += r'FUNC|VECT|MATRIX|FVECT|FMATR|ARRAY|DIST|LOAD|END|'
    keyws_reg += r'\$C[CPV]|@[LAWSR]'
    
    keywd_tag = {'disp':0, 'coor':0, 'shap':0 , 'gaus':0, 'stif':0, 'load':0, \
                 'mate':0, 'mass':0, 'damp':0 \
    }
    list_addr = {}
    xde_lists = {}
    
    
    from parse_xde import parse_xde
    xdefile = open('../0xde_source/'+argvs[1]+'.fde', mode='r')
    error = parse_xde(argvs[2],argvs[3],keywd_tag,xde_lists,list_addr,keyws_reg,xdefile)
    xdefile.close()
    if error == True:
        return
    
    #print(xde_lists)
    #for ll in xde_lists.keys():
    #    print(ll,xde_lists[ll])
    #for ll in list_addr.keys():
    #    print(ll,list_addr[ll])

    import json
    file = open('../1ges_target/'+argvs[2]+'.json',mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()
    
    from xde2ges import xde2ges
    gesfile = open('../1ges_target/'+argvs[2]+'.ges1', mode='w')
    xde2ges(argvs[2],argvs[3],keywd_tag,xde_lists,list_addr,keyws_reg,gesfile)
    gesfile.close()
    
    file = open('../1ges_target/'+argvs[2]+'.json1',mode='w')
    file.write(json.dumps(xde_lists,indent=4))
    file.close()
    
    end   = time()
    print ('parsing time: {}s'.format(end-start))

    from xde2md import xde2md
    mdfile = open('../1ges_target/'+argvs[1]+'.md', mode='w')
    xde2md(argvs[2],argvs[3],keywd_tag,xde_lists,list_addr,keyws_reg,mdfile)
    mdfile.close()
    
if __name__ == "__main__":
    exit(main())
    
# xde_list and list_addr:=
#{
#    "code": {
#        "BFmate": [],
#        "AFmate": [],
#        "func": [],
#        "stif": [],
#        "mass": [],
#        "damp": []
#    },
#    "disp": [],
#    "coef": [],
#    "vect": {},
#    "coor": [],
#    "func": [],
#    "fmatr": {},
#    "shap": {},
#    "gaus": "",
#    "mate": [],
#    "mass": [],
#    "damp": [],
#    "matrix": {},
#    "stif": [],
#    "load": [],
#}