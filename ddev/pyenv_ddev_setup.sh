#!/usr/bin/env bash

GREEN="\033[1;32m"
NOCOLOR="\033[0m"

if [[ "$OSTYPE" == "linux-gnu" ]]; then

  ## Install common dependencies
  echo -e "${GREEN}Installing common dependencies${NOCOLOR}"
  sudo apt update &&\
  sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl python-all-dev git \
    unixodbc unixodbc-dev tdsodbc

  ## Linux
  echo -e "${GREEN}Installing Pyenv${NOCOLOR}"
  curl https://pyenv.run | bash
  #pyenv
  #pyenv update
  export PATH="~/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"

  echo -e "${GREEN}Exporting Pyenv variables to bashrc${NOCOLOR}"
  echo 'export PATH="~/.pyenv/bin:$PATH"' >> ~/.bashrc
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc


  echo -e "${GREEN}Sourcing bashrc${NOCOLOR}"
  source ~/.bashrc

  echo -e "${GREEN}Updating pyenv metadata${NOCOLOR}"
  pyenv update && echo "Done"

elif [[ "$OSTYPE" == "darwin"* ]]; then
  ## Mac
  ## Install Hombrew: https://brew.sh/#install
  echo -e "${GREEN}Installing Homebrew${NOCOLOR}"
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

  echo -e "${GREEN}Installing Pyenv${NOCOLOR}"
  brew update && \
  brew install pyenv && \
  eval "$(pyenv init -)" && \
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  brew install readline xz && \
  sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
fi;

echo -e "${GREEN}Retrieving latest Python versions${NOCOLOR}"
## Set latest Python 2/3
if [[ "$OSTYPE" == "linux-gnu" ]]; then
  py2latest="$(pyenv install -l | grep -oP '^\s*2\.\d+\.(\d+)$' | sort -V | tail -n1)"
  py3latest="$(pyenv install -l | grep -oP '^\s*3\.8\.(\d+)$' | sort -V | tail -n1)"

elif [[ "$OSTYPE" == "darwin"* ]]; then
  py2latest="$(pyenv install -l | grep -oE '^\s*2\.\d+\.(\d+)$' | sort -V | tail -n1)"
  py3latest="$(pyenv install -l | grep -oE '^\s*3\.8\.(\d+)$' | sort -V | tail -n1)"
fi;

echo "Latest Python 2: $py2latest" && \
echo "Latest Python 3: $py3latest" && \

## Install latest Python 2/3
echo -e "${GREEN}Installing Python versions${NOCOLOR}"
pyenv install $py2latest && \
pyenv install $py3latest && \

## Set global python
# Choose which Python to set as global.

# pyglobal=$py2latest
pyglobal=$py3latest    # Note: Use Python2 if on Ubuntu14(trusty)

echo -e "${GREEN}Setting Global Python to ${pyglobal}.${NOCOLOR}"
pyenv global $pyglobal

echo -e "${GREEN}Listing Installed Python versions${NOCOLOR}"
pyenv versions


echo -e "${GREEN}Cloning integrations-core${NOCOLOR}"
git clone https://github.com/DataDog/integrations-core.git
echo -e "${GREEN}Cloning integrations-extras${NOCOLOR}"
git clone https://github.com/DataDog/integrations-extras.git

## Installs ddev

## dev from branch
#cd integrations-core/datadog_checks_dev/
#pip install -r requirements-dev.txt
#pip install -e .[cli]
#cd -

## stable from PyPI
pip install datadog-checks-dev[cli]

## Modifies ddev config find to view source config: e.g. /root/.local/share/dd-checks-dev/config.toml
ddev config set repos.core $(pwd)/integrations-core
ddev config set repos.extras $(pwd)/integrations-extras

echo -e "\n${GREEN}DONE. Manually run the following for good measure.${NOCOLOR} \n\nsource ~/.bashrc\n"
