#!/bin/bash
FAIL=$'\e[0;31m'
INFO=$'\e[0;33m'
OK=$'\e[0;32m'
FILE=$'\e[1;96m'
NC=$'\e[0m'

# Install dependencies
if [[ $1 = "-i" ]] || [[ $1 = "--install" ]];then
    echo "Installing dependencies..."
    echo
    sudo apt install rpi.gpio gpsd gpsd-clients python3-pip
    sudo pip3 install -r requirements.txt

# Remove dependencies
elif [[ $1 = "-r" ]] || [[ $1 = "--remove" ]];then
    echo "${INFO}[INFO]${NC} pip3 dependencies must be uninstalled manually."
    echo
    
# Help message
elif [[ $1 = "-h" ]] || [[ $1 = "--help" ]];then
    echo "The setup script for Purdue Orbital's balloon computer environment."
    echo "Usage: sudo ./setup.sh <args>"
    echo
    echo "Arguments:"
    echo -e "\t-i, --install\tInstall dependencies for the flight computer"
    echo -e "\t-r, --remove\tUninstall dependencies for the flight computer"
    echo -e "\t-h, --help\tOpen this message"
    echo

# Wrong number of arguments
elif [[ -z "$1" ]];then
    echo "${FAIL}[ERROR]${NC} Exactly one argument is accepted."
    echo "Try --help to see a list of available arguments."
    echo

# Invalid argument
else
    echo "${FAIL}[ERROR]${NC} Invalid argument $1."
    echo "Try --help to see a list of available arguments."
    echo
fi



