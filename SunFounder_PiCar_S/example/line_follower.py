#!/usr/bin/env python
'''
**********************************************************************
* Filename    : line_follower
* Description : An example for sensor car kit to followe line
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-21    New release
**********************************************************************
'''

from SunFounder_Line_Follower import Line_Follower
from picar import front_wheels
from picar import back_wheels
import time
import picar

picar.setup()

REFERENCES = [200, 200, 200, 200, 200]
calibrate = True
forward_speed = 30
backward_speed = 25
turning_angle = 40
acceleration = 1
vmax = 45
vmin = 25

max_off_track_count = 40

delay = 0.0005

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
lf = Line_Follower.Line_Follower()

lf.references = REFERENCES
fw.ready()
bw.ready()
fw.turning_max = 45

def straight_run():
	while True:
		bw.speed = 70
		bw.forward()
		fw.turn_straight()

def setup():
	if calibrate:
		cali()

def augment_speed(speed):
	newspeed = speed + acceleration
	return newspeed

def reduce_speed(speed):
	newspeed = speed - acceleration
	return newspeed

def forward():
	global turning_angle
	off_track_count = 0
	bw.speed = forward_speed
	speed = forward_speed

	a_step = 3
	b_step = 10
	c_step = 30
	d_step = 45
	bw.forward()

	while True :
		lt_status_now = lf.read_digital()
		# Angle calculate
		if	lt_status_now == [0,0,1,0,0]:
			step = 0
			if speed < vmax:
				speed = augment_speed(speed)
				bw.speed = speed
		elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
			step = a_step
			if speed < vmax:
				speed = augment_speed(speed)
				bw.speed = speed
		elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
			step = b_step
			if speed < vmax:
				speed = augment_speed(speed)
				bw.speed = speed
		elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
			step = c_step
			if speed > vmin:
				speed = reduce_speed(speed)
				bw.speed = speed
		elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
			step = d_step
			if speed > vmin:
				speed = reduce_speed(speed)
				bw.speed = speed
		elif sum(lt_status_now) > 3 : 
			break
		# Direction calculate
		if	lt_status_now == [0,0,1,0,0]:
			off_track_count = 0
			fw.turn(90)
		# turn right
		elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
			off_track_count = 0
			turning_angle = int(90 - step)
		# turn left
		elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
			off_track_count = 0
			turning_angle = int(90 + step)
		elif lt_status_now == [0,0,0,0,0]:
			off_track_count += 1
			if off_track_count > max_off_track_count:
				#tmp_angle = -(turning_angle - 90) + 90
				tmp_angle = (turning_angle-90)/abs(90-turning_angle)
				tmp_angle *= fw.turning_max
				bw.speed = backward_speed
				bw.backward()
				fw.turn(tmp_angle)
				
				lf.wait_tile_center()
				bw.stop()

				fw.turn(turning_angle)
				time.sleep(0.2)
				bw.speed = forward_speed
				bw.forward()
				time.sleep(0.2)

				

		else:
			off_track_count = 0
	
		fw.turn(turning_angle)
		time.sleep(delay)

	return speed

def stop(speed):
	while (speed > 0) : 
		speed = reduce_speed(speed)
		bw.speed = speed
		fw.turn(90)
		bw.stop()
		time.sleep(delay)

def wait_tile_1of3():
		while True:
			lt_status = lf.read_digital()
			if lt_status[2] == 1 or (lt_status[1] == 1 and lt_status[2] == 1) or (lt_status[3] == 1 and lt_status[2]):
				break

def backward():
	global turning_angle
	off_track_count = 0
	bw.speed = backward_speed

	a_step = 0
	b_step = 0
	c_step = 30
	d_step = 45
	step_offset = 15
	bw.backward()

	lt_status_now = lf.read_digital()
	while (lt_status_now < 4):
		lt_status_now = lf.read_digital()
		time.sleep(delay)
	time.sleep(2)
	while True :
		lt_status_now = lf.read_digital()
		# Angle calculate
		if	lt_status_now == [0,0,1,0,0]:
			step = 0
		elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
			step = a_step
		elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
			step = b_step
		elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
			step = c_step
		elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
			step = d_step
		# Direction calculate
		if	lt_status_now == [0,0,1,0,0]:
			off_track_count = 0
			fw.turn(90)
		elif lt_status_now[0] == 1:
			print('ICI')
			turning_angle = int(90 + step)
			fw.turn(turning_angle)
			time.sleep(0.2)
			bw.forward()
			time.sleep(1)
			bw.stop()
			time.sleep(0.2)
			fw.turn(90 - step_offset)
			time.sleep(0.2)
			bw.backward()
			time.sleep(0.5)
			fw.turn(90)
			time.sleep(0.2)
			lf.wait_tile_center
		elif lt_status_now[4] == 1:
			print('ICI2')
			turning_angle = int(90 - step)
			fw.turn(turning_angle)
			time.sleep(0.2)
			bw.forward()
			time.sleep(1)
			bw.stop()
			time.sleep(0.2)
			fw.turn(90 + step_offset)
			time.sleep(0.2)
			bw.backward()
			time.sleep(0.5)
			fw.turn(90)
			time.sleep(0.2)
			lf.wait_tile_center
		elif lt_status_now == [0,0,0,0,0]:
			off_track_count += 1
			""" if off_track_count > max_off_track_count:
				#tmp_angle = -(turning_angle - 90) + 90
				tmp_angle = (turning_angle-90)/abs(90-turning_angle)
				tmp_angle *= fw.turning_max
				bw.speed = backward_speed
				bw.forward()
				fw.turn(tmp_angle)
				
				lf.wait_tile_center()
				bw.stop()

				fw.turn(turning_angle)
				time.sleep(0.2)
				bw.speed = forward_speed
				bw.backward()
				time.sleep(0.2) """

				

		else:
			off_track_count = 0
	
		fw.turn(turning_angle)
		time.sleep(delay)


def cali():
	time.sleep(20)
	references = [0, 0, 0, 0, 0]
	print("cali for module:\n  first put all sensors on white, then put all sensors on black")
	mount = 100
	fw.turn(70)
	print("\n cali white")
	time.sleep(4)
	fw.turn(90)
	white_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	fw.turn(110)
	time.sleep(10)
	print("\n cali black")
	time.sleep(4)
	fw.turn(90)
	black_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print("Middle references =", references)
	time.sleep(10)

def destroy():
	bw.stop()
	fw.turn(90)

def main():
	speed = forward()
	stop(speed)
	backward()


if __name__ == '__main__':
	try:
		try:
			while True:
				setup()
				main()
				#straight_run()
		except Exception as e:
			print(e)
			print('error try again in 5')
			destroy()
			time.sleep(5)
	except KeyboardInterrupt:
		destroy()

