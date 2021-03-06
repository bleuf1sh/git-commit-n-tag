#!/bin/bash
# License located at https://github.com/bleuf1sh/git-byLines

LOCAL_GIT_REPO=~/git-byLines

function printBleuf1sh() {
  echo
  echo '               __   __'
  echo '              __ \ / __'
  echo '             /  \ | /  \'
  echo '                 \|/'
  echo '            _,.---v---._'
  echo '   /\__/\  /            \'
  echo '   \_  _/ /              \'
  echo '     \ \_|           @ __|'
  echo '  hjw \                \_'
  echo '  `97  \     ,__/       /'
  echo '    ~~~~`~~~~~~~~~~~~~~/~~~~~'
  echo '            bleuf1sh        '
  echo 
}

function resetColor() {
  echo -e "\033[0m\c"
}

function redColor() {
  echo -e "\033[0;31m\c"
}

function greenColor() {
  echo -e "\033[0;32m\c"
}

function blueColor() {
  echo -e "\033[0;34m\c"
}

function onSigterm() {
  redColor
  echo
  echo -e "Oops... something erred ):"
  resetColor
  exit 1
}

function refreshBash() {
  if [[ -e ~/.bash_profile ]]; then
    echo "sourcing ~/.bash_profile"
    source ~/.bash_profile
  fi
}

# usage: addTextIfKeywordNotExistToFile ~/path/to/file 'keyword' 'some string to append' 
function addTextIfKeywordNotExistToFile() {
  local file=$1
  local keyword=$2
  local line_to_add=$3

  if [ ! -e $file ]; then
    echo "Creating $file because did not exist"
    touch $file
  fi

  if grep -q "$keyword" $file; then
    echo "$keyword already exists in $file: $line_to_add"
  else
    echo "adding to $file: $line_to_add"
    echo "$line_to_add" | sudo tee -a $file
  fi
}

# usage: cloneGitRepo 'branch name' 
function cloneGitRepo() {
  local git_branch=$1
  echo
  echo "Clone Git Repo... $git_branch"
  
  if [ ! -d "$LOCAL_GIT_REPO" ]; then
    mkdir -p "$LOCAL_GIT_REPO"
    echo
    echo "Downloading Git Repo"
    git clone https://github.com/bleuf1sh/git-byLines.git "$LOCAL_GIT_REPO"
  else
    echo
    echo "Syncing Git Repo..."
    {
      pushd "$LOCAL_GIT_REPO"
      git checkout "$git_branch"
      popd
    } || {
      echo "An error occured changing to branch: $git_branch"
      echo "Moving on with business as usual... we'll try again later"
    }
    pushd "$LOCAL_GIT_REPO"
    git pull -r
    popd
  fi

  {
    pushd "$LOCAL_GIT_REPO"
    git checkout "$git_branch"
    popd
  } || {
    echo "An error occured changing to branch: $git_branch"
    echo "Moving on with business as usual"
  }

  greenColor
  echo 
  echo "Clone Git Repo... Done"
  resetColor
}

