from ultrasonic_module import Ultrasonic_Avoidance
import time
from filter import apply_fir_filter

UA = Ultrasonic_Avoidance()
threshold = 10



def main(array):
	
	distance = UA.get_distance()
	array.append(distance)
	filter = apply_fir_filter(array)
	status = UA.less_than(threshold)
	if filter[-1] != -1:
		print('distance', filter[-1], 'cm')
		time.sleep(0.2)
	else:
		print(False)
	""" if status == 1:
		print("Less than %d" % threshold)
	elif status == 0:
		print("Over %d" % threshold)
	else:
		print("Read distance error.")
 """
if __name__=='__main__':
	array = []
	for i in range(304): 
		distance = UA.get_distance()
		array.append(distance)
	while True:
		main(array)
