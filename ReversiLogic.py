#Christopher Stevenson 87923335 Lab Sec 5 Asst. 5

from collections import namedtuple
import itertools


Cell = namedtuple('Cell', 'position piece')
DirectionNumbers = namedtuple('DirectionNumbers', 'NS WE NESW NWSE') # NS = NorthSouth, NE = NorthEast, SW = SouthWest, NW = NorthWest, SE = SouthEast



class IllegalMove(Exception):
    pass
class GameOver(Exception):
    pass

class GameState:
    def __init__(self, Board:dict, dirboard:dict, FirstTurn:int, HowToWin:bool):    
        self.board = Board # This board represents the game board in the simplest manner possible. It will be used for easy reference to game pieces
        self.dirboard = dirboard # This board is the one who runs things. It's job is to map out all directions for each piece.
        self.CurrentTurn = FirstTurn
        self.WinnerMethod = HowToWin
        self.Winner = 0

    def PlayerCount(self, Board:dict, piece:int) -> int:
        #This function counts the number of pieces a given player has
        Result = 0
        for key in Board.keys():
            if Board[key].piece == piece:
                Result += 1
        return Result
    def DecideWinner(self, board:dict) -> None:
        #This function decides who the winner is
        Player1Score = self.PlayerCount(board, 1)
        Player2Score = self.PlayerCount(board, 2)
        if self.WinnerMethod == True: #Whoever has the most pieces on the board
            if Player1Score > Player2Score:
                self.Winner = 1 #Player 1 WINS
            elif Player2Score > Player1Score:
                self.Winner = 2 #Player 2 WINS
            else:
                self.Winner = 3 #Its a draw
        else:
            if Player1Score < Player2Score:
                self.Winner = 1
            elif Player2Score < Player1Score:
                self.Winner = 2
            else:
                self.Winner = 3 #Its a draw
    def ChangeTurn(self) -> None:
        #This function changes whose turn it is
        if self.CurrentTurn == 1:
            self.CurrentTurn = 2
        else:
            self.CurrentTurn = 1
            
        
    def PlacePiece(self, Board:dict,DirBoard:dict, Location:str) -> [str]:
        #This function takes a game board and places a piece at the specified location, IF THE MOVE IS VALID
        Winner = self.Winner
        CurrentTurn = self.CurrentTurn
        Captured = None
        if Winner != 0:
            raise GameOver
        if Location not in Board:
            raise IllegalMove
        if ValidMove(Board,DirBoard, Location, CurrentTurn) == True:
            #Place Piece, Then Capture all required pieces
            Captured = CapturePieces(Board, DirBoard, Location, CurrentTurn)
        if len(CountValidMoves(Board, DirBoard, Opponent(CurrentTurn))) == 0:
            #The opponent couldn't make any valid moves. Check if Current Player can make any valid moves
            if len(CountValidMoves(Board, DirBoard, CurrentTurn)) == 0:
                #CurrentPlayer Couldn't either. Game OVER. Decide Winner
                self.ChangeTurn()
                self.DecideWinner(Board)
            else:
                pass #Then the current player will go again
        else:
            self.ChangeTurn()
        
        return Captured
            
            

def Opponent(piece:int) -> int:
    #This function simply returns the opponent piece
    if piece == 1:
        return 2
    elif piece == 2:
        return 1

def _StringDirection(Board:dict, ListOCells:[str], Location=None) -> str:
    #This function takes a list of cell locations and returns a string representation of all the cells
    Result = ''
    for eachlocation in ListOCells:
        if Location == eachlocation:
            Result += '*' #If a Location is specified, then this will put * in that location instead of its piece
        else:
            Result += str(Board[eachlocation].piece)
    return Result


