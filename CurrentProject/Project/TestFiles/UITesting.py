from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask
from pandac.PandaModules import Vec3,Vec4,BitMask32
from direct.actor.Actor import Actor
import random
import sys
import os
import math
#Needed for accelerometer 
import serial

from Tkinter import *

####################################
# init
####################################
def init(data):
    # There is only one init, not one-per-mode
    data.mode = "titleScreen"
    data.cx = data.width/2
    data.cy = data.height/2
    data.playRect = button(data.cx-80,data.cy-40,
                                    data.cx+80,data.cy+40,"Play")
    data.backToTitle = button(20,20,80,40,"Back")
    data.course1 = button(data.cx-80,data.cy-40,
                                    data.cx+80,data.cy+40,"Course 1")
    data.backToCourses = button(20,20,80,40,"Back")
    data.playScreen = button(data.cx-80,data.cy-40,
                                    data.cx+80,data.cy+40,"Character 1")

####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "titleScreen"): titleScreenMousePressed(event, data)
    elif (data.mode == "courseScreen"):   courseScreenMousePressed(event, data)
    elif (data.mode == "charScreen"):  charScreenMousePressed(event, data)
    elif (data.mode == "playScreen"):  playScreenMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "titleScreen"): titleScreenKeyPressed(event, data)
    elif (data.mode == "courseScreen"):   courseScreenKeyPressed(event, data)
    elif (data.mode == "charScreen"):  charScreenKeyPressed(event, data)
    elif (data.mode == "playScreen"):  playScreenKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "titleScreen"): titleScreenTimerFired(data)
    elif (data.mode == "courseScreen"):   courseScreenTimerFired(data)
    elif (data.mode == "charScreen"):  charScreenTimerFired(data)
    elif (data.mode == "playScreen"):  playScreenTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "titleScreen"): titleScreenRedrawAll(canvas, data)
    elif (data.mode == "courseScreen"):   courseScreenRedrawAll(canvas, data)
    elif (data.mode == "charScreen"):  charScreenRedrawAll(canvas, data)
    elif (data.mode == "playScreen"):  playScreenRedrawAll(canvas, data)

####################################
# Title Screen mode
####################################

def titleScreenMousePressed(event, data):

    if (data.playRect.buttonSelected(event.x,event.y)):
        data.mode = "courseScreen"

def titleScreenKeyPressed(event, data):
    pass

def titleScreenTimerFired(data):
    pass

def titleScreenRedrawAll(canvas, data):
    data.playRect.drawButton(canvas)
    canvas.create_text(data.cx, data.cy/2, text="Mario Kart")
    
####################################
# Course Screen mode
####################################

def courseScreenMousePressed(event, data):
    if (data.backToTitle.buttonSelected(event.x,event.y)):
        data.mode = "titleScreen"
    elif (data.course1.buttonSelected(event.x,event.y)):
        data.mode = "charScreen"

def courseScreenKeyPressed(event, data):
    pass

def courseScreenTimerFired(data):
    pass

def courseScreenRedrawAll(canvas, data):
    canvas.create_text(data.cx, 20,
                       text="Courses", font="Arial 26 bold", anchor=N)
    data.backToTitle.drawButton(canvas)
    #Draw all the courses using FilePaths and titles
    #Incorporate the scrolling
    data.course1.drawButton(canvas)


####################################
# Character Screen mode
####################################

def charScreenMousePressed(event, data):
    if (data.backToCourses.buttonSelected(event.x,event.y)):
        data.mode = "courseScreen"
    elif (data.playScreen.buttonSelected(event.x,event.y)):
        moveMario()
def charScreenKeyPressed(event, data):
    pass

def charScreenTimerFired(data):
    pass

def charScreenRedrawAll(canvas, data):
    canvas.create_text(data.cx, 20,
                       text="Characters", font="Arial 26 bold", anchor=N)
    data.backToCourses.drawButton(canvas)
    #Draw all the Characters using FilePaths and titles
    #Incorporate the scrolling
    data.playScreen.drawButton(canvas)

####################################
# Play Screen mode
####################################

def playScreenMousePressed(event, data):
    pass

def playScreenKeyPressed(event, data):
    if (event.keysym == 'q'):
        data.mode = "titleScreen"

def playScreenTimerFired(data):
    pass

def playScreenRedrawAll(canvas, data):
    canvas.create_text(10, 10,
                       text="Press 'q' to quit!", font="Arial 10", anchor=NW)
    
####################################
# use the run function as-is
####################################

def run(width=600, height=600):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

