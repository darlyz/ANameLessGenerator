# -*- mode: python -*-

block_cipher = None


a = Analysis(['expr.py', 'genxde.py', 'parse_xde.py', 'xde2ges.py', 'xde_help.py'],
             pathex=['E:\\Allo_Libs\\OneDrive\\code_test\\python\\NewFelacGenerator\\fde_cmp\\3old_py\\old6_py_source'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='genxde.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='test.ico')
