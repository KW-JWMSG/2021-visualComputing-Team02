import numpy as np
import cv2 as cv

VIDEO_CAPTURE_ID = 1

class CamCalibration:
    def __init__(self):
        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objp  = np.zeros((10*7,3), np.float32)
        self.objp [:,:2] = np.mgrid[0:10,0:7].T.reshape(-1,2)

        self.objpoints = [] # 3d point in real world space
        self.imgpoints = [] # 2d points in image plane.

        
    
    def startCal(self):
        vidcap = cv.VideoCapture(VIDEO_CAPTURE_ID) 
        if not vidcap.isOpened():
            raise IOError("Cannot open webcam")

        while len(self.imgpoints) < 15:
            success, frame = vidcap.read()
            gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (10,7),None)
            if ret == True:
                corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),self.criteria)
                self.objpoints.append(self.objp)
                self.imgpoints.append(corners2)
                frame = cv.drawChessboardCorners(frame, (10,7), corners2,ret)
                self.imgsize = frame.shape[:-1]
            cv.imshow('img',frame)
            key = cv.waitKey(500)
            if(key == 113):
                break
        cv.destroyAllWindows()
    def saveFile(self):
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(self.objpoints, self.imgpoints, self.imgsize ,None,None)
        np.savez('cam_param.npz',ret=ret,mtx=mtx,dist=dist,rvecs=rvecs,tvecs=tvecs)


def main():
    calb = CamCalibration()
    calb.startCal()
    calb.saveFile()


if __name__ == "__main__":
    # execute only if run as a script
    main()