# Resolutions 1280x720

# ====OTHER INFO FOR MARKER====
#
# CHEAT CODES CAN BE ENTERED BY PLAYING AND THEN JUST
# TYPING THEM INTO THE KEYBOARD WHILE ON THE WINDOW
# ONCE TYPED PRESS ENTER TO ACTIVATE
#
# CHEAT CODES ARE: fastfire, imbored, nishikado
#
from math import sqrt
from tkinter import Canvas, Label, PhotoImage, Tk, Button, Frame, Text
from random import randint, choice

root = Tk()
root.title("Intergalactic Intruders")

# menu image
imageBackground = PhotoImage(file="Assets/HomeScreenImageAlpha.png")
# Windows xp boss screen
bossScreen = PhotoImage(file="Assets/WindowsXPWorkScreen.png")
bossScreemTempGlobal = None
# window icon
windowIcon = PhotoImage(file="Assets/Icon.png")

root.iconphoto(False, windowIcon)

# filePath
LEADERBOARDFILEPATH = "DataFiles/leaderBoards.txt"
SAVEFILE = "DataFiles/save.txt"
CONFIGFILEPATH = "DataFiles/config.txt"

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TOP_BANNER_HEIGHT = 50

REFRESHRATE_MS = 25

# Number at the begggining then (aliens + level)
NUMBER_OF_ALIENS = 2

IMAGE_ZOOM_MULTIPLIER = 5
ALIEN_HEIGHT = 8
ALIEN_WIDTH = 8
BULLET_HEIGHT = 4
BULLET_WIDTH = 2

bulletAlienHitBox = sqrt(((ALIEN_WIDTH/2 + BULLET_WIDTH/2) *
                         IMAGE_ZOOM_MULTIPLIER) ** 2 +
                         ((ALIEN_HEIGHT/2 + BULLET_HEIGHT/2) *
                         IMAGE_ZOOM_MULTIPLIER)**2)

root.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
# fixed resolution
root.minsize(1280, 720)

# Help screen images
leftArrowImg = PhotoImage(file="Assets/LeftKeyAlpha.png").zoom(5, 5)
rightArrowImg = PhotoImage(file="Assets/RightKeyAlpha.png").zoom(5, 5)
spaceBarImg = PhotoImage(file="Assets/SpaceBarAlpha.png").zoom(5, 5)

# Display Variables
canvas = None
upperFrameR = None
upperFrameL = None
# Label Variables
pausedMainMenuBtn = None
pausedLabel = None
scoreLabel = None
levelLabel = None
# Buttons from menu
startNewGameBtn = None
exitGameBtn = None
menuFrame = None

# Endgame widgets
nameLabel = None
submitBtn = None
saveGameBtn = None

# Initalize stuff
alienImages = ["Alien1Alpha.png",
               "Alien2Alpha.png",
               "Alien3Alpha.png",
               "Alien4Alpha.png"]
aliens = []

ship = None
shipBullet = None

# Ship keybindings
leftMove = 'Left'
rightMove = 'Right'
shootKey = 'space'


# GAME win/lose state
# gameState = 0 : lose
# gameState = 1 : neither (still playing)
# gameState = 2 : win
gameState = 1

score = 0
level = 1

userName = ""

# cheat code buffer
cheatCode = ""
# goFast - bullets moves faster
# imbored - skip level
# nishikado - adds 1978 points (totally no significance)
cheatCodes = ["fastfire", "imbored", "nishikado"]
# Used a cheat code Restart game to disable this to have a valid cheat
cheated = False

fastCheat = False
imboredCheat = False

# global pause
paused = False
pauseMenuCalled = False

# boss screen identifier
boss = False


# Get file and return it to caller at zoomed scale
def getImageZoomed(fileName):
    return PhotoImage(file=("Assets/" +
                            fileName)).zoom(IMAGE_ZOOM_MULTIPLIER,
                                            IMAGE_ZOOM_MULTIPLIER)


def createAliens():
    for i in range(NUMBER_OF_ALIENS + level):
        xPos = randint(20, WINDOW_WIDTH-100)
        yPos = randint(70, 125)  # avoid the frame at top
        image = getImageZoomed(choice(alienImages))
        speed = randint(5+int(level*0.25), 6+level)
        aliens.append(Alien(xPos, yPos, image, speed))


