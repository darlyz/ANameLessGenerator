pyinstaller -i test.ico -F check_xde.py expr.py felac_data.py genxde.py parse_xde.py xde_help.py xde2ges.py xde2html.py xde2md.py -n genxde.exe
pyinstaller -i test.ico -F run.py -n run.exe
cp ./dist/*.exe ./