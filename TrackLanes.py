import cv2
import argparse
import numpy as np

param1 = 190
param2 = 3

debug = 1


# setup track bars for Canny edge parameter
def trackbar1(pos):
    global param1
    param1 = pos


def trackbar2(pos):
    global param2
    param2 = pos

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True, help="output file name")
ap.add_argument("-i", "--input", required=True,  help="path to input video to read")
args = vars(ap.parse_args())

print "reading from: ", args["input"]
print "writing to: ", args["output"]


vc = cv2.VideoCapture(args["input"])
fps = vc.get(cv2.cv.CV_CAP_PROP_FPS)
size = (int(vc.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
print fps, size

videoWriter = cv2.VideoWriter(args["output"], cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps, size)
success, frame = vc.read()
cv2.imwrite("frame1.png", frame)

cv2.cv.NamedWindow("Params")
cv2.cv.CreateTrackbar('param1', "Params", param1, 255, trackbar1)
cv2.cv.CreateTrackbar('param2', "Params", param2, 30, trackbar2)

fcnt = 1
while success:
    # build mask by converting to gray scale and thresholding
    # convert to gray scale and filter
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # get contours from edges
    can = cv2.Canny(blur, param2, param1)
    (cnts, _) = cv2.findContours(can.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clone = frame.copy()
    for c in cnts:

        # calculate contour properties
        area = cv2.contourArea(c)
        peri = cv2.arcLength(c, True)
        
        # select desired contours
        if area > 0:
            box = cv2.minAreaRect(c)
            ((x, y), (w, h), theta) = box
            if (theta < -7.0 and theta >- 11.0) and w < 15 and w > 2 and h > 10:
                
                # draw in the minimum rectangles
                box = np.int0(cv2.cv.BoxPoints(box))
                cv2.drawContours(clone, [box], -1, (0, 255, 0), 2)
                if debug > 0:
                    cv2.putText(clone, '%0.1f' % theta, (int(x), int(y-15)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 200, 100), 1)
                    
                # identify center of rectangle
                cx = int(x+(w/2))
                cy = int(y+(h/2))
                cv2.circle(clone, (int(x), int(y)), 3, (0, 0, 255), -1)

                if debug > 0:
                    cv2.putText(clone, ' (%d,%d)' % (int(x), int(y)), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if debug > 1:
                    print x, y, w, h, theta
    
    if debug > 0:
        fnum = '%d %d %d' % (fcnt, param1, param2)
        cv2.putText(clone, fnum, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

    # save to AVI video file
    if fcnt < 810:
        videoWriter.write(clone)

    # echo frame to display
    cv2.imshow("img", clone)
    kb = cv2.waitKey(100) & 0xff
    if kb == 27:
        break

    # read in the next frame
    success, frame = vc.read()
    if debug > 1:
        print ">", fcnt, param1, med, len(cnts)
    fcnt += 1

vc.release()
cv2.destroyAllWindows()
print 'done'
