import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import datetime
import serial
from cvzone.FaceDetectionModule import FaceDetector

cred = credentials.Certificate("serviceCertificate.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://mripatmu-5bfce-default-rtdb.firebaseio.com/",
    'storageBucket': "mripatmu-5bfce.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
detector = FaceDetector()

Xposition = 90
Yposition = 90

ser = serial.Serial('COM3', '9600', timeout=5)
def toSerial(img,x, y):

    global Xposition, Yposition
    rows, cols, _ = img.shape

    center_x = int(rows / 2)
    center_y = int(cols / 2)

    medium_x = int(x+5)
    medium_y = int(y+5)

    v=2
    m=45

    if medium_x > center_x + m:
        Xposition += v
        if Xposition>= 180:
            Xposition = 180

    if medium_x < center_x - m:
        Xposition -= v
        if Xposition < 0:
            Xposition = 0
#######################################
    if medium_y > center_y + m:
        Yposition += v
        if Yposition>= 180:
            Yposition = 180


    if medium_y < center_x - m:
        Yposition -= v
        if Yposition < 0:
            Yposition = 0
    print((str(int(Xposition))+'  '+ str(int(Yposition))).encode('utf-8'))
    ser.write(('a'+ str(int(Xposition))+'b'+ str(int(Yposition))).encode('utf-8'))

def add_student_permission(student_id, status):
    ref = db.reference('permissions')
    ref.push({
        'id': student_id,
        'tanggal': datetime.datetime.now().isoformat(),
        'status':status})


while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img, draw=False)
    if bboxs:
        # get the coordinate
        fx, fy = bboxs[0]["center"][0], bboxs[0]["center"][1]
        pos = [fx, fy]
        # convert coordinat to servo degree
        servoX = np.interp(fx, [0, 640], [180, 0])
        servoY = np.interp(fy, [0, 480], [0, 180])

        if servoX < 0:
            servoX = 0
        elif servoX > 180:
            servoX = 180
        if servoY < 0:
            servoY = 0
        elif servoY > 180:
            servoY = 180

        ser.write(('a' + str(int(servoX)) + 'b' + str(int(servoY))).encode('utf-8'))
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(imgGray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    imgS = cv2.resize(img, (0, 0), None, 0.50, 0.50)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)

    for (x, y, w, h) in faces:
        faceCurFrame.append((y, x + w, y + h, x))

    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Out", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                datetimeObject = datetime.datetime.strptime(studentInfo['last_out_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_out'] += 1
                    ref.child('total_out').set(studentInfo['total_out'])
                    ref.child('last_out_time').set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    add_student_permission(studentInfo['name'],"alfa")
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_out']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)
                    cv2.putText(imgBackground, str(studentInfo['kelas']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Out", imgBackground)
    cv2.waitKey(1)