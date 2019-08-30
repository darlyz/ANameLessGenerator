pyinstaller -i ectec.ico -F ./src/check_xde.py ./src/expr.py ./src/felac_data.py genxde.py ./src/ges2c.py ./src/parse_xde.py ./src/xde_help.py ./src/xde2ges.py ./src/xde2html.py ./src/xde2md.py -n genxde.out
cp ./dist/genxde.out ./
rm -rf dist
rm -rf build
rm -f *.spec