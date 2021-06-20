import panda3d.core as p3c
from direct.actor.Actor import Actor
from panda3d.core import NodePath
from panda3d.core import Camera
class ActorClass :
    def __init__(self, ID, base):
        self.ID = ID
        self.base = base

        self.render = NodePath("render_"+str(ID))

        baseRegion = base.camNode.getDisplayRegion(0)
        baseRegion.setActive(0)
        baseResionWind = baseRegion.getWindow()

        self.region = baseResionWind.makeDisplayRegion()
        self.region.setSort(baseRegion.getSort())

        self.camNode = Camera("cam_"+str(ID))
        self.myCam = NodePath(self.camNode)
        self.myCam.setName("camera_"+str(ID))
        self.region.setCamera(self.myCam)

        self.myCam.reparentTo(self.render)
        # self.render.reparentTo(base.render)
        
        self._setActor()
    
    def _setActor(self):
        actor = None
        if self.ID == 1:
            actor = Actor("models/panda-model",
                                        {"walk": "models/panda-walk4"})
            actor.loop("walk")
            lMinPt, lMaxPt = p3c.Point3(), p3c.Point3()
            actor.calcTightBounds(lMinPt, lMaxPt)
            m_os2ls = p3c.LMatrix4.scaleMat(1/10, 1/10, 1/10)
            actor.setMat(m_os2ls)
            actor.setColor((1,0.5,0.5,1))
                
        elif self.ID == 4:
            # actor2
            actor = Actor('panda.egg')
            lMinPt, lMaxPt = p3c.Point3(), p3c.Point3()
            actor.calcTightBounds(lMinPt, lMaxPt)
            m_os2ls = p3c.LMatrix4.scaleMat(5, 5, 5)
            actor.setMat(m_os2ls)
            actor.setColor((0.5,0.5,1,1))

        
        elif self.ID == 5:
            # actor3
            actor = Actor('smiley.egg')
            lMinPt, lMaxPt = p3c.Point3(), p3c.Point3()
            actor.calcTightBounds(lMinPt, lMaxPt)
            m_os2ls = p3c.LMatrix4.scaleMat(30, 30, 30)
            actor.setMat(m_os2ls)
            actor.setColor((0.5,1,0.5,1))

        actor.reparentTo(self.render)

        self.actor = actor
        return actor

    def getCamera(self):
        return self.myCam

    def getActor(self):
        return self.actor
      
    def show(self):
        self.actor.show()

    def hide(self):
         self.actor.hide()