#Christopher Stevenson 87923335 Lab Sec 5 Asst. 5
from tkinter import *
import tkinter.ttk as ttk
import math
import os
from sys import platform
from ReversiLogic import *
from ReversiSound import *
from ReversiSettings import *
from ReversiDialog import *
from collections import namedtuple


CI = namedtuple('CI', 'x y width height')
Animation = namedtuple('Animation', 'Locationstr FinalStill')


AboutInfo = '''Reversi - Project 5 for ICS 32
Written By Christopher Stevenson.
Imported Modules (ReversiLogic, ReversiSound, ReversiSettings, ReversiDialog),
Graphics, Animations also designed by Christopher Stevenson.

Sound effects, courtesy of freesound.org.
Royalty-free sounds used under Creative Commons License, Attribution 3.0 Unported
http://creativecommons.org/licenses/by/3.0/

SOUND CREDITS (as required by Creative Commons License)
======================================================
Explosion4.wav by sarge4267
http://freesound.org/people/sarge4267/sounds/102734/

Punch In The Face by unfa
http://freesound.org/people/unfa/sounds/259714/

FallingGlisten by -Hero_of_the_winds-
http://freesound.org/people/-Hero_of_the_Winds-/sounds/221877/

Calm Waves Crashing Against A Beach by Motion_S
http://freesound.org/people/Motion_S/sounds/218387/

storm door slam 02 by volivieri
https://www.freesound.org/people/volivieri/sounds/161189/

Applause 2 by Sandermotions
https://www.freesound.org/people/Sandermotions/sounds/277021/

SUPPORT - cdsteve1@uci.edu
'''

def Resize(Image:PhotoImage, new_width:int, new_height:int) -> PhotoImage:
    #This function takes an image and resizes it relatively, NOT EXACTLY.
    Result = Image.zoom(1,1)
    DeltaWidth = new_width - Image.width()
    DeltaHeight = new_height - Image.height()
    ChangeWidth = math.ceil(new_width/Image.width())
    ChangeHeight = math.ceil(new_height/Image.height())
    if DeltaWidth < 0:
        #Make Image Width Smaller
        Result = Result.subsample(ChangeWidth,1)
    elif DeltaWidth > 0:
        Result = Result.zoom(ChangeWidth,1)
    if DeltaHeight < 0:
        #Make Image Height Smaller
        Result = Result.subsample(1, ChangeHeight)
    elif DeltaHeight > 0:
        Result = Result.zoom(1, ChangeHeight)
    return Result
        