def _FindDiagonal(DirBoard:dict, diag_direction:int, Location:str) -> str:
    #This function will Find the diagonal that passes through the Location specified
    Result = ''
    Counter = DirBoard['rdiagmp'][Location]
    DiagMap = DirBoard['diagmp']
    if Location.split('-')[1] == '1':
        CheckLocation = str(diag_direction) + '-c' + Location.split('-')[0]
        if CheckLocation in DirBoard:
            return CheckLocation #The Location given was the highest point of the diagonal, so return the appropriate ID
    else:
        CheckLocation = str(diag_direction) + '-r' + Location.split('-')[1]
        if CheckLocation in DirBoard and int(Location.split('-')[0]) in [DirBoard['maxcolumns'], 1]: #If the cell is in any of the second half of the diagonals
            #Hold UP. There are cells in the second half that can lead their own diagonal in a direction OTHER than our intended direction. Check for That too, and then we're good
            TheoreticalPrevious = (int(DirBoard['rdiagmp'][Location]) - int(diag_direction))
            if TheoreticalPrevious not in DiagMap:
                return CheckLocation
            else:
                RelativeLocation = (int(DiagMap[TheoreticalPrevious].split('-')[0]) - int(Location.split('-')[0]))
                if diag_direction == DirBoard['dir'].NWSE and RelativeLocation != -1:
                    return CheckLocation
                elif diag_direction == DirBoard['dir'].NESW and RelativeLocation != 1:
                    return CheckLocation
    
    
    while True: #Because the diagonals have variable length!!!
        Counter -= int(diag_direction)
        if Counter not in DiagMap:
            return '' #The requested diagonal was not found
        Result = DiagMap[Counter]
        NextPiece = Counter - int(diag_direction)
        if (NextPiece) not in DiagMap:
            break #Counter has already past the last cell in the diagonal because the theoretical next one doesn't exist. Break!
        elif diag_direction == DirBoard['dir'].NWSE and (int(DiagMap[NextPiece].split('-')[0]) - int(Result.split('-')[0])) != -1 : 
            break #Counter has went to a piece that doesn't follow direction pattern. Break!
        elif diag_direction == DirBoard['dir'].NESW and (int(DiagMap[NextPiece].split('-')[0]) - int(Result.split('-')[0])) != 1:
            break #Same situation as previous but different direction
    if Result.split('-')[1] == '1': #Create the ID of the Diagonal we need based on where the top was located
        Result = str(diag_direction) + '-c' + Result.split('-')[0]
    else:
        Result = str(diag_direction) + '-r' + Result.split('-')[1]
    if Result not in DirBoard: #This check prevents a diagonal with only two spaces from being returned
        return ''
    return Result

def ValidMove(Board:dict, DirBoard:dict, Location:str, piece:int) -> bool:
    #This function validates the move. Raises InvalidMoveError if it cannot be done.

    ###STAGE ONE. The obvious. Is the location already occupied?
    if Board[Location].piece != 0:
        raise IllegalMove

    ###STAGE TWO. Can the desired move be made??
    ##Need to check all directions to be sure.

    ##A move is only valid if the sequence follows currentpiece-opponent-currentpiece.
    for Direction in DirBoard['dir']:
##        for key in DirBoard.keys():
##            print(key + ':' + str(DirBoard[key]))
        if Direction == DirBoard['dir'].NS:
            DirBoardLookup = Direction + '-' + Location.split('-')[0]
        elif Direction == DirBoard['dir'].WE:
            DirBoardLookup = Direction + '-' + Location.split('-')[1]
        else:
            #For a Diagonal, we need to find the top of the diagonal
            DirBoardLookup = _FindDiagonal(DirBoard, Direction, Location)
        if DirBoardLookup != '':
            GetDirString = _StringDirection(Board, DirBoard[DirBoardLookup], Location)
            GetBasicDirString = ''.join(repeat for repeat,_ in itertools.groupby(GetDirString))

            #Where we are at in the direction is important. IF we're not adjacent to where we can make a valid move, its no good
            ValidCombo = (str(Opponent(piece)) + str(piece))
            if ('*' + ValidCombo) in GetBasicDirString: #Is the combination valid?
                #We Found a Valid Move!!!
                return True
            elif (ValidCombo[::-1] + '*') in GetBasicDirString:
                #We Found a Valid Move, but in the opposite direction
                return True
    #If interpreter gets to this point, The Move was NOT Valid
            
    raise IllegalMove

