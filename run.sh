#!/bin/bash
FAIL=$'\e[0;31m'
INFO=$'\e[0;33m'
OK=$'\e[0;32m'
FILE=$'\e[1;96m'
NC=$'\e[0m'

local_path='../'
traceback_path='logs/traceback.log'
program_path='src/'
program='balloon.py'
ARGS=''


# Move to run.sh working directory
cd $(dirname "$0")
cd ${program_path}

# Clear traceback.log
truncate -s 0 ${local_path}${traceback_path}

text="    ____                 __           
   / __ \__  ___________/ /_  _____   
  / /_/ / / / / ___/ __  / / / / _ \  
 / ____/ /_/ / /  / /_/ / /_/ /  __/  
/_/    \__,_/_/   \__,_/\__,_/\___/   
       ____       __    _ __        __
      / __ \_____/ /_  (_) /_____ _/ /
     / / / / ___/ __ \/ / __/ __ \`/ / 
    / /_/ / /  / /_/ / / /_/ /_/ / /  
    \____/_/  /_.___/_/\__/\__,_/_/   "

echo
echo "${INFO}${text}${NC}"
echo
echo "PURDUE ORBITAL, ${INFO}PURDUE UNIVERSITY${NC}"
echo "Avionics Sub Team"
echo

if [ "$EUID" -ne 0 ]
then
    echo "${FAIL}[Error]${NC} The script ${FILE}run.sh${NC} requires root permissions to execute."
    echo "Please run as root or use ${FILE}sudo <command>${NC}"
    exit 1
fi

echo "Checking Python version..."

version=$( python3 -c 'import sys; print(sys.version_info[1])')
if [[ ${version} -lt '6' ]]
then
    echo
    echo "${FAIL}[ERROR]${NC} Python version must be 3.6 or higher"
    echo "Your version is:"
    python3 --version
    echo "${FAIL}[Process Failed]${NC}"
    echo
    exit 1
fi

echo "Python check: ${OK}[PASS]${NC}"
echo

for i in "$@"
do
    case $i in
	-b|--balloon)
	    program='balloon.py'
	    ;;
	-r|--rocket)
	    program='rocket.py'
	    ;;
	-p|--printing)
	    ARGS+=' -p'
	    ;;
	-h|--help)
	    echo "The setup script for Purdue Orbital's balloon computer environment."
	    echo "Usage: sudo ./run.sh <args>"
	    echo
	    echo "Arguments:"
	    echo -e "\t-b, --balloon\tLaunch balloon environment"
	    echo -e "\t-r, --rocket\tLaunch rocket environment"
	    echo -e "\t-h, --help\tOpen this message"
	    echo
	    ;;
	*)
	    echo "${FAIL}[ERROR]${NC} Command line option $i is not a supported argument."
	    echo "Try --help to see a list of available arguments."
	    echo
	    exit 0
	    ;;
    esac
done

echo "Attempting to run ${FILE}${program_path}${program}${NC}"

sudo python3 ${program}${ARGS} 2> ${local_path}${traceback_path}
if [[ $? == '1' ]]
then
    traceback=$( tail -1 ${local_path}${traceback_path})
    echo "${traceback}"
    echo "${FILE}${program_path}${program}${NC} did not execute successfully"
    echo "See ${FILE}${traceback_path}${NC} for the full error stack."
    echo "${FAIL}[Process Failed]${NC}"
    echo
    exit 1
fi
	    
	


