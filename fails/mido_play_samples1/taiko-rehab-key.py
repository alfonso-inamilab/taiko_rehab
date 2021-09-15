# general imports 
import sys
import mido
from mido import MidiFile 
from mido import MidiTrack
from multiprocessing import Process
from pynput import keyboard  # DEBUG

key_pressed = False
def on_press(key):
    try:  # for normal keys
        # print('alphanumeric key {0} pressed'.format(key.char))
        pass
    except AttributeError:  #for special keys
        if key == keyboard.Key.up:
            print ("UP PRESSED")
            key_pressed = True
        # print('special key {0} pressed'.format(key))

def on_release(key):
    # print('{0} released'.format(key))
    if key == keyboard.Key.up:
        print ("UP RELEASED")
        key_pressed = False
    if key == keyboard.Key.esc:
        return False

def playMidi(portname, filename):
    output = mido.open_output(portname)
    midifile = MidiFile(filename)

    try:
        for message in midifile.play():
            if message.type == 'note_on':
                print (message)
            output.send(message)
        output.reset()
    except KeyboardInterrupt:
        output.reset()
        print("MIDI process closed.")


def playMidibyTrack(portname, filename):
    output = mido.open_output(portname)
    midifile = MidiFile(filename)

    try:
        for track in midifile.tracks:
            for msg in track:
                print (msg)
                # output.send(msg) 
    except KeyboardInterrupt:
        output.reset()
        print("MIDI process closed.")

def main():
    filename = sys.argv[1]
    if len(sys.argv) == 3:
        portname = sys.argv[2]
    else:
        portname = None

    p = Process(target=playMidi, args=(portname, filename))
    p.start()

    # Collect events until released
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    

    listener.join()
    p.join()
    
if __name__ == "__main__":
    main()