# Gets keybindings from file
def setKeyBindings():
    global leftMove, rightMove, shootKey
    try:
        configFile = open(CONFIGFILEPATH, "rt")
        for line in configFile.readlines():
            # if the line is not a comment
            if not line[0] == '#':
                values = line.strip('\n').split(',')
                if not values[1].lower() == 'p' or not values[1].lower()\
                   == '<p>' or not values[1].lower() == '<esc>':
                    if values[0] == 'L':
                        leftMove = values[1]
                    elif values[0] == 'R':
                        rightMove = values[1]
                    elif values[0] == 'S':
                        shootKey = values[1]
                    else:
                        print("Nothing", line)
    except Exception as e:
        print(e)


class Ship():
    def __init__(self, xPos, yPos):
        self.image = getImageZoomed("ShipAlpha.png")
        self.width = 40
        self.height = 40
        # x and y are taken from center of sprite
        # each pixel of the spite is 5 canvas units
        self.x = xPos
        self.y = yPos
        self.MovingLeft = False
        self.MovingRight = False
        self.xVelocity = 15  # set velocity of ship to allow bind calls
        self.dead = False  # state of the ship
        # allows for press callbacks and release callbacks
        # Try to set the keys to the movement and fire
        # if there is a problem then set as default
        try:
            canvas.bind("<"+leftMove+">", self.moveLeft)
            canvas.bind("<"+rightMove+">", self.moveRight)
            canvas.bind("<KeyRelease-"+leftMove+">", self.stopMoveLeft)
            canvas.bind("<KeyRelease-"+rightMove+">", self.stopMoveRight)
            canvas.bind("<"+shootKey+">", self.shoot)
        except:  # default
            canvas.bind("<Left>", self.moveLeft)
            canvas.bind("<Right>", self.moveRight)
            canvas.bind("<KeyRelease-Left>", self.stopMoveLeft)
            canvas.bind("<KeyRelease-Right>", self.stopMoveRight)
            canvas.bind("<space>", self.shoot)

        canvas.bind("p", pause)
        # cheat code control
        canvas.bind("<Return>", checkCode)
        canvas.bind("<Key>", getCheatChar)

    # create will be called when ready to play
    def create(self):
        canvas.create_image(self.x, self.y, image=self.image)

    def moveLeft(self, event):
        self.MovingLeft = True

    def moveRight(self, event):
        self.MovingRight = True

    def stopMoveLeft(self, event):
        self.MovingLeft = False

    def stopMoveRight(self, event):
        self.MovingRight = False

    #  here we move ship and check that it is within bounds
    #  this will be called each frame
    def update(self):
        if not paused:
            # to not go off screen on the left
            if self.MovingLeft and self.x > (0 + (self.width / 2) + 5):
                self.x -= self.xVelocity
                # canvas.move(self.image, -self.xVelocity,0)
                # to not go odd screen on the right
            if self.MovingRight and self.x < (WINDOW_WIDTH -
               (self.width / 2) + 5):
                self.x += self.xVelocity
                # canvas.move(self.image, self.xVelocity,0)
            canvas.create_image(self.x, self.y, image=self.image)
        # need to add boundries

    def shoot(self, event):
        global shipBullet
        if not self.dead:
            # if the bullet is dead (gone from screen then you can fire)
            # if bullet is not defined or is set to null originally then run
            if 'shipBullet' not in globals() or shipBullet is None:
                # spawn and create render if the game isnt paused
                if not paused:
                    shipBullet = Bullet(self.x, self.y-30)
                    shipBullet.dead = False
                    shipBullet.draw()


