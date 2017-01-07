import serial

ser = serial.Serial('/dev/tty.usbmodem1421', 9600)

ax = ay = az = 0.0

def read_data():
    global ax, ay, az
    ax = ay = az = 0.0
    line_done = 0

    # request data by sending a dot
    ser.write(".")
    #while not line_done:
    line = ser.readline() 
    angles = line.split(", ")
    if len(angles) == 3:    
        ax = float(angles[0])
        ay = float(angles[1])
        az = float(angles[2])
        line_done = 1 
        

def main():
    while 1:
        read_data()

    ser.close()
main()
    
    