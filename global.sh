#!/bin/env bash

#      ______            _____                        __  _           
#     / ____/___  ____  / __(_)___ ___  ___________ _/ /_(_)___  ____ 
#    / /   / __ \/ __ \/ /_/ / __ '/ / / / ___/ __ '/ __/ / __ \/ __ \
#   / /___/ /_/ / / / / __/ / /_/ / /_/ / /  / /_/ / /_/ / /_/ / / / /
#   \____/\____/_/ /_/_/ /_/\__, /\__,_/_/   \__,_/\__/_/\____/_/ /_/ 
#                          /____/                                     
# --------------------------------------------------------------------
export PIPENV_VERBOSITY=-1

CLI_TOOLS_PATH="$HOME/Github/cli-tools/.venv/bin"
if [[ -d $CLI_TOOLS_PATH ]]; then
    export PATH="$PATH:${CLI_TOOLS_PATH}"
fi


#       ___    ___                     
#      /   |  / (_)___ _________  _____
#     / /| | / / / __ '/ ___/ _ \/ ___/
#    / ___ |/ / / /_/ (__  )  __(__  ) 
#   /_/  |_/_/_/\__,_/____/\___/____/  
#                                      
# -------------------------------------
alias tm0='tmux a -t0'
alias tm1='tmux a -t1'
alias tm2='tmux a -t2'
alias tm3='tmux a -t3'


#                  __ 
#     ____  __  __/ /_
#    / __ \/ / / / __/
#   / /_/ / /_/ / /_  
#   \____/\__,_/\__/  
#                     
# --------------------
function out {
    tout $@
    gnome-session-quit --no-prompt
}


#              __                          
#       ____  / /_  _________  ____  __  __
#      / __ \/ __ \/ ___/ __ \/ __ \/ / / /
#     / /_/ / /_/ / /__/ /_/ / /_/ / /_/ / 
#    / .___/_.___/\___/\____/ .___/\__, /  
#   /_/                    /_/    /____/   
# -----------------------------------------
function machine {
    UNAME_OUT="$(uname -s)"
    case "${UNAME_OUT}" in
        Linux*)     machine=LINUX;;
        Darwin*)    machine=MAC;;
        CYGWIN*)    machine=CYGWIN;;
        MINGW*)     machine=MINGW;;
        MSYS_NT*)   machine=GIT;;
        *)          machine="UNKNOWN:${UNAME_OUT}"
    esac
    printf $machine
}
MACHINE=$(machine)
if [[ $MACHINE == "LINUX" ]]; then
    alias pbcopy="xclip -sel clip"
fi


#                 __                __                         __
#      __________/ /_              / /___  ______  ____  ___  / /
#     / ___/ ___/ __ \   ______   / __/ / / / __ \/ __ \/ _ \/ / 
#    (__  |__  ) / / /  /_____/  / /_/ /_/ / / / / / / /  __/ /  
#   /____/____/_/ /_/            \__/\__,_/_/ /_/_/ /_/\___/_/   
#                                                                
# ---------------------------------------------------------------
alias mysql_tunnel='echo ssh -N -L 3308:127.0.0.1:3306 nuobond'
alias ssh_tunnel="ssh -ND 31416 mis15tours"

#                    __  __                              __  _             __     
#       ____  __  __/ /_/ /_  ____  ____     ____ ______/ /_(_)   ______ _/ /____ 
#      / __ \/ / / / __/ __ \/ __ \/ __ \   / __ '/ ___/ __/ / | / / __ '/ __/ _ \
#     / /_/ / /_/ / /_/ / / / /_/ / / / /  / /_/ / /__/ /_/ /| |/ / /_/ / /_/  __/
#    / .___/\__, /\__/_/ /_/\____/_/ /_/   \__,_/\___/\__/_/ |___/\__,_/\__/\___/ 
#   /_/    /____/                                                                 
# --------------------------------------------------------------------------------
# 1. Alias for python environments
function activate {
  VENV_DIR=""
  if [[ -d "venv" ]]; then
    VENV_DIR="venv"
  else
    if [[ -d ".venv" ]]; then
      VENV_DIR=".venv"
    fi
  fi
  source "${VENV_DIR}/bin/activate"
  if [[ ! "$PYTHONPATH" =~ "$PWD" ]]; then
    export PYTHONPATH="$PWD:$PWD/src:$PYTHONPATH"
  fi 
}

#              ____   _             __           __ 
#     _____   / __/  (_)  ____ _   / /  ___     / /_
#    / ___/  / /_   / /  / __ '/  / /  / _ \   / __/
#   / /__   / __/  / /  / /_/ /  / /  /  __/  / /_  
#   \___/  /_/    /_/   \__, /  /_/   \___/   \__/  
#                      /____/                       
# --------------------------------------------------
function cfiglet_raw {
    if ! [ -x "$(command -v figlet)" ]; then
        echo 'Error: figlet is not installed.' >&2
        exit 1
    fi

    #1. define the COMMENT string 
    COMMENT="#"
    while getopts ":c:" OPTION; do
        case "$OPTION" in
        c)
            COMMENT=${OPTARG}
            ;;
        *)
            break
            ;;
        esac
        shift
    done


    #     __ _       _      _   
    #    / _(_) __ _| | ___| |_ 
    #   | |_| |/ _' | |/ _ \ __|
    #   |  _| | (_| | |  __/ |_ 
    #   |_| |_|\__, |_|\___|\__|
    #          |___/            
    # --------------------------
    #2. execute figlet command and replace "`" with "'" to avoid bash scaping issues
    figlet $@ | awk -v comment_string="${COMMENT}" '{print comment_string," ",$0}' | tr '`' "'"
    #3. add an extra line to the end of the figlet command
    dash_len=$(figlet $@ | awk '{if(length > x){x=length} }END{print x+2}')
    printf "%s" "${COMMENT} "
    for i in $(seq $dash_len); do printf "-";done
    #4. end with a new line
    printf "\n"
}

# 2. commented figlet, use to comment in C style mode use `cfiglet -c// arguments`
#    example:
#        cfiglet  hello python
#        cfiglet -c// -f slant C italic style
#        cfiglet -c-- SQL style
function cfiglet {
    if ! [ -x "$(command -v figlet)" ]; then
        echo 'Error: figlet is not installed.' >&2
        exit 1
    fi

    UNAME_OUT="$(uname -s)"
    case "${UNAME_OUT}" in
        Linux*)     machine=LINUX;;
        Darwin*)    machine=MAC;;
        CYGWIN*)    machine=CYGWIN;;
        MINGW*)     machine=MINGW;;
        MSYS_NT*)   machine=GIT;;
        *)          machine="UNKNOWN:${UNAME_OUT}"
    esac

    cfiglet_raw $@
    if [[ $machine == "LINUX" ]]; then
        cfiglet_raw $@ | xclip -sel clip
    fi
    if [[ $machine == "MAC" ]]; then
        cfiglet_raw $@ | pbcopy
    fi

}