class Bullet():
    def __init__(self, xPos, yPos):
        self.image = getImageZoomed("BulletAlpha.png")
        self.x = xPos
        self.y = yPos
        self.yVelocity = 15
        self.dead = True

    def draw(self):
        if not self.dead:
            canvas.create_image(self.x, self.y, image=self.image)

    # create image at location of the tip of the ship
    def update(self):
        global fastCheat
        # do not update until unpaused
        if not paused:
            if not self.dead:
                # if fast cheat active then increase speed
                if fastCheat:
                    self.y -= self.yVelocity*2
                else:
                    self.y -= self.yVelocity
            if self.y <= 0 + TOP_BANNER_HEIGHT:
                # needs to be killed externally
                self.dead = True  # might not be needed
            self.checkColisions()
            self.draw()

    def checkColisions(self):  # SPELL CHECK
        for alien in aliens:
            # check proximity to aliens
            # work out absolute distance between the two objects
            distance = sqrt(abs(alien.y - self.y)**2 +
                            abs(alien.x - self.x)**2)
            # this means that the bullet has hit
            if distance < bulletAlienHitBox:
                alien.dead = True  # set states
                self.dead = True
# Goes above the top of the screen
# Therefore out of range and will be deleted


class Alien():
    def __init__(self, xPos, yPos, image, speed):
        self.image = image
        self.width = 40
        self.height = 40
        # x and y are taken from center of sprite
        # each pixel of the spite is 5 canvas units
        self.x = xPos
        self.y = yPos
        self.xVelocity = speed  # set velocity of alien
        self.dead = False

    def update(self):
        global gameState
        # do not update until unpaused
        # can put these two conditions on the same line
        if not paused:
            if not self.dead:
                canvas.create_image(self.x, self.y, image=self.image)

                if self.y > WINDOW_HEIGHT-100:
                    # aliens win
                    gameState = 0  # lose

                if (self.x >= WINDOW_WIDTH - self.width / 2 - 5) or \
                        (self.x <= 0 + self.width / 2 + 5):
                    self.hitWall()
                self.x += self.xVelocity  # move

    # go down flip direction
    def hitWall(self):
        # invert direction
        # worse but safer code
        if self.x < 100:
            self.xVelocity = abs(self.xVelocity)
        elif self.x > 1200:
            self.xVelocity = -abs(self.xVelocity)
        # self.xVelocity = -self.xVelocity
        self.y += 60  # absolute


# CHEATS
# append to string
def getCheatChar(event):
    global cheatCode
    # after enter event can cause error to occur
    try:
        # if the character is a to z
        if 96 < ord(event.char.lower()) < 123:
            cheatCode += event.char
    except:
        pass


# when enter is pressed cheat code is checked
# enter event
def checkCode(event):
    global cheatCode, cheated, fastCheat, \
           imboredCheat, gameState, score

    for i in range(len(cheatCodes)):
        # see if the last section of the buffer is equal to a cheat code
        try:
            # Cheat used
            if cheatCodes[i] == cheatCode[-(len(cheatCodes[i])):]:
                cheated = True
                # Fastfire ( makes bullets go 2x speed)
                if i == 0:
                    fastCheat = True
                # Imbored (skips the level)
                elif i == 1:
                    # skip level
                    # addpoints
                    score += (10 + ((level-1)*1.5))*(level+NUMBER_OF_ALIENS)
                    imboredCheat = True
                    gameState = 2  # win
                # Nishikado (adds 1978 points to the score)
                elif i == 2:
                    score += 1978
                    drawScore()
                # the same year space invaders was made
                else:
                    pass
                # Debugging
                print("CHEAT:", cheatCodes[i], "activated.")
        except:
            pass  # avoid index error
    # clear cheat string buffer
    cheatCode = ""


# should be updated each time the score changes
def drawScore():  # flickering as its rendered each frame
    global score, scoreLabel, level
    try:
        scoreLabel.pack_forget()
    except:
        pass

    # casting galore
    zeros = '0'*(8-len(str(int(score))))
    # cast score to int and then string to remove decimals from float value
    scoreLabel = Label(upperFrameL,
                       text=("Score: " + zeros + str(int(score))),
                       font=('Small Fonts', 36),
                       bg='black',
                       fg='white',
                       justify="right")  # text flows out of rhs

    scoreLabel.pack(ipady=5, ipadx=5, anchor='ne')

    levelLabel = Label(upperFrameR,
                       text=("Level: " + str(level)),
                       font=('Small Fonts', 36),
                       bg='black',
                       fg='white',
                       justify="left")
    levelLabel.pack(ipady=5, ipadx=5, anchor='nw')


