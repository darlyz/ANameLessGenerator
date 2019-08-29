pyinstaller -i test.ico -F check_xde.py expr.py felac_data.py genxde.py ges2c.py parse_xde.py xde_help.py xde2ges.py xde2html.py xde2md.py -n genxde.out
cp ./dist/genxde.out ./
rm -rf dist
rm -rf build