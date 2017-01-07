from direct.showbase.ShowBase import ShowBase
#Importing for Collision
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask, CollisionPlane, Plane
from panda3d.core import CollisionHandlerEvent
from panda3d.core import CollisionSphere
from panda3d.core import CollisionTube
from panda3d.core import CollisionHandlerPusher
#General Panda3d Imports
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from panda3d.core import VBase4
from pandac.PandaModules import Vec3,Vec4,BitMask32, Point3
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *
#Direct GUI Imports
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGui import *
#Other Imports Needed
import random, sys, os, math
#Importing Pyserial for Accelerometer
import serial

#Create the Title Screen
class titleScreen(ShowBase):
    def __init__(self):
        def setControllaGame():
            #Call the Main Game with Controlla Setup
            Main(True)
        def setKeysGame():
            #Call the Main Game with Keys Setup
            Main(False)
        def instructions():
            showInstructions()
        #Create the title screen scene
        marioTitle = OnscreenImage(image = "Images/newTitleScreen.jpg", scale = (1.35,1,1))
        playControlla = DirectButton(image = "Images/controllaButton.jpg", scale=(0.3,0.2,0.2), frameColor=(1,0.5,0.5,1),command=setControllaGame,
                            pos=(0.96,0,-.75))
        playKeys = DirectButton(image = "Images/keysButton.jpg", scale=(0.3,0.2,0.2), frameColor=(1,0.5,0.5,1),command=setKeysGame,
                            pos=(-0.96,0,-.75))
        showInstructionsBtn = DirectButton(image = "Images/instrButton.jpg", scale=(0.3,0.2,0.2), frameColor=(1,0.5,0.5,1),command=instructions,
                            pos=(0.96,0,.75))


backgroundMusic = loader.loadMusic("Music/backgroundMusic.mp3")
backgroundMusic.play()
#To begin the game initialize this screen
titleScreen()

#Create the Instructions Screen
class showInstructions(ShowBase):
    def __init__(self):
        base.destroy()
        ShowBase.__init__(self)

        def backToMainScreen():
            titleScreen()
        
        background = OnscreenImage(image = "Images/instrBackground.png", scale = (1.35,1,1))
        #Creating the Instructions Screen Scene
        backToMain = DirectButton(image = "Images/bulletBack.jpg",scale=(.2,.2,.1),
                                            pos =(-1.05,0,.85) ,command=backToMainScreen)
        pauseText = OnscreenText('Pause: Press "p" ',scale=0.07,pos=(0,0.6),fg=(0,0,0,1))
        resetText = OnscreenText('Reset: Press "r" ',scale=0.07,pos=(0,0.5),fg=(0,0,0,1))
        arrowKeysText = OnscreenText('Key Controls: Arrow Keys to Move ',scale=0.07,pos=(0,.4),fg=(0,0,0,1))
        spaceKeyText = OnscreenText('Key Controls: Space to use Item ',scale=0.07,pos=(0,.3),fg=(0,0,0,1))
        onControllaText = OnscreenText('On Controlla:',scale=0.07,pos=(0,0.2),fg=(0,0,0,1))
        controllaBtn1 = OnscreenText('Button 1: (left side) Use Item',scale=0.07,pos=(0,0.1),fg=(0,0,0,1))
        controllaBtn2 = OnscreenText('Button 2: (1st right side) Move Forward',scale=0.07,pos=(0,0),fg=(0,0,0,1))
        controllaBtn3 =OnscreenText('Button 3: (2nd right side) Move Reverse',scale=0.07,pos=(0,-0.1),fg=(0,0,0,1))
        controllaTiltText = OnscreenText('Tilt Left & Right: Moving the Character left & right ',scale=0.07,pos=(0,-0.2),fg=(0,0,0,1))