def pauseExitToMenu():
    global pausedLabel, pausedMainMenuBtn, paused, gameState, pauseMenuCalled
    canvas.unbind("p")
    canvas.unbind("<space>")
    canvas.unbind("<return>")
    canvas.unbind("<Key>")
    pausedLabel.pack_forget()
    pausedMainMenuBtn.pack_forget()
    gameState = 1
    paused = False
    pauseMenuCalled = True  # Will interupt game loop
    clearWidgets(root)


# Pause function
def pause(event):
    global paused, pausedLabel, pausedMainMenuBtn
    paused = not paused  # invert bool
    if paused:
        pausedLabel = Label(canvas,
                            text="Paused, press P to resume",
                            font=('Small Fonts', 36),
                            bg="black",
                            fg="white")
        # has to be seperate line otherwise label will replicate
        pausedLabel.pack(expand=True)

        pausedMainMenuBtn = Button(canvas,
                                   text="Exit To Menu",
                                   font=('Small Fonts', 32),
                                   bg="black",
                                   fg="white",
                                   command=pauseExitToMenu)
        pausedMainMenuBtn.pack(expand=True, side='bottom', pady=15)

    # big text on screen
    # not paused
    else:
        # secure code incase paused label is none
        try:
            pausedLabel.pack_forget()
            pausedMainMenuBtn.pack_forget()
        except:
            pass


# this function is for the boss key, the function will be
# called on an escape key event
# for now the function does not pause the game
# the user will have to be done manually by the user
def bossScreenCall(event):
    global boss, canvas,  bossScreen, bossScreemTempGlobal
    boss = not boss
    if boss:
        # space image
        bossScreemTempGlobal = Label(root,
                                     image=bossScreen,
                                     bg="black")
        bossScreemTempGlobal.place(x=0, y=0)
    else:
        # remove image
        bossScreemTempGlobal.config(image='')


# returns the formatted leaderboard data
def getScoreData():
    scores = []
    message = ""
    file = open(LEADERBOARDFILEPATH, "rt")
    lines = file.readlines()
    for line in lines:
        items = line.split(',')
        scores.append(int(items[2]))  # insert scores into array
    scores.sort(reverse=True)  # sort array large to small
    message += ("Rank:\tName:\tLevel:\tScore:\t\tCheated:\n")
    for i in range(8):  # leaderboards
        try:  # formatting nightmare
            for line in lines:
                line = line.strip('\n')
                items = line.split(',')
                if int(items[2]) == scores[i]:
                    ending = ""  # last char dont add \n
                    if not i == 7:
                        ending = "\n"
                    else:
                        ending = ""
                    zeros = 8-len(items[2])
                    message += (str(i + 1) + "\t" + items[0] + "\t" +
                                items[1] + "\t" + ("0" * zeros) +
                                items[2] + "\t\t" + items[3] + ending)
        # out of index of spaces on board
        except:
            endingEmpty = ""  # last char dont add \n
            if not i == 7:
                endingEmpty = "\n"
            else:
                endingEmpty = ""
            message += (str(i+1)+"\t###\t####\t########\t\t#"+endingEmpty)
    return message


# after compleation of level this will progress to this
def nextLevel():
    global level

    canvas.unbind("<Key")
    canvas.unbind("<Enter>")

    level += 1
    playGame()
    # anyother level changes here


# Called if game is lost and is restarted
def restartGame():
    global level, gameState, ship, shipBullet, score, cheated, fastCheat
    # If new game occurs or resatarted then save file erased
    eraseSaveFile()
    canvas.unbind("<Key")
    canvas.unbind("<Enter>")

    # reset level, score and cheat flag
    level = 1
    score = 0
    cheated = False
    fastCheat = False
    # Set all aliens to dead
    for alien in aliens:
        alien.dead = True
    # for first level
    # then playgame will be called after
    drawHelpScreen()


# Checks for a savefile, if one exists then return true else, false
def saveFileExists():
    global level, score, cheated, fastCheat
    try:
        saveFile = open(SAVEFILE, "rt")
        saveFileLines = saveFile.readlines()
        # First line indicates wether there is a save
        if saveFileLines[0][0:4] == "Save":  # avoid \n char
            # if there is a save, load the data into the score and level vals
            values = saveFileLines[1].split(',')
            level = int(values[0])
            score = int(values[1])
            cheated = bool(int(values[2]))
            fastCheat = bool(int(values[3]))
            # Return true if a save exists
            saveFile.close()
            return True

        saveFile.close()
    # If file cannot be opened or the data cannot be read
    except:
        return False


