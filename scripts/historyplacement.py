##############################################################################
### The history window placement algorithm. ebind historyplacement.place   ###
### to the ob.EventAction.PlaceWindow event to use it.                     ###
##############################################################################

import windowplacement # fallback routines

##############################################################################
###       Options for the historyplacement module (Options in the          ###
###                windowplacement module also apply!)                     ###
##############################################################################
IGNORE_REQUESTED_POSITIONS = 0
"""When non-zero, the placement algorithm will attempt to place windows even
   when they request a position (like XMMS). Note this only applies to normal
   windows, not to special cases like desktops and docks."""
DONT_DUPLICATE = 1
"""When non-zero, if 2 copies of the same match in history are to be placed
   before one of them is closed (so it would be placed over-top of the last
   one), this will cause the second window to not be placed via history, and
   the FALLBACK will be used instead."""
FALLBACK = windowplacement.random
"""The window placement algorithm that will be used when history placement
   does not have a place for the window."""
CONFIRM_CALLBACK = 0
"""Set this to a function to have the function called before attempting to
   place a window via history. If the function returns a non-zero, then an
   attempt will be made to place the window. If it returns zero, the
   FALLBACK method will be directly applied instead."""
FILENAME = 'historydb'
"""The name of the file where history data will be stored. The number of
   the screen is appended onto this filename."""
##############################################################################

def place(data):
    """Place a window usingthe history placement algorithm."""
    _place(data)

###########################################################################
###########################################################################

###########################################################################
###      Internal stuff, should not be accessed outside the module.     ###
###########################################################################

import otk
import ob
import os
import string

_data = []

class _state:
    def __init__(self, appname, appclass, role, x, y):
        self.appname = appname
        self.appclass = appclass
        self.role = role
        self.x = x
        self.y = y
        self.placed = 0
    def __eq__(self, other):
        if self.appname == other.appname and \
           self.appclass == other.appclass and \
           self.role == other.role:
            return 1
        return 0

def _load(data):
    global _data
    try:
        file = open(os.environ['HOME'] + '/.openbox/' + FILENAME+"." +
                    str(data.screen), 'r')
        # read data
        for line in file.readlines():
            line = line[:-1] # drop the '\n'
            try:
                s = string.split(line, '\0')
                state = _state(s[0], s[1], s[2],
                               string.atoi(s[3]), string.atoi(s[4]))

                while len(_data)-1 < data.screen:
                    _data.append([])
                _data[data.screen].append(state)
                
            except ValueError: pass
            except IndexError: pass
        file.close()
    except IOError: pass

def _save(data):
    global _data
    file = open(os.environ['HOME']+'/.openbox/'+FILENAME+"."+str(data.screen),
                'w')
    if file:
        while len(_data)-1 < data.screen:
            _data.append([])
        for i in _data[data.screen]:
            file.write(i.appname + '\0' +
                       i.appclass + '\0' +
                       i.role + '\0' +
                       str(i.x) + '\0' +
                       str(i.y) + '\n')
        file.close()

def _create_state(data):
    global _data
    area = data.client.area()
    return _state(data.client.appName(), data.client.appClass(),
                  data.client.role(), area.x(), area.y())

def _find(screen, state):
    global _data
    try:
        return _data[screen].index(state)
    except ValueError:
        return -1
    except IndexError:
        while len(_data)-1 < screen:
            _data.append([])
        return _find(screen, state) # try again

def _place(data):
    global _data
    if data.client:
        if not (IGNORE_REQUESTED_POSITIONS and data.client.normal()):
            if data.client.positionRequested(): return
        state = _create_state(data)
        try:
            if not CONFIRM_CALLBACK or CONFIRM_CALLBACK(data):
                print "looking for : " + state.appname +  " : " + \
                      state.appclass + " : " + state.role

                i = _find(data.screen, state)
                if i >= 0:
                    coords = _data[data.screen][i]
                    print "Found in history ("+str(coords.x)+","+\
                          str(coords.y)+")"
                    if not (DONT_DUPLICATE and coords.placed):
                        data.client.move(coords.x, coords.y)
                        coords.placed = 1
                        return
                    else:
                        print "Already placed another window there"
                else:
                    print "No match in history"
        except TypeError:
            pass
    if FALLBACK: FALLBACK(data)

def _save_window(data):
    global _data
    if data.client:
        state = _create_state(data)
        print "looking for : " + state.appname +  " : " + state.appclass + \
              " : " + state.role

        i = _find(data.screen, state)
        if i >= 0:
            print "replacing"
            _data[data.screen][i] = state # replace it
        else:
            print "appending"
            _data[data.screen].append(state)

ob.ebind(ob.EventAction.CloseWindow, _save_window)
ob.ebind(ob.EventAction.Startup, _load)
ob.ebind(ob.EventAction.Shutdown, _save)

print "Loaded historyplacement.py"