def CapturePieces(Board:dict, DirBoard:dict, Location:str, piece:int) -> [list]:
    #Similar to ValidMove function, this function uses a valid move, and then captures all the specified pieces. Will also change Location's piece to current piece
    #Returns a list of all the cells that have been captured
    Result = []
    for Direction in DirBoard['dir']:
        if Direction == DirBoard['dir'].NS:
            DirBoardLookup = Direction + '-' + Location.split('-')[0]
        elif Direction == DirBoard['dir'].WE:
            DirBoardLookup = Direction + '-' + Location.split('-')[1]
        else:
            #For a Diagonal, we need to find the top of the diagonal
            DirBoardLookup = _FindDiagonal(DirBoard, Direction, Location)
        if DirBoardLookup != '':
            GetDirString = _StringDirection(Board, DirBoard[DirBoardLookup], Location)
            GetBasicDirString = ''.join(repeat for repeat,_ in itertools.groupby(GetDirString))
            
            ValidCombo = (str(Opponent(piece)) + str(piece))
            if ('*' + ValidCombo) in GetBasicDirString: #Is the combination valid?
                #We Found a Valid Move, Take Pieces accordingly!!!
                ReadDirection = GetDirString.index('*')
                while True: #Because we don't know how many of the opponents pieces there are after star
                    ReadDirection += 1
                    if GetDirString[ReadDirection] == str(piece):
                        break
                    ChangeLocation = DirBoard[DirBoardLookup][ReadDirection]
                    Board[ChangeLocation] = Cell(ChangeLocation, piece)
                    Result.append(ChangeLocation)
                    
            if (ValidCombo[::-1] + '*') in GetBasicDirString:
                #We Found a Valid Move, but in the opposite direction
                ReadDirection = GetDirString.index('*')
                while True: #Because we don't know how many of the opponents pieces there are BEFORE star
                    ReadDirection -= 1
                    if GetDirString[ReadDirection] == str(piece):
                        break
                    ChangeLocation = DirBoard[DirBoardLookup][ReadDirection]
                    Board[ChangeLocation] = Cell(ChangeLocation, piece)
                    Result.append(ChangeLocation)
    Board[Location] = Cell(Location, piece)
    return Result

def CountValidMoves(Board:dict, DirBoard:dict, piece:int) -> [list]:
    #Similar to the previous functions, this function counts the number of possible valid moves that can be made by a player.
    PossibleMoves = []
    for EachSpace in Board.keys():
        
        if Board[EachSpace].piece == piece:
           
            Location = EachSpace
            for Direction in DirBoard['dir']:
                if Direction == DirBoard['dir'].NS:
                    DirBoardLookup = Direction + '-' + Location.split('-')[0]
                elif Direction == DirBoard['dir'].WE:
                    DirBoardLookup = Direction + '-' + Location.split('-')[1]
                else:
                    #For a Diagonal, we need to find the top of the diagonal
                    DirBoardLookup = _FindDiagonal(DirBoard, Direction, Location)
                if DirBoardLookup != '':
                    GetDirString = _StringDirection(Board, DirBoard[DirBoardLookup], Location)
                    GetBasicDirString = ''.join(repeat for repeat,_ in itertools.groupby(GetDirString))
                    ValidCombo = (str(Opponent(piece)) + '0')
                    if ('*' + ValidCombo) in GetBasicDirString: #Is the combination valid?
                        #We Found a Valid Move, add one to possible moves
                        ReadDirection = GetDirString.index('*')
                        while True: #Because we don't know how many of the opponents pieces there are after star
                            
                            ReadDirection += 1
                            ChangeLocation = DirBoard[DirBoardLookup][ReadDirection]
                            if GetDirString[ReadDirection] == '0':
                                if ChangeLocation not in PossibleMoves:
                                    PossibleMoves.append(ChangeLocation)
                                break
                            
                            
                            
                        
                    if (ValidCombo[::-1] + '*') in GetBasicDirString:
                        #We Found a Valid Move, but in the opposite direction
                        ReadDirection = GetDirString.index('*')
                        while True: #Because we don't know how many of the opponents pieces there are BEFORE star
                            ReadDirection -= 1
                            ChangeLocation = DirBoard[DirBoardLookup][ReadDirection]
                            if GetDirString[ReadDirection] == '0':
                                if ChangeLocation not in PossibleMoves:
                                    PossibleMoves.append(ChangeLocation)
                                break
    return PossibleMoves




    
    
            
            

