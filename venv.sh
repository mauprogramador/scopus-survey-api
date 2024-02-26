#!/bin/bash

echo -e "\033[93mCreating Python Virtual Environment\033[m"

if [ $# -eq 0 ]; then
  python3 -m venv .venv
else
  python"$1" -m venv .venv
fi

source .venv/bin/activate

echo -e "\033[93mInstalling Venv Packages\033[m"

pip3 install --upgrade pip

pip3 install wheel

pip3 install poetry

deactivate

echo -e "\033[92mCompleted\033[m"
