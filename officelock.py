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
from time import sleep

fig_large = Figlet(
    font="cyberlarge",
    justify="center",
)
fig_small = Figlet(
    font="cybersmall",
    justify="center",
)
def main(stdscr):
    curses.halfdelay(20)
    curses.init_pair(1, COLOR_GREEN, COLOR_BLACK)
    GREEN = curses.color_pair(1)
    curses.init_pair(2, COLOR_WHITE, COLOR_RED)
    ERROR = curses.color_pair(2) | A_BOLD
    while True:
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
        while True:
            while True:
                try:
                    char = stdscr.getkey()
                    break;
                except curses.error as e:
                    if passcode:
                        passcode = "TIMEOUT"
                        char = '\n'
                        break;
            if char == '\n':
                break;
            if char == 'KEY_BACKSPACE':
                if len(passcode) > 0:
                    passcode = passcode[:-1]
                    curpos = stdscr.getyx()
                    stdscr.addstr(curpos[0],curpos[1]-4,"    ")
                    stdscr.move(curpos[0],curpos[1]-4)
            elif len(char) > 1:
                curpos = stdscr.getyx()
                maxyx = stdscr.getmaxyx()
                stdscr.addstr(maxyx[0]-1,int(maxyx[1]/2)-6,"INVALID KEY",ERROR)
                stdscr.move(curpos[0],curpos[1])
            else:
                passcode = passcode + char
                stdscr.addstr(" <*>")
            stdscr.refresh()

        # Check the passcode and act accordingly
        stdscr.clear()
        stdscr.addstr(0,0,fig_large.renderText("PASSCODE ENTERED"))
        stdscr.addstr(passcode)
        stdscr.refresh()
        sleep(2)

curses.wrapper(main)