def CreateGameBoard(numofcolumns:int, numofrows:int, TopLeft:str) -> [dict,list]:
        #This function takes a number of columns and rows and constructs a game board.
        #Dictionary Key Style (Column#-Row#)
        Result = {}
        for column in range(1,numofcolumns + 1):
            for row in range(1,numofrows + 1):
                LocationID = str(column) + '-' + str(row)
                Result[LocationID] = Cell(LocationID, 0)
                
        #By Default, create four pieces in the center of the game board.
        TopLeftC, TopRightC = 1, 2
        BottomLeftC, BottomRightC = 2, 1
        if TopLeft == 'B':
            TopLeftC, TopRightC = 2, 1
            BottomLeftC, BottomRightC = 1, 2
        CenterTopLeft = str(int(numofcolumns/2)) + '-' +  str(int(numofrows/2))
        CenterTopRight = str(int(CenterTopLeft.split('-')[0]) + 1) + '-' + CenterTopLeft.split('-')[1]
        CenterBottomLeft = CenterTopLeft.split('-')[0] + '-' + str(int(CenterTopLeft.split('-')[1]) + 1)
        CenterBottomRight = str(int(CenterTopLeft.split('-')[0]) + 1) + '-' + str(int(CenterTopLeft.split('-')[1]) + 1)
        Result[CenterTopLeft] = Cell(Result[CenterTopLeft].position, TopLeftC)
        Result[CenterTopRight] = Cell(Result[CenterTopRight].position, TopRightC)
        Result[CenterBottomLeft] = Cell(Result[CenterBottomLeft].position, BottomLeftC)
        Result[CenterBottomRight] = Cell(Result[CenterBottomRight].position, BottomRightC)
        return (Result, [CenterTopLeft,CenterTopRight,CenterBottomLeft,CenterBottomRight])





def _GoDiagonal(*args, **kwargs) -> None:
    #This sub-function traverses through the game board detecting all diagonal lines in NWSE and NESW direction

    ##Gather all necessary variables
    diag_start = args[0]['diag_start']
    diag_stop = args[0]['diag_stop']
    diag_step = args[0]['diag_step']
    diag_direction = args[0]['diag_direction']
    DiagMap = args[0]['DiagMap']
    numofcolumns, numofrows = args[0]['numofcolumns'], args[0]['numofrows']
    ResultDirection = args[0]['ResultDirection']
    rowcolumn = args[0]['rowcolumn']
    Result = args[0]['Result']
    
    
    for diagline in range(diag_start, diag_stop, diag_step):
        Counter = diagline
        ListOCells = []
        #Add the Very First Cell of the diagonal
        GetFirstLocID = DiagMap[diagline]
        ListOCells.append(GetFirstLocID)
        while True: #Because the diagonals have variable length!!!
            Counter += int(diag_direction)
            GetLocID = DiagMap[Counter]
            ListOCells.append(GetLocID)
            NextPiece = Counter + int(diag_direction)
            if (NextPiece) not in DiagMap:
                break #Counter has already past the last cell in the diagonal because the theoretical next one doesn't exist. Break!
            elif diag_direction == ResultDirection.NWSE and (int(DiagMap[NextPiece].split('-')[0]) - int(GetLocID.split('-')[0])) != 1:
                break #Counter has went to a piece that doesn't follow direction pattern. Break!
            elif diag_direction == ResultDirection.NESW and (int(DiagMap[NextPiece].split('-')[0]) - int(GetLocID.split('-')[0])) != -1:
                break #Same situation as previous but different direction
        if rowcolumn == 'col':
            Result[diag_direction + '-c' + GetFirstLocID.split('-')[0]] = ListOCells
        elif rowcolumn == 'row':
            Result[diag_direction + '-r' + GetFirstLocID.split('-')[1]] = ListOCells
            
