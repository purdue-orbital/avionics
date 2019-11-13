#!/bin/bash
FAIL='\033[0;31m'
INFO='\033[0;33m'
OK='\033[0;32m'
FILE='\033[0;36m'
NC='\033[0m'

traceback_path='logs/traceback.log'
program_path='src/origin.py'
status_log_path='logs/status[].log'

# Clear traceback.log
truncate -s 0 ${traceback_path}

echo "Checking Python version..."

version=$( python3 -c 'import sys; print(sys.version_info[1])')
if [[ ${version} -lt '5']]; then
    echo
    echo "${FAIL}[ERROR]${NC} Python version must be 3.5 or higher"
    echo "Your version is:"
    python3 --version
    echo "${FAIL}[Process Failed]${NC}"
    echo
    exit 1
fi

echo "Attempting to run ${FILE}${program_path}${NC}"

sudo python3 ${program_path} 2> ${traceback_path}
if [[$? == '1']]; then
    traceback=$( tail -1 ${traceback_path})
    echo "${traceback}"
    echo "^%0.s" $(seq 1 ${#traceback})
    echo "${FILE}${program_path}${NC} did not execute successfully"
    echo "See ${INFO}${traceback_path}${NC} for the full error stack."
    echo "${FAIL}[Process Failed]${NC}"
    echo
    exit 1
fi

exit 0