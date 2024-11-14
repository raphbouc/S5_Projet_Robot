from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
import time

UA = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
threshold = 10

value_array = []

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

def main():
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

if __name__=='__main__':
	while True:
		main()