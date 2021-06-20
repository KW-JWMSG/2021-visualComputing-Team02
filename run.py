from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3c

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

import cv2 as cv
import numpy as np
import math

from VideoClass import VideoClass
from ActorClass import ActorClass

class FinalCode:
    def __init__(self):
        self.video = VideoClass()
        self.frame_w, self.frame_h = self.video.getVideoSize()
        self.aspect = self.frame_w / self.frame_h
        self.tex = self._newTexture()
        self.base = self._newBase()
        self.arucoSquareSize = 40 #mm
        self.patternPoints = self._newPatternPoints()
        self.arucoDict = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_50)
        self.arucoParams = cv.aruco.DetectorParameters_create()
        self.textObject = OnscreenText(text="", pos=(self.aspect - 0.05, -0.95), scale=(0.07, 0.07), fg=(1, 0.5, 0.5, 1), align=p3c.TextNode.A_right, mayChange=1)
        self.textObject.reparentTo(self.base.aspect2d)
        self.actor_1 = ActorClass(1,self.base)
        self.actor_4 = ActorClass(4,self.base)
        self.actor_5 = ActorClass(5,self.base)

        self.base.taskMgr.add(self._updateBase, 'video frame update1')
        pass

    def _newTexture(self):
        tex = p3c.Texture()
        tex.setup2dTexture(self.frame_w, self.frame_h, p3c.Texture.T_unsigned_byte, p3c.Texture.F_rgb)
        return tex


    def _newBase(self):
        
        base = ShowBase()
        base.disableMouse()
        winProp = p3c.WindowProperties()
        winProp.setSize(self.frame_w, self.frame_h)
        base.win.requestProperties(winProp)
        background = OnscreenImage(image=self.tex) # Load an image object
        background.reparentTo(base.render2dp)
        # We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering.
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)

        return base

    def _newPatternPoints(self):
        pattern_size = (2, 2)
        pattern_points = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
        pattern_points *= self.arucoSquareSize
        return pattern_points

    def _drawCorner(self,frame,corners):
        intrisic_mtx = self.video.getIntrisicMtx()
        (topLeft, topRight, bottomRight, bottomLeft) = corners
        axis = np.float32([[self.arucoSquareSize,0,0], [0,self.arucoSquareSize,0], [0,0,self.arucoSquareSize]]).reshape(-1,3)
        ret, rvecs, tvecs = cv.solvePnP(self.patternPoints, 
                                                np.asarray([topLeft, topRight, bottomLeft, bottomRight]).reshape(-1, 2), 
                                                    intrisic_mtx, None)
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, intrisic_mtx, None)
        cv.line(frame, tuple(topLeft.ravel().astype(int)), tuple(imgpts[0].ravel().astype(int)), (0,0,255), 5) # X
        cv.line(frame, tuple(topLeft.ravel().astype(int)), tuple(imgpts[1].ravel().astype(int)), (0,255,0), 5) # Y
        cv.line(frame, tuple(topLeft.ravel().astype(int)), tuple(imgpts[2].ravel().astype(int)), (255,0,0), 5) # Z

        return rvecs, tvecs
    
    def _getMatView(self, rvecs, tvecs):
        rmtx = cv.Rodrigues(rvecs)[0]
        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0]],
                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1]],
                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2]],
                                [0.0       ,0.0       ,0.0       ,1.0    ]])
        
        inverse_matrix = np.array([[ -1.0, +1.0, -1.0, 1.0],
                                [+1.0,-1.0,+1.0,-1.0],
                                [+1.0,-1.0,+1.0,-1.0],
                                [ 1.0, 1.0, 1.0, 1.0]])
        view_matrix = view_matrix * inverse_matrix
        view_matrix = np.transpose(view_matrix)


        return p3c.LMatrix4(view_matrix[0][0],view_matrix[0][1],view_matrix[0][2],view_matrix[0][3],
                view_matrix[1][0],view_matrix[1][1],view_matrix[1][2],view_matrix[1][3],
                view_matrix[2][0],view_matrix[2][1],view_matrix[2][2],view_matrix[2][3],
                view_matrix[3][0],view_matrix[3][1],view_matrix[3][2],view_matrix[3][3])

    def _drawActor(self,actor,frame,corners):
        rvecs, tvecs = self._drawCorner(frame,corners)
        matview = self._getMatView(rvecs, tvecs)
        matview.invertInPlace()

        cam_pos = matview.xformPoint(p3c.LPoint3(0, 0, 0))
        cam_view = matview.xformVec(p3c.LVector3(0, 0, -1))
        cam_up = matview.xformVec(p3c.LVector3(0, 1, 0))
        intrisic_mtx = self.video.getIntrisicMtx()
        fov_x = 2 * math.atan(self.frame_w/(2 * intrisic_mtx[0][0])) * 180 / math.pi
        fov_y = 2 * math.atan(self.frame_h/(2 * intrisic_mtx[1][1])) * 180 / math.pi

        camera = actor.getCamera()
        camLens = camera.getNode(0).getLens(0)

        camera.setPos(cam_pos)
        camera.lookAt(cam_pos + cam_view, cam_up)

        camLens.setNearFar(10, 10000)
        camLens.setFov(fov_x, fov_y)

        actor.show()
        pass

    def _updateBase(self, task):
        self.textObject.setText("No AR Marker Detected")
        success, frame = self.video.read()
        if not success:
            self.textObject.setText("Video Image Error")
            return task.cont 

        # hide all actors
        self.actor_1.hide()
        self.actor_4.hide()
        self.actor_5.hide()

        (corners, ids, rejected) = cv.aruco.detectMarkers(frame, self.arucoDict, parameters=self.arucoParams)
        detactedID = []
        if len(corners) > 0:
            ids = ids.flatten()
            for markerCorner, markerID in zip(corners, ids):
                detactedID.append(markerID)
                corners = markerCorner.reshape((4, 2))

                if markerID == 1:
                    self._drawActor(self.actor_1,frame,corners)
                if markerID == 4:
                    self._drawActor(self.actor_4,frame,corners)
                if markerID == 5:
                    self._drawActor(self.actor_5,frame,corners)

        self.textObject.setText("[INFO] ArUco marker ID: %s"%(str(detactedID)))
        

        frame = cv.flip(frame, 0)
        self.tex.setRamImage(frame)
        return task.cont


    def runbase(self):
        self.base.run()

def main():
    final = FinalCode()
    final.runbase()


if __name__ == "__main__":
    # execute only if run as a script
    main()