# Save game will write data to save file
def saveGame(event):
    global level, score, saveGameBtn
    # Write to file (erasing past data)
    # If file doesnt exist make one (x)
    saveFile = open(SAVEFILE, "w")
    saveFile.write("Save\n" + str(level+1) + "," + str(int(score)) +
                   "," + str(int(cheated)) + "," + str(int(fastCheat)))
    saveFile.close()
    saveGameBtn.config(state="disabled")


# Open file and write no data (effectivly erasing the data)
def eraseSaveFile():
    file = open(SAVEFILE, "w")
    file.write("")


# Pass 3 characters (NAME)
def submitCheckName(event):
    global userName, cheated, score, submitBtn, level
    # if username is 3 letters long then
    if (len(userName) == 3):
        cheatedChar = ""
        if cheated is False:
            cheatedChar = "N"
        elif cheated is True:
            cheatedChar = "Y"
        file = open(LEADERBOARDFILEPATH, "at")
        # write to file
        file.write("\n" + userName + "," + str(level) + "," +
                   str(int(score)) + "," + cheatedChar)
        file.close()

        # Disable the way to submit a name
        submitBtn.config(state="disabled")  # grey out button
        canvas.unbind("<Enter>")
        userName = ""


def updateLabel():
    global userName, nameLabel
    try:  # if label isnt created yet
        nameLabel.pack_forget()
    except:
        pass
    nameLabel = Label()
    nameLabel = Label(canvas,
                      text=userName,
                      font=('Small Fonts', 36),
                      bg="black",
                      fg="white")
    nameLabel.pack(expand=False, pady=5, side='bottom')


# character managment
def inputCharacters(event):
    global userName
    try:
        if 96 < ord(event.char.lower()) < 123:
            # Name is 3 letters
            if not len(userName) > 2:
                # need to show the name on screen
                userName += event.char.upper()
                updateLabel()
        elif (event.keysym == 'BackSpace'):
            userName = userName[:-1]
            updateLabel()
        else:
            pass
    # event gets random characters not entered and throws a type error
    except TypeError:
        pass


# when someone wins or loses this function
def showFinalGameState():
    global gameState, submitBtn, imboredCheat, saveGameBtn
    # Disable pause, shoot and enter cheats (char and enter) in menu area
    canvas.unbind("p")
    canvas.unbind("<space>")
    canvas.unbind("<return>")
    canvas.unbind("<Key>")
    if gameState == 0:  # lose

        # end game
        # erase the save file
        eraseSaveFile()
        # will call fucntion same as pressing submit
        canvas.bind("<Key>", inputCharacters)
        canvas.bind("<Return>", submitCheckName)

        gameLoseMsg = """Game Over, the aliens have taken earth!
Please type your initials (3 Characters)"""

        endOfGameMsgLbl = Label(canvas,
                                text=gameLoseMsg,
                                font=('Small Fonts', 36),
                                bg="black",
                                fg="white").pack(expand=False,
                                                 side='top',
                                                 pady=100)
        # submit name
        # write name, score, cheated flag
        exitToMenuBtn = Button(canvas,
                               text="Exit To Menu",
                               font=('Small Fonts', 32),
                               bg="black",
                               fg="white",
                               command=drawMenu).pack(expand=False,
                                                      pady=5,
                                                      side='bottom')

        restartBtn = Button(canvas,
                            text="Restart",
                            font=('Small Fonts', 32),
                            bg="black",
                            fg="white",
                            command=restartGame).pack(expand=False,
                                                      pady=5,
                                                      side='bottom')

        submitBtn = Button(canvas,
                           text="Submit",
                           font=('Small Fonts', 32),
                           bg="black",
                           fg="white")

        # upon release of the submit button the function will be called
        submitBtn.bind('<ButtonRelease>', submitCheckName)
        submitBtn.pack(expand=False, pady=20, side='bottom')

    elif gameState == 2:  # win
        if imboredCheat:
            # reset cheat
            imboredCheat = False

        gameWinMsg = """Level passed, congratulation commander,
 you have saved the earth from the aliens... for now.\n
Checkpoint reached, you may save your game\n if you want to \
return to it later.\nBut dying will lose the save."""

        endOfLevelMsgLbl = Label(canvas,
                                 text=gameWinMsg,
                                 font=('Small Fonts', 30),
                                 bg="black",
                                 fg="white").pack(expand=False,
                                                  pady=100,
                                                  side='top')

        exitToMenuBtn = Button(canvas,
                               text="Exit To Menu",
                               font=('Small Fonts', 24),
                               bg="black",
                               fg="white",
                               command=drawMenu).pack(expand=False,
                                                      pady=5,
                                                      side='bottom')

        nextLevelBtn = Button(canvas,
                              text="Next Level",
                              font=('Small Fonts', 24),
                              bg="black",
                              fg="white",
                              command=nextLevel).pack(expand=False,
                                                      pady=5,
                                                      side='bottom')

        saveGameBtn = Button(canvas,
                             text="Save",
                             font=('Small Fonts', 24),
                             bg="black",
                             fg="white")
        saveGameBtn.bind('<ButtonRelease>', saveGame)
        saveGameBtn.pack(expand=False, pady=10, side='bottom')
    # gamestate == 1 (game still running)
    else:
        pass


