import pyaudio
import wave
import sys
import os
import numpy as np
import time
#import src
import serial
import pylab
import string
import csv
import struct

start = time.time()
#----- Gyro initialize------------------------------
'''
A few second Calibration for Arduino + Gyroscope(MPU6050)
until Gyro is ready.
We have to usually enter the number '2' from Key board.
 So '2' is entered using script.
'''
ser = serial.Serial('/dev/cu.usbserial-A104WPYL',115200)
time.sleep(5)

f = open('test.txt','w')

for loop in range(10):
    l = ser.readline()
    try:
        line0       = l.decode('utf-8')
    except UnicodeDecodeError:
        line0 = " "
        pass
#	line0       = l.decode('utf-8')
    line1       =  line0.strip("^M")

    refer = 'Send'
    if  refer in line0 :
        ser.write(b'2')
    print(line1)

#------- End  Gyro inisialize -------------------------

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
#WAVE_OUTPUT_FILENAME = "sample.wav"
iDeviceIndex = 2

p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                input_device_index = iDeviceIndex,
                frames_per_buffer = chunk)

print("* recording")
all = []
starttime                    = time.time()
dec_data                    = np.zeros((2,1024))
dec_data_Row          = np.zeros(1024)
dec_data_Rowtemp = np.zeros(1024)

cycle = 0
dec_data_Row=np.array([[],[]])

for i in range(0, int(RATE / chunk * RECORD_SECONDS)):

#------------ Gyro functin --------------------

    l = ser.readline()
    line0      = l.decode('utf-8')
    line01     = line0.strip("^M")
    line1      = str(line01)

    line01     = line1.replace("	"," ")
    line02     = line01.split(' ')

    timeNow   = time.time()-starttime
    line02_noCL = float(line02[3].rstrip())
    line02_noCL_math = line02_noCL/2.0

    line3     = str(timeNow) + ": " + str(line02[1]) + str(": ")+str(line02[2]) +str(":")+ str(float(line02_noCL_math))+":"+str(line02[3])
    data = stream.read(chunk)
    data0 = data
    all.append(data0)

#    print(" line3 = {0} , data = {1} ".format(line3,data))
#    sys.ext()
#    all.append(data)

    dec_data[0:,] = np.frombuffer(data,dtype="int16") / float(2**15)
#    print(dec_data)
#    sys.exit()

    dec_data[1:,]=str(line02[1])
    dec_data_Row = np.concatenate((dec_data_Row,dec_data),axis =1)
    print("This is  ".format(dec_data_Row))

    print(line3)
    print(dec_data_Row)
    print('shape is :',np.shape(dec_data_Row))
    print('sycle is  :', cycle)
#    f.write(dec_data_Row)

    f.write(line3)

    cycle = cycle +1
#    following "with " script ocure the code problem . never use
#    with open('some.csv', 'w') as f:
#        writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
#        writer.writerows() # 2次元配列も書き込める
#    writer.writerow(list)     # list（1次元配列）の場合
#    writer.writerows() # 2次元配列も書き込める
#    if cycle >3 :
#        with open('some.csv', 'w') as h:
#            writer = csv.writer(h, dec_data_Row)
#        h.close()
#        sys.exit()

#--------- End Gyro functin
f.close()
print("* donerecording")
stream.close()
p.terminate()

data0 =b''.join(all)
print("all is ******** %s" % str(data0) )# if this line is removed, Error occur.

print(np.shape(data))
print(np.shape(dec_data))

#data = b''.join(all).decode()
#data = b''.join(all).decode()
#data = b''.join(comments).decode()
#data = "".join([b'www', b'www'])
result = np.frombuffer(data0,dtype="int16") / float(2**15)
print(result)
pylab.plot(result)
pylab.ylim([-1.0,1.0])
pylab.show()
elapsed_time = time.time() - start
print (("elapsed_time:{0}".format(elapsed_time)) + "[sec]")

outfile = open('fin_ids.csv','w')
out = csv.writer(outfile)
out.writerows(map(lambda x: [x], result))
#out.writerows(map(lambda x: [x], list(dec_data_Row)))
outfile.close()