class GraphicsBoard():


    def PlayerMove(self, Location:str):
        #This function detects when the player has clicked on a space.
        #But is the Move Valid Though?
        if Location in self.CurrentPossibleMoves:
            #Move was Valid
            #Place piece in location
            self._StopAnimation(True)
            self.sp.PlaySound('DropPiece.wav')
            self.PlacePiece(Location, self.CurrentGameState.CurrentTurn)
            if self.CurrentGameState.Winner == 0: # The following animations should only have a chance of happening while the game is still in progress
                PreviousTurn = self.CurrentGameState.CurrentTurn
                PiecesToChange = self.CurrentGameState.PlacePiece(self.GameBoard, self.DirGB, Location)
                
                if (len(PiecesToChange) + 1) > self.MostCaptures: ##Keep watch on who's making the most moves in the game
                        self.MostCaptures = (len(PiecesToChange) + 1)
                        self.MostCapturesBy = self.CurrentGameState.CurrentTurn
                        
                if PreviousTurn == Opponent(self.CurrentGameState.CurrentTurn):
                    self.DisableStranded = 0 #Allow for the stranded animation to play.
                    self.AnimatePiece(PiecesToChange, self.CurrentGameState.CurrentTurn) #If it is the other player's turn, Animate Pieces Accordingly
                else:
                    self.AnimatePiece(PiecesToChange, Opponent(PreviousTurn)) #If it is the current players turn again, Animate Pieces according to the current turn
                    if self.DisableStranded == 0:
                        self.DisableStranded = self.CurrentGameState.CurrentTurn

                        if self.CurrentGameState.CurrentTurn == 1:
                            self.Caption = 'White Moves Again!_white'
                            self.AnimateBillBoard(self.BlackStranded, 6, 750)
                        else:
                            self.Caption = 'Black Moves Again!_white'
                            self.AnimateBillBoard(self.WhiteStranded, 6, 750)
                        self.sp.PlaySound('Stranded!.wav')
            
            self.CurrentPossibleMoves.remove(Location)
            ##Update the Game Board Score
            self.SCORECANVAS.itemconfigure('P1S',text='White - ' + str(self.CurrentGameState.PlayerCount(self.GameBoard,1)))
            self.SCORECANVAS.itemconfigure('P2S',text='Black - ' + str(self.CurrentGameState.PlayerCount(self.GameBoard,2)))
            for OldSpaces in self.CurrentPossibleMoves: ##Change back unused highlights
                self.CANVAS.itemconfigure(OldSpaces, image=self.NotHighlighted)
            self.CurrentPossibleMoves.clear()

        if self.GameOver == False:
            if self.CurrentGameState.Winner == 0:
                #Change Current Turn Piece
                if self.CurrentGameState.CurrentTurn == 1:
                    self.SCORECANVAS.itemconfigure('CT',image=self.CTWhite)
                    self.CurrentPossibleMoves = CountValidMoves(self.GameBoard,self.DirGB, 1)
                else:
                    self.SCORECANVAS.itemconfigure('CT',image=self.CTBlack)
                    self.CurrentPossibleMoves = CountValidMoves(self.GameBoard,self.DirGB, 2)
            elif self.CurrentGameState.Winner == 1:
                #The White Player won the game
                #self.AnimationPlaying = True
                self.GameOver = True
                self.AnimateBillBoard(self.WhiteWin,13,235, 1000)
                self.sp.PlaySound('BatterUp!.wav')
            elif self.CurrentGameState.Winner == 2:
                #The Black Player won the game
                #self.AnimationPlaying = True
                self.GameOver = True
                self.AnimateBillBoard(self.BlackWin,13,235, 1000)
                self.sp.PlaySound('BatterUp!.wav')
            elif self.CurrentGameState.Winner == 3:
                #The game was a draw.
                #self.AnimationPlaying = True
                self.GameOver = True
                self.Caption = 'TIE GAME_black'
                self.DelayCode = "13#self.sp.PlaySound('DualLoss!.wav')" # Play a sound at frame 16 during the animation
                self.AnimateBillBoard(self.TieGame, 29,155, 1000)
        if self.UHighlights == True:
            for possiblemove in self.CurrentPossibleMoves:
                self.CANVAS.itemconfigure(possiblemove, image=self.Golden)


    def __init__(self, numofcolumns:int, numofrows:int, TopLeft:str, FirstTurn:str, HowToWin:str, UHighlights:bool, Background='ReversiBck.gif'):
        #1. Set up the Game Board Tkinter Object and Window
        Main = Tk()
        self.Main = Main
        self.CANVAS = Canvas(Main)
        self.CANVASCI = CI(0,0,871,828)
        CANVAS = self.CANVAS
        Main.title('Reversi')
        if platform == 'win32':
            Main.wm_iconbitmap('ReversiIco.ico')
        Main.geometry('871x828') # SUBJECT TO CHANGE
        CANVAS.configure(background='white')

        ##Also Set Up Some Image References Early on
        self.BlackPiece = PhotoImage(file='BlackGIF.gif')
        self.BlackPieceStill = self.BlackPiece.subsample(4,4)
        self.WhitePiece = PhotoImage(file='WhiteGIF.gif')
        self.WhitePieceStill = self.WhitePiece.subsample(4,4)
        self.Highlighted = PhotoImage(file='pieceholder_highlight.gif').subsample(4,4)
        self.NotHighlighted = PhotoImage(file='pieceholder.gif').subsample(4,4)
        self.Golden = PhotoImage(file='pieceholder_poss.gif').subsample(4,4)

        #Set up variables that are required for animation sequences to work
        self.AnimationID = 0 
        self.AnimateFrame = None 
        self.AnimateIndex = 1
        self.CurrentAnimation = None
        self.GameOver = False #When the game comes to an end, the final animation will be rendered and this variable will prevent user input on the board from being processed
        
        self.BillBoardFrame = None
        self.BillBoardIndex = 0
        self.BillBoardAnimation = None
        self.BbAnimationID = 0
        self.BlackWin = PhotoImage(file='BlackWin.gif')
        self.WhiteWin = PhotoImage(file='WhiteWin.gif')
        self.BlackStranded = PhotoImage(file='BlackStranded.gif')
        self.WhiteStranded = PhotoImage(file='WhiteStranded.gif')
        self.TieGame = PhotoImage(file='Draw.gif')
        self.DisableStranded = 0 #When nonzero, this prevents the stranded animation from being played. Used to prevent the animation from repeating back to back for one player moving again multiple times
        self.Caption = '' #This is used to create a caption whenever an animation is displayed on the scoreboard. Follows Syntax 'text'_'textcolor'
        self.DelayCode = '' #This is used to fire an event at a certain frame. Syntax: FrameNumber#Code to Execute
        self.AnimationPlaying = False
        

        #2. Create the Background Image
        BCKG = PhotoImage(file=Background)
        BCKG = Resize(BCKG, 871, 828)
        CANVAS.create_image(0,0, image=BCKG, anchor=NW)

        self.UHighlights = UHighlights #Show the player where he/she can move?
        BorderCI = CI(110, 40, 700,350)#These are just approximate coordinates for a 16x16 Game Board. SUBJECT TO CHANGE
        #3. CREATE ALL THE CELLS. The Spacing of The Cells Decide how big the Window will have to be initially
        CellWidth = 40
        CellHeight = 22
        CellSpace = self.NotHighlighted
        CurrentTurn = 'black.gif'
        if FirstTurn == 'W':
            CurrentTurn = 'white.gif'
        CTI2 = PhotoImage(file=CurrentTurn).subsample(4,4)
        DeltaCell = CI(BorderCI.x + 15, BorderCI.y + 10, CellSpace.width(), CellSpace.height())
        
        for eachrow in range(1, numofrows + 1):
            for eachcol in range(1, numofcolumns + 1):
                #For Each One, Add a Cell Space accordingly
                createid = str(eachcol) + '-' + str(eachrow)
                Cell = CANVAS.create_image(DeltaCell.x , DeltaCell.y,image=CellSpace, tags=(createid,'CELL','EMPTY'), anchor=NW)
                CANVAS.tag_bind(Cell, '<ButtonPress-1>', lambda event, Location=createid: self.PlayerMove(Location))
                CANVAS.tag_bind(Cell, '<Enter>', lambda event, Location=createid: self.Highlight(Location))
                CANVAS.tag_bind(Cell, '<Leave>', lambda event, Location=createid: self.DeHighlight(Location))
                DeltaCell = CI(DeltaCell.x + CellWidth, DeltaCell.y, DeltaCell.width, DeltaCell.height)
                if eachcol == numofcolumns and numofcolumns>=8:
                    BorderCI = CI(BorderCI.x,BorderCI.y, (DeltaCell.x), (DeltaCell.y)) #Resize Column Border appropriately if the number of columns is greater than 8
            if eachrow == numofrows:
                BorderCI = CI(BorderCI.x,BorderCI.y, DeltaCell.x, (DeltaCell.y))
            else:
                DeltaCell = CI(BorderCI.x + 15 , DeltaCell.y + CellHeight + 18, DeltaCell.width, DeltaCell.height)
            
            
        #4. Draw The BORDER, updating width and height to the number of rows and columns
        BorderCI = CI(BorderCI.x,BorderCI.y, BorderCI.width + 5, BorderCI.height + 5) # Just adding some extra space to the ends of the border
        CANVAS.create_polygon(BorderCI.x, BorderCI.y, BorderCI.width , BorderCI.y, BorderCI.width, BorderCI.y + BorderCI.height, BorderCI.x, BorderCI.y + BorderCI.height,width=10,fill='',outline='#2A5A9C',tags='PolygonBorder',joinstyle=ROUND)
        CANVAS.tag_raise('CELL') #Ensure that the cells can be clicked by the user.

        #5. Draw The ScoreBoard
        BOARDCANVAS = Canvas(width=500,height=131,bg='#709CDB')
        self.SCORECANVAS = BOARDCANVAS
        SB = PhotoImage(file='ScoreBoardBorder.gif')
        self.SB = SB
        if numofcolumns > 12:
            SBCI = CI(BorderCI.width - (SB.width() /2),BorderCI.y + BorderCI.height + 73, SB.width(), SB.height()) #Right Justify the Score Board if the number of columns will allow for it
        else:
            SBCI = CI(BorderCI.x + (SB.width()/2),BorderCI.y + BorderCI.height + 73, SB.width(), SB.height()) #Otherwise, Left Justify the Score Board
        ScoreBoard = CANVAS.create_window(SBCI.x,SBCI.y,tags='all')
        CANVAS.itemconfigure(ScoreBoard,window=BOARDCANVAS)
        
        #Create the border image and the score text items
        BOARDCANVAS.create_image(0, 0,image=SB,tags=('BORDER'),anchor=NW)
        ScoreFont = ('Comic Sans MS', 18,'bold')
        Player1Score = BOARDCANVAS.create_text(20, 10, text='White - 2', tags=('P1S','all'), anchor=NW, font=ScoreFont)
        Player2Score = BOARDCANVAS.create_text(20, 60, text='Black - 2', tags=('P2S','all'), anchor=NW, font=ScoreFont)
        
        #6. On ScoreBoard, display who's turn it currently is
        self.CTBlack = PhotoImage(file='black.gif').subsample(3,3)
        self.CTWhite = PhotoImage(file='white.gif').subsample(3,3)
        CTI = self.CTBlack
        if FirstTurn == 'W':
            CTI = self.CTWhite

        BOARDCANVAS.create_image(360, 70,image=CTI,tags='CT')
        CaptionFont = ('Comic Sans MS', 14,'bold')
        CTLabel = BOARDCANVAS.create_text(360, 30, text='Current Turn:', tags=('all','CTT'), font=CaptionFont)

        #8. Resize the Board dimensions down to what is appropriate
        newwidth= int(SBCI.x) + int(float(SBCI.width / 2)+ 20)
        newheight = SBCI.y + 65
        Main.geometry('{}x{}'.format(newwidth,newheight ))
        self.CANVASCI = CI(0,0,newwidth,newheight)
        CANVAS.bind("<Configure>", self.ResizeBoard)
        #

        #9. Establish the Sound Player and create a mute button
        self.sp = SoundPlayer()
        self.SoundOn = PhotoImage(file='SoundON.gif').subsample(2,2)
        self.SoundOFF = PhotoImage(file='SoundOFF.gif').subsample(2,2)
        SoundButton = CANVAS.create_image(25,120,image=self.SoundOn, tags='ToggleSound',anchor = NW)
        CANVAS.tag_bind('ToggleSound', '<ButtonPress-1>', lambda event: self.ToggleSound(event))

        #10. Create a New Game Button
        self.NewGameI = PhotoImage(file='NewGame.gif').subsample(2,2)
        NewGameButton = CANVAS.create_image(25, 50 ,image=self.NewGameI, tags='NewGame',anchor = NW)
        CANVAS.tag_bind('NewGame', '<ButtonPress-1>', lambda event: self.NewGame(event))

        #11. Create an About Button
        self.AboutGameI = PhotoImage(file='AboutButton.gif').subsample(2,2)
        NewGameButton = CANVAS.create_image(25, 190 ,image=self.AboutGameI, tags='AButton',anchor = NW)
        CANVAS.tag_bind('AButton', '<ButtonPress-1>', lambda event: self.About(event))

        ##Game Statistics Variables
        self.AnimateStats = False
        self.Stats = []
        self.StatsIndex = 0
        self.MostCaptures = 0
        self.MostCapturesBy = 0
        self.GameTime = 0
        self.Main.after(1000, self._TimeTick)
        #### Starting Game Logics
        self.GameBoard, Centers = CreateGameBoard(numofcolumns, numofrows,TopLeft)
        self.DirGB = CreateDirBoard(self.GameBoard, numofcolumns,numofrows)
        if FirstTurn == 'W':
            FT = 1
        else:
            FT = 2
        if HowToWin == '>':
            HTW = True
        else:
            HTW = False
        self.CurrentGameState = GameState(self.GameBoard, self.DirGB, FT, HTW)
        
        
        if TopLeft == 'W':
            self.PlacePiece(Centers[0],1)
            self.PlacePiece(Centers[1],2)
            self.PlacePiece(Centers[2],2)
            self.PlacePiece(Centers[3],1)
            
        else:
            self.PlacePiece(Centers[0],2)
            self.PlacePiece(Centers[1],1)
            self.PlacePiece(Centers[2],1)
            self.PlacePiece(Centers[3],2)
        if FirstTurn == 'W':
            self.CurrentPossibleMoves = CountValidMoves(self.GameBoard,self.DirGB, 1)
        else:
            self.CurrentPossibleMoves = CountValidMoves(self.GameBoard,self.DirGB, 2)
        if UHighlights == True:
            for possiblemove in self.CurrentPossibleMoves:
                self.CANVAS.itemconfigure(possiblemove, image=self.Golden)
        CANVAS.pack(fill=BOTH,expand=True)
        Main.mainloop()

    def _TimeTick(self) -> None:
        #This function keeps track of the overall game time in seconds
        if self.CurrentGameState.Winner == 0:
            self.GameTime += 1
            self.Main.after(1000, self._TimeTick)

    def About(self, event) -> None:
        #This function displays information about my implementation of Reversi
        DG = Dialog(None, 'About Reversi', AboutInfo, False, 10)
        
    def NewGame(self, event) -> None:
        if self.CurrentGameState.Winner == 0:
            DG = Dialog(self.ConfirmNewGame,'Start New Game', 'Are you sure you would like to start a new game?')
        else:
            self.ConfirmNewGame('Yes')

    def ConfirmNewGame(self, Response:str) -> None:
        #This function confirms whether or not the user would like to start a new game
        if Response == 'Yes':
            RESTARTGAME(self)
        
    def Highlight(self, Location:str):
        #This function detects when the mouse pointer is over a cell and highlights the cell appropriately
        if 'EMPTY' in self.CANVAS.gettags(Location):
            self.CANVAS.itemconfigure(Location, image=self.Highlighted)
    def DeHighlight(self, Location:str):
        #This function detects when the mouse pointer left a cell and de/highlights the cell appropriately
        if 'EMPTY' in self.CANVAS.gettags(Location) and Location not in self.CurrentPossibleMoves:
            self.CANVAS.itemconfigure(Location, image=self.NotHighlighted)
        elif Location in self.CurrentPossibleMoves and self.UHighlights == True:
            self.CANVAS.itemconfigure(Location, image=self.Golden)
        elif Location in self.CurrentPossibleMoves and self.UHighlights == False:
            self.CANVAS.itemconfigure(Location, image=self.NotHighlighted)
            
    def ResizeBoard(self, event):
        #This function takes the Canvas and ensures that it is up to scale with the window.
        WidthBefore = self.CANVASCI.width
        HeightBefore = self.CANVASCI.height
        self.CANVAS.config(width=event.width, height=event.height)
        self.CANVASCI = CI(0,0, event.width, event.height)
        ScaleFactorW = float(event.width)/WidthBefore
        ScaleFactorH = float(event.height)/HeightBefore
        self.CANVAS.scale("all", 0, 0, ScaleFactorW, ScaleFactorH)
        self.CANVAS.scale("BORDER",0,0, ScaleFactorW, ScaleFactorH)

    def ToggleSound(self, event):
        #This function enables/disables sound
        if self.sp.SoundEnabled == True:
            self.sp.SoundEnabled = False
            self.CANVAS.itemconfigure('ToggleSound',image=self.SoundOFF)
        else:
            self.sp.SoundEnabled = True
            self.CANVAS.itemconfigure('ToggleSound',image=self.SoundOn)
            

    def SkipAnimation(self) -> None:
        #This function forces a currently playing animation to skip to its final frame.
        if self.CurrentAnimation != None:
            for location in self.CurrentAnimation.Locationstr:
                self.CANVAS.itemconfigure(location, image=self.CurrentAnimation.FinalStill)
            self.CurrentAnimation = None
             
            
    
    def AnimatePiece(self, Locationstr:[str], ToPiece:int) -> None:
        #This function takes a list of pieces and animates all the pieces to the specified piece.
        self.AnimationID += 1
        if self.CurrentAnimation != None:
            self.SkipAnimation()
        if ToPiece == 1: #Change piece(s) to black
            self.CurrentAnimation = Animation(Locationstr, self.BlackPieceStill)
            self.Main.after(150, self._Animate, Locationstr,self.WhitePiece,self.BlackPieceStill, self.AnimationID)
        elif ToPiece == 2:
            self.CurrentAnimation = Animation(Locationstr, self.WhitePieceStill)
            self.Main.after(150, self._Animate, Locationstr,self.BlackPiece,self.WhitePieceStill, self.AnimationID)
            
            
    def _Animate(self,Locationstr:[str], WithPiece:PhotoImage,FinalStill:PhotoImage, AnimationID:int) -> None:
        #This function animates the desired pieces on the GameBoard
        if self.AnimationID != AnimationID:
            return None #If the animation was skipped, exit animation loop
        WithPiece.configure(format="gif -index " + str(self.AnimateIndex))
        self.AnimateFrame = WithPiece.subsample(4,4)

        for location in Locationstr:
            if self.AnimateIndex != 4:
                self.CANVAS.itemconfigure(location, image=self.AnimateFrame)
            else:
                self.CANVAS.itemconfigure(location, image=FinalStill)
            
        if self.AnimateIndex == 4:
            self.AnimateIndex = 1
        else:
            self.AnimateIndex += 1
            self.Main.after(200, self._Animate,Locationstr, WithPiece, FinalStill, AnimationID)

    def PlacePiece(self, Location:str, piece:int) -> None:
        #Without Animation, place a piece on the board
        self.CANVAS.dtag(Location,'EMPTY')
        if piece == 1:
            self.CANVAS.itemconfigure(Location, image=self.WhitePieceStill)
        elif piece == 2:
            self.CANVAS.itemconfigure(Location, image=self.BlackPieceStill)

    def _StopAnimation(self, BackToBorder:bool) -> None:
        #This function stops an animation from playing if there is one currently playing
        if self.AnimationPlaying == True:
            self.BillBoardIndex = 0
            self.AnimationPlaying = False
            self.SCORECANVAS.delete('A_CAPTION') #If there was a caption used during the animation, delete it
            self.Caption = ''
            self.DelayCode = ''
            if BackToBorder == True:
                self.BbAnimationID -= 1
                self._BackToBorder()
            
    def AnimateBillBoard(self, WithAnimation:PhotoImage, NumofFrames, Speed, EndDelay=0) -> None:
        #This function takes an animation and displays it as an overlay over the score board
        self.BbAnimationID += 1
        if self.AnimationPlaying == True:
            #An animation is currently playing. STOP the animation and then execute the newer animation
            self._StopAnimation(False)
            
        self.SCORECANVAS.itemconfigure('P1S', state=HIDDEN)
        self.SCORECANVAS.itemconfigure('P2S', state=HIDDEN)
        self.SCORECANVAS.itemconfigure('CT', state=HIDDEN)
        self.SCORECANVAS.itemconfigure('CTT', state=HIDDEN)
        self.BillBoardAnimation = WithAnimation
        self.AnimationPlaying = True
        
        self.Main.after(Speed, self._AnimateBillBoard, WithAnimation, NumofFrames,Speed, self.BbAnimationID, EndDelay) #Start The Animation
        if self.Caption != '':
            ScoreFont = ('Comic Sans MS', 14,'bold')
            CaptionText = self.SCORECANVAS.create_text(20, 10, text=self.Caption.split('_')[0], tags=('A_CAPTION','all'), anchor=NW, font=ScoreFont,fill=self.Caption.split('_')[1])
        else:
            self.SCORECANVAS.delete('A_CAPTION') #Ensure that the Animation Caption wasnt there from a previous animation
            

    def _AnimateBillBoard(self, WithAnimation:PhotoImage, NumofFrames:int, Speed:int, BbAnimationID:int, EndDelay=0) -> None:
        #This function runs an animation on the scoreboard.
        if self.BbAnimationID != BbAnimationID or self.AnimationPlaying == False:
            return None #Billboard animation was changed while another animation was playing. Stop the loop for the previous animation
        if self.BillBoardIndex != NumofFrames:
            WithAnimation.configure(format="gif -index " + str(self.BillBoardIndex))
            self.SCORECANVAS.itemconfigure('BORDER', image=WithAnimation)

        if self.DelayCode != '':
            if self.DelayCode.split('#')[0] == str(self.BillBoardIndex):
                exec(self.DelayCode.split('#')[1])
        if self.BillBoardIndex == NumofFrames:
            self.BillBoardIndex = 0

            if EndDelay == 0:
                self._StopAnimation(True)
            else:
                self.Main.after(EndDelay, self._StopAnimation, True)
        else:
            self.BillBoardIndex += 1
            self.Main.after(Speed, self._AnimateBillBoard, WithAnimation, NumofFrames,Speed, BbAnimationID, EndDelay)

    def GetTime(self, length:int) -> str:
        #This function takes a time in seconds and makes it look user friendly
        minutes = math.floor(length /60)
        seconds = length - (minutes * 60)
        secondstr = str(seconds)
        if seconds == 0:
            secondstr += '0'
        if seconds < 10:
            secondstr = '0' + secondstr
        return str(minutes) + ':' + secondstr
    
    def _BackToBorder(self):
        #This function simply sets the scoreboard border to its original value
        self.SCORECANVAS.itemconfigure('BORDER', image=self.SB)
        self.SCORECANVAS.itemconfigure('P1S', state=NORMAL)
        self.SCORECANVAS.itemconfigure('P2S', state=NORMAL)
        self.SCORECANVAS.itemconfigure('CT', state=NORMAL)
        self.SCORECANVAS.itemconfigure('CTT', state=NORMAL)
        if self.CurrentGameState.Winner != 0: #If a winner was determined, display the game statistics instead of the score and current turn.
            self.AnimateStats = True
            self.Stats.append('White - ' + str(self.CurrentGameState.PlayerCount(self.GameBoard,1)))
            self.Stats.append('Black - ' + str(self.CurrentGameState.PlayerCount(self.GameBoard,2)))
            if self.MostCapturesBy == 1:
                self.Stats.append('Most Captures in One Move: White - ' + str(self.MostCaptures))
            else:
                self.Stats.append('Most Captures in One Move: Black - ' + str(self.MostCaptures))
            self.Stats.append('Total Time: ' + self.GetTime(self.GameTime))
            self.SCORECANVAS.bind('<Enter>', lambda event: self.StopStats(event), add='+')
            self.SCORECANVAS.bind('<Enter>', lambda event: self.StopStats(event), add='+')
            self.SCORECANVAS.bind('<Leave>', lambda event: self.StartStats(event), add='+')
            self.SCORECANVAS.bind('<Leave>', lambda event: self.StartStats(event), add='+')
            self.SCORECANVAS.bind('<ButtonPress-1>', lambda event: self.ChangeStats(event), add='+')
            self.SCORECANVAS.itemconfigure('CT', state=HIDDEN)
            self.SCORECANVAS.itemconfigure('CTT', state=HIDDEN)
            self.Main.after(2000, self._AnimateStats)

    def StopStats(self, event) -> None:
        #This function disables the animation of game statistics so that the user can control what they want to see
        self.AnimateStats = False

    def StartStats(self, event) -> None:
        #This function re-enables the animation of game statistics
        self.AnimateStats = True

    def ChangeStats(self, event) -> None:
        #This function changes the statistics displayed
        self._SwitchStats()

    def _SwitchStats(self) -> None:
        #This function switches statistics shown on the scoreboard
        if self.StatsIndex == 0:
            #Change to the total time played and the most captures a one time
            
            self.SCORECANVAS.itemconfigure('P1S',text=self.Stats[2])
            self.SCORECANVAS.itemconfigure('P2S',text=self.Stats[3])
            self.SCORECANVAS.itemconfigure('P1S',fill='black')
            self.SCORECANVAS.itemconfigure('P2S',fill='black')
            self.StatsIndex = 1
        elif self.StatsIndex == 1:
            #Change back to the Scores
            if self.CurrentGameState.Winner == 1:
                self.SCORECANVAS.itemconfigure('P1S',fill='Gold')
            elif self.CurrentGameState.Winner == 2:
                self.SCORECANVAS.itemconfigure('P2S',fill='Gold')
            self.SCORECANVAS.itemconfigure('P1S',text=self.Stats[0])
            self.SCORECANVAS.itemconfigure('P2S',text=self.Stats[1])
            self.StatsIndex = 0
        
    def _AnimateStats(self) -> None:
        #This function animates the game statistics
        if self.AnimateStats == True:
            self._SwitchStats()
        self.Main.after(2000, self._AnimateStats)
        
            
    

def STARTGAME(WINDOW, numofcolumns:int, numofrows:int, TopLeft:str, WhosFirst:str, HowToWin:str, UHighlights:bool) -> None:
    #This function closes the Settings Window and immediately starts the game
    WINDOW.MAIN.destroy()
    GraphicsBoard(numofcolumns, numofrows, TopLeft, WhosFirst, HowToWin, UHighlights)


def RESTARTGAME(WINDOW) -> None:
    #This function restarts the entire game
    WINDOW.sp = None
    WINDOW.Main.destroy()
    GetSettings = SettingsMenu(STARTGAME)
if __name__ == '__main__':
    GetSettings = SettingsMenu(STARTGAME)
    


