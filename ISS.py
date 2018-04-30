import sqlite3
import datetime
import time
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)

isTimePassed = 0	#Flag for checking next closest time
timeDiff = 0		#Difference between now and next closest
addNxtDy = 0		#Flag for checking if 24 Hrs need to be added
theTimeNow = 0		#Stores the time now
nextClosest = 0		#Stores next closest time
justPassed = 0		#Stores just passed time
StartMaxEnd = "0"	#Flag for checking if next closest is timeStart, timeMax or timeEnd
currentYear = 2016


def sitAware(strToCheck):	#Provides "Situational Awareness", "lowers" isTimePassed flag, and stores data in timeDiff, nextClosest and theTimeNow
	global isTimePassed
	global timeDiff
	global addNxtDy
	global nextClosest
	global theTimeNow

	nowTime = datetime.datetime.now()
	timeToCheck = datetime.datetime.strptime(strToCheck, "%d %b %H:%M:%S")
	if addNxtDy == 1: timeToCheck += datetime.timedelta(hours=24)		#Adjusts time to be compared by 1 day
	timeToCheck = timeToCheck.replace(year = currentYear)
	
	if nowTime >= timeToCheck:
		isTimePassed = 1		#This Time has passed, hence keep flag at 1
	elif nowTime < timeToCheck:
		isTimePassed = 0		#The Time is yet to come, hence change flag to 0
		timeDiff = timeToCheck - nowTime
		nextClosest = timeToCheck
		theTimeNow = nowTime


def nxtDyChk(timePrev, timeNext):	#Checks if time crossed midnight, and raises addNxtDy flag
	global addNxtDy
	Prev = datetime.datetime.strptime(timePrev, "%H:%M:%S")
	Next = datetime.datetime.strptime(timeNext, "%H:%M:%S")
	if Next < Prev:
		addNxtDy = 1


def adjustTimeMax(origDate, origTimeStart, origTimeMax):		#Checks if timeMax needs adjustment (only called when sitAware finds upcoming event to be timeEnd)
	prevTime = datetime.datetime.strptime(origTimeStart, "%H:%M:%S")
	nextTime = datetime.datetime.strptime(origTimeMax, "%H:%M:%S")
	if nextTime < prevTime:
		newMax = datetime.datetime.strptime(origDate, "%d %b %H:%M:%S")
		newMax += datetime.timedelta(hours=24)
		newMax = newMax.replace(year = currentYear)
		return newMax
	elif nextTime >= prevTime:
		newMax = datetime.datetime.strptime(origDate, "%d %b %H:%M:%S")
		newMax = newMax.replace(year = currentYear)
		return newMax


def LEDSlow():
	
	ser.write(b'0')
	time.sleep(10)
	time.sleep(0.5)	#To compensate for delay on Arduino side


def LEDFast():
	
	ser.write(b'1')
	time.sleep(10)
	time.sleep(0.5)	#To compensate for delay on Arduino side


def LEDAtMax():
	
	ser.write(b'2')
	time.sleep(5)
	time.sleep(0.5)	#To compensate for delay on Arduino side


exitWhile = False	#Flag to exit the While loop and end the script
while (exitWhile == False):
	
	conn = sqlite3.connect('/home/pi/Code/ISS.db')
	curs = conn.cursor()
	ISSData = curs.execute('SELECT * FROM ISS ORDER BY ID')
	
	for item in ISSData:
		dateStr = item[1] + " " + item[2]
		sitAware(dateStr)
		if isTimePassed == 0:		#Nothing to do. Set variable to "Start" and exit the For loop.
			StartMaxEnd = "Start"
			break
	
		dateStr = item[1] + " " + item[3]
		nxtDyChk(item[2], item[3])		#To check if timeMax crosses midnight, if yes then sitAware will adjust
		sitAware(dateStr)
		if isTimePassed == 0:			#Upcoming event is timeMax, so set variables accordingly and exit loop
			StartMaxEnd = "Max"		#The following lines set the variable justPassed to timeStart
			startStr = item[1] + " " + item[2]
			startStrStripped = datetime.datetime.strptime(startStr, "%d %b %H:%M:%S")
			startStrStripped = startStrStripped.replace(year = currentYear)
			justPassed = startStrStripped
			break
	
		dateStr = item[1] + " " + item[4]
		nxtDyChk(item[3], item[4])		#To check if timeEnd crosses midnight, if yes then sitAware will adjust
		sitAware(dateStr)
		if isTimePassed == 0:			#Upcoming event is timeEnd, so set variables accordingly and exit loop
			StartMaxEnd = "End"		#The following lines set the variable justPassed to timeMax
			maxStr = item[1] + " " + item[3]
			justPassed = adjustTimeMax(maxStr, item[2], item[3])	#To make sure that timeMax also needs to be adjusted in case timeEnd was adjusted
			break
		addNxtDy = 0		#To reset before next iteration in case timeEnd and/or timeMax+timeEnd were compensated for date change
	
	curs.close()
	
	
#	print ("isTimePassed ", isTimePassed)
#	print ("timeDiff ", timeDiff)
#	print ("addNxtDy ", addNxtDy)
#	print ("theTimeNow ", theTimeNow)
#	print ("nextClosest ", nextClosest)
#	print ("justPassed ", justPassed)
#	print ("StartMaxEnd ", StartMaxEnd)
	
	
	if isTimePassed == 0:
		if StartMaxEnd == "Max":
			if theTimeNow > (nextClosest - datetime.timedelta(seconds = 10)):
				LEDAtMax()
			elif timeDiff < ((nextClosest - justPassed) / 3):
				LEDFast()
			else:
				LEDSlow()
		elif StartMaxEnd == "End":
			if theTimeNow < (justPassed + datetime.timedelta(seconds = 10)):
				LEDAtMax()
			elif timeDiff > ((nextClosest - justPassed) * 2 / 3):
				LEDFast()
			else:
				LEDSlow()
		else:
		#	time.sleep(10)	#To reduce processor load
			exitWhile = True
	else:
	#	time.sleep(10)	#To reduce processor load
		exitWhile = True

	#Reset variables
	isTimePassed = 0
	timeDiff = 0
	addNxtDy = 0
	theTimeNow = 0
	nextClosest = 0
	justPassed = 0
	StartMaxEnd = "0"

