#!/bin/bash

echo -e "\033[93mChecking Prerequisites...\033[m"

# Checking if Python3 is installed
if command -v python3 &>/dev/null; then
    echo -e "\033[92mPython3 is installed ✔\033[m"
else
    echo -e "\033[91mPython3 is not installed ˟\033[m"
    exit 1
fi

version="3.11"

# Checking if Python3.11 is installed
if [ -x "$(command -v python3.11)" ]; then
    echo -e "\033[92mPython3.11 is installed ✔ \033[93m$(python3.11 -V)\033[m"
else
    echo -e "\033[91mPython3.11 is not installed ˟\033[m"
    echo -ne "\nWould you like to continue with \033[93m$(python3 -V)\033[m? [Y/N]: "
    read answer
    if [ "$answer" = "Y" ] || [ "$answer" = "y" ]; then
        version="$(python3 --V 2>&1 | awk '{print $2}')"
        echo -e "\033[91mThere may be some unexpected errors ‼\033[m"
        echo -e "\n\033[92mRunning with $(python3 -V) ✔"
    else
        echo -e "\nPlease install \033[93mPython3.11\033[m\n"
        exit 1
    fi
fi

# Checking if Pip is installed
if command -v pip &>/dev/null; then
    echo -e "\033[92mPip is installed ✔ \033[93mPip $(pip --version | awk '{print $2}')\033[m"
else
    echo -e "\033[91mPip is not installed ˟\033[m"
    exit 1
fi

# Checking if Venv is installed
if python3 -c 'import venv' &>/dev/null; then
    echo -e "\033[92mVenv Module is installed ✔\033[m"
else
    echo -e "\033[91mVenv Module is not installed ˟\033[m"
    exit 1
fi

echo -e "\033[93mCreating Python Virtual Environment...\033[m"

python"$version" -m venv .venv

# Check the exit status of the venv creation
if [ $? -ne 0 ]; then
    echo -e "\033[91mFailed to create Python Venv ˟ \033[93mRemoving Directory...\033[m"
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    exit 1
fi

echo -e "\033[92mVirtual Environment created ✔ \033[m(\033[34;1m.venv\033[m)"

source .venv/bin/activate

echo -e "\033[93mUpgrading Pip and Installing Packages...\033[m"

pip3 install --upgrade pip

pip3 install wheel

pip3 install poetry

echo -e "\033[92mWheel and Poetry packages installed ✔\033[m"

deactivate

echo -e "\033[92mCompleted\033[m"
echo -e "\nPlease run\033[93m make install\033[m\n"
