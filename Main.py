from cscore import CameraServer as cs
import cv2 as cv
import numpy as np
from Detectors.Note_Detector import Note_Detector
from Detectors.FRC_Apriltag_Detector import FRC_Apriltag_Detector
import math

def main(table):
    april_tag_yaw = table.getDoubleTopic("april_tag_yaw")
    april_tag_pitch = table.getDoubleTopic("april_tag_pitch")
    april_tag_roll = table.getDoubleTopic("april_tag_roll")
    
    april_tag_x = table.getDoubleTopic("april_tag_x")
    april_tag_y = table.getDoubleTopic("april_tag_y")
    april_tag_z = table.getDoubleTopic("april_tag_z")
    
    note_detector = Note_Detector(320,240)
    april_tag_detector = FRC_Apriltag_Detector(320, 340)
    
    cs.enableLogging()

    camera = cs.startAutomaticCapture()
    camera.setResolution(640,480)

    cvSink = cs.getVideo()

    outputStream = cs.putVideo("Rectangle", 320, 240)
    img = np.zeros(shape = (320,240,3),dtype=np.uint8)

    red = (0,0,255)
    green = (0,255,0)
    blue = (255,0,0)

    line_length = 50

    while 1:
        time, img = cvSink.grabFrame(img)
        if time == 0:
            outputStream.notifyError(cvSink.getError())
            print(cvSink.getError())
            continue
        
        notes = note_detector.get_notes(img)
        april_tags = april_tag_detector.get_frc_apriltags(img)

        for note in notes:
            cv.ellipse(img, note, (255, 0, 0), 2)
            print(note)
        
        for april_tag in april_tags:
            cv.line(img, april_tag.top_left_point, april_tag.top_right_point, red, 2)
            cv.line(img, april_tag.top_right_point, april_tag.bottom_right_point, red, 2)
            cv.line(img, april_tag.bottom_right_point, april_tag.bottom_left_point, red, 2)
            cv.line(img, april_tag.bottom_left_point, april_tag.top_left_point, red, 2)
            
            x_x = int(line_length * (math.cos(april_tag.yaw) * math.cos(april_tag.roll)) + april_tag.center[0])
            x_y = int(line_length * (math.cos(april_tag.pitch) * math.sin(april_tag.roll) + math.cos(april_tag.roll) * math.sin(april_tag.pitch) * math.sin(april_tag.yaw)) + april_tag.center[1])

            y_x = int(line_length * (-math.cos(april_tag.yaw) * math.sin(april_tag.roll)) + april_tag.center[0])
            y_y = int(line_length * (math.cos(april_tag.pitch) * math.cos(april_tag.roll) - math.sin(april_tag.pitch) * math.sin(april_tag.yaw) * math.sin(april_tag.roll)) + april_tag.center[1])

            z_x = int(line_length * math.sin(april_tag.yaw) + april_tag.center[0])
            z_y = int(line_length * (-math.cos(april_tag.yaw) * math.sin(april_tag.pitch)) + april_tag.center[1])

            cv.line(img, april_tag.center, (x_x, x_y), red, 2)
            cv.line(img, april_tag.center, (y_x, y_y), green, 2)
            cv.line(img, april_tag.center, (z_x, z_y), blue, 2)
            
            print(april_tag.center)
            print(april_tag.yaw, april_tag.pitch, april_tag.roll)
            
            april_tag_yaw.set(april_tag.yaw) 
            april_tag_pitch.set(april_tag.pitch) 
            april_tag_roll.set(april_tag.roll) 
    
            april_tag_x.set(april_tag.x) 
            april_tag_y.set(april_tag.y) 
            april_tag_z.set(april_tag.z)   
                     
        outputStream.putFrame(img)

if __name__ == "__main__":
    import logging
    import ntcore

    logging.basicConfig(level = logging.DEBUG)
    nt = ntcore.NetworkTableInstance.getDefault()
    nt.setServerTeam(4295)
    nt.startClient4(__file__)
    table = nt.getTable("datatable")
    
    main(table)