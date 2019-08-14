# parse_xde.py
# pre_parse() 解析后标准格式
注：pre_parse() 保存对象全为字符串格式、关键字不区分大小写，其余元素区分大小写，保留错误格式

以下为要素关键字以及保存内容

## 一、流程无关要素
注： '| <--' 表示可能格式替换为左边形式
### disp:
    [
    "DISP u v w"                        | <-- "DISP u,v,w"
    ]
### coor:
    [
    "COOR x y z"                        | <-- "COOR x,y,z"
    ]
### coef:
    [
    "COEF un vn wn"                     | <-- "COEF un,vn,wn"
    ]
### func:
    [
    "FUNC uxx vxx wyy"                  | <-- "FUNC uxx,vxx,wyy"
    ]
### shap:
    [
    "SHAP %1 %2",
    "SHAP q 4",
    "SHAP %1 %2c v_w",
    "SHAP q 4c v_w",
    "SHAP %1 %4 w",
    ]
### gaus:
    [
    "GAUS %3",
    "GAUS g2"
    ]
### mate:
    [
    "MATE a b c d 1 2. .3 4e5"          | <-- "MATE a b c d 1,2.;.3 4e5"
    ]
### vect:
    [
    "VECT u u v w"                      | <-- "VECT u=u v w" or "VECT u=u,v,w"
    ]
### matrix:
    [
    "MATRIX sm 3 3",
    "(1.-pv) pv pv",
    "pv (1.-pv) pv",
    "pv pv (1.-pv)",
    "MATRIX qrevm",
    "1./3.0 -1./6.0 -1./6.0",
    "-1./6.0 1./3.0 -1./6.0",
    "-1./6.0 -1./6.0 1./3.0"
    ]
### fvect:
    [
    "FVECT fev 3"
    ]
### fmatr:
    [
    "FMATR fem 3 3"
    ]
### mass:
#### mass form 1
    [
    "MASS %1"
    "MASS %1 a b 0"                     | <-- "MASS %1 a,b,0"
    ]
#### mass form 2
    [
    "MASS"
    "DIST = +[u;u]*a + [v;v]*b"
    ]
### damp:
#### damp form 1
    [
    "DAMP %1"
    "DAMP %1 a b 0"                     | <-- "DAMP %1 a,b,0"
    ]
#### damp form 2
    [
    "DAMP",
    "DIST = +[u;u]*a + [v;v]*b"
    ]
### stif:
    [
    "STIF",
    "DIST = +[u;u]*a + [v;v]*b"
    ]
### load:
#### load form 1
    [
    "LOAD fx fy fz"                     | <-- "LOAD fx,fy,fz"
    ]
#### load form 2
    [
    "LOAD = [u]*fx +[v]*fy +[w]*fz"
    ]

## 二、流程相关要素
按照区域定义顺序存储到相应位置
### 区域关键字
    "BFmate": 位于 mate行 前
    "AFmate"：位于 mate行 后
    "func"  ：位于 FUNC段 中
    "stif"  ：位于 STIF段 中，弱形式之前
    "mass"  ：位于 MASS段 中，弱形式之前
    "damp"  ：位于 DAMP段 中，弱形式之前
## code:
### \$cc or \$c6:
    "$CC fact=pe/(1.0+pv)/(1.0-2.0*pv);"
### $CV:
    "$CV ^dwave_i_j=+^d_i_j+^qrev_i_j*dt"
    "$CV aa = {un/x}
### $CP:
    "$CP dwave_i_j=+d_i_j+qrev_i_j*dt"
### $I:
    初始化位置声明
### @L:
    "@L gradv.xyz m ^e x y z un vn wn"
### @A:
    "@A fe_i_j=+[fe_i_j]+[fe_j_i]"
### @R:
    "@R fe_i_j=+[u_i]+[fe_j_i]"
### @S:
    "@S fev fe 1 5 9"
    注：fev 必须 由 fvect 或 fmatr 声明
