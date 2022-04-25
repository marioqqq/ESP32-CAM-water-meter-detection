import cv2
import numpy as np
from pickle import load
import time
from openpyxl import load_workbook
import pandas as pd
import mysql.connector

mydb = mysql.connector.connect(
    host="192.168.100.11",
    user="bakalarka",
    password="raspberry",
    database="home2")
mycursor = mydb.cursor()


def get_picture():
    img = cv2.imread("/home/pi/shared/main2/picture.jpg")
    return img


def coordinates():
    with open("/home/pi/shared/main2/x.txt", "rb") as text_x:
        x = load(text_x)

    with open("/home/pi/shared/main2/y.txt", "rb") as text_y:
        y = load(text_y)

    with open("/home/pi/shared/main2/w.txt", "rb") as text_w:
        w = load(text_w)

    with open("/home/pi/shared/main2/h.txt", "rb") as text_h:
        h = load(text_h)

    return x, y, w, h


def val():
    mycursor.execute(f"SELECT * FROM new ORDER BY time DESC LIMIT 1")
    myresult = mycursor.fetchall()
    return myresult[0][1]


def save_statistics(img, x, y, w, h, value, timestr):
    constantx = [935, 1100, 1250]
    constanty = 55
    for i in range(3):
        cv2.rectangle(img, (x[i]+constantx[i], y[i]+constanty),
                      (x[i]+w[i]+constantx[i]+5, y[i]+h[i]+constanty+8), (0, 0, 255), 3)
    cv2.putText(img, f"{value}", (950, 465),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    cv2.imwrite(f"/home/pi/shared/main2/statistics/{timestr}.jpg", img)


def excel(timestr):
    df = pd.read_excel("/home/pi/shared/main2/statistics/statistics.xlsx")
    row = df.index[-1] + 3
    workbook = load_workbook(
        filename="/home/pi/shared/main2/statistics/statistics.xlsx")
    sheet = workbook.active
    sheet[f"A{row}"] = timestr
    sheet[f"B{row}"] = "To be reviewed"
    workbook.save(filename="/home/pi/shared/main2/statistics/statistics.xlsx")
    workbook.close()


if __name__ == "__main__":
    img = get_picture()
    x, y, w, h = coordinates()
    value = val()
    timestr = time.strftime("%Y%m%d-%H%M%S")
    save_statistics(img, x, y, w, h, value, timestr)
    excel(timestr)