def CreateDirBoard(GBoard:dict, numofcolumns:int, numofrows:int) -> dict:
    #This function takes a number of columns and rows and constructs the BOSS.
    Result = {}
    ResultDirection = DirectionNumbers(str(numofcolumns), '1', str(numofcolumns -1), str(numofcolumns + 1)) 
    #The keys for this dictionary will follow this format: ##-## (Direction Number-Step Number)
    #Step Number is a way to uniquely identify a straight line across the game board. For the North-South Direction, it will simply be column number, for East-West, row number.
    #But for the Diagonals, this step number will work in a way that is from top to bottom

    DiagMapCount = 0
    DiagMap = {} #This map is used to help create the diagonal line values later on
    ReverseDiagMap = {} 
    #Adding North South values
    for column in range(1, numofcolumns + 1):
        ListOCells = []
        for row in range(1, numofrows + 1):
            LocationID = str(column) + '-' + str(row)
            ListOCells.append(LocationID)
        Result[ResultDirection.NS + '-' + str(column)] = ListOCells

    #Adding East West values, while establishing DiagMap
    for row in range(1, numofrows + 1):
        ListOCells = []
        for column in range(1, numofcolumns + 1):
            LocationID = str(column) + '-' + str(row)
            ListOCells.append(LocationID)
            DiagMapCount += 1
            DiagMap[DiagMapCount] = str(column) + '-' + str(row)
            ReverseDiagMap[str(column) + '-' + str(row)] = DiagMapCount
        Result[ResultDirection.WE + '-' + str(row)] = ListOCells

    #Adding NorthWestSouthEast values. This is gonna be hard.
    diag_direction = ResultDirection.NWSE
    diag_start = numofcolumns - 2
    diag_stop = 0
    diag_step = -1
    rowcolumn = 'col'
   # print(locals())
    _GoDiagonal(locals()) #This function needs access to most of the variables in this function, and passing them one by one is just extra space being taken up
    
    ##Adding Second Half of NWSE values
    diag_start = 1 + int(ResultDirection.NS)
    diag_stop = ((numofrows * numofcolumns) - (numofcolumns - 1)) - int(ResultDirection.NS)
    diag_step = int(ResultDirection.NS)
    rowcolumn = 'row'
    _GoDiagonal(locals())
    
    #Adding NorthEastSouthWest values. This wont be as hard.
    diag_direction = ResultDirection.NESW
    diag_start = 3
    diag_stop = numofcolumns + 1
    diag_step = 1
    rowcolumn = 'col'
    _GoDiagonal(locals())

    #Adding Second Half of NESW values
    diag_start = int(ResultDirection.NS) *2
    diag_stop = (numofrows * numofcolumns) - int(ResultDirection.NS)
    diag_step = int(ResultDirection.NS)
    rowcolumn = 'row'
    _GoDiagonal(locals())

    #Finally, it would be intuitive to have access to the Direction Numbers in the Dictionary
    Result['dir'] = ResultDirection
    #Also to have access to the Diagonal Map, in both its regular direction and inverse direction.
    Result['diagmp'] = DiagMap
    Result['rdiagmp'] = ReverseDiagMap
    Result['maxcolumns'] = numofcolumns
    #Return the dictionary
    return Result