#Rishav Dutta's Idea to make a button Class
#My Code
class button(object):
    def __init__(self, x0,y0,x1,y1, text):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text

    def buttonSelected(self, x, y):
        if ((self.x0<=x<=self.x1) and (self.y0<=y<=self.y1)):
            return True
        else:
            return False

    def drawButton(self, canvas):
        canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1)
        canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2, 
                                                text=self.text)

class moveMario(ShowBase):

    def __init__(self):

        # Set up the window, camera, etc.
        ShowBase.__init__(self)
        self.ser = serial.Serial('/dev/tty.usbmodem1421',9600)
        # Set the background color to black
        self.win.setClearColor((0, 0, 0, 1))

        # This is used to store which keys are currently pressed.
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "reverse": 0, "cam-left": 0, "cam-right": 0}

        #Initialize Track
        self.track = self.loader.loadModel("luigi_circuit")
        self.track.setScale(1.5)
        self.track.reparentTo(render)
    
        #Intitial where Mario needs to be
        #marioStartPos = self.track.find("**/start_point").getPos()
        marioStartPos = Vec3(50, -29, 0.35) #Actual start possition
        #Using ralph because the model is made with correct collision masking and animation
        self.marioActor = Actor("models/ralph",
                                {"run": "models/ralph-run",
                                 "walk": "models/ralph-walk"})
        self.marioActor.setScale(0.1,0.1,0.1)
        self.marioActor.setH(self.marioActor, 270)
        self.marioActor.reparentTo(self.render)
        self.marioActor.setPos(marioStartPos + (0, 0, 0.5))

        #Floater above so Camera has something to look at
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.marioActor)
        self.floater.setZ(2.0)

        taskMgr.add(self.move, "moveTask")
        # Game state variables
        self.isMoving = False

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(self.marioActor.getX()+100, self.marioActor.getY(), 1)

        #Collision Rays
        self.cTrav = CollisionTraverser()

        self.marioGroundRay = CollisionRay()
        self.marioGroundRay.setOrigin(0, 0, 9)
        self.marioGroundRay.setDirection(0, 0, -1)
        self.marioGroundCol = CollisionNode('marioRay')
        self.marioGroundCol.addSolid(self.marioGroundRay)
        self.marioGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.marioGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.marioGroundColNp = self.marioActor.attachNewNode(self.marioGroundCol)
        self.marioGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.marioGroundColNp, self.marioGroundHandler)
       
        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0, 0, 9)
        self.camGroundRay.setDirection(0, 0, -1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = self.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)



    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value


    def move(self, task):

        elapsed = globalClock.getDt()
        # If a move-key is pressed, move Mario in the specified direction.
        startpos = self.marioActor.getPos()

        line = self.ser.readline()
        listOfCoord = line.split(":")
        if (len(listOfCoord) == 7):                
            x = listOfCoord[1]
            g = listOfCoord[3]
            r = listOfCoord[5]
    
            if (10<=float(x)<=180):
                #MAKE IT TURN RIGHT
                self.setKey("right", True)
                
                self.setKey("left", False)
                
            elif (180<float(x)<=350):
                #MAKE IT TURN LEFT
                self.setKey("right", False)
                self.setKey("left", True)
            else:
                self.setKey("right", False)
                self.setKey("left", False)

            #Make it move forward 
            if (int(g) == 1): self.setKey("forward", True)   
            else: self.setKey("forward", False)
            #Make it move in Reverse
            if (int(r) == 1): self.setKey("reverse", True)
            else: self.setKey("reverse", False)



        if self.keyMap["left"]:
            self.marioActor.setH(self.marioActor.getH() + 50 * elapsed)
            self.camera.setX(self.camera, +5 * elapsed)
        if self.keyMap["right"]:
            self.marioActor.setH(self.marioActor.getH() - 50 * elapsed)
            self.camera.setX(self.camera, -5 * elapsed)
        if self.keyMap["forward"]:
            self.marioActor.setY(self.marioActor, -100 * elapsed)
        if self.keyMap["reverse"]:
            self.marioActor.setY(self.marioActor, 100 * elapsed)


        #When moving - run the animation - Taken from roaming ralph example
        if self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"]:
            if self.isMoving is False:
                self.marioActor.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.marioActor.stop()
                self.marioActor.pose("walk", 5)
                self.isMoving = False

        #Camera uses - modified from roaming ralph
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

        #Collission terrain checking - taken from roaming ralph
        entries = list(self.marioGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.marioActor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.marioActor.setPos(startpos)

        # Keep the camera at level - taken from roaming ralph
        entries = list(self.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.camera.getZ() < self.marioActor.getZ() + 1.0:
            self.camera.setZ(self.marioActor.getZ() + 1.0)
            
        self.camera.lookAt(self.floater)

        return task.cont


run(600, 600)