#Christopher Stevenson 87923335 Lab Sec 5 Asst. 5

from sys import platform

class SoundPlayer():
    def __init__(self):
        self.OS = 0
        self.SoundEnabled = True
        if platform == 'win32':
            self.OS = 1
        elif platform == 'darwin':
            self.OS = 2
    def __del__(self):
        self.Stop() # If the game is being closed, ensure to stop all sounds
    def PlaySound(self, file:str) -> None:
        #Based on two supported operating systems, play the requested sound
        if self.SoundEnabled == True:
            if self.OS == 1:
                import winsound
                winsound.PlaySound(file, winsound.SND_ASYNC)
            else:
                import subprocess
                subprocess.Popen(['afplay', file])
    def Stop(self) -> None:
        #Based on two supported operating systems, stop playing all sounds
        if self.SoundEnabled == True:
            if self.OS == 1:
                import winsound
                winsound.PlaySound(None, winsound.SND_NODEFAULT)
            else:
                import subprocess
                subprocess.Popen(['killall',  'afplay'])
