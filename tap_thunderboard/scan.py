from bluepy.btle import *
import struct
import sys
import datetime
from time import sleep
from tap_thunderboard.tbsense import Thunderboard
import threading

def getThunderboards():
    scanner = Scanner(0)
    devices = scanner.scan(3)
    tbsense = dict()
    for dev in devices:
        scanData = dev.getScanData()
        for (adtype, desc, value) in scanData:
            if desc == 'Complete Local Name':
                if 'Thunderboard #' in value:
                    deviceId = int(value.split('#')[-1])
                    tbsense[deviceId] = Thunderboard(dev)

    return tbsense

def sensorLoop(fb, tb, devId):
    #session = fb.getSession(devId)
    #tb.session = session
    
    value = tb.char['power_source_type'].read()
    if ord(value) == 0x04:
        tb.coinCell = True

    while True:

        text = ''

        text += '\n' + tb.name + '\n'
        data = dict()
        data['deviceId'] = devId
        data['when'] = datetime.datetime.now().isoformat()

        try:

            for key in tb.char.keys():
                if key == 'temperature':
                        data['temperature'] = tb.readTemperature()
                        text += 'Temperature:\t{} C\n'.format(data['temperature'])

                elif key == 'humidity':
                    data['humidity'] = tb.readHumidity()
                    text += 'Humidity:\t{} %RH\n'.format(data['humidity'])

                elif key == 'ambientLight':
                    data['ambientLight'] = tb.readAmbientLight()
                    text += 'Ambient Light:\t{} Lux\n'.format(data['ambientLight'])

                elif key == 'uvIndex':
                    data['uvIndex'] = tb.readUvIndex()
                    text += 'UV Index:\t{}\n'.format(data['uvIndex'])

                elif key == 'co2' and tb.coinCell == False:
                    data['co2'] = tb.readCo2()
                    text += 'eCO2:\t\t{}\n'.format(data['co2'])

                elif key == 'voc' and tb.coinCell == False:
                    data['voc'] = tb.readVoc()
                    text += 'tVOC:\t\t{}\n'.format(data['voc'])

                elif key == 'sound':
                    data['sound'] = tb.readSound()
                    text += 'Sound Level:\t{}\n'.format(data['sound'])

                elif key == 'pressure':
                    data['pressure'] = tb.readPressure()
                    text += 'Pressure:\t{}\n'.format(data['pressure'])

        except Exception as e:
            print(e, file=sys.stderr)
            return

        #print(text)
        print(data)
        sys.stdout.flush()
        #fb.putEnvironmentData(session, data)
        sleep(1)


def dataLoop(fb, thunderboards):
    threads = []
    for devId, tb in thunderboards.items():
        sensorLoop(fb, tb, devId)
        #t = threading.Thread(target=sensorLoop, args=(fb, tb, devId))
        #threads.append(t)
        #print('Starting thread {} for {}'.format(t, devId))
        #t.start()


def run():
    fb = None
    while True:
        thunderboards = getThunderboards()
        if len(thunderboards) == 0:
            print("No Thunderboard devices found!", file=sys.stderr)
        else:
            dataLoop(fb, thunderboards)