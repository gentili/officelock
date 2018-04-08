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

fig_large = Figlet(
    font="cyberlarge",
    justify="center",
)
fig_small = Figlet(
    font="cybersmall",
    justify="center",
)

def gif_loop(gif, duration):

    imgs = fb.ready_gif(gif, True)
    event = Event()
    starttime = datetime.now()
    for img, dur in cycle(imgs):
        Timer(dur, lambda e:event.set(), [event]).start()
        fb.show_img(img)
        event.wait()
        event.clear()
        td = datetime.now() - starttime
        if td > timedelta(seconds=duration):
            return

def playsound(soundname):
    Popen(["aplay", "sounds/{}.wav".format(soundname)],
          stdin=DEVNULL,
          stdout=DEVNULL,
          stderr=DEVNULL,
          )

def main(stdscr):
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
        stdscr.addstr(0,0,fig_large.renderText(
            "Office Lock System Engaged"
        ),GREEN|A_BOLD)
        stdscr.addstr(
            fig_small.renderText("ENTER CODE"),
            GREEN
        )
        stdscr.addstr("\n\n")
        stdscr.refresh()

        # Clear any kestrokes in the queue
        try:
            while True:
                stdscr.getkey()
        except curses.error:
            pass

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

        elif passcode == "24601":
            stdscr.bkgd(' ', SUCCESS)
            stdscr.addstr(0,0,fig_large.renderText("Shutdown Initiated"),SUCCESS)
            stdscr.refresh()
            playsound('crash')
            run(['sudo', 'poweroff'])

        elif passcode == "90210":
            return

        elif passcode == "911":
            playsound('accessgranted')
            gif_loop(
                fb.ready_img('../../Pictures/computer_art/fire__r10061297101.gif', False),
                # fb.ready_img('../../Pictures/computer_art/lonely.gif', False),
                10,
            )
            fb.black_scr()
            continue


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
            errscreen(passcode)
            fullfilelist = []
            for root, directories, filenames in os.walk('../../Pictures/'):
                for filename in filenames:
                    fullfilelist.append(os.path.join(root,filename))
            try:
                passnum = int(passcode)
                if passnum < len(fullfilelist):
                    playsound('warning')
                    gif_loop(
                        fb.ready_img(fullfilelist[passnum], False),
                        10,
                    )
                    fb.black_scr()
            except Exception:
                pass

            playsound('invalidcode')
            errscreen("INVALID CODE")
        stdscr.refresh()
        sleep(2)

curses.wrapper(main)
print_figlet("Restart")