# check if all aliens are dead -> winstate
def checkWinState():
    global gameState
    if len(aliens) == 0:
        gameState = 2  # set game state to win


# draws the ship each frame
def drawShip():
    ship.update()


# here objects should be deleted
def drawShipBullet():
    global shipBullet
    try:
        shipBullet.update()
        # if bullet should be deleted then...
        if shipBullet.dead:
            del shipBullet
    except:  # if object is not created yet
        pass


def drawAliens():
    global score, gameState
    for alien in aliens:
        alien.update()
        if alien.dead:
            # add 10 point to score and remove the alien
            # times the score by a multiplyer based on the level
            # if the game is still running
            score += 10 + ((level-1)*1.5)
            drawScore()
            aliens.remove(alien)
            del alien


# same as draw aliens but this adds no points and is called upon board creation
def clearAliens():  # aliens are still drawn on screen
    global aliens
    for alien in aliens:
        del alien  # delete each object in list
    aliens = []  # then clear list (list is just to delte all alien objs)


# this will be called from someone pressing a start button
def gameLoop():
    global gameState, canvas
    loop = canvas.after(REFRESHRATE_MS, gameLoop)
    canvas.delete('all')  # clear canvas to redraw

    if pauseMenuCalled:
        canvas.after_cancel(loop)
        drawMenu()
    else:
        drawShip()
        drawShipBullet()
        drawAliens()
        checkWinState()
        # checkColisions() # Colision now internal
        # if the game has been won or lost then...
        # check win as first
        if not gameState == 1:
            # cancel the gameloop and then display end screen
            canvas.after_cancel(loop)
            showFinalGameState()


def createGame():
    global ship, canvas, upperFrameR, upperFrameL, score, level, gameState

    canvas = Canvas(root,
                    width=WINDOW_WIDTH,
                    height=WINDOW_HEIGHT,
                    bg="black")
    canvas.pack(fill="both", expand=True)

    # backgroundLabel = Label( canvas, image=gameBackground)
    # backgroundLabel.place(x = 0, y = 0)

    upperFrameR = Frame(canvas,
                        width=WINDOW_WIDTH/2,
                        height=TOP_BANNER_HEIGHT,
                        bg="black")

    upperFrameR.place(x=0)  # top left
    upperFrameR.pack_propagate(False)  # stop frame from shrinking

    upperFrameL = Frame(canvas,
                        width=WINDOW_WIDTH/2,
                        height=TOP_BANNER_HEIGHT,
                        bg="black")

    upperFrameL.place(x=WINDOW_WIDTH/2)  # top left
    upperFrameL.pack_propagate(False)  # stop frame from shrinking

    # clear aliens from pas board # DOESNT WORK
    clearAliens()

    # subject to change
    ship = Ship(400, WINDOW_HEIGHT - 60)
    # create the ship
    ship.create()
    createAliens()

    # set gamestate to running
    gameState = 1

    drawScore()

    # allow keyboard inputs to be registered by canvas
    canvas.focus_set()


