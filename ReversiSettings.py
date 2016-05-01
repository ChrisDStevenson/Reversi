#Christopher Stevenson 87923335 Lab Sec 5 Asst. 5
from tkinter import *

from collections import namedtuple
from sys import platform
try:
    from ReversiGUILogic import Resize 
except ImportError:
    pass #Only import the Resize function if the module is being imported. Program assumes that it is being imported from ReversiGUI Logic
CI = namedtuple('CI', 'x y width height')
class SettingsMenu():
    def __init__(self,StartGameFunction, Background='ReversiBck.gif'):
        #Setup the main configuration for the settings window
        import tkinter.ttk as ttk
        Settings = Tk()
        self.MAIN = Settings
        self.SCANVAS = Canvas(Settings)
        CANVAS = self.SCANVAS
        Settings.title('Reversi - Game Setup')
        if platform == 'win32':
            self.MAIN.wm_iconbitmap('ReversiIco.ico')
        Settings.geometry('500x600')
        Settings.resizable(0,0)
        

        #Create the Background
        BCKG = PhotoImage(file=Background)
        BCKG = Resize(BCKG, 600, 600)
        CANVAS.create_image(0,0, image=BCKG, anchor=NW)

        #Create The Banner
        self.SettingsTitle = PhotoImage(file='SettingsBanner.gif').subsample(2,2)
        ReversiBanner= CANVAS.create_image(50,40,image=self.SettingsTitle,anchor=NW)
        ReversiBannerCI = CI(150,40,self.SettingsTitle.width(),self.SettingsTitle.height())

        #Create Section 1. The Number of Columns and Rows
        CaptionFont = ('Comic Sans MS', 14,'bold')
        CTLabel = CANVAS.create_text(100, ReversiBannerCI.y + 100, text='Columns:', tags=('all','SEC1T'), font=CaptionFont, fill='white')
        ReqNumber = Settings.register(self._RequireNumber)
        RejectCNumber = Settings.register(self._RejectCNumber)
        RejectRNumber = Settings.register(self._RejectRNumber)
        self.numofcolumns = StringVar()
        self.numofcolumns.trace('w',self._VerifySettings)
        self.numofrows = StringVar()
        self.numofrows.trace('w',self._VerifySettings)
        NumofColumns = ttk.Entry(CANVAS, font=CaptionFont, width=5, textvariable=self.numofcolumns, validate='all',validatecommand=(ReqNumber,'%P', '%d'),invalidcommand=RejectCNumber)
        CANVAS.create_window(200, ReversiBannerCI.y + 100, tags='Columns')
        CANVAS.itemconfigure('Columns',window=NumofColumns)
        NumofColumns.focus_set()

        CTLabel2 = CANVAS.create_text(300, ReversiBannerCI.y + 100, text='Rows:', tags=('all','SEC1T'), font=CaptionFont, fill='white')
        NumofRows = ttk.Entry(CANVAS, font=CaptionFont, width=5,textvariable=self.numofrows,validate='all',validatecommand=(ReqNumber,'%P', '%d'),invalidcommand=RejectRNumber)
        self.RN = NumofRows
        CANVAS.create_window(390, ReversiBannerCI.y + 100, tags='Rows')
        CANVAS.itemconfigure('Rows',window=NumofRows)

        #Create Section 2. Who's First and Who gets Top Left
        CTLabel3 = CANVAS.create_text(135, ReversiBannerCI.y + 150, text="Who's First:", tags=('all','FT'), font=CaptionFont, fill='white')
        self.BlackPiece = PhotoImage(file='BlackGIF.gif').subsample(2,2)
        self.WhitePiece = PhotoImage(file='WhiteGIF.gif').subsample(2,2)
        self.WhosFirst = 'B'
        FirstTurn = CANVAS.create_image(100, ReversiBannerCI.y + 200 ,image=self.BlackPiece, tags=('FirstTurn'), anchor=NW)
        CANVAS.tag_bind('FirstTurn', '<ButtonPress-1>', lambda event, ID='FirstTurn': self._SwitchPlayer(ID))

        #Create Section 3. Who has the Top Left of the Center?
        CTLabel4 = CANVAS.create_text(345, ReversiBannerCI.y + 163, text="Who Has Top-Left \n      Center:", tags=('all','FT'), font=CaptionFont, fill='white')
        self.TopLeft = 'W'
        TopCenter = CANVAS.create_image(300, ReversiBannerCI.y + 200 ,image=self.WhitePiece, tags=('TopCenter'), anchor=NW)
        CANVAS.tag_bind('TopCenter', '<ButtonPress-1>', lambda event, ID2='TopCenter': self._SwitchPlayer(ID2))

        #Create Section 4. How to decide the winner?
        self.HowToWin = '>'
        self.RBDisable = PhotoImage(file='pieceholder_highlight.gif').subsample(2,2)
        self.RBEnable = PhotoImage(file='pieceholder_poss.gif').subsample(2,2)
        CTLabel5 = CANVAS.create_text(280, ReversiBannerCI.y + 325, text="Winner has the Most Pieces", tags=('all','HTW'), font=CaptionFont, fill='white')
        MostPieces = CANVAS.create_image(70, ReversiBannerCI.y + 290, image=self.RBEnable, tags=('MostPieces'), anchor=NW)
        CANVAS.tag_bind('MostPieces', '<ButtonPress-1>', lambda event, MyTag='MostPieces': self._SwitchWin(event, MyTag))

        CTLabel6 = CANVAS.create_text(280, ReversiBannerCI.y + 380, text="Winner has the Least Pieces", tags=('all','HTW'), font=CaptionFont, fill='white')
        MostPieces = CANVAS.create_image(70, ReversiBannerCI.y + 345, image=self.RBDisable, tags=('LeastPieces'), anchor=NW)
        CANVAS.pack(fill=BOTH,expand=True)
        CANVAS.tag_bind('LeastPieces', '<ButtonPress-1>', lambda event, MyTag='LeastPieces': self._SwitchWin(event, MyTag))

        #Create Section 5. The version of Reversi
        CTLabel7 = CANVAS.create_text(10, 10, text="You are playing the FULL version of Reversi", tags=('all','FT'), font=CaptionFont, fill='lime green',anchor=NW)

        #Create Section 6. Whether or not the user wants highlights in the game
        self.HighlightOn = PhotoImage(file='checkbox1.gif').subsample(2,2)
        self.HighlightOff = PhotoImage(file='checkbox0.gif').subsample(2,2)
        self.UHighlights = True
        CTLabel8 = CANVAS.create_text(265, ReversiBannerCI.y + 425, text="Highlights?", tags=('all','HTW'), font=CaptionFont, fill='white')
        CANVAS.create_image(175, ReversiBannerCI.y + 413, image=self.HighlightOn, tags=('all','Highlights'), anchor=NW)
        CANVAS.tag_bind('Highlights', '<ButtonPress-1>', lambda event: self._HighlightsSwitch(event))
        
        #FINALLY Create the Start Button
        self.OverStartButton = False #If the cursor is over the start button and the user enters valid input, this variable will help change the cursor accordingly
        self.StartButtonEnabled = False
        StartButton = PhotoImage(file='StartButton.gif')
        StartButtonDisabled = PhotoImage(file='StartButton_Disabled.gif')
        StartButtonImage = CANVAS.create_image(110, ReversiBannerCI.y + 445, image=StartButton, disabledimage=StartButtonDisabled, tags=('Start'), anchor=NW, state=DISABLED)
        CANVAS.tag_bind('Start', '<ButtonPress-1>', self._STARTGAME)

        self.STARTGAME = StartGameFunction #This will call the start game function from the main GUI Logic file
        
        
        CANVAS.pack(fill=BOTH,expand=True)
        Settings.mainloop()

    def _STARTGAME(self, event) -> None:
        #This function passes parameters to start a game!
        #Assumes that there is a function named STARTGAME outside of class. 
        self.STARTGAME(self, int(self.numofcolumns.get()), int(self.numofrows.get()), self.TopLeft, self.WhosFirst, self.HowToWin, self.UHighlights)


        
    def _HighlightsSwitch(self, event) -> None:
        #This function enables or disables highlights
        if self.UHighlights == True:
            self.UHighlights = False
            self.SCANVAS.itemconfigure('Highlights', image=self.HighlightOff)
        else:
            self.UHighlights = True
            self.SCANVAS.itemconfigure('Highlights', image=self.HighlightOn)

    def _RestrictNumber(self, text:str) -> bool:
        #This function ensures that a number is between 4 and 16 inclusive
        if not 4 <= int(text) <= 16 or (int(text) % 2) != 0:
            return False
        return True
    def _VerifySettings(self, *args) -> None: #We really only care about self, so index, mode, and callback
        #This function verifies the settings. If everything is valid, the Game Start button is enabled
        self.SCANVAS.focus()
        if self.numofcolumns.get() != '' and self.numofrows.get() != '' and self._RestrictNumber(int(self.numofcolumns.get())) == True and  self._RestrictNumber(int(self.numofrows.get())) == True:
            self.SCANVAS.itemconfigure('Start',state=NORMAL)
            self.StartButtonEnabled = True
        else:
            self.SCANVAS.itemconfigure('Start',state=DISABLED)
            self.StartButtonEnabled = False
    

    def _SwitchWin(self, event, Tag:str):
        #This function switches the how to win radio buttons accordingly
        if Tag == 'MostPieces':
            self.HowToWin = '>'
            self.SCANVAS.itemconfigure('MostPieces', image=self.RBEnable)
            self.SCANVAS.itemconfigure('LeastPieces', image=self.RBDisable)
        elif Tag == 'LeastPieces':
            self.HowToWin = '<'
            self.SCANVAS.itemconfigure('LeastPieces', image=self.RBEnable)
            self.SCANVAS.itemconfigure('MostPieces', image=self.RBDisable)
            

    def _SwitchPlayer(self, WithTag:str) -> None:
        #This function controls the image switching involved for the setting of Who gets First Turn and who gets the top left center piece
        if WithTag =='FirstTurn':
            if self.WhosFirst == 'B':
                self.WhosFirst = 'W'
                self.SCANVAS.itemconfigure('FirstTurn',image=self.WhitePiece)
            else:
                self.WhosFirst = 'B'
                self.SCANVAS.itemconfigure('FirstTurn',image=self.BlackPiece)
        elif WithTag == 'TopCenter':
            if self.TopLeft == 'B':
                self.TopLeft = 'W'
                self.SCANVAS.itemconfigure('TopCenter',image=self.WhitePiece)
            else:
                self.TopLeft = 'B'
                self.SCANVAS.itemconfigure('TopCenter',image=self.BlackPiece)

    def _RejectCNumber(self) -> None:
        #Clear the number of columns text box because the input wasn't valid
        self.numofcolumns.set('')
    def _RejectRNumber(self) -> None:
        #Clear the number of columns text box because the input wasn't valid
        self.numofrows.set('')
    def _RequireNumber(self, text:str, vtype:str) -> bool:
        #This function requires that a number be present in text
        if text.isdigit() == True:
            if vtype == '-1': #If the type of validation is revalidation
                if self._RestrictNumber(int(text)) == False:
                    #If the number isn't between 4 and 16 inclusive or isnt even, it isnt valid
                    return False
            else:
                if self._RestrictNumber(int(text)) == False:
                    self.SCANVAS.itemconfigure('Start',state=DISABLED) # Disable the Start Button until valid input has been entered
            return True
        else:
            return False
