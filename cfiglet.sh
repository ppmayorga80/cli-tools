#!/usr/bin/env bash

figlet $@ | awk '{print "# "$0}'
