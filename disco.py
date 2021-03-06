#!/usr/bin/python
"""
REQUIRES PYGAME

Turns a Launchpad into a disco floor similar to the effect in Crypt of the Necrodancer
"""
import time
import sys
import getopt
from pygame import midi as midi
midi.init()
bpm=120
skip=False
pad_in=None
pad_out=None
in_chan=3
out_chan=2
fastmode=False
def usage():
    print "launchpad disco!!!!"
    print
    print "usage: disco -b bpm"
    print "-h --help   : displays help"
    print "-b --bpm    : tempo of disco!!"
    print "-s --skip   : if it skips the 8th beat"
    print "-f --fast   : skips needing to press enter"
    print "-i --input  : midi input channel"
    print "-o --output : midi output channel"
    print
    print "example:"
    print "disco -b 120"
    print "disco -b 160 -s"
    sys.exit(0)
def send_signal(mode,data1,data2,time=0):
    pad_out.write([[[mode,data1,data2],time]])
def note_on(key_xy,vel_col):
    key=16*key_xy[1]+key_xy[0]
    vel=16*vel_col[1]+vel_col[0]
    send_signal(144,key,vel)
def reset():
    send_signal(176,0,0)
def control(update,display):
    data=4*update+display+32
    send_signal(176,0,data)
def swap(state):
    if state:
        control(0,1)
    else:
        control(1,0)
    return not state
def loop():
    global pad_in
    global pad_out
    global fastmode
    control(0,1)
    for i in range(8):
        for j in range(8):
            if (i+j)%2==0:
                note_on([i,j],[0,3])
    control(1,0)
    for i in range(8):
        for j in range(8):
            if (i+j)%2==1:
                note_on([i,j],[3,0])
    delay=60.0/bpm
    count=1
    if skip:
        beat=8
    else:
        beat=1
        count=1.2
    state=True
    while pad_in.poll():
        pad_in.read(2)
    if not fastmode:
        raw_input("press enter to start")
    while True:
        if pad_in.poll():
            break
        if count%beat!=0:
            state=swap(state)
        count+=1
        time.sleep(delay)
        
    send_signal(176,0,48)
    reset()
    del pad_in
    del pad_out
    midi.quit()
    sys.exit(0)
def main():
    global bpm
    global skip
    global pad_in
    global pad_out
    global in_chan
    global out_chan
    global fastmode
    if not len(sys.argv[1:]):
        usage()
    try:
        opts,args=getopt.getopt(sys.argv[1:],"hb:sfi:o:",
        ["help","bpm","skip","fast","input","output"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    if len(args):
        usage()
    for o,a in opts:
        if o in ["-h","--help"]:
            usage()
        elif o in ["-b","--bpm"]:
            bpm=float(a)
        elif o in ["-s","--skip"]:
            skip=True
        elif o in ["-f","--fast"]:
            fastmode=True
        elif o in ["-i","--input"]:
            in_chan=int(a)
        elif o in ["-o","--output"]:
            out_chan=int(a)
        else:
            assert False,"Unhandled Option"
    if midi.get_device_info(in_chan)!=('ALSA', 'Launchpad S MIDI 1', 1, 0, 0):
        print "[!] Launchpad input channel invalid"
        sys.exit(0)
    if midi.get_device_info(out_chan)!=('ALSA', 'Launchpad S MIDI 1', 0, 1, 0):
        print "[!] Launchpad output channel invalid"
        sys.exit(0)
    pad_in=midi.Input(in_chan)
    pad_out=midi.Output(out_chan)
    loop()
main()