### @W:
    "@W ep fe 6 3 2"
    注：ep 必须 由 vect 或 matrix 声明 并且元素必须为 func 声明的变量
### common:
    "COMMON double *inelm%1%2;"
### array:
    "ARRAY dev[3],dep[3],^e[3][3],^d[3][3],^qrev[3][3],^dwave[3][3],^dsv1[3][3]"

## 三、混合要素
### array:
注：如二所示，array 行保留在 xde_dict 的 流程相关保留字 'code' 所定义的相应位置之外，
             xde_dict 新增一关键字 'array' 保存 所有 array 行
             
    [
    "ARRAY dev[3],dep[3],^e[3][3],^d[3][3],^qrev[3][3],^dwave[3][3],^dsv1[3][3]"
    ]

# sec_parse() 解析后标准格式
注：sec_parse() 对非流程要素稍作处理，以便check_xde程序进行语法检查，流程相关要素保留原始字符串形式，同时对重复声明的 'disp', 'coef', 'coor', 'gaus', 'mate' 做警告与处理
### disp:
    ['u', 'v', 'w']
### coor:
    ['x', 'y', 'z']
### coef:
    ['un', 'vn', 'wn']
### func:
    [
        ['exx', 'eyy', 'ezz'],
        ['exy', 'eyx', 'ezx']
    ]
