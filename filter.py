import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from typing import Literal


def averaged_input(input, array):
    new_avg = (sum(array) + input) / (len(array) + 1)
    return new_avg


def push_to_data_array(input, array, max_length):
    if len(array) < max_length:
        array.append(input)
    else:
        array.pop(0)
        array.append(input)


def create_fake_measurements(min=20, max=100, min_error=5, max_error=150, length=1000, num_errors=50):
    smooth_data = np.linspace(min, max, length)

    error_indices = np.random.choice(len(smooth_data), num_errors, replace=False)
    for idx in error_indices:
        # Random errors between min error and max error to simulate sonar misreadings
        smooth_data[idx] = np.random.uniform(min_error, max_error)

    # Convert to a list for easy viewing/manipulation
    fake_measurements = smooth_data.tolist()
    return fake_measurements


def test_linear_increment_floating_average(input_min_value=20, input_max_value=100, input_min_error=5,
                          input_max_error=150, fake_input_length=1000, num_errors=50, max_length=10):
    
    fake_measurements = create_fake_measurements(input_min_value, input_max_value, input_min_error,
                                                 input_max_error, fake_input_length, num_errors)
    data = fake_measurements[:max_length]
    filtered_data = []
    for input in fake_measurements[max_length:]:
        print("==========================")
        print(f"Valeur en entree: {input}")
        push_to_data_array(input, data, max_length)
        output = averaged_input(input, data)
        filtered_data.append(output)
        print(f"Valeur en sortie: {output}")

    print(f"longueur des donnees retenu: {len(data)}")
    print(f"longueur de filtered data {len(filtered_data)}")
    rmse = calculate_rmse(fake_measurements[max_length:], filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(fake_measurements[max_length:], label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title(f"Valeur d'entrée vs valeur de sortie pour une moyenne flottante de {max_length} échantillons")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def generate_step_increment(min_error=5, max_error=200, num_errors=10):
    # Parameters
    total_samples = 1000
    step_interval = 100 
    initial_value = 50
    increment = 10

    # Generate step signal
    steps = total_samples // step_interval
    step_signal = np.array([initial_value + i * increment for i in range(steps) for _ in range(step_interval)])

    error_indices = np.random.choice(len(step_signal), num_errors, replace=False)
    for idx in error_indices:
        # Random errors between min error and max error to simulate sonar misreadings
        step_signal[idx] = np.random.uniform(min_error, max_error)

    return step_signal.tolist()

def test_step_increment_floating_average(max_length=10):
    step_signal = generate_step_increment()
    data = step_signal[:max_length]
    filtered_data = []
    for input in step_signal[max_length:]:
        print("==========================")
        print(f"Valeur en entree: {input}")
        push_to_data_array(input, data, max_length)
        output = averaged_input(input, data)
        filtered_data.append(output)
        print(f"Valeur en sortie: {output}")

    print(f"longueur des donnees retenu: {len(data)}")

    rmse = calculate_rmse(step_signal[max_length:], filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(step_signal[max_length:], label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title(f"Valeur d'entrée vs valeur de sortie pour une moyenne flottante de {max_length} échantillons")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()


def apply_fir_filter(data, cutoff=1, fs=8, numtaps=101):

    # Design a FIR filter with the specified cutoff frequency and number of taps
    fir_coeff = signal.firwin(numtaps, cutoff, fs=fs)
    # The length of the filtered data must be 3x + 1 the number of taps
    # numtaps is the filter order, the bigger the better but it also requires a bigger buffer
    filtered_data = signal.filtfilt(fir_coeff, [1.0], data)
    
    return filtered_data


def test_linear_increment_fir_filter(input_length=1000, input_errors=100, fc=1, fs=8, filter_numtaps=101):
    input_data = create_fake_measurements(length=input_length, num_errors=input_errors)
    buffer_array = []
    filtered_data = []

    for input in input_data:
        print("========================")
        push_to_data_array(input, buffer_array, (filter_numtaps*3+1))
        if len(buffer_array) < (filter_numtaps*3+1):
            print(f"Loading Buffer")
            continue
        print(f"Valeur en entrée: {input}")
        filtered_data = apply_fir_filter(buffer_array, fc, fs, filter_numtaps)
        print(f"Valeur en sortie: {filtered_data[-1]}")
    
    rmse = calculate_rmse(buffer_array, filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(buffer_array, label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title("Valeur d'entrée vs valeur de sortie dans le buffer à la fin du test")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def test_step_increment_fir_filter(input_length=1000, input_errors=100, fc=1, fs=8, filter_numtaps=101):
    step_signal = generate_step_increment()
    buffer_array = []
    filtered_data = []

    for input in step_signal:
        print("========================")
        push_to_data_array(input, buffer_array, (filter_numtaps*3+1))
        if len(buffer_array) < (filter_numtaps*3+1):
            print(f"Loading Buffer")
            continue
        print(f"Valeur en entrée: {input}")
        filtered_data = apply_fir_filter(buffer_array, fc, fs, filter_numtaps)
        print(f"Valeur en sortie: {filtered_data[-1]}")

    rmse = calculate_rmse(buffer_array, filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(buffer_array, label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title("Valeur d'entrée vs valeur de sortie dans le buffer à la fin du test")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def calculate_rmse(input, output):
    rmse = np.sqrt(np.mean((np.array(input) - np.array(output))**2))
    return rmse



if __name__ == '__main__':

    # test_linear_increment_floating_average()
    test_linear_increment_fir_filter(filter_numtaps=303, input_errors=20)
    # test_step_increment_floating_average()
    # test_step_increment_fir_filter()
