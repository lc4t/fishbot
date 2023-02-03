#! /bin/bash
echo "starting from entrypoint.sh for sanic"
cd /app/src
# pip3 config set global.index-url https://pypi.douban.com/simple/
pip3 install -r requirements.txt
python3 main.py