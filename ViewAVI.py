#!/usr/bin/env python
import cv2
import os

fnum = 1
record = True
finished = False
ix = -1
iy = -1
upLeft = (0, 0)
lowRight = (0, 0)
tempLeft = (0, 0)

# mouse click event handler
def onMouse(event, x, y, flags, param):
    global record, finished, ix, iy, upLeft, lowRight, tempLeft
    if event == cv2.cv.CV_EVENT_LBUTTONDOWN:
        tempLeft = (x, y)
    elif event == cv2.cv.CV_EVENT_LBUTTONUP:
        lowRight = (x, y)
        upLeft=tempLeft
    elif event == cv2.cv.CV_EVENT_RBUTTONUP:
        finished = True


# main loop
def main():
    global record, finished, fnum, wid, ht

    print 'working in ', os.getcwd()
    fname = raw_input('Video file name ')
    print 'file exists? ', os.path.isfile(fname)

    cameraCapture = cv2.VideoCapture(fname)
    cv2.namedWindow(fname)
    cv2.setMouseCallback(fname, onMouse)

    # setup for outputing an .avi movie
    fps = 10
    avisize = (int(cameraCapture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
               int(cameraCapture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
    wid, ht = avisize
    videoWriter = cv2.VideoWriter('BirdCount.avi',
                                  cv2.cv.CV_FOURCC('I', '4', '2', '0'), fps, avisize)

    # show first frame of input video, then select "sensing" rectangle with center mouse button
    success, frame = cameraCapture.read()
    cv2.putText(frame, 'Select Watch Rectangle with Left Mouse Button', (60, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 250, 250), 2)
    cv2.imshow(fname, frame)
    record = False
    finished = False
    print ('Select Watch Rectangle with Left Mouse Button')
    while upLeft == (0, 0) or lowRight == (0, 0):
        cv2.waitKey(100)

    # setup video reader loop
    rlim = 210.0
    birdCount = 0
    oldred = 0.0

    # loop through entire input video file unless key pressed or Right Mouse Click
    while success and not finished and cv2.waitKey(1) == -1:
        cv2.putText(frame, 'frame %d' % fnum, (120, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (50, 250, 250), 1)
        cv2.putText(frame, 'Bird Count = %d' % birdCount, (60, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 250, 250), 2)

        # locate sense rectangle
        r1 = upLeft[1]
        r2 = lowRight[1]
        c1 = upLeft[0]
        c2 = lowRight[0]
        rect = frame[r1:r2, c1:c2]

        # check bird threshold
        red = 3*rect[:, :, 2].sum()/rect.size
        green = 3*rect[:, :, 1].sum()/rect.size
        blue = 3*rect[:, :, 0].sum()/rect.size
        print blue, ',', green, ',', red, ',', birdCount

        # check threshold for bird detection
        if oldred < 1:
            oldred = red
            rlim = 0.75*red
        if (red < rlim) and (oldred > rlim):
            birdCount += 1
        oldred = red

        # write annotated frame to output video file
        videoWriter.write(frame)

        # echo frame to display
        cv2.imshow(fname, frame)

        # get next input frame
        cv2.waitKey(100)
        success, frame = cameraCapture.read()
        fnum += 1

    # clean up before exiting
    cameraCapture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
