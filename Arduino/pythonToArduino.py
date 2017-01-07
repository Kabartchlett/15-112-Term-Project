from time import sleep
import serial

ser = serial.Serial('/dev/tty.usbmodem1421',9600)
x = 0
y = 0
z = 0

def main():


	while(True):
		line = ser.readline()			
		listOfCoord = line.split(":")
		
		if (len(listOfCoord) >= 6):
			x = listOfCoord[1]
			print("X: %s" % x)				
			y = listOfCoord[3]
			print("Y: %s" % y)
			z = listOfCoord[5]
			print("Z: %s" % z)
			
		else:
			print("Waiting......")



main()






