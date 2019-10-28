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
 Arduino (NANO)+ Gyroscope(MPU6050)を動作させるには数秒の準備時間の後にキーボードから”２”を
 入力してやる必要があり、ここでは５秒待った後に”２”をシリアル入力してジャイロ(MPU6050)を起動
 します。
'''
ser = serial.Serial('/dev/cu.usbserial-A104WPYL',115200) # 使用しているMac の入力
time.sleep(5) #

f = open('gyro.csv','w') # ジャイロの結果を入れるファイルを用意

'''
# ジャイロの準備が出来たら　Arduinoから”Send any character to begin DMP programming and demo: ”のメッセージが送られます。
'''
for loop in range(10): # ”Send” を含むメッセージの受信を確認する。取りそのねを避けるために10回トライさせた
    l = ser.readline()
    try:
        line0       = l.decode('utf-8')
    except UnicodeDecodeError:
        line0 = " "
        pass
    line1       =  line0.strip("^M")

    refer = 'Send' # 準備完了の　'Send' を確認
    if  refer in line0 :
        ser.write(b'2') # '2'をバイト列でArduinoに送信
    print(line1) # 状態をモニタ、10回トライは不要かもしれない

#------- End  Gyro inisialize -------------------------
'''
筋電データーをマイク端子で入力するpyaudio の条件を決めます。

'''
chunk = 1024 #　データーを取り込む　ひとかたまり、１０２４ポイントのデータをまとめて取り込む
FORMAT = pyaudio.paInt16
CHANNELS = 1 # モノラル
RATE = 44100 # 1秒に44100のchunk つまり　　44100 x 1024 /1sec のデータサンプリング
RECORD_SECONDS = 3 # ３秒間のデーターサンプルとした
#WAVE_OUTPUT_FILENAME = "sample.wav"# 出力データ　を.wav 形式で保存もできる
iDeviceIndex = 2 #  ? web からのコピーだったと思います

p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                input_device_index = iDeviceIndex,
                frames_per_buffer = chunk)

print("* recording") # 確認のためpyaudio のスタートを宣言（実装では不要）
all = []
starttime                    = time.time() #時間を測るために
dec_data                    = np.zeros((2,1024))
dec_data_Row          = np.zeros(1024)
dec_data_Rowtemp = np.zeros(1024)

cycle = 0
dec_data_Row=np.array([[],[]])

'''
　pyaudio　のデータ取得回数をいれます。この場合は三秒で何チャンク回かを決めています。
 　for の中にジャイロのデータ取得も含まれていますので、1chunk で1回ジャイロのデーター取得となります。
'''
for i in range(0, int(RATE / chunk * RECORD_SECONDS)): # pyaudio　のデータ取得回数をいれます。

#------------ Gyro functin --------------------

    l = ser.readline()

    line0      = l.decode('utf-8') #文字の指定
    line01     = line0.strip("^M") # Aruduinoからの改行文字を削除
    line1      = str(line01)

    line01     = line1.replace("	"," ") #長い空白を短めた
    line02     = line01.split(' ') #　空白文字で　ジャイロの値を分離
    print(line02)

    timeNow   = time.time()-starttime #現在の時間
    # line3 =  時間　＋　x軸　　＋　y軸　　＋z軸
    line3     = str(timeNow) + ": " + str(line02[1]) + str(": ")+str(line02[2]) +str(":")+ str(line02[3])
    data = stream.read(chunk)
    data0 = data
    all.append(data0)

    dec_data[0:,] = np.frombuffer(data,dtype="int16") / float(2**15)
#    print(dec_data)
#    sys.exit()

    dec_data[1:,]=str(line02[1])
    dec_data_Row = np.concatenate((dec_data_Row,dec_data),axis =1)
    f.write(line3)

    cycle = cycle +1
#--------- End Gyro functin
f.close()
print("* donerecording")
stream.close()
p.terminate()

data0 =b''.join(all)

print(np.shape(data))
print(np.shape(dec_data))

result = np.frombuffer(data0,dtype="int16") / float(2**15)# pyaudio 筋電のデータ
pylab.plot(result)
pylab.ylim([-1.0,1.0])
pylab.show()
elapsed_time = time.time() - start
print (("elapsed_time:{0}".format(elapsed_time)) + "[sec]")

outfile = open('EMG_wave.csv','w')#筋電波形
out = csv.writer(outfile)
out.writerows(map(lambda x: [x], result))
outfile.close()
