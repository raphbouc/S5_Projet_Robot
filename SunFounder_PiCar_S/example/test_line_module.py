from SunFounder_Line_Follower import Line_Follower
import line_follower as cali
import time

lf = Line_Follower.Line_Follower()

previous = lf.read_analog()
while True:
	cali.cali()
	current = lf.read_analog()
	print("Previous : ", previous)
	print("Current : ", current)
	print("Diff : ", [current[i] - previous[i] for i in range(len(current))])
	print(lf.read_digital())
	print('')
	previous = current
	time.sleep(2)

