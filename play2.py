import re
import sys
from subprocess import Popen, PIPE
import os
import curses
import random
import time

replay = False
shuffle = False

player = None;

promptHeader = "Give command: "
promptLine = "[a/b/c/d]: "

if len(sys.argv) > 1:
	args = sys.argv[1:]
	for thing in args:
		if thing == "r" or thing == "R":
			replay = True
		if thing == "s" or thing == "S":
			shuffle = True
	print replay, shuffle
			

process = Popen("ls -R",shell=True,stdout=PIPE)
stdout, stderr = process.communicate()
files = []
dirs = stdout.split("./")
for i in range(len(dirs)):
	dirs[i] = dirs[i].strip()
if len(dirs) > 1:
	for i in range(len(dirs)):
		hold = dirs[i].split(":")
		if len(hold) > 1:
			pts = hold[1].split("\n")
			for thing in pts:
				files.append(hold[0]+"/"+thing)
		else:
			for thing in hold[0].split("\n"):
				files.append(thing)
else: 	
	files = stdout.split("\n")


path,patherr = (Popen("pwd",stdout=PIPE)).communicate()

def show_songs(songs, current):
	height,width = stdscr.getmaxyx()
	maxLength = width-3
	space = height - 5
	stdscr.clear()
	low = current-(space/2)-1
	if low<(space/2):
		low = 0
	high = low + space	
    
	stdscr.addstr(0,0,"DirPlay Playlist")
	stdscr.addstr(1,0," " + ("-"*(width-2)) + " ")
	for song in range(len(songs))[low:high]:
                line = songs[song]
                if song == current:   
                        line = "* "+line
                stdscr.addstr(song-low+3,0,line[:maxLength])
        stdscr.refresh()
	return (height,width)

def show_prompt(header,line):
	height,width = stdscr.getmaxyx()
	header = header + (" " * (width-len(header)))
	line = line + (" " * (width-len(line)))
	stdscr.addstr(height-2,0,header[:width-1])
	stdscr.addstr(height-1,0,line[:width-1])
	stdscr.refresh()

def sane():
	curses.echo()
	curses.nocbreak()
	curses.endwin()

def die():
	sane()
	os.system("killall afplay && killall DirPlay")
	sys.exit()


def playArray(a):
	global replay,files

	if shuffle == True:
		random.shuffle(a)
	it = 0
	tarry = 0
	while it < len(a):
		song = a[it]
#		os.system("afplay "+song)
		location =  path[:-1]+"/"+song
		location = location.replace('"','\\"')
		show_songs(a,a.index(song))
		player = Popen('afplay "'+location+'"',shell=True,stdout=PIPE)
		it += 1
		it -= tarry
		playing = player.poll()
		stdscr.timeout(10)
		show_prompt(promptHeader, promptLine)
		while playing == None:
			playing = player.poll()
			curses.echo()
			try:
				input = stdscr.getch()
			except:
				continue

			if input == ord("q"):
				show_prompt("Quitting!: ","Why? ")
				die()
			elif input == ord("h"):
				show_prompt("Saying hello! ","Goodbye? ")
			elif input == ord("s"):
				random.shuffle(a)
				it = a.index(song)
				show_songs(a,it)
				it += 1
				show_prompt("Shuffled! "+promptHeader,promptLine)
			elif input == ord("u"): #broken; files apparently isn't deep copied!
				a = files
				it = a.index(song)
				show_songs(a,it)
				it += 1
				show_prompt("Original order restored. "+promptHeader,promptLine)
			elif input == ord("r"):
				replay = not(replay)
				if replay == True:
					rM = "On"
				else:
					rM = "Off"
				show_prompt("Replay set to "+rM+". "+promptHeader,promptLine)

#			elif input == ord("t"):
#				if tarry == 0:
#					tarry = 1
#					it -= 1
#					show_prompt("Tarrying on this song. "+promptHeader,promptLine)
#				else:
#					tarry = 0
#					show_prompt("Tarry off. "+promptHeader,promptLine)
			### Skip/Go Back left right arrow keys
			elif input == curses.KEY_RIGHT:
				player.terminate()
			elif input == curses.KEY_LEFT:
				player.terminate()
				it -= 2
			elif input == curses.KEY_UP:
				script = """
					set theOutput to output volume of (get volume settings)
					set theOutput to theOutput + 6.25
					if theOutput > 100 then set theOutput to 100
					set volume output volume (theOutput)
					"""
				os.system("osascript -e '"+script+"'")
				show_prompt("Volume up. "+promptHeader,promptLine)
			elif input == curses.KEY_DOWN:
				script = """
					set theOutput to output volume of (get volume settings)
					set theOutput to theOutput - 6.25
					if theOutput < 0 then set theOutput to 0
					set volume output volume (theOutput)
					"""
				os.system("osascript -e '"+script+"'")
				show_prompt("Volume down. "+promptHeader,promptLine)
		playerO,playerE = player.communicate()
		code = player.returncode
		if code == -2:
			die()			

if __name__ == "__main__":
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)

	try:
		playArray(files)
		while replay == True:
			playArray(files)
	finally:
		curses.echo()
		curses.nocbreak()
		curses.endwin()
