#!/usr/bin/env python

from pyfiglet import Figlet, figlet_format
import getpass
import curses
from curses import (
    A_BOLD, 
    A_NORMAL,
    COLOR_RED,
    COLOR_BLACK,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_WHITE,
)
from subprocess import Popen, DEVNULL
from time import sleep
from datetime import datetime, timedelta

fig_large = Figlet(
    font="cyberlarge",
    justify="center",
)
fig_small = Figlet(
    font="cybersmall",
    justify="center",
)

def playsound(soundname):
    Popen(["aplay", "sounds/{}.wav".format(soundname)],
          stdin=DEVNULL,
          stdout=DEVNULL,
          stderr=DEVNULL,
          )

def main(stdscr):
    curses.halfdelay(1)
    curses.init_pair(1, COLOR_GREEN, COLOR_BLACK)
    GREEN = curses.color_pair(1)
    curses.init_pair(2, COLOR_WHITE, COLOR_RED)
    ERROR = curses.color_pair(2) | A_BOLD
    curses.init_pair(3, COLOR_WHITE, COLOR_GREEN)
    SUCCESS = curses.color_pair(3) | A_BOLD
    playsound('startup')
    while True:
        stdscr.bkgd(' ', 0)
        stdscr.clear()
        stdscr.addstr(0,0,fig_large.renderText(
            "Office Lock System Engaged"
        ),GREEN|A_BOLD)
        stdscr.addstr(
            fig_small.renderText("ENTER CODE"),
            GREEN
        )
        stdscr.addstr("\n\n")
        stdscr.refresh()

        # Passcode entry loop
        passcode = ""
        starttime = datetime.now()
        while True:
            char = ''
            while not char:
                try:
                    char = stdscr.getkey()
                    starttime = datetime.now()
                except curses.error as e:
                    td = datetime.now() - starttime
                    if passcode and td > timedelta(seconds=5):
                        passcode = "TIMEOUT"
                        char = '\n'
            if char == '\n':
                break;
            if char == 'KEY_BACKSPACE':
                if len(passcode) > 0:
                    passcode = passcode[:-1]
                playsound('keypress')
            elif len(char) > 1:
                curpos = stdscr.getyx()
                maxyx = stdscr.getmaxyx()
                stdscr.addstr(maxyx[0]-1,int(maxyx[1]/2)-6,"INVALID KEY",ERROR)
                stdscr.move(curpos[0],curpos[1])
                playsound('warning')
            else:
                passcode = passcode + char
                playsound('keypress')

            curpos = stdscr.getyx()
            maxyx = stdscr.getmaxyx()
            stdscr.move(curpos[0],0)
            stdscr.clrtoeol()
            starstr = ""
            for i in range(len(passcode)):
                starstr = starstr + " <*>"
            starstr = starstr.lstrip()
            if len(starstr) > maxyx[1]:
                passcode = "TOOLONG"
                break;
            stdscr.addstr(curpos[0],
                          int((maxyx[1] - len(starstr))/2),
                          starstr)
            stdscr.refresh()

        # Check the passcode and act accordingly
        stdscr.clear()
        def errscreen(message):
            stdscr.bkgd(' ', ERROR)
            stdscr.addstr(0,0,fig_large.renderText("ACCESS DENIED"),ERROR)
            stdscr.addstr(fig_small.renderText(message),ERROR)

        if passcode == "6858":
            playsound('accessgranted')
            stdscr.bkgd(' ', SUCCESS)
            stdscr.addstr(0,0,fig_large.renderText("ACCESS GRANTED"),SUCCESS)

        elif passcode == "TOOLONG":
            playsound('error')
            errscreen("CODE TOO LONG")

        elif passcode == "TIMEOUT":
            playsound('error')
            errscreen("ENTRY TIMEOUT")

        elif not passcode:
            playsound('error')
            errscreen("NO CODE ENTERED")

        else:
            playsound('invalidcode')
            errscreen("INVALID CODE")
        stdscr.refresh()
        sleep(2)

curses.wrapper(main)
