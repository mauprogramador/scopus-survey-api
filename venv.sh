#!/bin/bash

REQUIRED_VERSION="3.12"
VENV_NAME=".venv"

trap "echo -e '\033[35;1m!\033[m \033[91mGot an interruption ✘\033[m'; exit 1" SIGINT
echo "Checking Prerequisites..."
echo -e "- Using version\033[37;1m ^$REQUIRED_VERSION\033[m for \033[37;1mPython3\033[m"

# Checking Python
if command -v python3 &>/dev/null; then

	if command -v python"$REQUIRED_VERSION" &>/dev/null; then
		echo -e "-\033[32m $(python"$REQUIRED_VERSION" -V) found ✔\033[m"
	else
		echo -e "-\033[91m Python $REQUIRED_VERSION not found ✘\033[m"
		echo ""
		echo -e "\033[33m$(python3 -V) found, but Python $REQUIRED_VERSION is required, please install it\033[m"
		exit 1
	fi
else
	echo -e "-\033[91m Python3 not found ✘\033[m"
	echo ""
	echo -e "\033[33mPython $REQUIRED_VERSION is required, please install it\033[m"
	exit 1
fi

# Checking Pip
if command -v pip &>/dev/null; then
	echo -e "-\033[32m Pip $(pip --version | awk '{print $2}') found ✔\033[m"
else
	echo -e "-\033[91m Pip not found ✘\033[m"
	echo ""
	echo -e "\033[33mPip is required, please install it\033[m"
	exit 1
fi

# Checking Venv
if python3 -c 'import venv' &>/dev/null; then
	echo -e "-\033[32m Venv module found ✔\033[m"
else
	echo -e "-\033[91m Venv module not found ✘\033[m"
	echo ""
	echo -e "\033[33mVenv module is required, please install it\033[m"
	exit 1
fi

echo "Creating Virtual Environment..."

if [ ! -d "$VENV_NAME" ]; then
	python"$REQUIRED_VERSION" -m venv "$VENV_NAME"
else
	echo -e "-\033[91m Venv conflicting ✘ \033[m"
	echo ""
	echo -e "\033[33mVenv directory \033[m(\033[37;1m$VENV_NAME\033[m\033[m)\033[33m already exists, skipping creation\033[m"
	exit 1
fi

# Check Exit Status
if [ $? -ne 0 ]; then
	echo -e "-\033[91m Failed to create Venv ✘ \033[m"
	echo ""
	echo -e "\033[33mRemoving Venv directory, please try later\033[m"

	if [ -d "$VENV_NAME" ]; then
		rm -rf "$VENV_NAME"
	fi
	exit 1
fi

echo -e "-\033[32m Venv \033[m(\033[37;1m$VENV_NAME\033[m\033[m)\033[32m created ✔\033[m"

# shellcheck source=.venv/
source "$VENV_NAME/bin/activate"

echo "Setting Pip, Setuptools and Wheel..."

pip install --upgrade pip setuptools wheel

# Check Exit Status
if [ $? -ne 0 ]; then
	echo -e "-\033[91m Failed in Setting Packages ✘ \033[m"
	echo ""
	echo -e "\033[33mRemoving Venv directory, please try later\033[m"

	if [ -d "$VENV_NAME" ]; then
		deactivate
		rm -rf "$VENV_NAME"
	fi
	exit 1
fi

echo -e "-\033[32m Packages installed ✔\033[m"

deactivate

echo -e "\033[92mAll Done ✔\033[m"
exit 0
