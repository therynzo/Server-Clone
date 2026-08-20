#!/bin/bash
set -e

# Setup Colors
RED='\033[0;31m'
NC='\033[0m'
WHITE='\033[1;37m'

clear

# Animated Red TheRynzo Banner (Simple & Clean)
echo -e "${RED}"
cat << "EOF" | while read -r line; do echo "$line"; sleep 0.1; done
 _____ _       ___
|_   _| |_ ___| _ \_  _ _ _  ____ ___
  | | | ' \ -_)   / || | ' \|_  // _ \
  |_| |_||_\___|_|_\_, |_||_|/__/\___/
                   |__/
EOF
echo -e "${NC}"

# Animated Subtitle
SUBTITLE="Server-Clone Setup"
echo -e "${RED}"
for (( i=0; i<${#SUBTITLE}; i++ )); do
    echo -n "${SUBTITLE:$i:1}"
    sleep 0.05
done
echo -e "${NC}\n"

echo -e "${RED}====================================================${NC}"
echo -e "${WHITE}  INITIALIZING DEPLOYMENT${NC}"
echo -e "${RED}====================================================${NC}\n"

# 1. Environment Detection (Termux vs Ubuntu)
if [ -n "$PREFIX" ] && [ -x "$PREFIX/bin/apt" ]; then
    ENV_TYPE="Termux (Mobile)"
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    ENV_TYPE="Ubuntu/Debian (VPS)"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

echo -e "${RED}➤${NC} ${WHITE}Detected Environment:${NC} ${RED}$ENV_TYPE${NC}"
sleep 1

# 2. System Update & Upgrades
echo -e "${RED}➤${NC} ${WHITE}Updating system packages...${NC}"
if [ "$ENV_TYPE" == "Termux (Mobile)" ]; then
    pkg update -y && pkg upgrade -y
else
    sudo apt-get update -y && sudo apt-get upgrade -y
fi
sleep 1

# 3. Installing Dependencies (Python & Git)
echo -e "${RED}➤${NC} ${WHITE}Installing Python & Git...${NC}"
if [ "$ENV_TYPE" == "Termux (Mobile)" ]; then
    pkg install python git -y
else
    sudo apt-get install python3 python3-pip git -y
fi
sleep 1

# 4. Cloning the Repository
echo -e "${RED}➤${NC} ${WHITE}Fetching Repository from GitHub...${NC}"
if [ -d "Server-Clone" ]; then
    echo -e "${RED}➤${NC} ${WHITE}Cleaning up old directory...${NC}"
    rm -rf Server-Clone
fi
git clone https://github.com/therynzo/Server-Clone.git
cd Server-Clone
sleep 1

# 5. Installing Python Requirements
echo -e "${RED}➤${NC} ${WHITE}Installing dependencies (requirements.txt)...${NC}"
$PIP_CMD install -r requirements.txt
sleep 1

# 6. Launching the Bot
echo -e "\n${RED}====================================================${NC}"
echo -e "${WHITE}  STARTING BOT.PY${NC}"
echo -e "${RED}====================================================${NC}\n"

$PYTHON_CMD bot.py
