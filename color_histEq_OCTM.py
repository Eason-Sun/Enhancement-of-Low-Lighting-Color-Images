import cv2
import numpy as np
from scipy.optimize import linprog
import math

def demosaicing (img):
    rows, cols, channels = img.shape
    cfaImg = np.empty(shape=(rows, cols, channels), dtype=np.uint8)
    for x in range(0, rows):
        for y in range(0, cols):
            if x % 2 == 0:
                if y % 2 == 0:
                    cfaImg[x][y][0] = img[x][y][0]
                    cfaImg[x][y][1] = 0
                    cfaImg[x][y][2] = 0

                else:
                    cfaImg[x][y][0] = 0
                    cfaImg[x][y][1] = img[x][y][1]
                    cfaImg[x][y][2] = 0
            else:
                if y % 2 == 0:
                    cfaImg[x][y][0] = 0
                    cfaImg[x][y][1] = img[x][y][1]
                    cfaImg[x][y][2] = 0
                else:
                    cfaImg[x][y][0] = 0
                    cfaImg[x][y][1] = 0
                    cfaImg[x][y][2] = img[x][y][2]

    cv2.imshow("cfa",cfaImg)
    BLACK = [0, 0, 0]
    cfaImgPadding1 = cv2.copyMakeBorder(cfaImg, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=BLACK)
    bilinearImg = np.empty(shape=(rows + 2, cols + 2, channels), dtype=np.uint8)

    sum = 0
    counter = 0
    for x in range(1, rows + 1):
        for y in range(1, cols + 1):
            if x % 2 == 1:
                if y % 2 == 1:
                    bilinearImg[x][y][0] = cfaImgPadding1[x][y][0]
                    bilinearImg[x][y][1] = int(0.25 * (
                            int(cfaImgPadding1[x][y - 1][1]) + int(cfaImgPadding1[x][y + 1][1]) + int(
                        cfaImgPadding1[x - 1][y][1]) + int(cfaImgPadding1[x + 1][y][1])))
                    bilinearImg[x][y][2] = int(0.25 * (
                            int(cfaImgPadding1[x - 1][y - 1][2]) + int(cfaImgPadding1[x - 1][y + 1][2]) + int(
                        cfaImgPadding1[x + 1][y - 1][2]) + int(cfaImgPadding1[x + 1][y + 1][2])))
                else:
                    bilinearImg[x][y][0] = int(0.5 * (int(cfaImgPadding1[x][y - 1][0]) + int(cfaImgPadding1[x][y + 1][0])))
                    bilinearImg[x][y][1] = cfaImgPadding1[x][y][1]
                    bilinearImg[x][y][2] = int(0.5 * (int(cfaImgPadding1[x - 1][y][2]) + int(cfaImgPadding1[x + 1][y][2])))
            else:
                if y % 2 == 1:
                    bilinearImg[x][y][0] = int(0.5 * (int(cfaImgPadding1[x - 1][y][0]) + int(cfaImgPadding1[x + 1][y][0])))
                    bilinearImg[x][y][1] = cfaImgPadding1[x][y][1]
                    bilinearImg[x][y][2] = int(0.5 * (int(cfaImgPadding1[x][y - 1][2]) + int(cfaImgPadding1[x][y + 1][2])))
                else:
                    bilinearImg[x][y][0] = int(0.25 * (
                            int(cfaImgPadding1[x - 1][y - 1][0]) + int(cfaImgPadding1[x - 1][y + 1][0]) + int(
                        cfaImgPadding1[x + 1][y - 1][0]) + int(cfaImgPadding1[x + 1][y + 1][0])))
                    bilinearImg[x][y][1] = int(0.25 * (
                            int(cfaImgPadding1[x][y - 1][1]) + int(cfaImgPadding1[x][y + 1][1]) + int(
                        cfaImgPadding1[x - 1][y][1]) + int(cfaImgPadding1[x + 1][y][1])))
                    bilinearImg[x][y][2] = cfaImgPadding1[x][y][2]
            sum += abs(int(img[x - 1][y - 1][0]) - bilinearImg[x][y][0])
            counter += 1
            # print(bilinearImg[x][y])
    return bilinearImg

def adjust_gamma(image, gamma):
    table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

def hist_equalization (intensity_channel):
    hist, bins = np.histogram(intensity_channel, 256, [0,255])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()

    for x in np.nditer(intensity_channel, op_flags=['readwrite']):
        x[...] = cdf_normalized[x[...]] * 255

    return intensity_channel

