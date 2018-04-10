#!/usr/bin/env python

from pyfiglet import Figlet, figlet_format, print_figlet
import os
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
from subprocess import Popen, DEVNULL, run
from time import sleep
from datetime import datetime, timedelta
from FBpyGIF import fb
from itertools import cycle
import imghdr
from threading import Timer, Event
from random import randint

fig_large = Figlet(
    font="cyberlarge",
    justify="center",
)
fig_small = Figlet(
    font="cybersmall",
    justify="center",
)

def flushkeys(stdscr):
    try:
        while True:
            stdscr.getkey()
    except curses.error:
        pass

def gif_loop(gif, stdscr):

    imgs = fb.ready_gif(gif, True)
    event = Event()
    flushkeys(stdscr)
    for img, dur in cycle(imgs):
        if dur == 1:
            dur = 0.001
        Timer(dur, lambda e:event.set(), [event]).start()
        fb.show_img(img)
        try:
            return stdscr.getkey()
        except curses.error:
            pass
        event.wait()
        event.clear()

def playsound(soundname):
    Popen(["aplay", "sounds/{}.wav".format(soundname)],
          stdin=DEVNULL,
          stdout=DEVNULL,
          stderr=DEVNULL,
          )

def main(stdscr):
    fullfilelist = []
    for root, directories, filenames in os.walk('../../Pictures/'):
        for filename in filenames:
            fullfilelist.append(os.path.join(root,filename))
    curses.curs_set(False)
    curses.halfdelay(1)
    curses.init_pair(1, COLOR_GREEN, COLOR_BLACK)
    GREEN = curses.color_pair(1)
    curses.init_pair(2, COLOR_WHITE, COLOR_RED)
    ERROR = curses.color_pair(2) | A_BOLD
    curses.init_pair(3, COLOR_WHITE, COLOR_GREEN)
    SUCCESS = curses.color_pair(3) | A_BOLD
    fb.ready_fb()
    playsound('startup')
    while True:
        stdscr.bkgd(' ', 0)
        stdscr.clear()
        stdscr.addstr(4,0,fig_large.renderText(
            "Office Lock System Engaged"
        ),GREEN|A_BOLD)
        stdscr.addstr(
            fig_small.renderText("ENTER CODE"),
            GREEN
        )
        stdscr.addstr("\n\n")
        stdscr.refresh()

        # Clear any kestrokes in the queue
        flushkeys(stdscr)

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
            stdscr.addstr(7,0,fig_large.renderText("ACCESS DENIED"),ERROR)
            stdscr.addstr(fig_small.renderText(message),ERROR)

        passnum = len(fullfilelist)
        try:
            passnum = int(passcode)
        except Exception:
            pass


        if passcode == "6858":
            playsound('accessgranted')
            stdscr.bkgd(' ', SUCCESS)
            stdscr.addstr(7,0,fig_large.renderText("ACCESS GRANTED"),SUCCESS)

        elif passcode == "24601":
            stdscr.bkgd(' ', SUCCESS)
            stdscr.addstr(7,0,fig_large.renderText("Shutdown Initiated"),SUCCESS)
            stdscr.refresh()
            playsound('crash')
            run(['sudo', 'poweroff'])

        elif passcode == "438007":
            stdscr.bkgd(' ', SUCCESS)
            stdscr.addstr(7,0,fig_large.renderText("Reboot Initiated"),SUCCESS)
            stdscr.refresh()
            playsound('crash')
            run(['sudo', 'reboot'])

        elif passcode == "\t=":
            return

        elif passcode == "TOOLONG":
            playsound('error')
            errscreen("CODE TOO LONG")

        elif passcode == "TIMEOUT":
            playsound('error')
            errscreen("ENTRY TIMEOUT")

        elif not passcode:
            playsound('error')
            errscreen("NO CODE ENTERED")

        elif passcode == "12345":
            playsound('warning')
            stdscr.refresh()
            curpic = randint(0,len(fullfilelist)-1)
            while True:
                char = gif_loop(
                    fb.ready_img(fullfilelist[curpic], False),
                    stdscr,
                )
                playsound('keypress')
                if char == '\n':
                    break;
                elif char == '-':
                    curpic = curpic - 1
                    if curpic < 0:
                        curpic = len(fullfilelist) - 1
                elif char == '+':
                    curpic = curpic + 1
                    if curpic >= len(fullfilelist):
                        curpic = 0

            fb.black_scr()
            continue

        elif passnum < len(fullfilelist):
            playsound('warning')
            stdscr.refresh()
            gif_loop(
                fb.ready_img(fullfilelist[passnum], False),
                stdscr,
            )
            fb.black_scr()
            continue

        else:
            playsound('invalidcode')
            errscreen("INVALID CODE")
        stdscr.refresh()
        sleep(2)

curses.wrapper(main)
print_figlet("Restart")
