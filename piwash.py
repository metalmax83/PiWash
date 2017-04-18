from RPi import GPIO as gpio
from time import sleep
import lcddriver
from math import floor, ceil

################################################
#Hardware Settings (RPi3/2)
gpio.setmode(gpio.BOARD)

#Servo Pins
pinBrushArm = 11
pinSuctionArmMove = 12
pinSuctionArmLift = 13

#Relais Pins
pinMotor = 15
pinVacuumPump = 16
pinDosingPump = 18
pinBrushVibration = 32

#Button Pins
pinBack = 29
pinStart = 31
pinUp = 33
pinDown = 35

#Fluid Level Sensor Pins
pinOutUsedFluid = 36
pinInUsedFluid = 37
pinOutFreshFluid = 38
pinInFreshFluid = 40

################################################
#Default Settings

#Durations (in s)
durWashing = 180
durVibration = 150
durRound = 1.35
durFreshFluidPumping = durRound * 4

#ServoPositions (in degrees)
posSuctionInner = 90
posSuctionOuter = 60
posSuctionRest = 0
posSuctionLow = 0
posSuctionLift = 90

posBrushArmLow = 0
posBrushArmLift = 90


################################################
#Constants

allLeft = ("L","L","L","L")
allRight = ("R","R","R","R")
allCenter = ("C","C","C","C")

lastChar1 = 0x93
lastChar2 = 0xD3
lastChar3 = 0xA7
lastChar4 = 0xE7

lastChars = [lastChar1,lastChar2,lastChar3,lastChar4]

arrowLeft = 0x7F

################################################
#Global variables

currentMenu = None
currentMenuPosition = 0
currentCursorLine = 2
currentMenuItem = ""
currentMenuItemFunc = None
currentlyBlocked = False

################################################
def buttonCallback(pin):
	print("Button Pushed %d"%pin)
	global currentCursorLine
	if pin==pinDown:
		maxPos = len(currentMenu["items"])
		delCursor()
		if currentCursorLine < 4:
			currentCursorLine+=1
		else:
			if currentMenuPosition < maxPos - 3:
				scrollMenu(0)
		setCursor()
	if pin==pinUp:
		delCursor()
		if currentCursorLine > 2:
			currentCursorLine-=1
		else:
			if currentMenuPosition > 0:
				scrollMenu(1)
		setCursor()
	
	if pin==pinStart:
		if currentlyBlocked:
			return 0
		print(currentMenuItemFunc.__name__)
		currentMenuItemFunc()

def setupPins():
	gpio.setup(pinDown,gpio.IN,pull_up_down=gpio.PUD_UP)
	gpio.add_event_detect(pinDown, gpio.RISING, callback=buttonCallback, bouncetime=250)
	gpio.setup(pinUp,gpio.IN,pull_up_down=gpio.PUD_UP)
	gpio.add_event_detect(pinUp, gpio.RISING, callback=buttonCallback, bouncetime=250)
	gpio.setup(pinStart,gpio.IN,pull_up_down=gpio.PUD_UP)
	gpio.add_event_detect(pinStart, gpio.RISING, callback=buttonCallback, bouncetime=250)
	gpio.setup(pinMotor,gpio.OUT)
	gpio.output(pinMotor,gpio.HIGH)

def startCleaning():
	global currentlyBlocked
	currentlyBlocked = True
	gpio.output(pinMotor,gpio.LOW)
	sleep(10)
	gpio.output(pinMotor,gpio.HIGH)
	currentlyBlocked = False
def checkFluidLevels():
	pass

def showStatistics():
	pass

def showOptions():
	pass


################################################
#Menu Structure
mainMenu = {"title":"PiWash - Main Menu"}
mainMenu["items"] = ["Start LP Cleaning","Fluid Levels","Statistics","Options"]
mainMenu["functions"] = [startCleaning,checkFluidLevels,showStatistics,showOptions]



def showMenu(menu):
	global currentMenu; global currentMenuPosition; global currentCursorLine
	currentMenu = menu
	currentMenuPosition = 0
	currentCursorLine = 2
	numOfItems = len(menu["items"])
	if numOfItems>=3:
		strList = [menu["title"]] + menu["items"][:3]
	else:
		strList = [menu["title"]] + menu["items"] + [" " for i in range(3-numOfItems)]
	updateLcd(strList)
	setCursor()

def scrollMenu(dir):
	global currentMenu; global currentMenuPosition; global currentCursorLine
	if dir == 0:
		currentMenuPosition+=1
	else:
		currentMenuPosition-=1
	strList = [currentMenu["title"]] + currentMenu["items"][currentMenuPosition:currentMenuPosition+3]
	print(strList)
	updateLcd(strList)
	
def setCursor():
	global currentMenuItem; global currentMenuItemFunc
	pos = lastChars[currentCursorLine-1]
	lcd.lcd_write(pos)
	lcd.lcd_write(arrowLeft,lcddriver.Rs)
	lcd.lcd_write(pos)
	currentMenuItem = currentMenu["items"][currentMenuPosition+currentCursorLine-2]
	currentMenuItemFunc = currentMenu["functions"][currentMenu["items"].index(currentMenuItem)]

def delCursor():
	pos = lastChars[currentCursorLine-1]
	lcd.lcd_write(pos)
	lcd.lcd_write(ord(" "),lcddriver.Rs)

def updateLcd(strList,alignList=("L","L","L","L"),delay=0):
	lcd.lcd_clear()
	for line,strLine in enumerate(strList):
		if alignList[line] == "R":
			strLine = " " * (20-len(strLine)) + strLine
		elif alignList[line] == "C":
			numberOfSpaces = (20-len(strLine))/2
			strLine = " " *int(floor(numberOfSpaces)) + strLine + " " * int(ceil(numberOfSpaces))
		lcd.lcd_display_string(strLine,line+1)
		if not line==4: sleep(delay)
	
	
def startUp():
	global lcd
	lcd = lcddriver.lcd()
	lcd.lcd_clear()
	strWelcome = ["Welcome","to","PiWash","Record Cleaner"]
	updateLcd(strWelcome,alignList=allCenter,delay=.3)
	sleep(3)
	showMenu(mainMenu)
	setupPins()
	
	

def main():
	startUp()
	while True:
		pass
	
if __name__=="__main__":
	main()
	
	
