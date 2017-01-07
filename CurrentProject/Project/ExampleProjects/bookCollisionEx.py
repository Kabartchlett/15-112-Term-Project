import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *


class World(DirectObject):
	def __init__(self):
		self.colNode1 = CollisionNode('colNode1')
		colSphere1 = CollisionSphere(4.1,30,0,1)
		self.colNode1.addSolid(colSphere1)
		self.colNP1 = render.attachNewNode(self.colNode1)
		self.colNP1.show()

		self.colNode2 = CollisionNode('colNode2')
		colSphere2 = CollisionSphere(0,30,0,1)
		self.colNode2.addSolid(colSphere2)
		self.colNP2 = render.attachNewNode(self.colNode2)
		self.colNP2.show()

		self.cTrav = CollisionTraverser()
		self.cHan = CollisionHandlerQueue()
		self.cTrav.addCollider(self.colNP1, self.cHan)

		self.accept('a', self.move, extraArgs = [-0.5])
		self.accept('d', self.move, extraArgs = [0.5])
		taskMgr.add(self.checkCollisions, "Check Collisions")

	def move(self, dir):
		self.colNP1.setX(self.colNP1, dir)

	def checkCollisions(self, task):
		self.cTrav.traverse(render)
		print(self.cHan.getNumEntries())
		return task.again

w = World()
w.run()