### shap:
    [
        ['%1', '%2'],
        ['q', '4,],
        ['%1', '%2c', 'v_w'],
        ['q', '4c', 'v_w'],
        ['%1', '%4', 'w']
    ]
### gaus:
    ['%3']
     or
    ['g2']
### mate:
    ['a', 'b', 'c', 'd', '1', '2.', '.3', '4e5']
### vect:
    {
        'u': ['u', 'v', 'w'],
        'f': ['fx', 'fy', 'fz']
    }
### matrix:
    {
        'sm': 
            [
                3, 
                3, 
                ['(1.-pv)', 'pv', 'pv'], 
                ['pv', '(1.-pv)', 'pv'], 
                ['pv', 'pv', '(1.-pv)']
            ], 
        'qrevm': 
            [
                3, 
                3, 
                ['1./3.0', '-1./6.0', '-1./6.0'], 
                ['-1./6.0', '1./3.0', '-1./6.0'], 
                ['-1./6.0', '-1./6.0', '1./3.0']
            ]
    }
### fvect:
    {
        'fev': [3],
        'fep': [3]
    }
### fmatr:
    {
        'fe': [3, 3],
        'fv': [2, 3]
    }
### mass:
#### mass form 1
    ['%1']
     or
    ['%1', 'a', 'b', '0']
#### mass form 2
    "MASS"
    "DIST = +[u;u]*a + [v;v]*b"
### damp:
#### damp form 1
    ['%1']
     or
    ['%1', 'a', 'b', '0']
#### damp form 2
    "DAMP"
    "DIST = +[u;u]*a + [v;v]*b"
### stif:
    "STIF"
    "DIST = +[u;u]*a + [v;v]*b"
### load:
#### load form 1
    ['fx', 'fy', 'fz']
#### load form 2
    "LOAD = [u]*fx +[v]*fy +[w]*fz"

# fnl_parse() 解析后标准格式
注：fnl_parse() 进一步将 xde_dict 的内容转换为可读形式
## 一、流程无关要素
注：除如下说明格式更改外，其他要素无更改
### mass:
#### mass form 1
    ['%1']                      -->     ['lump', '1.0']
     or
    ['%1', 'a', 'b', '0']       -->     ['lump', 'a', 'b', '0']
### damp:
#### damp form 1
    ['%1']                      -->     ['lump', '1.0']
     or
    ['%1', 'a', 'b', '0']       -->     ['lump', 'a', 'b', '0']
### mate:
    ['a', 'b', 'c', 'd', '1', '2.', '.3', '4e5']
      V
      V
    {
        "a": "1",
        "b": "2.",
        "c": ".3",
        "d": "4e5"
    }

### shap:
#### form 1: c8 element
    [
        ['%1', '%2']
    ]
      V
      V
    {
        "c8": ["u", "v", "w"]
    }
#### form 2: no mater ever else
    [
        ['q', '4,]
    ]
      V
      V
    {
        "q4": ["u", "v", "w"]
    }
#### form 3: c27 element
    [
        ['%1', '%2'],
        ['%1', '%4', 'w']
    ]
      V
      V
    {
        "c27": ["u", "v"],
        "c8" : ["w"]
    }
#### form 4: c8 element
    [
        ['%1', '%2'],
        ['%1', '%2c', 'w']
    ]
      V
      V
    {
        "c8": ["u", "v"],
        "c8c": ["v_w"]
    }

## 二、流程相关要素
### \$cc / \$c6:
    "$CC fact=pe/(1.0+pv)/(1.0-2.0*pv);"
    --> "Insr_Code: fact=pe/(1.0+pv)/(1.0-2.0*pv);"
        means 'Insert Code'
### $CV:
    "$CV ^dwave_i_j=+^d_i_j+^qrev_i_j*dt"
    "$CV aa = {un/x}
    --> "Tnsr_Asgn: ^dwave_i_j=+^d_i_j+^qrev_i_j*dt"
    --> "Tnsr_Asgn: aa = {un/x}
        means 'Tensor Assign or Coupled variables derivative Assign'
### $CP:
    "$CP dwave_i_j=+d_i_j+qrev_i_j*dt"
    --> "Cplx_Asgn: dwave_i_j=+d_i_j+qrev_i_j*dt"
        means 'Complex Assign'
### @L:
    "@L gradv.xyz m ^e x y z un vn wn"
    --> "Oprt_Asgn: ^e_i_j=gradv.xyz(x,y,z,un,vn,wn)"
        means 'Operator Assign'
### @A:
    "@A fp_1=+[fev_i]*ddfv_i+[fep_j]*ddfp_j*1.0"
    --> "Func_Asgn: [fp_1]=+[fev_i]*ddfv_i+[fep_j]*ddfp_j*1.0",
        means 'F tensor(Fvect,Fmatr) or Func variables Assign'
### @R:
    "@R fe_i_j=+[u_i]+[fe_j_i]"
    --> "Func_Asgn: [fe_i_j]=+[u_i]+[fe_j_i]",
        means 'F tensor(Fvect,Fmatr) or Func variables Assign'
### @S:
    "@S fev fe 1 5 9"
    --> "Func_Asgn: [fev_i]=fe[1,5,9]"
        means 'F tensor(Fvect,Fmatr) or Func variables Assign'
### @W:
    "@W ep fe 6 3 2"
    --> "Func_Asgn: ep_i=fe[6,3,2]"
        means 'F tensor(Fvect,Fmatr) or Func variables Assign'
### 注 @A, @R, @S, @W 统一为 Func_Asgn 后

    等号左边: 带'[]'表示 F 张量, 通过下标区分 Fvect 或 Fmatr
             无'[]'表示 func 张量, 通过下标区分 vect 或 matrix
    等号右边：非表达式结构，fe表示 F 张量，中括号内数字表示元素位置
             表达式结构，中括号内表示 F 或 Func 张量，中括号外表示 普通张量

# 三、混合要素
    根据 array 声明新增 array_vect, array_matrix 关键字
    将 "array dev[3],^e[3][2]" 中
    'dev[3]' 添加到 array_vect 中:
        {
            'dev': ['dev[1]', 'dev[2]', 'dev[3]']
        }
    '^e[3][2]' 添加到 array_matrix 中:
        {
            '^e':
                [
                    3,
                    2,
                    ['^e[1][1]', '^e[1][2]'],
                    ['^e[2][1]', '^e[2][2]'],
                    ['^e[3][1]', '^e[3][2]']
                ]
        }