 # -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 16:52:39 2015

@author: Cole Gulino
"""

import numpy as np
import pickle, sys, os
import time
import RPi.GPIO as GPIO
import picamera
from multiprocessing import Process
import CharRec as cr

def findCell(cellNo):
    for cell in maze:
        if cell.number == cellNo:
            return cell

def printAdjacent(adjacentCells):
    if (adjacentCells[0] == None):
        stringN = "North: None"
    else:
        stringN = "North: " + str(adjacentCells[0].number)
    if (adjacentCells[1] == None):
        stringS = " South: None "
    else:
        stringS = " South: " + str(adjacentCells[1].number)
    if (adjacentCells[2] == None):
        stringE = " East: None "
    else:
        stringE = " East: " + str(adjacentCells[2].number)
    if (adjacentCells[3] == None):
        stringW = " West: None"
    else:
        stringW = " West: " + str(adjacentCells[3].number)

    return stringN + stringS + stringE + stringW

def printAdjacentStart(adjacentCells):
    if (adjacentCells[0] == True):
        stringN = "North: True "
    else:
        stringN = "North: False "
    if (adjacentCells[1] == True):
        stringS = " South: True "
    else:
        stringS = " South: False "
    if (adjacentCells[2] == True):
        stringE = " East: True "
    else:
        stringE = " East: False "
    if (adjacentCells[3] == True):
        stringW = " West: True "
    else:
        stringW = " West: False "

    return stringN + stringS + stringE + stringW

def printClosedList(list):
    string = ""
    for cell in list:
	if (cell == None):
		string += "None "
	else:
        	string += str(cell.number) + " "

    return string

def searchMaze(maze_mode):
    global currentCell
    global endCell
    global startCell
    global prevCell
    global facing
    global closedlist

    print maze_mode
    #Find the starting and ending squares
    if (maze_mode == "5x5"):
        startCell = findCell(48)
        endCell = findCell(9)
    elif (maze_mode == "6x6"):
        startCell = findCell(48)
        endCell = findCell(1)
    elif (maze_mode == "7x7"):
        startCell = findCell(49)
        endCell = findCell(1)
    else:
        data.write("Error: Maze mode not initialized properly.")
        
    #closedlist = []
    nextrun = []
    if (maze_mode == "5x5" or maze_mode == "6x6"):
        facing = "north" #initial facing direction
    else:
        facing = "north"

    #Set current cell to be the start cell
    currentCell = startCell
    count = 0
    data.write("Initial Square: "+ str(currentCell.number))
    data.write('\n')
    #Run the Algorithm to go from start square to end square
    prevCell = None
    tempCell = currentCell
    closedlist.append(currentCell)
    currentCell = currentCell.nextCell()
    prevCell = tempCell
    closedlist.append(currentCell)
    while (currentCell != endCell):
        #set the current cell to the next cell
        #count += 1
        tempCell = currentCell
        currentCell = currentCell.nextCell()
        prevCell = tempCell
        data.write(str(currentCell.number))
        data.write('\n')
        closedlist.append(currentCell)

    #Now write the path to a file
    secondPath = []
    currentCell = startCell
    #print "Start Cell chosen: ", str(startCell.chosen.number)
    data.write("Start Cell chosen: " + str(startCell.chosen.number))
    data.write("\n")
    secondPath.append(currentCell.number)
    data.write("Second Run Generation")
    data.write('\n')

    while True:
        if (currentCell.chosen == endCell):
            break
        else:
            currentCell = currentCell.chosen
            secondPath.append(currentCell.number)
        #print str(currentCell.number)
        data.write(str(currentCell.number))
        data.write('\n')

    secondPath.append(endCell.number)

    criticalRunFile = open('cRun.txt','wb')
    pickle.dump(secondPath, criticalRunFile)
    criticalRunFile.close()
    

#Functions for movement
def forward():
    GPIO.output(out_pin1, 1)
    GPIO.output(out_pin2, 1)
    while GPIO.input(in_pin) == 0:
        #do nothing
        pass
    GPIO.output(servo, 0)
    GPIO.output(out_pin1, 0)
    GPIO.output(out_pin2, 0)
    while GPIO.input(in_pin) == 1:
        #do nothing   
        pass
def left():
    GPIO.output(out_pin1, 1)
    GPIO.output(out_pin2, 0)
    while GPIO.input(in_pin) == 0:
        #wait
        pass
    GPIO.output(servo, 0)
    GPIO.output(out_pin1, 0)
    GPIO.output(out_pin2, 0)
    while GPIO.input(in_pin) == 1:
        #wait
        pass

def right():
    GPIO.output(out_pin1, 0)
    GPIO.output(out_pin2, 1)
    while GPIO.input(in_pin) == 0:
        #wait
        pass
    GPIO.output(servo, 0)
    GPIO.output(out_pin1, 0)
    GPIO.output(out_pin2, 0)
    while GPIO.input(in_pin) == 1:
        #wait
        pass

def cForward():
    GPIO.output(servo, 1)
    forward()

def cleft():
    GPIO.output(servo, 1)
    left()

def cright():
    GPIO.output(servo, 1)
    right()

def findFacing(cNum, pNum):
    global facing
    if (cNum == pNum - 7):
        facing = "north"
    elif (cNum == pNum - 1):
        facing = "west"
    elif (cNum == pNum + 1):
        facing = "east"
    else:
        facing = "south"
    #data.write("Facing: " + facing)
    #data.write('\n')

def move(start, end):
    #Now determine where it needs to go
    if (end == start + 7):
        #Going south
        if (facing == "north"):
            right()
            right()
            forward()
        elif (facing == "south"):
            forward()
        elif (facing == "east"):
            right()
            forward()
        elif (facing == "west"):
            left()
            forward()
    elif (end == start - 1):
        #Going west
        if (facing == "north"):
            left()
            forward()
        elif (facing == "south"):
            right()
            forward()
        elif (facing == "east"):
            right()
            right()
            forward()
        elif (facing == "west"):
            forward()
    elif (end == start + 1):
        #Going east
        if (facing == "north"):
            right()
            forward()
        elif (facing == "south"):
            left()
            forward()
        elif (facing == "east"):
            forward()
        elif (facing == "west"):
            right()
            right()
            forward()
    elif (end == start - 7):
        #Going North
        if (facing == "north"):
            forward()
        elif (facing == "south"):
            right()
            right()
            forward()
        elif (facing == "east"):
            left()
            forward()
        elif (facing == "west"):
            right()
            forward()

class Cell:
    def __init__(self, number, N, S, E, W):
        #Cell object to hold all of the cells in the maze
        self.number = number # Number in the maze
        #T or F if there is a wall on N, S, E, or W side of the wall
        self.N = N
        self.E = E
        self.W = W
	self.S = S
        self.adjacentCells = []
	self.chosen = None
        #Find the x and y coordinates for the cell when initialized
        self.x = self.number % 7 - 1
        if self.x == -1:
            self.x = self.x % 7
        if self.number % 7 == 0:
            self.y = self.number / 7 - 1
        else:
            self.y = self.number / 7
        self.openlist = []
        self.ManhattanDistance = 10000
        self.visitedList = []
	self.index = 0
	self.visitedList.append(None)
	self.visitedList.append(None)
	self.camera = False
        data.write(str(self.number) + ": "+ str(self.x)+ " "+ str(self.y) + printAdjacentStart([self.N, self.S, self.E, self.W]))
        data.write('\n')

    #Method for finding the next cell to move to
    def nextCell(self):
	if (prevCell == None):
        	facing = "north"
	else:
		findFacing(self.number, prevCell.number)
        self.gatherProxSensor()
        if (maze_mode != "5x5"):
            self.takeImage()
        return self.findPath()
    
    #Gather proximity sensors from the map
    def gatherProxSensor(self):
        if (facing == "south"):
            if (GPIO.input(front_wall) == 1):
                self.S = True
		self.camera = True
            else:
                self.S = False
            if (GPIO.input(right_wall) == 1):
                self.W = True
            else:
                self.W = False
            if (GPIO.input(left_wall) == 1):
                self.E = True
            else:
                self.E = False
            self.N = False
        elif (facing == "north"):
            if (GPIO.input(front_wall) == 1):
                self.N = True
		self.camera = True
            else:
                self.N = False
            if (GPIO.input(right_wall) == 1):
                self.E = True
            else:
                self.E = False
            if (GPIO.input(left_wall) == 1):
                self.W = True
            else:
                self.W = False
            self.S = False
        elif (facing == "east"):
            if (GPIO.input(front_wall) == 1):
                self.E = True
		self.camera = True
            else:
                self.E = False
            if (GPIO.input(right_wall) == 1):
                self.S = True
            else:
                self.S = False
            if (GPIO.input(left_wall) == 1):
                self.N = True
            else:
                self.N = False
            self.W = False
        elif (facing == "west"):
            if (GPIO.input(front_wall) == 1):
                self.W = True
		self.camera = True
            else:
                self.W = False
            if (GPIO.input(right_wall) == 1):
                self.N = True
            else:
                self.N = False
            if (GPIO.input(left_wall) == 1):
                self.S = True
            else:
                self.S = False
            self.E = False
            
    def takeImage(self):
        if (self.camera == True):
	    data.write("Took a picture")
	    data.write('\n')
            os.system("raspistill -o /home/pi/nav/imageName.jpg -n -t 10 -w 2592 -h 1944 -ex night")
            recProcess = Process(target=cr.recChar, args=("imageName.jpg", self.number, "charList.txt",))
            recProcess.start()
            self.camera = False

    def findAdjacentCells(self):
        #Get North
        if (self.N == True):
            self.adjacentCells.append(None)
        elif (self.number - 7 < 0):
            self.adjacentCells.append(None)
        else:
            self.adjacentCells.append(findCell(self.number-7))
        #Get South
        if (self.S == True):
            self.adjacentCells.append(None)
        elif (self.number + 7 > 50):
            self.adjacentCells.append(None)
        else:
            self.adjacentCells.append(findCell(self.number+7))
        #Get East
        if (self.E == True):
            self.adjacentCells.append(None)
        elif (self.number % 7 == 0):
            self.adjacentCells.append(None)
        else:
            self.adjacentCells.append(findCell(self.number+1))
        #Get West
        if (self.W == True):
            self.adjacentCells.append(None)
        elif (self.number % 7 == 1):
            self.adjacentCells.append(None)
        else:
            self.adjacentCells.append(findCell(self.number-1))

    def findPath(self):
        if (len(self.adjacentCells) == 0):
            #print "Calling self.findAdjacentCells()"
            self.findAdjacentCells()
	data.write("Adjacent Cells: " + printAdjacent(self.adjacentCells))
	data.write('\n')
	data.write("Visited List: " + printClosedList(self.visitedList))
	data.write('\n')
	nextCell = None
        for cell in self.adjacentCells:
            if (cell != None and cell != prevCell):
                self.openlist.append(cell)
            if (cell == endCell):
                #Check to see if the final square is around the robot
		self.chosen = cell
		self.visitedList[self.index] = cell
                nextCell = cell
	data.write("Open List: " + printClosedList(self.openlist))
	data.write('\n')
        while (nextCell == None):
            if (len(self.openlist) == 0):
                #3 wall case, chose the previous square
                #print "3 wall case"
                self.chosen = prevCell
		self.visitedList[self.index] = self.chosen
                nextCell = prevCell
            elif (len(self.openlist) == 1):
                #2 wall case, choose only one in the list
                self.chosen = self.openlist[0]
		self.visitedList[self.index] = self.chosen
                nextCell = self.openlist[0]
                #print "2 wall case"
            #elif (len(self.openlist) == 2 or len(self.openlist) == 3):
            else:
                #1 wall case or no wall case
                #print "1 wall case or no wall case"
                newlist = []
                for cell in self.openlist:
                    if (cell not in closedlist):
                        newlist.append(cell)
                if (len(newlist) == 1):
                    #if theres one thats not in close list, chose it
                    self.chosen = newlist[0]
		    self.visitedList[self.index] = self.chosen
                    nextCell = self.chosen
                elif (len(newlist) == 0):
		    data.write("Both are in the closed list")
		    data.write('\n')
		    data.write("Open List again: " + printClosedList(self.openlist))
		    data.write('\n')
		    data.write("Visited list again: " + printClosedList(self.visitedList))
		    data.write('\n')
		    #newList = []
                    #if both are in closed list chose the one you havent chosen before that wasn't visited in the last two
		    for cell in self.openlist:
			if cell in self.visitedList:
				pass
			else:
		    		data.write("cell chosen: " + str(cell.number))
		    		data.write('\n')
		    		self.chosen = cell
		    		self.visitedList[self.index] = self.chosen
		    		nextCell = self.chosen
				break
		    
                else:
                    #If neither are in closed list, chose the one closer to the final square
                    for cell in newlist:
                        #calculate Manhattan Distance for each cell in self.openlist
                        cell.ManhattanDistance = abs(cell.x-self.x)+abs(cell.y-self.y)+abs(endCell.x-cell.x)+abs(endCell.y-cell.y)
                    #find minimum Manhattan Distance
                    min1 = min(newlist, key=lambda cell: cell.ManhattanDistance)
		    i = newlist.index(min1)
		    del newlist[i]
		    min2 = min(newlist, key=lambda cell:cell.ManhattanDistance)
		    if (min1.ManhattanDistance != min2.ManhattanDistance):
			self.chosen = min1
			self.visitedList[self.index] = self.chosen
			nextCell = self.chosen
		    else:
			#Chose the one that you don't have to turn for
			data.write("Choosing the one which is in the same direction")
			data.write("\n")
			if ((facing == "north" and min1.number == self.number - 7) or (facing == "south" and min1.number == self.number + 7) or (facing == "west" and min1.number == self.number - 1) or (facing == "east" and min1.number == self.number + 1)):
				self.chosen = min1
				self.visitedList[self.index] = self.chosen
				nextCell = self.chosen
			elif ((facing == "north" and min2.number == self.number - 7) or (facing == "south" and min2.number == self.number + 7) or (facing == "west" and min2.number == self.number -1 ) or (facing == "east" and min2.number == self.number + 1)):
				self.chosen = min2
				self.visitedList[self.index] = self.chosen
				nextCell = self.chosen  
			else:
				self.chosen = min1
				self.visitedList[self.index] = self.chosen
				nextCell = self.chosen
				
	if (self.index == 0):
		self.index = 1
	elif (self.index == 1):
		self.index = 0
	#data.write(printClosedList(self.visitedList))
	#data.write('\n')
	del self.openlist[:]
        #Use the movement function to determine how to move
        move(self.number, nextCell.number)

        return nextCell



start_time = time.time()

#Set up pins for input and output
GPIO.setmode(GPIO.BOARD)
in_pin = 40
out_pin1 = 38
out_pin2 = 36
front_wall = 35
right_wall = 33
left_wall = 37
#select_6x6 = 13
#select_7x7 = 11
#maze_select2 = 27
red_LED = 12
servo = 32
button = 15
green_LED = 16

GPIO.setup(in_pin, GPIO.IN)
GPIO.setup(front_wall, GPIO.IN)
GPIO.setup(right_wall, GPIO.IN)
GPIO.setup(left_wall, GPIO.IN)
#GPIO.setup(select_6x6, GPIO.IN)
#GPIO.setup(select_7x7, GPIO.IN)
GPIO.setup(out_pin1, GPIO.OUT, initial = 0)
GPIO.setup(out_pin2, GPIO.OUT, initial = 0)
GPIO.setup(18, GPIO.IN)
GPIO.setup(red_LED, GPIO.OUT, initial = 0)
GPIO.setup(servo, GPIO.OUT, initial = 0)
GPIO.setup(button, GPIO.IN)
GPIO.setup(green_LED, GPIO.OUT)

current_maze = []
maze_mode = ""

GPIO.output(green_LED, 0)
#file for seeing all of the stuff printed to the output
data = open('data.txt', 'a')
data.truncate()

#CHOOSE MAZE MODE HERE
maze_mode = "7x7"

print maze_mode
#Append the objects to the current maze list
data.write("========================================")
data.write('\n')
data.write("    Printing all of the maze squares    ")
data.write('\n')
data.write("========================================")
data.write('\n')

maze = [] #Put all of the generated maze squares in an array

#Generate empty maze
for i in range(1, 50):
    cell = Cell(i, False, False, False, False)
    maze.append(cell)

data.write("========================================")
data.write('\n')
data.write("         Beginning A* Algorithm         ")
data.write('\n')
data.write("========================================")
data.write('\n')
#data.write("Start square: "+ str(startCell.number) + "  End square: " +  str(endCell.number))
#data.write('\n')

prevCell = None
currentCell = None
facing = None
startCell = None
closedlist = []
#Call the searchMaze() algorithm
searchProcess = Process(target=searchMaze, args=(maze_mode,))
searchProcess.start()
searchProcess.join()

#Turn on the redLED and wait for the button push
GPIO.output(red_LED, 1)

while (GPIO.input(button) == 0):
    pass

if (maze_mode != "5x5"):
    #If 6x6 or 7x7, check run the script to the usb
    os.system("./usbCopy.sh")

GPIO.output(red_LED, 0)
GPIO.output(green_LED, 1)

while (GPIO.input(button) == 1):
    pass

#Wait for button push again to run second part
while (GPIO.input(button) == 0):
    pass

GPIO.output(green_LED, 0)

#Once button is pushed run the critical path algorithm
if (maze_mode == "5x5" or maze_mode == "6x6"):
    facing = "north"
else :
    facing = "north"
    
#get the run info from text file cRun.txt created by the searchProcess
secondList = pickle.load(open("cRun.txt", "rb"))
data.write(str(secondList))
data.write('\n')

#prevCell = None
for i in range(0, len(secondList) - 1):
    #move to the next cell
    move(secondList[i], secondList[i+1])
    #update facing
    findFacing(secondList[i+1], secondList[i])

GPIO.output(red_LED, 1)

time.sleep(5)

GPIO.output(red_LED, 0)

#Clean up the GPIO ports
GPIO.cleanup()
data.close()

