from ftplib import FTP
import cv2
import numpy as np
from pickle import dump
import time
import smbclient


def get_picture():
    ftp = FTP(host='IP', user='USER', passwd='PASSWD')
    files = []
    ftp.retrlines("NLST", callback=files.append)

    with open("/home/pi/shared/main2/picture.jpg", 'wb') as fp:
        ftp.retrbinary(f'RETR {files[-1]}', fp.write)

    smbclient.ClientConfig(username="pi", password="raspberry")
    with smbclient.open_file(r"\\192.168.100.11\rpi\home\pi\Shared\picture.jpg", 'wb') as fp:
        ftp.retrbinary(f'RETR {files[-1]}', fp.write)

    ftp.quit()

    gray = cv2.imread('/home/pi/shared/main2/picture.jpg')
    gray_new = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)

    cv2.imwrite('/home/pi/shared/main2/picture.jpg', gray_new)
    img = cv2.imread('/home/pi/shared/main2/picture.jpg')
    return img


def edit_picture(img):
    img = img[55:355, :]  # 60:355
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    return hsv


def get_digits(hsv):
    digit01 = hsv.copy()[:, 935:1055]  # 945 1075
    digit001 = hsv.copy()[:, 1100:1220]  # 1115 1245
    digit0001 = hsv.copy()[:, 1250:1370]  # 1265 1395
    digits = [digit01, digit001, digit0001]
    return digits


def apply_filter(digits):
    filter = []

    for i in range(len(digits)):
        filter.append(digits[i].copy())
        # lower, upper = np.array([90, 55, 0]), np.array(
        #     [179, 255, 255])  # 55, 32, 0
        # filter[i] = cv2.inRange(filter[i], lower, upper)

    lower1, upper1 = np.array([0, 0, 0]), np.array([179, 255, 112])
    filter[0] = cv2.inRange(filter[0], lower1, upper1)

    lower2, upper2 = np.array([0, 0, 0]), np.array([179, 255, 97])
    filter[1] = cv2.inRange(filter[1], lower2, upper2)

    lower3, upper3 = np.array([0, 0, 0]), np.array([179, 255, 65])
    filter[2] = cv2.inRange(filter[2], lower3, upper3)
    return filter


def crop_digits(filter):
    x = []
    y = []
    h = []
    w = []

    for i in range(3):
        contours, hierarchy = cv2.findContours(
            filter[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
                x.append(0)
                y.append(0)
                h.append(0)
                w.append(0)
                x[i], y[i], w[i], h[i] = cv2.boundingRect(approx)
                if (h[i] >= (1.195*w[i])):  # 1.165
                    # cv2.rectangle(digits[i], (x[i], y[i]), (x[i]+w[i], y[i]+h[i]), (255, 255, 255), 2)
                    break
        digits[i] = cv2.cvtColor(digits[i], cv2.COLOR_HSV2RGB)
        # for j in range(3):
        #     cv2.imwrite(f'/home/pi/shared/main2/{j}.jpg', digits[j])
    return digits, x, y, w, h


def rotation():
    rotation = cv2.imread('/home/pi/shared/main2/rotation.jpg')
    rotation = cv2.resize(rotation, (75, 125))
    rotation = cv2.cvtColor(rotation, cv2.COLOR_RGB2GRAY)
    number, rotation = cv2.threshold(rotation, 127, 255, cv2.THRESH_BINARY)
    return rotation


def create_new_digits(digits, x, y, w, h, rotation_img):
    new_digits = []
    gray_img = []

    for i in range(len(digits)):
        if (h[i] < (1.6*w[i])):
            new_digits.append(digits[i].copy()[(y[i]-30):(
                y[i]+h[i]+40), (x[i]-4):(x[i]+w[i]+4)])
        else:
            new_digits.append(
                digits[i].copy()[(y[i]):(y[i]+h[i]+3), (x[i]-4):(x[i]+w[i]+4)])
        # new_digits.append(digits[i].copy()[(y[i]-6):(y[i]+h[i]+3), (x[i]-4):(x[i]+w[i]+4)])
        new_digits[i] = cv2.resize(new_digits[i], (w[i], 125))
        gray_img.append(cv2.cvtColor(new_digits[i].copy(), cv2.COLOR_RGB2GRAY))
        if i == 0:
            gray_img[i] = cv2.threshold(
                gray_img[i], 140, 255, cv2.THRESH_BINARY)[1]  # 150
        elif i == 1:
            gray_img[i] = cv2.threshold(
                gray_img[i], 120, 255, cv2.THRESH_BINARY)[1]  # 140
        else:
            gray_img[i] = cv2.threshold(
                gray_img[i], 85, 255, cv2.THRESH_BINARY)[1]  # 127

    gray_img.append(rotation_img)
    google = cv2.hconcat(gray_img)
    google = cv2.medianBlur(google, 5)
    cv2.imwrite("/home/pi/shared/main2/google.jpg", google)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    cv2.imwrite(
        f"/home/pi/shared/main2/statistics/{timestr}-google.jpg", google)


def coordinates(x, y, w, h):
    with open("/home/pi/shared/main2/x.txt", "wb") as text_x:
        dump(x, text_x)

    with open("/home/pi/shared/main2/y.txt", "wb") as text_y:
        dump(y, text_y)

    with open("/home/pi/shared/main2/w.txt", "wb") as text_w:
        dump(w, text_w)

    with open("/home/pi/shared/main2/h.txt", "wb") as text_h:
        dump(h, text_h)


if __name__ == "__main__":
    img = get_picture()
    hsv = edit_picture(img)
    digits = get_digits(hsv)
    filter = apply_filter(digits)
    digits, x, y, w, h = crop_digits(filter)
    rotation_img = rotation()
    create_new_digits(digits, x, y, w, h, rotation_img)
    coordinates(x, y, w, h)
