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
# -------------------------------------
alias tm0='tmux a -t0'
alias tm1='tmux a -t1'
alias tm2='tmux a -t2'
alias tm3='tmux a -t3'
alias logout="[[ -o login ]] && logout || qdbus org.kde.ksmserver /KSMServer logout 0 0 1"

#       __                        __ 
#      / /___  ____ _____  __  __/ /_
#     / / __ \/ __ '/ __ \/ / / / __/
#    / / /_/ / /_/ / /_/ / /_/ / /_  
#   /_/\____/\__, /\____/\__,_/\__/  
#           /____/                   
# -----------------------------------
function my_logout {
    #[[ -o login ]] && logout || qdbus org.kde.ksmserver /KSMServer logout 0 0 1
    #qdbus org.kde.ksmserver /KSMServer logout 0 0 1
    #gnome-session-quit --no-prompt
    loginctl terminate-user $USER
}

#      __                
#     / /_____ ___  _____
#    / __/ __ '__ \/ ___/
#   / /_/ / / / / / /    
#   \__/_/ /_/ /_/_/     
# -----------------------
function tmr {
    ARGUMENTS="$@"
    if [[ $ARGUMENTS == "" ]]; then
        ARGUMENTS="-ms"
    fi

    PSID=$(pgrep -f mr | xargs ps -fp | grep -E "\bmr\b" | awk -F' ' '{print $2}')

    if [[ $ARGUMENTS == "-v" ]]; then
        if [[ $PSID == "" ]]; then
            echo "mr is NOT RUNNING 😴"
        else
            echo "mr is RUNNING with PSID=$PSID 😎😎😎"
        fi
    else
        if [[ $PSID == "" ]]; then
            echo "Starting mr command with $ARGUMENTS" 
            nohup mr "$ARGUMENTS" &        
            PSID=$(ps -lea | grep mr | awk -F' ' '{print $4}')
            echo "mr is running now with PSID=$PSID 😎😎😎"
        else
            echo "Killing PSID=$PSID 🛑"
            kill $PSID
        fi
    fi
}


#                  __ 
#     ____  __  __/ /_
#    / __ \/ / / / __/
#   / /_/ / /_/ / /_  
#   \____/\__,_/\__/  
# --------------------
function tout {
    #default arguments
    ARGUMENTS="$@"
    if [[ $ARGUMENTS == "" ]]; then
        H=$((1+$RANDOM%2))
        M=$((15+$RANDOM%30))
        S=$((15+$RANDOM%30))

        ARGUMENTS="$H:$M:$S"
    fi

    #tmux project name
    PSID=$(pgrep -f out | xargs ps -fp | grep -E "\bout\b" | awk -F' ' '{print $2}')
    SESSION_NAME="timer"

    #decide if we attach or create a new tmux session
    tmux has-session -t $SESSION_NAME 2>/dev/null
    if [ "$?" -eq 1 ] ; then
        IS_MACOS=$(neofetch | grep OS | grep -oh macOS)
        if [[ $IS_MACOS ]]; then
            e1="osascript -e 'tell application \"loginwindow\" to  «event aevtrlgo»'"
            echo "Session executed in MAC OS"
            tmux new-session -d -s $SESSION_NAME "out $ARGUMENTS && ${e1}"
        else
          e1="loginctl terminate-user $USER"
          e2="gnome-session-quit --no-prompt"
          echo "No Session found.  Creating and executing."
          if [[ $XDG_CURRENT_DESKTOP == "KDE" ]]; then
              echo "Session executed in KDE"
              tmux new-session -d -s $SESSION_NAME "out $ARGUMENTS && ${e1}"
          else
              echo "Session executed in GNOME"
              tmux new-session -d -s $SESSION_NAME "out $ARGUMENTS && ${e1} || ${e2}"
          fi
        fi
    else
        echo "Session found."
    fi
    echo "Connecting to session: $SESSION_NAME"
    tmux attach-session -t $SESSION_NAME
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

