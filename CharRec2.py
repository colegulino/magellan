# -*- coding: utf-8 -*-
"""
Created on Thu April 9 15:12:11 2015

@author: Cole Gulino, Mohamed Shemy

To run a specific letter, specify the letter in the command line
"""
import sys
import cv2
import numpy as np
from multiprocessing import Process
from multiprocessing import Queue

def showImage(image):
    cv2.imshow('img', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def cvtBandW(letter, threshold):
    bw_letter = []
    for i in xrange(0,20):
        for j in xrange(0,20):
            if letter[i,j] > threshold:
                bw_letter.append(1)
            else:
                bw_letter.append(-1)
    return bw_letter
    
def hardlims(vector):
    for i in range(400):
        if vector[i] >= 0:
            vector[i] = 1
        else:
            vector[i] = -1
    return vector

def recChar(characterName, square, fileName):
    #Open the file to append to
    file0 = open(fileName, 'a')
    image = cv2.imread(characterName)

    #Turn the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Set the gray scale threshold for the image
    (ret, th_image) = cv2.threshold(gray_image, 25, 255, 0)
    contours, hierarchy = cv2.findContours(th_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[len(contours)-2]

    #Find the x,y,width, and height of the contour around the letter
    x,y,width,height = cv2.boundingRect(contour)

    #create an image the size of the letter
    letter = gray_image[y:y+height,x:x+width]

    #resize the letter to be a square matrix
    letter = cv2.resize(letter, (20,20))

    #Get the weight matrix from the file
    try:
        Wn = np.loadtxt('weight_matrix_numbers.txt')
        Wl = np.loadtxt('weight_matrix_letters.txt')
        #print "Downloaded Weight Matrices."
    except:
        print "Error: Cannont find file"
        sys.exit()
    Wn = np.array(Wn)
    Wl = np.array(Wl)

    #Find if the image is on red or blue
    pixel = image[0,0]
    if pixel[2] > pixel[0]:
        W = []
        W = Wl
        #Convert image to black and white
        bw_letter = cvtBandW(letter, 135)
        bw_letter = np.transpose(bw_letter)
    else:
        #print "Weight Numbers Chosen"
        W = []
        W = Wn
        #Convert image to black and white
        bw_letter = cvtBandW(letter, 80)
        bw_letter = np.transpose(bw_letter)

    #Multiply the test vector with the weight matrix
    result_vector = np.dot(W, bw_letter)
    result_vector = hardlims(result_vector)
    result_vector_t = result_vector.reshape((20,20))


    #Open the dictionary of the ltters
    try:
        dictionary = {}
        dictionary = open('letter_dict.txt', 'r').read()
        dictionary = eval(dictionary)
    except:
        print "Error: file cannot be read."

    charList = []
    posDict = {}
    #Try to test characters for result in dictionary if they are close
    for char, vector in dictionary.items():
        count = 0
        if np.array_equal(result_vector, vector):
            #print "The result for " + letter_file + " is: " + char + " in Square: " + str(square)
            file0.write("Square: " + str(square) + " Character: " + str(char))
            file0.write('\n')
            return
        else:
            for element in xrange(400):
                if result_vector[element] == vector[element]:
                    count += 1
            percent = (float(count)/len(result_vector))
            if percent >= 0.80:
                #print char, ": ", (float(count)/len(result_vector))*100, "%", " in Square: " + str(square)
                posDict[percent] = char
    if (len(posDict) != 0):
        maxPercent = max(posDict.keys())
        file0.write("Square: " + str(square) + " Character: " + str(posDict[maxPercent]) + " Percent: " + str(maxPercent))
        file0.write('\n')
    file0.close()
