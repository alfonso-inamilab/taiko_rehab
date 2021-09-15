# coding: utf-8
import time
from ctypes import *
from midiio import midiout

def main():
    c_s = create_string_buffer(32)
    ret = midiout.GetDeviceName(0, c_s, 32)
    if not ret:
        u'MIDIデバイスが見つかりません'
        return

    s0 = c_s.value
    print (s0)

    mo = midiout.Open(s0)
    if mo:
        try:
            print ('MIDIデバイスオープンしました')
            grand_piano = '\xc0\x00'
            midiout.PutMIDIMessage(mo, grand_piano, len(grand_piano))
            time.sleep(0.1)

            code_c = ('\x24', '\x30', '\x3c', '\x40', '\x43', '\x48')
            code_g = ('\x2b', '\x37', '\x3b', '\x3e', '\x43', '\x47')
            for c in code_c:
                message = '\x90%s\x64' % c
                midiout.PutMIDIMessage(mo, message, len(message))
            time.sleep(2)

            for c in code_c:
                message = '\x90%s\x00' % c
                midiout.PutMIDIMessage(mo, message, len(message))
            for c in code_g:
                message = '\x90%s\x64' % c
                midiout.PutMIDIMessage(mo, message, len(message))
            time.sleep(2)

            for c in code_g:
                message = '\x90%s\x00' % c
                midiout.PutMIDIMessage(mo, message, len(message))
            for c in code_c:
                message = '\x90%s\x64' % c
                midiout.PutMIDIMessage(mo, message, len(message))
            time.sleep(4)
        finally:
            ret = midiout.Close(mo)
            if ret:
                print ('MIDIデバイスクローズしました')
            else:
                print ('MIDIデバイスクローズ失敗')
    else:
        print ('MIDIデバイスが開けません')

if __name__ == '__main__':
    main()