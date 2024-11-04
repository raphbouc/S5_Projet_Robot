import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from typing import Literal


def averaged_input(input, array):
    new_avg = (sum(array) + input) / (len(array) + 1)
    return new_avg

def median_input(array):
    sorted_array = sorted(array)
    n = len(sorted_array)
    
    # Calculer la médiane
    if n % 2 == 0:  # Si le nombre d'éléments est pair
        median = (sorted_array[n // 2 - 1] + sorted_array[n // 2]) / 2
    else:  # Si le nombre d'éléments est impair
        median = sorted_array[n // 2]
        
    return median

def push_to_data_array(input, array, max_length):
    if len(array) < max_length:
        array.append(input)
    else:
        array.pop(0)
        array.append(input)

def filter_uppervalue(input, array, threshold, min_threshold, max_threshold, fake_measurements=None, start_index=0):
    if len(array) < 5:
        push_to_data_array(input, array, 5)
        return array[-1]
    
    average_last_five = sum(array[-5:]) / 5

    if (input - average_last_five > threshold):
        return array[-1]
    elif abs(input - average_last_five) > min_threshold and abs(input - average_last_five) < max_threshold:
        push_to_data_array(input, array, 5)
        return array[-1]
    else: 
        # Mode de vérification : on doit accepter les prochaines valeurs similaires
        for _ in range(5):  # On va vérifier jusqu'à 5 prochaines valeurs
            if fake_measurements is not None and start_index < len(fake_measurements):
                new_input = get_next_input(fake_measurements, start_index)
                start_index += 1
            else:
                break  # Si pas de valeurs à lire, sortir de la boucle
            
            if new_input > min_threshold:  # Si c'est du bruit
                print(f"Valeur {new_input} considérée comme bruit et ignorée.")
                continue  # Ignorer cette valeur et passer à la suivante
            
            if abs(new_input - average_last_five) <= threshold:  # Vérifie la proximité
                push_to_data_array(new_input, array, 5)  # Ajoute la valeur si elle est proche
                print(f"Valeur {new_input} ajoutée à l'array.")
            else:
                print(f"Valeur {new_input} trop éloignée de la moyenne, arrêt de la vérification.")
                break  # Si une valeur ne correspond pas, on sort de la boucle

        # Retourne la dernière valeur ajoutée après vérification
        return array[-1]

def get_next_input(fake_measurements, index):
    return fake_measurements[index]

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

def test_linear_increment_median(input_min_value=20, input_max_value=100, input_min_error=5,
                          input_max_error=150, fake_input_length=1000, num_errors=50, max_length=10):
    
    fake_measurements = create_fake_measurements(input_min_value, input_max_value, input_min_error,
                                                 input_max_error, fake_input_length, num_errors)
    data = fake_measurements[:max_length]
    filtered_data = []
    for input in fake_measurements[max_length:]:
        print("==========================")
        print(f"Valeur en entree: {input}")
        push_to_data_array(input, data, max_length)
        output = median_input(data)
        filtered_data.append(output)
        print(f"Valeur en sortie: {output}")

    print(f"longueur des donnees retenu: {len(data)}")
    print(f"longueur de filtered data {len(filtered_data)}")
    rmse = calculate_rmse(fake_measurements[max_length:], filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(fake_measurements[max_length:], label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title(f"Valeur d'entrée vs valeur de sortie pour une médiane de {max_length} échantillons")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()


def test_linear_increment_uppervalue_filter(input_min_value=20, input_max_value=100, input_min_error=5,
                          input_max_error=150, fake_input_length=1000, num_errors=50, max_length=10):
    
    fake_measurements = create_fake_measurements(input_min_value, input_max_value, input_min_error,
                                                 input_max_error, fake_input_length, num_errors)
    data = fake_measurements[:max_length]
    filtered_data = []
    for input in fake_measurements[max_length:]:
        print("==========================")
        print(f"Valeur en entree: {input}")
        output = filter_uppervalue(input, data, 20, 0, 5, fake_measurements)
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

def test_step_increment_median(max_length=10):
    step_signal = generate_step_increment()
    data = step_signal[:max_length]
    filtered_data = []
    for input in step_signal[max_length:]:
        print("==========================")
        print(f"Valeur en entree: {input}")
        push_to_data_array(input, data, max_length)
        output = median_input(data)
        filtered_data.append(output)
        print(f"Valeur en sortie: {output}")

    print(f"longueur des donnees retenu: {len(data)}")

    rmse = calculate_rmse(step_signal[max_length:], filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(step_signal[max_length:], label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title(f"Valeur d'entrée vs valeur de sortie pour une médiane de {max_length} échantillons")
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
    first_filtered_data = []
    second_filtered_data = []
    third_filtered_data = []

    for input in input_data:
        print("========================")
        push_to_data_array(input, buffer_array, (500))
        if len(buffer_array) < (500):
            print(f"Loading Buffer")
            continue
        print(f"Valeur en entrée: {input}")
        first_filtered_data = apply_fir_filter(buffer_array, 2, fs, filter_numtaps)
        second_filtered_data = apply_fir_filter(first_filtered_data, 1, fs, filter_numtaps)
        third_filtered_data = apply_fir_filter(second_filtered_data, 0.1, fs, filter_numtaps)
        print(f"Valeur en sortie: {first_filtered_data[-1]}")
    
    rmse = calculate_rmse(buffer_array, second_filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(buffer_array, label='Original Data')
    plt.plot(first_filtered_data, label='Filtered Once', linestyle='--')
    plt.plot(second_filtered_data, label='Filtered Twice', linestyle='-.')
    plt.plot(third_filtered_data, label='Filtered 3 Times', linestyle='--')
    plt.title("Valeur d'entrée vs valeur de sortie du filtre sur 500 échantillons")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def test_step_increment_fir_filter(input_length=1000, input_errors=100, fc=2, fs=8, filter_numtaps=101):
    step_signal = generate_step_increment()
    buffer_array = []
    first_filtered_data = []
    second_filtered_data = []
    third_filtered_data = []

    for input in step_signal:
        print("========================")
        push_to_data_array(input, buffer_array, (filter_numtaps*3+1))
        if len(buffer_array) < (filter_numtaps*3+1):
            print(f"Loading Buffer")
            continue
        print(f"Valeur en entrée: {input}")
        first_filtered_data = apply_fir_filter(buffer_array, fc, fs, filter_numtaps)
        second_filtered_data = apply_fir_filter(first_filtered_data, 1, fs, filter_numtaps)
        third_filtered_data = apply_fir_filter(second_filtered_data, 0.1, fs, filter_numtaps)
        print(f"Valeur en sortie: {first_filtered_data[-1]}")

    rmse = calculate_rmse(buffer_array, first_filtered_data)
    print(f"rmse: {rmse}")

    # Plotting the result
    plt.plot(buffer_array, label='Original Data')
    plt.plot(first_filtered_data, label='Filtered Once', linestyle='--')
    plt.plot(second_filtered_data, label='Filtered Twice', linestyle='--')
    plt.plot(third_filtered_data, label='Filtered 3 Times', linestyle='--')
    plt.title("Valeur d'entrée vs valeur de sortie dans le buffer à la fin du test")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

def calculate_rmse(input, output):
    rmse = np.sqrt(np.mean((np.array(input) - np.array(output))**2))
    return rmse

def create_rii_filter(fs=8, fc=1, ws=1.5, rp=0.2, rs=60, filter_type: Literal["butter", "cheby1", "cheby2", "ellip"]= "butter"):
    fs = fs
    fc = fc
    wp = fc / (fs / 2)
    ws = ws / (fs / 2)
    rp = rp
    rs = rs
    if filter_type == "butter":
        N_min, wn = signal.buttord(wp, ws, rp, rs, fs=fs)
        print(f"wn {wn}")
        b, a = signal.butter(N_min, wn, btype="low", output='ba')
        print(f"ordre du filtre {filter_type}: {N_min}")
    elif filter_type == "cheby1":
        N_min, wn = signal.cheb1ord(wp, ws, rp, rs, fs=fs)
        b, a = signal.cheby1(N_min, rp, wn, btype="low", output='ba')
        print(f"ordre du filtre {filter_type}: {N_min}")

    elif filter_type == "cheby2":
        N_min, wn = signal.cheb2ord(wp, ws, rp, rs, fs=fs)
        b, a = signal.cheby2(N_min, rp, wn, btype="low", output='ba')
        print(f"ordre du filtre {filter_type}: {N_min}")

    elif filter_type == "ellip":
        N_min, wn = signal.ellipord(wp, ws, rp, rs, fs=fs)
        b, a = signal.ellip(N_min, rp, rs, wn, btype="low", output='ba')
        print(f"ordre du filtre {filter_type}: {N_min}")

    return b, a, N_min

def apply_rii_filter(data, b, a):
    return signal.filtfilt(b, a, data)

def test_linear_increment_rii_filter(input_length=1000, input_errors=100, fs=8, fc=1, ws=1.5, rp=0.2, rs=60, filter_type: Literal["butter", "cheby1", "cheby2", "ellip"]= "butter"):
    input_data = create_fake_measurements(length=input_length, num_errors=input_errors)
    b, a, n = create_rii_filter(filter_type=filter_type)
    buffer_array = []
    filtered_data = []

    for input in input_data:
        print("========================")
        push_to_data_array(input, buffer_array, (67))
        if len(buffer_array) < (67):
            print(f"Loading Buffer")
            continue
        print(f"Valeur en entrée: {input}")
        filtered_data = apply_rii_filter(buffer_array, b, a)
        print(f"Valeur en sortie: {filtered_data[-1]}")
    
    rmse = calculate_rmse(buffer_array, filtered_data)
    print(f"rmse: {rmse}")
    print(f"filter order: {n}")

    # Plotting the result
    plt.plot(buffer_array, label='Original Data')
    plt.plot(filtered_data, label='Filtered Data', linestyle='--')
    plt.title("Valeur d'entrée vs valeur de sortie dans le buffer à la fin du test")
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()


if __name__ == '__main__':

    # test_linear_increment_rii_filter(fc=0.2, ws=0.5, filter_type="butter")
    # test_linear_increment_rii_filter(fc=0.2, ws=0.5, filter_type="cheby1")
    # test_linear_increment_rii_filter(fc=0.2, ws=0.5, filter_type="cheby2")
    # test_linear_increment_rii_filter(fc=0.2, ws=0.5, filter_type="ellip")
    # test_linear_increment_floating_average()
    # test_linear_increment_fir_filter(filter_numtaps=101, input_errors=20)
    test_step_increment_fir_filter(filter_numtaps=101, input_errors=20)
    # test_linear_increment_uppervalue_filter()
    # test_linear_increment_median()
    # test_step_increment_floating_average()
    # test_step_increment_median()
    # test_step_increment_fir_filter()
