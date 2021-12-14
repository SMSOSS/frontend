# Scanner for PT
#

import cv2
from pyzbar import pyzbar
import mysql.connector
from mysql.connector import Error

# SQL Start
def connect(host, user, password, db):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=db
       )
        print("[INFO] MySQL Database connection successful")
    except Error as err:
        print(f"[ERROR] '{err}'")

    return connection

def read(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def update(connection, command):
    cursor = connection.cursor()
    cursor.execute(command)
    connection.commit()

# SQL: Logics
def brain(password):
    connection = connect("localhost", "user", "password", "tiferet")
    cmd = ("SELECT isdeliver, istaken FROM food WHERE NOT istaken=1 AND NOT iscooked=0 AND password=({})".format(password)) # locker validity check
    sts = read(connection, cmd)
    if not sts:
        # add hook for open locker
        password = int(password)
        password = password-10000 # deliverman
        cmd = ("SELECT isdeliver, istaken FROM food WHERE NOT istaken=1 AND NOT iscooked=0 AND password=({})".format(password)) # locker validity check
        sts = read(connection, cmd)
        if not sts:
            print("[ERROR] scanner: invalid qr detect")
            return
        print("[DEBUG] real password is ({})".format(password))
        cmd = ("UPDATE food SET isdeliver=1 WHERE password=({})".format(password))
        update(connection, cmd)
    else:
        cmd = ("UPDATE food SET istaken=1 WHERE password=({})".format(password))
        update(connection, cmd)
        cmd = ("SELECT locker FROM food WHERE istaken=1 AND password=({})".format(password))
        ln = read(connection, cmd)
        ln = ln[0]
        cmd = ("UPDATE lockerdata SET isoccupy=0 WHERE lockerid=({})".format(ln))
        update(connection, cmd)

# Barcode start
def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y , w, h = barcode.rect
        #1
        barcode_info = barcode.data.decode('utf-8')
        brain(barcode_info)
        rmvtxt = "Please remove QRCode"
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
        
        #2
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, rmvtxt, (x + 6, y - 6), font, 1.0, (144, 238, 144), 1)
        #3
        with open("barcode_result.txt", mode ='w') as file:
            file.write("Recognized Barcode:" + barcode_info)
    return frame

def main():
    #1
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    #2
    while ret:
        ret, frame = camera.read()
        frame = read_barcodes(frame)
        cv2.imshow('Barcode/QR code reader', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    #3
    camera.release()

    cv2.destroyAllWindows()
#4
if __name__ == '__main__':
    main()
