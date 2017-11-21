import time

class _GetCh:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        self.angle = 0.0
        self.throttle = 0.25
        self.keypress_mode=None
        #self.keypress_condition=False
        LEFT_ANGLE_X = 0.7
        THROTTLE_TIME_X = 5
        RIGHT_ANGLE_Y = 0.8
        THROTTLE_TIME_Y = 5
        LEFT_ANGLE_Z = 0.9
        THROTTLE_TIME_Z = 5


# class _GetCh:
#   def __init__(self):
#     try:
#       self.impl = _GetChWindows()
#     except ImportError:
#       try:
#         self.impl = _GetChMacCarbon()
#       except ImportError:
#         self.impl = _GetChUnix()
#   def __call__(self):
#     return self.impl()

    def update(self):
        #InKey = _GetChUnix()
        # Try different OS for identifying keys pressed
        try:
          InKey = _GetChWindows()
        except ImportError:
          try:
            InKey = _GetChMacCarbon()
          except ImportError:
            InKey = _GetChUnix()     
        # Check for matched keys and take action
        c = InKey()        
        while c != 3:
          if c == 32:
            self.keypress_mode='pause'
            print("keypress_mode = ", self.keypress_mode)
          elif c == 51:
            print("doing 3-point turn")
          else:
            self.keypress_mode='run'
            print(c)
            print("keypress_mode = ", self.keypress_mode)            
          c = InKey()


    def run_threaded(self):
        return self.keypress_mode


class _GetChWindows:
  def __init__(self):
    import msvcrt
  def __call__(self):
    import msvcrt
    if msvcrt.kbhit():
      while msvcrt.kbhit():
        ch = msvcrt.getch()
      while ch in b'\x00\xe0':
        msvcrt.getch()
        ch = msvcrt.getch()
      return ord( ch.decode() )
    else:
      return -1

class _GetChMacCarbon:
  def __init__(self):
    import Carbon
    Carbon.Evt
  def __call__(self):
    import Carbon
    if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
      return ""
    else:
      (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
      return msg & 0x000000FF

class _GetChUnix:
  def __init__(self):
    import tty, sys, termios # import termios now or else you'll get the Unix
                             # version on the Mac
  def __call__(self):
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ord(ch)