# usage: install 'git branch name' 
function install() {
  local git_branch=$1
  echo "Installing from git branch: $git_branch"

  # Find Python
  local python_ref=""
  if [ $(which python3) ]; then
    local python_ref="python3"
  elif [ $(which python) ]; then
    local python_ref="python"
  fi
  
  if test -z "$python_ref"; then
    redColor
    echo 'Python Not Found!'
    echo 'Go install it and then try again'
    resetColor
    exit 1
  fi
  
  echo "Found Python Ref:$python_ref"
  $python_ref --version

  # Find Python PIP
  local pip_ref=""
  if [ $(which pip3) ]; then
    local pip_ref="pip3"
  elif [ $(which pip) ]; then
    local pip_ref="pip"
  fi
  
  if test -z "$pip_ref"; then
    redColor
    echo 'Python PIP Not Found!'
    echo 'Go install it and then try again'
    echo 'If you use brew then try reinstalling python... otherwise try this:'
    echo "curl -sL \"https://bootstrap.pypa.io/get-pip.py\" > get-pip.py && sudo $python_ref get-pip.py"
    resetColor
    exit 1
  fi
  
  echo "Found Python PIP Ref:$pip_ref"
  $pip_ref --version

  # Check that PIP matches PYTHON
  local python_version="${python_ref//[!0-9]/}"
  local pip_version="${pip_ref//[!0-9]/}"
  if [ "$str1" == "$str2" ]; then
    echo "Python and PIP Versions Match"
  else
    redColor
    echo "Python and PIP Versions DO NOT MATCH... ABORTING..."
    resetColor
    exit 1
  fi

  # Clone the GIT repo
  cloneGitRepo "$git_branch"

  # Install dependencies using PIP
  echo
  echo "Installing Dependencies..."
  pushd "$LOCAL_GIT_REPO"
  $pip_ref install colorama --upgrade --target ./local_pip
  popd
  echo "Installing Dependencies... Done"

  # START BASH INSTALLATION
  local path_to_bash_profile=~/.bash_profile
  if [ -e $path_to_bash_profile ]; then
    if grep -q "git-byLines" $path_to_bash_profile; then
      echo "git-byLines are already mentioned in $path_to_bash_profile"
      echo
      read -p "Should the install continue? (y/N) " answer
      echo
      if [ $answer != "y" ]; then
        redColor
        echo "Goodbye"
        resetColor
        exit 1
      fi
    fi
  fi

  greenColor
  local bash_byLines="
function byLines() { 
  command $python_ref $LOCAL_GIT_REPO/byLines.py \"\$@\" ; 
}
  "
  local bash_git_override="
function git() { 
  command git \"\$@\" && byLines \"\$@\" ; 
}
  "
  addTextIfKeywordNotExistToFile $path_to_bash_profile "function byLines()" "$bash_byLines"
  addTextIfKeywordNotExistToFile $path_to_bash_profile "function git()" "$bash_git_override"
  # END BASH INSTALLATION
  
  # START FISH INSTALLATION
  mkdir -p ~/.config/fish
  local path_to_fish_config=~/.config/fish/config.fish  
  local fish_source_bleufish_config="source ~/.config/fish/bleuf1sh.fish"
  addTextIfKeywordNotExistToFile $path_to_fish_config "$fish_source_bleufish_config" "$fish_source_bleufish_config"

  local fish_byLines="
function byLines --description 'git-byLines'
  command $python_ref $LOCAL_GIT_REPO/byLines.py \$argv; 
end
  "
  local fish_git_override="
function git --description 'git-byLines override'
  command git \$argv && byLines \$argv; 
end
  "
  
  local path_to_bleufish_config=~/.config/fish/bleuf1sh.fish
  addTextIfKeywordNotExistToFile $path_to_bleufish_config "function byLines --description 'git-byLines'" "$fish_byLines"
  addTextIfKeywordNotExistToFile $path_to_bleufish_config "function git --description 'git-byLines override'" "$fish_git_override"
  # END BASH INSTALLATION

  resetColor
}

function intro() {
  greenColor

  printBleuf1sh

  resetColor

  echo "This script will install git-byLines to bash (:"
  
  greenColor
  echo
  read -p "----- PRESS ANY KEY TO CONTINUE -----" throw_away
  echo
  sleep 1

  echo
  read -p "Install git-byLines to bash? (y/N) " answer
  echo
  if [ $answer != "y" ]; then
    redColor
    echo "Goodbye"
    resetColor
    exit 1
  fi
  resetColor
}





# Fail fast if something goes wrong
set -e
trap onSigterm SIGKILL SIGTERM

default_git_branch="master"
git_branch=${1:-$default_git_branch}   # Defaults to master

intro && install "$git_branch"
greenColor
echo 'Installation done! Enjoy!'
resetColor
refreshBash