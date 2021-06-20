import cv2 as cv
import numpy as np

VIDEO_CAPTURE_ID = 1

class VideoClass:

    def __init__(self, calb_npz="cam_param.npz"):
        self.vidcap = cv.VideoCapture(VIDEO_CAPTURE_ID)
        if not self.vidcap.isOpened():
            raise IOError("Cannot open webcam")
        self._setCalb(calb_npz)
        
    def _setCalb(self,calb_npz=None):
        if(calb_npz is not None):
            try:
                self.calb_npz = np.load(calb_npz)
            except FileNotFoundError:
                print("calb npz file can not found!!")
                self.calb_npz = None
    
    def getVideoSize(self):
        if self.calb_npz is None:
            frame_w = int(self.vidcap.get(cv.CAP_PROP_FRAME_WIDTH))
            frame_h = int(self.vidcap.get(cv.CAP_PROP_FRAME_HEIGHT))
            return frame_w, frame_h
        else:
            success, frame = self.read()
            frame_h = len(frame)
            frame_w = len(frame[0])
            return frame_w, frame_h

    def read(self):
        success, frame = self.vidcap.read()
        if( self.calb_npz is not None):
            intrisicMtx = self.getIntrisicMtx()
            distCoefs = self.getDistCoefs()
            newcameraMtx, roi = self.getNewCameraMtx()
            dst = cv.undistort(frame,intrisicMtx,distCoefs,None,newcameraMtx)
            x,y,w,h = roi
            dst = dst[y:y+h,x:x+w]
            return success, dst
        else:
            return success, frame
    
    def getIntrisicMtx(self):
        return self.calb_npz['mtx']
    def getDistCoefs(self):
        return self.calb_npz['dist']
    def getNewCameraMtx(self):
        frame_w = int(self.vidcap.get(cv.CAP_PROP_FRAME_WIDTH))
        frame_h = int(self.vidcap.get(cv.CAP_PROP_FRAME_HEIGHT))
        intrisicMtx = self.getIntrisicMtx()
        distCoefs = self.getDistCoefs()
        newcameraMtx, roi = cv.getOptimalNewCameraMatrix(intrisicMtx,distCoefs,(frame_w,frame_h),1,(frame_w,frame_h))
        return newcameraMtx, roi

def main():
    vid = VideoClass(calb_npz="cam_param.npz")
    while True:
        success, frame = vid.read()
        cv.imshow('test',frame)
        key = cv.waitKey(10)
        if(key == 113):
            break


if __name__ == "__main__":
    # execute only if run as a script
    main()