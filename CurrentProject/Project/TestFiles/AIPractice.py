import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask
from pandac.PandaModules import Vec3,Vec4,BitMask32
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import *
from panda3d.ai import *
import random
import sys
import os
import math
#Needed for accelerometer 
import serial


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

class World(DirectObject):
 
    def __init__(self):
        base.disableMouse()
        base.cam.setPosHpr(0,0,55,0,-90,0)
 
        self.loadModels()
        self.setAI()
 
    def loadModels(self):
        # Seeker
        ralphStartPos = Vec3(-10, 0, 0)
        self.seeker = Actor("models/ralph",
                                 {"run":"models/ralph-run"})
        self.seeker.reparentTo(render)
        self.seeker.setScale(0.5)
        self.seeker.setPos(ralphStartPos)
        # Target
        self.target = loader.loadModel("models/arrow")
        self.target.setColor(1,0,0)
        self.target.setPos(10,5,0)
        self.target.setScale(1)
        self.target.reparentTo(render)
 
    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
 
        self.AIchar = AICharacter("seeker",self.seeker, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        self.AIbehaviors.seek(self.target)
        self.seeker.loop("run")
 
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()            
        return Task.cont

demo = World()
run()


