#!/bin/bash

echo -e "\033[35;1m>\033[m Checking Prerequisites..."

# Checking if Python3 (and which of it) is installed
if command -v python3 &>/dev/null; then

    if command -v python3.11 &>/dev/null; then
        echo -e "-\033[92m $(python3.11 -V) installed ✔\033[m"
        version="11"
    else
        version=$(ls -1 /usr/bin/python3* | grep -Eo 'python3\.[0-9]*$' | sort -V | uniq | tail -n 1 | grep -oP '\d+\.\K\d+')

        echo -e "-\033[91m Python 3.11 not installed ✘\033[m"
        echo -e "\033[93mWARNING:\033[m This application was built on \033[37;1mPython3.11.0rc1\033[m, so some unexpected errors may occur when using a different version."

        echo -ne "\033[35;1m?\033[m Would you like to continue with \033[37;1m$(python3."$version" -V)\033[m? [\033[32my\033[m/\033[31mn\033[m]: "
        read answer

        if [ "$answer" = "Y" ] || [ "$answer" = "y" ]; then
            echo -e "-\033[92m Running with $(python3."$version" -V) ✔\033[m"
        else
            echo -e "\033[35;1m!\033[m Please install \033[37;1mPython\033[m at least version \033[37;1m3.11\033[m. For further information visit https://docs.python-guide.org/starting/install3/linux/"
            exit 1
        fi
    fi
else
    echo -e "-\033[91m Python3 not installed ✘\033[m"
    echo -e "\033[35;1m!\033[m Please install \033[37;1mPython\033[m at least version \033[37;1m3.11\033[m. For further information visit https://docs.python-guide.org/starting/install3/linux/"
    exit 1
fi

# Checking if Pip is installed
if command -v pip &>/dev/null; then
    echo -e "-\033[92m Pip $(pip --version | awk '{print $2}') installed ✔\033[m"
else
    echo -e "-\033[91m Pip not installed ✘\033[m"
    exit 1
fi

# Checking if Venv is installed
if python3 -c 'import venv' &>/dev/null; then
    echo -e "-\033[92m Venv Module installed ✔\033[m"
else
    echo -e "-\033[91m Venv Module not installed ✘\033[m"
    exit 1
fi

echo -e "\033[35;1m>\033[m Creating \033[37;1mPython Virtual Environment\033[m..."

if [ ! -d ".venv" ]; then
    python3."$version" -m venv .venv
fi

# Check the exit status of the venv creation
if [ $? -ne 0 ]; then
    echo -e "-\033[91m Failed to create Python Venv ✘ \033[m"
    echo -e "\033[35;1m>\033[m Removing directory..."
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    exit 1
fi

echo -e "-\033[92m Virtual Environment \033[m(\033[34;1m.venv\033[m\033[m)\033[92m created ✔\033[m"

source .venv/bin/activate

echo -e "\033[35;1m>\033[m Upgrading \033[37;1mPip\033[m and installing packages...\033[m"

pip install --upgrade pip

pip3 install wheel

pip3 install poetry

echo -e "-\033[92m Wheel and Poetry packages installed ✔\033[m"

deactivate

if [ ! -f ".env" ]; then
    touch .env
fi

echo -e "\033[35;1m>\033[m Completed. Please run\033[37;1m make install\033[m\n"
