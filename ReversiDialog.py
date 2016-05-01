#Christopher Stevenson 87923335 Lab Sec 5 Asst. 5
from tkinter import *
from sys import platform

class Dialog():
    def __init__(self, CallBackFunction, Title, TextToDisplay:str, YesNo=True, FontSize=14):
        Main = Toplevel()
        self.Main = Main
        self.CANVAS = Canvas(Main)
        CANVAS = self.CANVAS
        Main.title(Title)
        if platform == 'win32':
            Main.wm_iconbitmap('ReversiIco.ico')
        CANVAS.configure(background='white')

        CaptionFont = ('Comic Sans MS', FontSize)
        CTLabel = CANVAS.create_text(25,25, text=TextToDisplay, tags=('all','Prompt'), font=CaptionFont,anchor=NW, fill='black')
        if YesNo == True:
            self.YesI = PhotoImage(file='YesButton.gif').subsample(2,2)
            self.NoI = PhotoImage(file='NoButton.gif').subsample(2,2)
            YesButton = CANVAS.create_image(25,50,image=self.YesI, tags='YesButton',anchor = NW)
            CANVAS.tag_bind('YesButton', '<ButtonPress-1>', lambda event: self.Yes(event))
            NoButtonX = CANVAS.bbox(CTLabel)[2] - self.NoI.width()
            NoButton = CANVAS.create_image(NoButtonX,50,image=self.NoI, tags='NoButton',anchor = NW)
            CANVAS.tag_bind('NoButton', '<ButtonPress-1>', lambda event: self.No(event))
        

        self.CallBackFunction = CallBackFunction
        self.Handled = False #This ensures that the Cancel Function doesnt confuse yes or no with cancel
        CANVAS.bind('<Destroy>', lambda event: self.Cancel(event))
        ##Resize the Window According to the width and height of the text
        GetTextWidth = CANVAS.bbox(CTLabel)[2] - CANVAS.bbox(CTLabel)[1]
        GetTextHeight = CANVAS.bbox(CTLabel)[3] - CANVAS.bbox(CTLabel)[1]
        Main.geometry(str(GetTextWidth+ 50) + 'x' + str(GetTextHeight + 100))

        CANVAS.pack(fill=BOTH,expand=True)
        Main.resizable(0,0)
        Main.mainloop()

    def Yes(self,event) -> None:
        #The user clicked yes
        self.Handled = True
        self.Main.destroy()
        if self.CallBackFunction != None:
            self.CallBackFunction('Yes')

    def No(self, event) -> None:
        #The user clicked no
        self.Handled = False
        self.Main.destroy()
        if self.CallBackFunction != None:
            self.CallBackFunction('No')

    def Cancel(self, event)-> None:
        #The user just closed the window
        if self.Handled == False:
            if self.CallBackFunction != None:
                self.CallBackFunction('Cancel')
