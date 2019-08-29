pyinstaller -i test.ico -F check_xde.py expr.py felac_data.py genxde.py ges2c.py parse_xde.py xde_help.py xde2ges.py xde2html.py xde2md.py -n genxde.exe
copy dist\genxde.exe .\
rd /q /s dist
rd /q /s build