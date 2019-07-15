pyinstaller -i test.ico -F check_xde.py expr.py felac_data.py genxde.py parse_xde.py xde_help.py -n genxde.exe
pyinstaller -i test.ico -F felac_data.py genxde2md.py parse_xde.py -n xde2md.exe
pyinstaller -i test.ico -F run.py -n run.exe
cp ./dist/*.exe ./