def OCTM_ver1 (intensity_channel):
    hist, bins = np.histogram(intensity_channel, 256, [0, 255])
    p = hist / np.sum(hist)
    max_dynamic_range = 0

    for i in range(len(p) - 1, -1, -1):
        if p[i] > 0.0001:
            max_dynamic_range = i + 1
            break
        p[i] = 0
    print(max_dynamic_range, p)
    A = np.array([[1] * max_dynamic_range])
    b = np.array([255])
    boundsList = np.array([(0.5, None)] * max_dynamic_range)
    res = linprog(p[:max_dynamic_range] * (-1), A_ub=A, b_ub=b, bounds=boundsList, options={"disp": True})
    s = res.x
    T = np.array([])
    for i in range(max_dynamic_range):
        T = np.append(T, [math.floor(0.5 + np.sum(s[:(i+1)]))])
    # T[0] = 0
    for x in np.nditer(intensity_channel, op_flags=['readwrite']):
        if x[...] >= max_dynamic_range:

            x[...] = 255
        else:
            x[...] = T[x[...]]
    return intensity_channel

def OCTM (intensity_channel):

    hist, bins = np.histogram(intensity_channel, 256, [0, 255])
    p = hist / np.sum(hist)
    max_dynamic_range = 0

    for i in range(len(p) - 1, -1, -1):
        if p[i] > 0.0001:
            max_dynamic_range = i + 1
            break
        p[i] = 0
    print(max_dynamic_range,p)
    A = np.array([[1] * max_dynamic_range])
    # b = np.array([255])
    # boundsList = np.array([(0.5, None)] * max_dynamic_range)

    for i in range(max_dynamic_range - 1):
        new = np.array([0] * max_dynamic_range)
        new[i:i+2:1]=1
        A = np.append(A, [new], axis=0)

    # b = np.append(np.array([255]),[40]*(max_dynamic_range-1))
    # boundsList = np.append(np.array([(0, 20)]), [(2.2, None)] * (max_dynamic_range-1), axis=0)

    b = np.append(np.array([255]),[50]*(max_dynamic_range-1))
    boundsList = np.append(np.array([(0, 25)]), [(2.5, None)] * (max_dynamic_range-1), axis=0)

    res = linprog(p[:max_dynamic_range]*(-1), A_ub=A, b_ub=b, bounds=boundsList, options = {"disp": True})
    s = res.x
    # print(p[:max_dynamic_range]*(-1))
    print(s, np.sum(s))
    T = np.array([])

    for i in range(max_dynamic_range):
        T = np.append(T, [math.floor(0.5 + np.sum(s[:(i+1)]))])
    # T[0] = 0
    for x in np.nditer(intensity_channel, op_flags=['readwrite']):
        if x[...] >= max_dynamic_range:

            x[...] = 255
        else:
            x[...] = T[x[...]]
    return intensity_channel

img = cv2.imread('Original_Images/image1.png')
cv2.imshow("original_image", img)
img_de = demosaicing(img)
cv2.imshow("demosaicing_image", img_de)
H1, S1, V1 = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
H2, S2, V2 = cv2.split(cv2.cvtColor(img_de, cv2.COLOR_BGR2HSV))
H3, S3, V3 = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))

otcm_V2 = OCTM(V2)
octm_image = cv2.cvtColor(cv2.merge([H2, S2, otcm_V2]), cv2.COLOR_HSV2BGR)
cv2.imshow("octm_image2", octm_image)
# cv2.imwrite("OCTM_Images/bayer_OCTM_Image1.jpg", octm_image)
#
# eq_V1 = hist_equalization(V1)
# eq_image = cv2.cvtColor(cv2.merge([H1, S1, eq_V1]), cv2.COLOR_HSV2BGR)
# eq_image = adjust_gamma(eq_image, 1.2)
# cv2.imshow("eq_image", eq_image)
# cv2.imwrite("HistEq_Images/HistEq_Image4.jpg", eq_image)

# eq_V3 = cv2.equalizeHist(V3)
# eq_image2 = cv2.cvtColor(cv2.merge([H3, S3, eq_V3]), cv2.COLOR_HSV2BGR)
# cv2.imshow("eq_image_buildin", eq_image2)
# cv2.imwrite("HistEq_local/HistEq_local_Image1.png", eq_image2)

# V1_GC = adjust_gamma(V1, 0.2)
# gc_image = cv2.cvtColor(cv2.merge([H2, S2, V1_GC]), cv2.COLOR_HSV2BGR)
# cv2.imshow("gamma correction", gc_image)
# cv2.imwrite("GC_Images/GC_Image1.png", gc_image)


cv2.waitKey(0)

# c = np.array([-1, 4])
# A = np.array([[-3, 1], [1, 2]])
# b = np.array([6, 4])
#
# x0_bounds = (None, None)
# x1_bounds = (-3, None)
# boundsList = np.array([x0_bounds])
# boundsList = np.append(boundsList,[x1_bounds],axis=0)
#
# res = linprog(c, A_ub=A, b_ub=b, bounds=boundsList, options={"disp": True})
# print(res)