#Creates the Primary Run Game Page
class Main(ShowBase):
    #Initialization Page
    def __init__(self, ifControlla):
        # Setting up the Window
        base.destroy()
        ShowBase.__init__(self)

        #Creating the Back Button Menu First Screen
        def backToTitleScreen():
            titleScreen()
        backToMain = DirectButton(image = "Images/bulletBack.jpg",scale=(.2,.2,.1),
                                            pos =(1.05,0,-.85) ,command=backToTitleScreen)
        #Intialiize the Main Collision 
        traverser = CollisionTraverser()
        base.cTrav = traverser

        #If the user is using keys or the controlla then only change values accordingly
        if (ifControlla):
            self.useControlla = True
        else:
            self.useControlla = False

        # Set the background color of the window to black
        self.win.setClearColor((0, 0, 0, 1))

        # This is used to store which keys are currently pressed
        #Cite: The idea of using the set to track moving var. is from roaming-ralph example in Panda3d then I modified
        #Cite URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "reverse": 0,
            "cam-left": 0, "cam-right": 0, "item": 0, "speedFwd": 0}

        #Kept track of previous marioActor in the previous frame (Used to find vector of shell)
        self.prevX = 0
        self.prevY = 0

        #Defining if the game has started or is counting down
        self.gameInSession = False
        self.gameBeginning = True
        #Load all of the needed functions
        self.loadModels()
        self.gameStates()
        self.createGraphics()
        self.setupCamera()
        self.settingAI()
        self.wallCollisionSetup()
        #Initilization of the collision functions
        self.terrainCollisionSetup()
        self.lapPlaneCollisionSetup()
        self.itemBoxCollisionSetup()
        self.shellCollisionSetup()
        #Movement controls of the Mario Actor (Controlla or Keys)
        self.makeActorMove()
        self.keyControls()

        #Now run the frame task which will continiously run the game
        taskMgr.add(self.frame, "frameTask")
    
    def frame(self, task):
        #Check if the game isn't in session and it begins to count down
        if (self.gameBeginning):
            self.gameBeginning = False
            self.beforeGameCountDown()

        #Check if the game is in session and keep functions updated
        if (self.gameInSession):
            self.updateTime()
            self.updateAI()
            self.checkLap()
            self.checkGameOver()
            self.controlActor()
            self.moveActor()

        #When the game is over, only keep these functions udpated
        if (self.gameOver):
            self.updateEndAI()
            self.updateAI()
            self.updateAITime()
        
        #Updating the Plane (Tube) to track which lap your on
        if (self.lapPlaneIsInPosition == False):
            self.updateLapPlane()

        #Updating the item box so when the user hits it, it reapears in it's orginal image
        if (self.itemBoxInPos == False):
            curTime = globalClock.getFrameTime()
            if ((curTime-self.boxTime) > 1):
                self.itemBoxInPos = True
                for box in self.allBoxObject:
                    if (box.getPos() ==  self.missingBoxPos):
                        box.resetPos()

        #Finding the degree of the vector of the user so that we can output shell in direction
        #Citing: Rishav Dutta (rishavd) helped me ge the math for this function.
        try: 
            self.degree = math.degrees(math.atan((self.prevY-y)/(self.prevX-x)))
        except:
            pass

        #Allowing the green shell to only appear for 5 seconds
        if (self.greenShellMove):
            curTime = globalClock.getFrameTime()
            #Offsetting the time so we can correctly count
            if ((curTime-self.shellTime) > 5):
                self.greenShellMove = False
                self.greenShellModel.hide()
            else:
                self.greenShellModel.setY(self.greenShellModel, 45*(self.degree))
        
        #Allowing the power-up (Big Mushroom) to work for 5 seconds
        if (self.marioBig):
            curTime = globalClock.getFrameTime()
            #Offsetting the time so we can correctly count
            if ((curTime -self.MegaMushTime) > 5):
                self.marioBig = False
                self.marioActor.setScale(.3)

        #Allowing the power-up of mushroom speed to work for 5 seconds
        if (self.mushroomSpeed):
            curTime = globalClock.getFrameTime()
            #Offsetting the time so we can correctly count
            if ((curTime - self.mushroomTime) > 5):
                self.mushroomSpeed = False
                self.setKey("speedFwd", False)
            else:
                self.setKey("speedFwd", True)

        marioBeginningPos = self.marioActor.getPos()
        x = marioBeginningPos[0]
        y = marioBeginningPos[1]
        #Update each of these every frame
        self.cameraMovement()
        self.terrainCollision()
        self.aiTerrainCollision()
        #Continue the task (so it works by frame)
        return task.cont


    #Each "perform" is to set the scale and gameState variable of the corresponding item
    def performBananaItem(self):
        #Interval Positions
        pass
    def performMushroomItem(self):
        self.mushroomItem = False
        self.mushroomSpeed = True
        self.mushroomTime = globalClock.getFrameTime()
    def performMegaMushroomItem(self):
        self.megaMushroomItem = False
        self.marioActor.setScale(0.5)
        self.marioBig = True
        self.MegaMushTime = globalClock.getFrameTime()
    def performGreenShellItem(self):
        self.greenShellItem = False
        #Throw the AI Shell
        shellStartPos = self.marioActor.getPos()
        self.greenShellModel.setPos(shellStartPos)
        self.greenShellModel.show()
        self.greenShellMove = True
        self.shellTime = globalClock.getFrameTime()
    
    def checkLap(self):
        #Set the display text on what lap your on
        if (self.mainLap == 0):
            curLap = "1"
        else:
            curLap = str(self.mainLap)
        #Check if the all three laps have been achieved and declare GameOver variables
        if (self.mainLap > 3):
            self.gameInSession = False
            self.gameOver = True
            #Track the time of the AI so it can be displayed when the game is over (currently needs debugged)
            delay = 6
            self.aiEndTime = self.aiEndTime - self.startTime - delay
            yourEndTime = globalClock.getFrameTime()
            formatedTime = self.formatTime(yourEndTime-6.31)
            #Display all the text to create the game over screen
            self.displayTime1.setText(formatedTime)
            self.displayGameOver.show()
            self.displayMarioText.show()
            self.displayTime1.show()
            self.displayAIText.show()
            self.displayTime2.show()
            self.resetTextHigh.show()
        else:
            self.displayLap.setText("Lap: " + curLap + "/3")
           
    #Function the inputs the value that globalClock gives and formats it readable time
    def formatTime(self, inTime):
        secTime = inTime
        minTime = secTime/60
        milTime = ((secTime%1)*100)
        #You need to subtract time to display the correct seconds over a minute
        if (minTime < 1):
            timeSubtraction = 0
        else:
            timeSubtraction = (60*int(minTime))

        return ("%0.2d:%0.2d:%0.2d" % (minTime, secTime-timeSubtraction, milTime))

    def checkGameOver(self):
        if (self.gameOver):
            self.gameOverBG.show()
            self.displayGameOver.setText("Game Over")

    def resetGame(self):
        if (self.useControlla):
            Main(True)
        else:
            Main(False)
    # Records the state of the arrow keys or control keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    def keyControls(self):
        self.accept("escape", sys.exit)
        self.accept("p", self.changeGameSession)
        self.accept("r", self.resetGame)
        #Setting the key of the main dictionary to constantly change moving parameters
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("arrow_down", self.setKey, ["reverse",1])
        self.accept("space", self.setKey, ["item",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("arrow_down-up", self.setKey, ["reverse",0])
        self.accept("space-up", self.setKey, ["item",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

    #Used to make the pause of game session
    def changeGameSession(self):
        if (self.gameInSession):
            self.gameInSession = False
            self.centerBG.show()
            self.pausedInText.show()
            self.unPause.show()
            self.resetText.show()

        else:
            self.gameInSession = True
            self.centerBG.hide()
            self.pausedInText.hide()
            self.unPause.hide()
            self.resetText.hide()

    #Cite: Roamgin-ralph Example Camera setup
    #CIte URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
    def setupCamera(self):
        #Floater above so Camera has something to look at
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.marioActor)
        self.floater.setZ(2.0)
         # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.marioActor.getX()+100, self.marioActor.getY(), 1)

    #Function to draw all the graphics. Hide not needed graphics and Show() later
    def createGraphics(self):
        #Main Top Timer
        self.runTime=OnscreenText('Time: 00:00:00',scale=0.07,pos=(-1.05,.92),fg=(255,255,255,1))
        #Count Down in the beginning
        #self.countDownBG = DirectFrame(frameColor=(0.941176,0.972549, 1,1), frameSize=(0,1,0,0.3), pos=(-0.5,-1,0.4))
        #self.countDown=OnscreenText('Waiting', scale=0.2, pos=(0,0.5), fg=(255,0,0,1))
        self.start = OnscreenImage(image="Images/start/start0.jpg", scale=0.3, pos=(0.8,-1,0.5))
        #Main Lap Display
        self.displayLap=OnscreenText('Lap: 1/3', scale=0.07, pos=(-1.17, .82), fg=(255,255,255,1))

        #Create all graphics for the Game Over screen
        self.gameOverBG = DirectFrame(frameColor=(0.941176,0.972549, 1,0.4), frameSize=(-1,1,-1,1), pos=(0,0,0))
        self.gameOverBG.hide()
        self.displayGameOver=OnscreenText('Game Over', scale=0.2, pos=(0,0.5), fg=(0,0,0,1))
        self.displayGameOver.hide()
        self.displayMarioText=OnscreenText('Mario (You):', scale=0.1, pos=(-0.5,0), fg=(0,0,0,1))
        self.displayMarioText.hide()
        self.displayTime1=OnscreenText('', scale=0.1, pos=(0.5,0), fg=(0,0,0,1))
        self.displayTime1.hide()
        self.displayAIText=OnscreenText('Yoshi:', scale=0.1, pos=(-0.5,-0.5), fg=(0,0,0,1))
        self.displayAIText.hide()
        self.displayTime2=OnscreenText('Waiting...', scale=0.1, pos=(0.5,-0.5), fg=(0,0,0,1))
        self.displayTime2.hide()
        #Create the frame to be a back drop for pause and pause text
        self.centerBG = DirectFrame(frameColor=(0.941176,0.972549, 1,0.4), frameSize=(-1,1,-1,1), pos=(0,0,0))
        self.centerBG.hide()
        self.pausedInText = OnscreenText("Paused", pos=(0,0,0))
        self.pausedInText.hide()
        self.unPause = OnscreenText("Press p to unpause the game", pos=(0,-0.1,0))
        self.unPause.hide()
        self.resetText = OnscreenText("Press r to reset the game", pos=(0,-0.25,0))
        self.resetText.hide()
        self.resetTextHigh = OnscreenText("Press r to reset the game", pos=(0,0.3,0))
        self.resetTextHigh.hide()

    #Game states are the variables that need to be initialized and used throughout the whole program
    def gameStates(self):
        #Is the character moving
        self.isMoving = False

        self.gameOver = False
        #Used in count collisions
        self.currentCount = 0
        self.collCount = 0
        #Which lap your on
        self.mainLap = 0
        #Used for the collision of the lap plane (tracking laps)
        self.lapPlaneIsInPosition = True
        self.lapTimeCount = 0
        #Used to essentially hide the boxes and then repositioning of boxes
        self.missingBoxPos = (0,0,0)
        self.boxTime = 0
        self.itemBoxInPos = True    
        #Items ready to be used booleans
        self.bananaItem = False
        self.mushroomItem = False
        self.redShellItem = False
        self.greenShellItem = False
        self.megaMushroomItem = False
        #Booleans to have true when the item actions is taking place
        self.greenShellMove = False
        self.marioBig = False
        self.mushroomSpeed = False
        #Created for the shell angle
        self.degree = 30

        #used to re-calibrate the controllaaaaaa
        self.refPoint = 0

        #Main Timer
        self.startTime = globalClock.getDt()
        #track the Time of the AI ending the game
        self.aiEndTime = 0

        #Only initialize this variable if using controlla
        if (self.useControlla):
            try:
                self.ser = serial.Serial('/dev/tty.usbmodem1421',9600)
            except:
                #If they don't have the controlla plugged in, display text and stop game
                self.gameInSession = False
                self.gameBeginning = False
                self.backDrop = DirectFrame(frameColor=(0.941176,0.972549, 1,0.4), frameSize=(-1,1,-1,1), pos=(0,0,0))
                self.plugInText = OnscreenText("Please plug in Controlla (as Drake says)", pos=(0,0,0))
                self.resetText = OnscreenText("Press r to reset the game", pos=(0,-0.25,0))
    

    def terrainCollisionSetup(self):
        #Cite: The Ray terrain Collision for main char. and camera is from roaming-ralph example in Panda3d
        #I then creates my own to keep the ai and the shell level with the terrain
        #Cite URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph

        #First create the rays as a solid Object (setting origin and direction)
        #The Collision Node of the ray with a bitMask to hide rays
        #Create Node Path to the main actor adding the nodes from the solid
        #Start a handler queue to track all the collison traversed node paths
        #Add to the main traverser
        self.marioGroundRay = CollisionRay()
        self.marioGroundRay.setOrigin(0, 0, 9)
        self.marioGroundRay.setDirection(0, 0, -1)
        self.marioGroundCol = CollisionNode('marioRay')
        self.marioGroundCol.addSolid(self.marioGroundRay)
        self.marioGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.marioGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.marioGroundColNp = self.marioActor.attachNewNode(self.marioGroundCol)
        self.marioGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.marioGroundColNp, self.marioGroundHandler)

        self.shellGroundRay = CollisionRay()
        self.shellGroundRay.setOrigin(0, 0, 9)
        self.shellGroundRay.setDirection(0, 0, -1)
        self.shellGroundCol = CollisionNode('shellRay')
        self.shellGroundCol.addSolid(self.shellGroundRay)
        self.shellGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.shellGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.shellGroundColNp = self.greenShellModel.attachNewNode(self.shellGroundCol)
        self.shellGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.shellGroundColNp, self.shellGroundHandler)

        self.aiGroundRay = CollisionRay()
        self.aiGroundRay.setOrigin(0,0,9)
        self.aiGroundRay.setDirection(0,0,-1)
        self.aiGroundCol = CollisionNode('AIRay')
        self.aiGroundCol.addSolid(self.aiGroundRay)
        self.aiGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.aiGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.aiGroundColNp = self.secondRacer.attachNewNode(self.aiGroundCol)
        self.aiGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.aiGroundColNp, self.aiGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0, 0, 9)
        self.camGroundRay.setDirection(0, 0, -1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = self.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

    #CITE: Each "collision setup", I learned how and created it from the panda3d documentation
    #Cite URL: https://www.panda3d.org/manual/index.php/Collision_Handlers
    def wallCollisionSetup(self):
        #Used to have collision with the entire track and objs add to collide with main Char.
        self.pusher = CollisionHandlerPusher()
        
        self.marioActorColl = self.initCollisionSphere(self.marioActor)
        self.secondRacerColl = self.initCollisionSphere(self.secondRacer)
        # Add this object to the pusher
        self.pusher.addCollider(self.marioActorColl[0], self.marioActor)
        # Add this object to the traverser
        base.cTrav.addCollider(self.marioActorColl[0], self.pusher)

    def shellCollisionSetup(self):
        #New traverser to track just the shell's into objects
        self.cTravShell = CollisionTraverser()

        self.pusher.addInPattern('into-%in')

        self.greenShellColl = self.initCollisionSphere(self.greenShellModel)
        self.cTravShell.addCollider(self.greenShellColl[0], self.pusher)
        self.accept('into-' + self.greenShellColl[1], self.collideShell)

    def itemBoxCollisionSetup(self):
        #New traverser to track if char. runs into a box
        self.cTravBox = CollisionTraverser()
        self.itemHandler = CollisionHandlerQueue()

        self.pusher.addInPattern('into-%in')
        self.collCount2 = 0

        allBoxes = [self.itemBox0, self.itemBox1, self.itemBox2,
                    self.itemBox3, self.itemBox4, self.itemBox5,
                    self.itemBox6, self.itemBox7, self.itemBox8,
                    self.itemBox9, self.itemBox10, self.itemBox11]
        #Loop through each and every box - checking the collision
        for num in range(len(allBoxes)):
            name = "boxCol" + str(num)
            self.name = self.initItemBoxSphere(allBoxes[num])
            self.cTravBox.addCollider(self.name[0], self.pusher)
            self.accept('into-' + self.name[1], self.collideBox)

    def lapPlaneCollisionSetup(self):
        #Create new traveres for lap plane
         self.cTravLap = CollisionTraverser()
        #Track if the user exist the plane or crosses the finishing line       
         self.pusher.addInPattern('outof-%in')

        # Make a variable to store the unique collision string count.
         self.collCount = 0
         self.lapPlaneCol = self.initCollisionTube(self.lapPlane)
         self.cTravLap.addCollider(self.lapPlaneCol[0], self.pusher)

         #Accept the events sent by the collisions.
         self.accept('outof-' + self.lapPlaneCol[1], self.collideLap)

    #If the shell has an object collide with it, do this event
    def collideShell(self, collEntry):
        pass

    #Box object has collided into another object (Main Char.)
    def collideBox(self, collEntry):
        for box in self.allBoxObject:
            boxColTitle = "self." + collEntry.getIntoNode().getName()
            if (boxColTitle == box.getTitle()):
                self.boxTime = globalClock.getFrameTime()
                self.missingBoxPos = box.getPos()
                self.itemBoxInPos = False
                box.setPos((0,0,0))

        self.itemBoxChooser()
    #Track if the main char. ran into the lap plane
    def collideLap(self, collEntry):
        #object has collided into another object")
        self.lapTimeCount = globalClock.getFrameTime()
        self.lapPlaneIsInPosition = False
        self.mainLap += 1

    #randomize the objects when runnning into an item box
    def itemBoxChooser(self):
        num = random.randint(1,2)
        # if (num == 1):
        #     self.itemBoxGreenShell.show()
        #     self.greenShellItem = True

        #     self.mushroomItem = False
        #     self.itemBoxMushroom.hide()
        #     self.megaMushroomItem = False
        #     self.itemBoxMegaMushroom.hide()
        if (num == 1):
            self.mushroomItem = True
            self.itemBoxMushroom.show()

            self.greenShellItem = False
            self.itemBoxGreenShell.hide()
            self.megaMushroomItem = False
            self.itemBoxMegaMushroom.hide()
        elif (num == 2):
            self.megaMushroomItem = True
            self.itemBoxMegaMushroom.show()
            
            self.greenShellItem = False
            self.itemBoxGreenShell.hide()
            self.mushroomItem = False
            self.itemBoxMushroom.hide()
        
    #CiteL Each collision object below is created from looking at the Panda3D Documentation
    #Cite URL: https://www.panda3d.org/manual/index.php/Collision_Solids
    def side1CollisionTube(self, obj, show=False):
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius()

        x = center[0]
        y = center [1]
        z = center[2]

        # Create a collision sphere and name it something understandable to track the obj.
        collTubeStr = 'CollisionHull' + str(self.collCount) + "_" + obj.getName()
        self.collCount += 1
        cNode = CollisionNode(collTubeStr)
        cNode.addSolid(CollisionTube(x-(radius/2), y, z, x+(radius/2), y, z, 1))       
        cNodePath = obj.attachNewNode(cNode)

        if show:
            cNodePath.show()
        #Just like the rays, we have to create a nodePath in relation to the solid =
        #NodePaths will be used to go through evetns and handlers
        return (cNodePath, collTubeStr)

    def initCollisionTube(self, obj, show=False):
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius()
      
        x = center[0]
        y = center [1]
        z = center[2]

        collTubeStr = 'CollisionHull' + str(self.collCount) + "_" + obj.getName()
        self.collCount += 1
        cNode = CollisionNode(collTubeStr)
        cNode.addSolid(CollisionTube(x, y-radius, z-.5, x, y+radius, z-.5, 0.5))       
        cNodePath = obj.attachNewNode(cNode)

        if show:
            cNodePath.show()
        #Just like the rays, we have to create a nodePath in relation to the solid =
        #NodePaths will be used to go through evetns and handlers
        return (cNodePath, collTubeStr)

    def initCollisionSphere(self, obj, show=False):
        # Get the size of the object for the collision sphere.
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        x = center[0]
        y = center[1]
        z = center[2]
        #Reduce the sphere size of the main character objects
        radius = (bounds.getRadius()*1)*.6
 
        collSphereStr = 'CollisionHull' + str(self.collCount) + "_" + obj.getName()
        self.collCount += 1
        cNode = CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(Vec3(x, y, z+.25), radius))
 
        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()
        #Just like the rays, we have to create a nodePath in relation to the solid =
        #NodePaths will be used to go through evetns and handlers
        return (cNodepath, collSphereStr)

    def initItemBoxSphere(self, obj, show=False):
        # Get the size of the object for the collision sphere of the item boxes
        bounds = obj.getLoader().getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius() * 1
 
        #Name the itemBox to track in loops which one was collided into
        collSphereStr = 'itemBox' + str(self.collCount-1)
        self.collCount += 1
        cNode = CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(center, radius))
 
        cNodepath = obj.getLoader().attachNewNode(cNode)
        if show:
            cNodepath.show()
        #Just like the rays, we have to create a nodePath in relation to the solid =
        #NodePaths will be used to go through evetns and handlers
        return (cNodepath, collSphereStr)


    def updateTime(self):
        #Before the game there is a 3 sec. delay and during the count down there is a 3 sec delay
        delay = 6
        secTime = globalClock.getFrameTime() - self.startTime - delay
        minTime = secTime/60
        milTime = ((secTime%1)*100)
        if (minTime < 1):
            timeSubtraction = 0
        else:
            timeSubtraction = (60*int(minTime))

        self.runTime.setText("Time: %0.2d:%0.2d:%0.2d" % (minTime, secTime-timeSubtraction, milTime))
        if (secTime > 1.3):
            self.start.hide()
    #Constantly check if the lap plane is in position- tracking the time is needed
    def updateLapPlane(self):
        newTime = globalClock.getFrameTime() - self.lapTimeCount
        if (newTime > 3):
            self.lapPlane.setPos(38,-34,1.7)
            self.lapPlaneIsInPosition = True
        else:
            self.lapPlane.setPos(0,0,0)
                
    def updateAITime(self):
        if (self.aiEndTime != 0):
            delay = 6
            self.aiEndTime = self.aiEndTime - self.startTime - delay
            formatedTime = self.formatTime(self.aiEndTime)
            #Currently Hardcoded as the aiTime (Though this is the correct time he should end)
            aiTime = "00:01:25:58"
            self.displayTime2.setText(aiTime)

    #When the game is in waiting to be in session
    def beforeGameCountDown(self):
        secTime = globalClock.getFrameTime() - self.startTime

        if (self.gameInSession == False):
            self.gameBeginning = True
            if (secTime > 3):
                self.countDownFunc(secTime)

    #Once the game has started to countdown change the images
    def countDownFunc(self, offsetTime):
        firstTime = globalClock.getFrameTime() - offsetTime
        self.currentCount = globalClock.getFrameTime()  - firstTime - 3

        if (self.currentCount <= 1):
            #self.countDown.setText("3")
            self.start.setImage("Images/start/start1.jpg")
        elif(self.currentCount <= 2):
            #self.countDown.setText("2")
            self.start.setImage("Images/start/start2.jpg")
        elif(self.currentCount <= 3):
           # self.countDown.setText("1")
            self.start.setImage("Images/start/start3.jpg")
        elif(self.currentCount > 3):
            #self.countDown.setText("Go")
            self.start.setImage("Images/start/start4.jpg")
            self.gameInSession = True
    #Just like the accept arrow keys, this reads from Arduino serial and allows turns, fwds, etc
    def controlActor(self):
        if (self.useControlla):
            line = self.ser.readline()
        else:
            line = ""
        #In the Arduino Program file, I made the values of the serial read with colons to seperate
        #Each value so I can interpret it 
        listOfCoord = line.split(":")
        #I know the length needs to be 9, other lengths are when it is initializing
        if (len(listOfCoord) == 9):                
            x = listOfCoord[1]
            i = listOfCoord[3]
            g = listOfCoord[5]
            r = listOfCoord[7]

            #x is the current reference point (usually 0) of the center for accel.
            #If all three buttons hit then re-calibrate
            if (int(g) == 1 and int(i) == 1 and int(r) == 1):
                #Initialize Calibration
                self.refPoint = int(float(x))


            #Complicated way of reading the values and interpreting so that we can allow recalibrating
            #The user can move forward within 20 values: Right 10 to 100 and left from 360 to 260
            #Since the recalibrate changes the ref. point it may not always be 0
            #Also note that x values can only be from 0 to 360 (degrees of a circle)
            #Thus a complicated series of if and else statements to account for the above ref. point calibrations

            if (self.refPoint+10 >= 360):
                self.rightOver360 = True
                self.newRefPointRight = (self.refPoint+10) - 360
                self.rightHighOver360 = True
                self.newRightHighPoint = self.newRefPointRight+90
            else:
                self.rightOver360 = False
                self.newRefPointRight = self.refPoint+10
                if (self.newRefPointRight+90>=360):
                    self.rightHighOver360 = True
                    self.newRightHighPoint = (self.newRefPointRight+90) - 360
                else:
                    self.rightHighOver360 = False
                    self.newRightHighPoint = self.newRefPointRight+90
                 
            if (self.rightOver360):
                #always will have rightHighOver 360 to be True
                if (self.newRefPointRight< float(x) < self.newRightHighPoint):
                    #MAKE IT TURN RIGHT
                    self.turningRight = True
                     #MAKE IT TURN RIGHT
                    self.setKey("right", True)
                    self.setKey("left", False)
                else:
                    self.turningRight = False
            else:
                if (self.rightHighOver360):
                    if (self.newRefPointRight< float(x) or float(x)<self.newRightHighPoint):
                        #MAKE IT TURN RIGHT
                        self.turningRight = True
                        #MAKE IT TURN RIGHT
                        self.setKey("right", True)
                        self.setKey("left", False)
                    else:
                        self.turningRight = False
                else:
                    if (self.newRefPointRight< float(x) < self.newRightHighPoint):
                        #MAKE IT TURN RIGHT
                        self.turningRight = True
                        #MAKE IT TURN RIGHT
                        self.setKey("right", True)
                        self.setKey("left", False)
                    else:
                        self.turningRight = False


            if (self.refPoint-10 <= 0):
                self.leftUnder0 = True
                self.newRefPointLeft = (self.refPoint-10) + 360
                self.leftLowUnder0 = True
                self.newLeftLowPoint = self.newRefPointLeft-90
            else:
                self.leftUnder0 = False
                self.newRefPointLeft = self.refPoint-10
                if (self.newRefPointLeft-90<=00):
                    self.leftLowUnder0 = True
                    self.newLeftLowPoint = (self.newRefPointLeft-90) + 360
                else:
                    self.leftLowUnder0 = False
                    self.newLeftLowPoint = self.newRefPointLeft-90
        

            if (self.leftUnder0):
                #always will have leftHighOver 360 to be True
                if (self.newRefPointLeft> float(x) > self.newLeftLowPoint):
                    #MAKE IT TURN Left
                    self.turningLeft = True
                    self.setKey("right", False)
                    self.setKey("left", True)
                else:
                    self.turningLeft = False
            else:
                if (self.leftLowUnder0):
                    if (self.newRefPointLeft> float(x) or float(x)>self.newLeftLowPoint):
                        #MAKE IT TURN Left
                        self.turningLeft = True
                        self.setKey("right", False)
                        self.setKey("left", True)
                    else:
                        self.turningLeft = False
                else:
                    if (self.newRefPointLeft>float(x) > self.newLeftLowPoint):
                        #MAKE IT TURN Left
                        self.turningLeft = True   
                        self.setKey("right", False)
                        self.setKey("left", True)
                    else:
                        self.turningLeft = False

            if (self.turningRight == False and self.turningLeft == False):
                self.notInTurn = True
                #MAKE It not Turn
                self.setKey("right", False)
                self.setKey("left", False)

            #Make it move forward 
            if (int(g) == 1): 
                self.setKey("forward", True)   
            else: 
                self.setKey("forward", False)
            #Make it move in Reverse
            if (int(r) == 1): 
                self.setKey("reverse", True)
            else: 
                self.setKey("reverse", False)
            if (int(i) == 1): 
                self.setKey("item", True)
            else:
                self.setKey("item", False)

    #Cite: Manipulated the roaming ralph code to set my directions and position in correspondence to the set
    #Cite URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
    def moveActor(self):
        elapsed = globalClock.getDt()
        marioCurrentPos = self.marioActor.getPos()

        if self.keyMap["left"]:
            self.prevX = marioCurrentPos[0]
            self.prevY = marioCurrentPos[1]
            self.marioActor.setH(self.marioActor.getH() + 50 * elapsed)
            self.camera.setX(self.camera, +6 * elapsed)
        if self.keyMap["right"]:
            self.prevX = marioCurrentPos[0]
            self.prevY = marioCurrentPos[1]
            self.marioActor.setH(self.marioActor.getH() - 50 * elapsed)
            self.camera.setX(self.camera, -6 * elapsed)
        if self.keyMap["forward"]:
            if self.keyMap["speedFwd"]:
                self.marioActor.setY(self.marioActor, -45 * elapsed)
            else:
                self.marioActor.setY(self.marioActor, -25 * elapsed)
        if self.keyMap["reverse"]:
            self.marioActor.setY(self.marioActor, 25 * elapsed)


        if self.keyMap["item"]:
            #perform whatever the item is
            if (self.mushroomItem):
                self.itemBoxDisplay.show()
                self.itemBoxMushroom.hide()
                #self.performBananaItem()
                self.performMushroomItem()
            elif(self.greenShellItem):
                self.itemBoxDisplay.show()
                self.itemBoxGreenShell.hide()
                self.performGreenShellItem()           
            elif(self.megaMushroomItem):
                self.itemBoxDisplay.show()
                self.itemBoxMegaMushroom.hide()
                self.performMegaMushroomItem()
    #Cite: Directly taken from the romaing-ralph example and modified so the distance keeps up
    #Cite URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
    def cameraMovement(self):
        camvec = self.marioActor.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 5.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 5))
            camdist = 5.0
        if camdist < 2.5:
            self.camera.setPos(self.camera.getPos() - camvec * (2.5 - camdist))
            camdist = 2.5

    #Cite: Checking collision and moving ralph - taken from roaming ralph
    #Cite URL: https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
    def terrainCollision(self):
        startpos = self.marioActor.getPos()
        #When we creating the rays, nodepaths, handler, then we created the queue
        #This queue needs to be sifted through and find values that need to be tracked
        entries = list(self.marioGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.marioActor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.marioActor.setPos(startpos)
 
        #Checking collision and moving camera - taken from roaming ralph
        entries = list(self.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.camera.getZ() < self.marioActor.getZ() + 1.0:
            self.camera.setZ(self.marioActor.getZ() + 1.0)
            
        self.camera.lookAt(self.floater)

    #Cite: Modified the terrain collision above from the roaming ralph example
    def aiTerrainCollision(self):
        aiStartPos = self.secondRacer.getPos()
        entries = list (self.aiGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
       
        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.secondRacer.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.secondRacer.setPos(aiStartPos)   

    #Cite: Creating the AI. Used the documentation from the Panda3D tutorial
    #Cite URL: https://www.panda3d.org/manual/index.php/Getting_Started
    def settingAI(self):
        self.secondRacer.loop("run")

        #First I'll create the Ai world
        self.aiWorld = AIWorld(render)
        if (self.useControlla):
            self.aiChar = AICharacter("secondRacer", self.secondRacer, 11.2, 0.05, 10)
        else:
            self.aiChar = AICharacter("secondRacer", self.secondRacer, 20, 0.05, 10)
        self.aiWorld.addAiChar(self.aiChar)
        self.aiBehaviors = self.aiChar.getAiBehaviors()

        #Path follow - in reverse
        self.aiBehaviors.pathFollow(1)
        for lap in range(12):
                
             for num in range(len(self.aiPositions)-1,0,-1):
                newNodePos = self.aiPositions[num]
                self.aiBehaviors.addToPath(newNodePos)

        self.aiBehaviors.startFollow()
    #Created an AI of the main character after the game ended to continue to go around the track
    def makeActorMove(self):
        self.newAIWorld = AIWorld(render)
        self.newAIChar = AICharacter("marioActor", self.marioActor, 20, 0.05, 10)
        self.newAIWorld.addAiChar(self.newAIChar)
        self.newAIBehaviors = self.newAIChar.getAiBehaviors()

        #Path follow - in reverse
        self.newAIBehaviors.pathFollow(1)
        for lap in range(9):
            for num in range(len(self.aiPositions)-1,0,-1):
                newNodePos = self.aiPositions[num]
                self.newAIBehaviors.addToPath(newNodePos)

        self.newAIBehaviors.startFollow()

    def updateEndAI(self):
        self.newAIWorld.update()

    #to update the AIWorld    
    def updateAI(self):
        self.aiWorld.update()

    def loadModels(self):
        #Initialize Track
        self.track = self.loader.loadModel("All_Tracks/luigi_circuit")
        self.track.setScale(1.5)
        self.track.reparentTo(render)

        #Finish Line 
        self.lapPlane = self.loader.loadModel("models/lapPlane")
        self.lapPlane.setPos(38,-34,1.7)
        self.lapPlane.reparentTo(render)
        self.lapPlane.hide()

        #Adding Track
        self.side1 = self.loader.loadModel("models/side1")
        self.side1.setPos(30,-30,1.5)
        self.side1.reparentTo(render)
        self.side1.hide()
        
        #Adding MysteryBox
        self.itemBoxPlaces = [(30, -31.5, 1.2), (30, -30, 1.2), (30, -28.5, 1.2),
                         (-0.5, -15, 2.7), (1, -15, 2.7), (2.5, -15, 2.7),
                         (9, 23.5, 4.7), (7.5, 22, 4.7), (6, 20.5, 4.7),
                         (78, -16, 2.7), (79.5,-16, 2.7),(81, -16, 2.7)]

        self.allBoxObject = []
        self.itemBox0 = itemBox(self.itemBoxPlaces[0], "self.itemBox0")
        self.allBoxObject.append(self.itemBox0)
        self.itemBox1 = itemBox(self.itemBoxPlaces[1], "self.itemBox1")
        self.allBoxObject.append(self.itemBox1)
        self.itemBox2 = itemBox(self.itemBoxPlaces[2], "self.itemBox2")
        self.allBoxObject.append(self.itemBox2)
        self.itemBox3 = itemBox(self.itemBoxPlaces[3], "self.itemBox3")
        self.allBoxObject.append(self.itemBox3)
        self.itemBox4 = itemBox(self.itemBoxPlaces[4], "self.itemBox4")
        self.allBoxObject.append(self.itemBox4)
        self.itemBox5 = itemBox(self.itemBoxPlaces[5], "self.itemBox5")
        self.allBoxObject.append(self.itemBox5)
        self.itemBox6 = itemBox(self.itemBoxPlaces[6], "self.itemBox6")
        self.allBoxObject.append(self.itemBox6)
        self.itemBox7 = itemBox(self.itemBoxPlaces[7], "self.itemBox7")
        self.allBoxObject.append(self.itemBox7)
        self.itemBox8 = itemBox(self.itemBoxPlaces[8], "self.itemBox8")
        self.allBoxObject.append(self.itemBox8)
        self.itemBox9 = itemBox(self.itemBoxPlaces[9], "self.itemBox9")
        self.allBoxObject.append(self.itemBox9)
        self.itemBox10 = itemBox(self.itemBoxPlaces[10], "self.itemBox10")
        self.allBoxObject.append(self.itemBox10)
        self.itemBox11 = itemBox(self.itemBoxPlaces[11], "self.itemBox11")
        self.allBoxObject.append(self.itemBox11)

        #Add Boxes to the item display list
        self.itemBoxDisplay = OnscreenImage(image = "Images/BoxDisplay.jpg", scale=(.1), pos=(-1.2,-1,-.88))
        #self.itemBoxDisplay.hide()
        self.itemBoxRedShell = OnscreenImage(image = "Images/RedShellItem.jpg", scale=(.1), pos=(-1.2,-1, -.88))
        self.itemBoxRedShell.hide()
        self.itemBoxMushroom = OnscreenImage(image = "Images/mushroomItem.jpg", scale=(.1), pos=(-1.2,-1, -.88))
        self.itemBoxMushroom.hide()
        self.itemBoxBanana = OnscreenImage(image = "Images/bananaItem.jpg", scale=(.1), pos=(-1.2,-1, -.88))
        self.itemBoxBanana.hide()
        self.itemBoxGreenShell = OnscreenImage(image = "Images/greenShellItem.jpg", scale=(.1), pos=(-1.2,-1, -.88))
        self.itemBoxGreenShell.hide()
        self.itemBoxMegaMushroom = OnscreenImage(image = "Images/megaMushroomItem.jpg", scale=(.1), pos=(-1.2,-1, -.88))
        self.itemBoxMegaMushroom.hide()

        self.bananaModel = self.loader.loadModel("models/bananaModel")
        self.bananaModel.setScale(.03)
        self.bananaModel.setPos(38,-31,2)
        self.bananaModel.reparentTo(render)
        self.bananaModel.hide()
        
        self.greenShellModel = self.loader.loadModel("models/greenShellModel")
        self.greenShellModel.setScale(.004)
        self.greenShellModel.setPos(38,-31,2)
        self.greenShellModel.reparentTo(render)
        self.greenShellModel.hide()

        #Intitial where Mario needs to be
        marioStartPos = Vec3(50, -29, 2.5) #Actual start possition for Luigi_Circuit

        #Using ralph because the model is made with correct collision masking and animation
        self.marioActor = Actor("models/marioKart") 
        self.marioActor.setScale(.3)
        self.marioActor.setH(self.marioActor, 270)
        self.marioActor.reparentTo(self.render)
        self.marioActor.setPos(marioStartPos)

        # AI Character
        secRacerPos = Vec3(50, -30, .7)
        self.secondRacer = Actor("models/yoshiKart")
        self.secondRacer.setScale(0.3)
        self.secondRacer.setH(self.secondRacer, 270)
        self.secondRacer.reparentTo(self.render)
        self.secondRacer.setPos(secRacerPos)
        #Each nodes' specific positions for the luigi_circuit
        self.aiPositions = [( 31,-30,  1),(  9,-30,1.5),( 3,-25,1.5),
                     (-10, 15,  5),(  3, 25,  5), (  9, 25, 5),
                     ( 40, -4,0.8),( 49, -9,0.8), (58, -6, 0.82),
                     ( 65, -6,1.4),( 72, -9, 1.5),( 73, -9, 1.7),
                     ( 74, -9, 2.3),( 75, -9, 2.4),( 79, -9,2.5),
                     ( 81.5,-16,2.5),( 78,-29,2.5),
                     ( 68,-36,2.5),(66,-35,2.4), ( 54,-33,0.8),
                     ( 37,-31,0.7)  ]
        
        #Create the AI and draw the nodes - path for the AI
        for num in range(len(self.aiPositions)):
            name = "target"+str(num)
            self.name = loader.loadModel("models/arrow")
            self.name.setColor(1,0,0)
            self.name.setPos(self.aiPositions[num])
            self.name.setScale(1)
            self.name.reparentTo(render)
            self.name.hide()


#Class to create every item box - loading thema nd receiving certain information from them
class itemBox(object):
    def __init__(self, pos, boxName):
        self.boxName = boxName
        self.pos = pos
        self.name = loader.loadModel('models/itemBox')
        self.name.reparentTo(render)
        self.name.setScale(0.4)
        self.name.setPos(self.pos)

    def getLoader(self):
        return self.name

    def getTitle(self):
        return self.boxName

    def setPos(self, newPos):
        self.name.setPos(newPos)
    def getPos(self):
        return self.pos

    def resetPos(self):
        self.name.setPos(self.pos)


base.run()




