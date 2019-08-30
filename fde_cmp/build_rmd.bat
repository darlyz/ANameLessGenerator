pyinstaller -i ectec.ico -F .\src\check_xde.py .\src\expr.py .\src\felac_data.py genxde.py .\src\ges2c.py .\src\parse_xde.py .\src\xde_help.py .\src\xde2ges.py .\src\xde2html.py .\src\xde2md.py .\src\__init__.py -n genxde.exe
copy dist\genxde.exe .\
rd /q /s dist
rd /q /s build
del /q *.spec