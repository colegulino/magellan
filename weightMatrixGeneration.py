# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 21:28:54 2015

@author: Cole Gulino, Mohamed Shemy
"""
#import the python libraries needed, scipy, numpy, and cv2
from scipy import linalg as scili
import numpy as np
import cv2

#Set some arrays to store the values, the P, and the test matrices
values = []
P = []
test = []

#create the function to run hardlims on the vector
def hardlims(vector):
    for i in range(400):
        if vector[i] >= 0:
            vector[i] = 1
        else:
            vector[i] = -1
    return vector
    
def showImage(image):
    cv2.imshow('img', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def cvtBandW(letter):
    bw_letter = []
    for i in xrange(0,20):
        for j in xrange(0,20):
            if letter[i,j] > 80:
                bw_letter.append(1)
            else:
                bw_letter.append(-1)
    return bw_letter
    
    
#create a dictionary for the letters and their arrays
mydict = {}
strings = ['0','1','2','3','4','5','6','7','8','9','A', 'A2', 'B','C','D','E','F','G','H','I','J',\
'K','L','M','N','O','P','Q','R','S','T','U','V', 'V2','W','X','Y','Z','&','AST','@',\
'$','!','#','(','%','^',')']
print len(strings)

for string in strings:
    #convert the list of stirngs into jpeg names found in the Char_Rec folder and print the name
    img_name = "test" +string+".jpg"
    print img_name
    #use cv2 package to convert the image into an array
    image = cv2.imread(img_name)
    #Use cv2 package to convert the image array to grayscale
    g_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #Set the threshold for what is white and what is gray
    (ret, th_image) = cv2.threshold(g_image, 25, 255, 0)
    #Set the contours for the images
    contours, hierarchy = cv2.findContours(th_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #Get the contour that corresponds to the letter
    contour = contours[len(contours) - 2]
    #Show a box around the image contour and print a rectangle around it
    x,y,width,height = cv2.boundingRect(contour)
    #cv2.rectangle(g_image, (x,y), (x+width,y+height), (0,255,0),2)
    #Get the image around contour
    letter = g_image[y:y+height, x:x+width]
    #resize letter to 20x20 pixels
    letter = cv2.resize(letter, (20,20))
    bw_letter = cvtBandW(letter)
    '''
    for i in xrange(0,20):
        for j in xrange(0,20):
            if letter[i,j] > 80:
                bw_letter.append(1)
            else:
                bw_letter.append(-1)
    '''
    
    #Append each bw_letter to the input array
    P.append(bw_letter)
    #Save the array in the dictionary
    mydict[string] = bw_letter
    test = bw_letter
    
#Convert P to a numpy matrix
P = zip(*P)
print P
np.savetxt('P_matrix.txt', P)
#Run the pseudoinverse algorithm with scipy(P+ = (P'P)^-1P')
P_plus = scili.pinv(P)
#Generate the weight matrix matrix W = TP+; T = P
W = np.dot(P, P_plus)
#Save the weight matrix to a file
np.savetxt('weight_matrix.txt', W)
#Save the dictionary to a text file
file1 = open('letter_dict.txt', 'w')
file1.write(str(mydict))
file1.close()

#Test the new weight matrix
test_vector = np.dot(W, test)
#Use hardlims on test_vector
test_vector = hardlims(test_vector)
         
#See if you can locate the test_vector in the dictionary
test_vector2 = mydict['V']
test_vector2 = np.dot(W, test_vector2)
test_vector2 = hardlims(test_vector2)
print "Expecting to recognize a ')' and a 'V'"
for ch, ary in mydict.items():
    if np.array_equal(test_vector, ary):
        print "Test vector 1[)]: " + ch
    if np.array_equal(test_vector2, ary):
        print "Test vector 1[V]: " + ch