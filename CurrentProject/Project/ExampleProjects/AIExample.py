import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *
 
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
        # Target1
        self.target1 = loader.loadModel("models/arrow")
        self.target1.setColor(1,0,0)
        self.target1.setPos(10,-10,0)
        self.target1.setScale(1)
        self.target1.reparentTo(render)
        # Target2
        self.target2 = loader.loadModel("models/arrow")
        self.target2.setColor(0,1,0)
        self.target2.setPos(10,10,0)
        self.target2.setScale(1)
        self.target2.reparentTo(render)
        # Target3
        self.target3 = loader.loadModel("models/arrow")
        self.target3.setColor(0,0,1)
        self.target3.setPos(-10,10,0)
        self.target3.setScale(1)
        self.target3.reparentTo(render)
        # Target4
        self.target4 = loader.loadModel("models/arrow")
        self.target4.setColor(1,0,1)
        self.target4.setPos(-10,-10,0)
        self.target4.setScale(1)
        self.target4.reparentTo(render)
 
        self.seeker.loop("run")
 
    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
 
        self.AIchar = AICharacter("seeker",self.seeker, 60, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        #Path follow (note the order is reveresed)
        self.AIbehaviors.pathFollow(1)
        self.AIbehaviors.addToPath(self.target4.getPos())
        self.AIbehaviors.addToPath(self.target3.getPos())
        self.AIbehaviors.addToPath(self.target2.getPos())
        self.AIbehaviors.addToPath(self.target1.getPos())
 
        self.AIbehaviors.startFollow()
 
        #AI World update
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()            
        return Task.cont
 
w = World()
run()