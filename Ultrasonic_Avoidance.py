#!/usr/bin/env python
'''
**********************************************************************
* Filename    : Ultrasonic_Avoidance.py
* Description : A module for SunFounder Ultrasonic Avoidance
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-26    New release
**********************************************************************
'''
import time
import RPi.GPIO as GPIO

value_array = []

class Ultrasonic_Avoidance(object):
	timeout = 0.0005

	def __init__(self, channel):
		self.channel = channel
		GPIO.setmode(GPIO.BCM)

	def distance(self):
	# 	Todo
		pass

def push_to_data_array(input, array, max_length):
    if len(array) < max_length:
        array.append(input)
    else:
        array.pop(0)
        array.append(input)

def median_input(array):
    sorted_array = sorted(array)
    n = len(sorted_array)
    
    # Calculer la médiane
    if n % 2 == 0:  # Si le nombre d'éléments est pair
        median = (sorted_array[n // 2 - 1] + sorted_array[n // 2]) / 2
    else:  # Si le nombre d'éléments est impair
        median = sorted_array[n // 2]
        
    return median

def test():
	UA = Ultrasonic_Avoidance(17)
	threshold = 10
	while True:
		distance = UA.get_distance()
		push_to_data_array(distance, value_array)
		output_val = median_input(value_array)
		status = UA.less_than(threshold)
		if distance != -1:
			print('distance', distance, 'cm')
			print(f"filtered distance {output_val}")
			time.sleep(0.2)
		else:
			print(False)
		if status == 1:
			print("Less than %d" % threshold)
		elif status == 0:
			print("Over %d" % threshold)
		else:
			print("Read distance error.")

if __name__ == '__main__':
	test()