# Game info pre-play screen
def drawHelpScreen():
    global leftArrowImg, rightArrowImg, spaceBarImg
    # clear screen draw help menu
    clearWidgets(root)

    helpMsg = """Hello commander, this is the current situation.
The aliens are coming in fleets, it's up to you
to defeat our home, Earth.\n
You are our last line of defence, good luck."""
    helpMsg2 = """Use left and right arrow keys to move. Space to shoot. (By default)\n
Need a break? Press P. Boss coming? Press <ESC>

If Cheats are enabled that will be recorded for that game."""

    canvas = Canvas(root,
                    width=WINDOW_WIDTH,
                    height=WINDOW_HEIGHT,
                    bg="grey")
    canvas.pack(fill="both", expand=True)
    helpMsgLbl = Label(canvas,
                       text=helpMsg,
                       font=('Small Fonts', 24),
                       bg="grey").pack(expand=False,
                                       pady=40,
                                       side='top')

    canvas.create_image(400, 300, image=leftArrowImg, anchor='w')
    canvas.create_image(500, 300, image=rightArrowImg, anchor='w')
    canvas.create_image(600, 300, image=spaceBarImg, anchor='w')

    readyBtn = Button(canvas,
                      text="Im Ready.",
                      font=('Small Fonts', 24),
                      bg="darkgrey",
                      command=playGame)
    readyBtn.pack(expand=False, side='bottom', padx=5, pady=15)

    helpMsgLbl = Label(canvas,
                       text=helpMsg2,
                       font=('Small Fonts', 24),
                       bg="grey").pack(expand=False,
                                       pady=10,
                                       side='bottom')


def clearWidgets(root):
    widgetList = root.winfo_children()
    for item in widgetList:
        if item.winfo_children():
            # any children widgets created will be also removed
            widgetList.extend(item.winfo_children())
    for i in widgetList:
        # for each widget in the list pack forget it
        try:
            i.pack_forget()
        except:
            pass


def drawMenu():
    global canvas, startNewGameBtn, exitGameBtn, imageBackground,\
           score, gameState, paused, pauseMenuCalled

    clearWidgets(root)

    pauseMenuCalled = False

    canvas = Canvas(root,
                    width=WINDOW_WIDTH,
                    height=WINDOW_HEIGHT,
                    bg="grey")
    canvas.pack(fill="both", expand=True)

    # Title screen (intro)
    canvas.create_image(0, 0, image=imageBackground, anchor='nw')

    # this button will be called regardless
    exitGameBtn = Button(canvas,
                         text="Exit Game",
                         font=('Small Fonts', 24),
                         bg="darkgrey",
                         command=root.quit)

    exitGameBtn.pack(expand=False, side='bottom', padx=5, pady=5)

    startNewGameBtn = Button(canvas,
                             text="New Game",
                             font=('Small Fonts', 24),
                             bg="darkgrey",
                             command=restartGame)

    startNewGameBtn.pack(expand=False, side='bottom', padx=5, pady=5)

    # if file exists then the button will be enabled and game will resume
    loadGameBtn = Button(canvas,
                         text="Resume",
                         font=('Small Fonts', 24),
                         bg="darkgrey",
                         command=playGame)

    # If a file does not exist then disable the load button
    if not saveFileExists():
        loadGameBtn.config(state="disabled")
    loadGameBtn.pack(expand=False, side='bottom', padx=5, pady=5)

    # Score data which will be inserted into leaderboards
    data = getScoreData()

    # create box
    text_box = Text(canvas,
                    height=9,
                    width=50,
                    font=('Small Fonts', 20),
                    bg="grey")

    text_box.pack(expand=False, side='bottom', pady=20, padx=5)  # Postion box
    text_box.insert('end', data)  # Inset info into text pox
    text_box.config(state='disabled')  # To stop from editing
    text_box.see("end")


def playGame():
    global canvas, startNewGameBtn, exitGameBtn, gameState
    clearWidgets(root)  # clear buttons lables etc.

    createGame()
    gameLoop()


# screen update loop
if __name__ == "__main__":
    setKeyBindings()
    root.bind("<Escape>", bossScreenCall)
    drawMenu()

root.mainloop()
