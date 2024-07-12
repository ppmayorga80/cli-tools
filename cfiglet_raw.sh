#!/usr/bin/env bash

#        _                       _   
#     __| | ___   ___ ___  _ __ | |_ 
#    / _' |/ _ \ / __/ _ \| '_ \| __|
#   | (_| | (_) | (_| (_) | |_) | |_ 
#    \__,_|\___/ \___\___/| .__/ \__|
#                         |_|        
# -----------------------------------
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

# case $1 in
#     -c=*|--comment=*)
#         COMMENT="${1#*=}"
#         shift # past argument=value
#         ;;
#     -c|--comment)
#         shift # past argument=value
#         COMMENT=$1
#         shift
#         ;;
#     -c*)
#         COMMENT="${1#*c}"
#         shift
#         ;;
# esac


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