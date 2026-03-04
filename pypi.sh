#!/usr/bin/env sh

# to use this env type either:
# . pypi.sh
# or
# source pypi.sh

python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install setuptools wheel

echo '
import os
os.unlink(__file__)

from setuptools import setup, find_packages

setup(
  name="jstamp",
  version="0.0.1",
  packages=find_packages(),
  description="Python to JavaScript signatures for ESM out of introspection",
  author="Andrea Giammarchi",
  install_requires=[],
)

' > setup.py

rm -rf ./pypi
rm -rf ./wheel
mkdir -p ./wheel/jstamp/
cp ./jstamp.py ./wheel/jstamp/__init__.py
cp ./setup.py ./wheel/
cd wheel
python setup.py bdist_wheel
sleep 1
cd ..
mv wheel/dist ./pypi
mv wheel/*.egg-info ./pypi
rm -rf wheel
mv pypi/*.whl ./
rm -rf pypi
rm -f setup.py

unzip -o ./jstamp-0.0.1-py3-none-any.whl -d ./pypi/
mv *.whl ./pypi/
