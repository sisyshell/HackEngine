#!/usr/bin/python
import sys, subprocess

# ANSI color codes
RS="\033[0m"    # reset
HC="\033[1m"    # hicolor
UL="\033[4m"    # underline
INV="\033[7m"   # inverse background and foreground
FBLK="\033[30m" # foreground black
FRED="\033[31m" # foreground red
FGRN="\033[32m" # foreground green
FYEL="\033[33m" # foreground yellow
FBLE="\033[34m" # foreground blue
FMAG="\033[35m" # foreground magenta
FCYN="\033[36m" # foreground cyan
FWHT="\033[37m" # foreground white
BBLK="\033[40m" # background black
BRED="\033[41m" # background red
BGRN="\033[42m" # background green
BYEL="\033[43m" # background yellow
BBLE="\033[44m" # background blue
BMAG="\033[45m" # background magenta
BCYN="\033[46m" # background cyan
BWHT="\033[47m" # background white

def error(text):
  print(FRED+"[Error] "+str(text)+FWHT)

def success(text):
  print(FGRN+"[Success] "+str(text)+FWHT)
  
def info(text):
  print(FWHT+"[Information] "+str(text)+FWHT)
  
def warnnig(text):
  print(FWHT+"[Information] "+str(text)+FWHT)

# Banner
def logo():
  if sys.platform == 'linux' or sys.platform == 'linux2':
    subprocess.call("clear", shell=True)
  else:
    subprocess.call("cls", shell=True)
  print(FCYN+"+"+"-"*63+"+")
  print("|" +BCYN+FBLK+ " "*63 +FCYN+BBLK+ "|")
  print("|" +BCYN+FBLK+ " "*24 + "HackEngine v0.1 " + " "*23 +FCYN+BBLK+ "|")
  print("|" +BCYN+FBLK+ " "*63 +FCYN+BBLK+ "|")
  print(FCYN+"+"+"-"*63+"+")
  print(FWHT+BBLK)