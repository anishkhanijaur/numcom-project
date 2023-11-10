import time

import numpy as np
import pygame
import fourier_file
import sys

def audio_from_function(func, graph_width, fourier=False, n_terms=0):
    '''
    # Define the mathematical function you want to replicate as a Python function
    # def my_function(x):
    #     return np.sin(x) + np.sin(2 * x)

    # Parameters for sound generation
    sample_rate = 44100  # The number of samples per second (standard for audio)
    duration = 3  # Duration of the sound in seconds
    amplitude = 0.5  # Amplitude of the sound

    # Create a time array
    time_arr = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Calculate the function's output for each time point
    output = np.array([my_function(2 * np.pi * t) for t in time_arr])

    # Normalize the output to be in the range [-1, 1]
    max = np.max(np.abs(output)) or 1
    output = np.array([float(item)/float(max) for item in output])

    # Initialize the pygame mixer
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
    pygame.mixer.set_num_channels(1)

    # Convert the numpy array to a sound sample
    sound = pygame.sndarray.make_sound((output * 32767).astype(np.int16))

    # Play the sound
    sound.play()

    # Wait for the sound to finish
    pygame.time.delay(int(duration * 1000))
    '''

    # Parameters for sound generation
    sample_rate = 20000 #44100  # The number of samples per second (standard for audio)
    duration = 1  # Duration of the sound in seconds
    num_samples = int(sample_rate * duration)
    one_sec = 1000

    # Calculate the function's output for each time point
    # TODO: Implement this to be able to be togglable
    # fourier_func = fourier_file.fourier_approximation(func, time_arr, 50)

    # Populate the sound buffer
    buf = np.zeros((num_samples, 2))
    if fourier:
       ...
    else:
        # for index in range(len(buf)):
        current_index = 0
        for index in np.linspace(0, sample_rate, num_samples):
            value = func(index) * 1700_000 # Get the y value at frequency index
            buf[current_index][0] = value # left
            buf[current_index][1] = value # right
            current_index += 1

    buf = buf.astype(np.int16)



    # Play the sound
    sound = pygame.sndarray.make_sound(buf)
    print(f"length from pg {pygame.mixer.Sound.get_length(sound)}")
    sound.play(loops=-1) #, maxtime=int(duration * one_sec))
    # If the value of the sound ends up being 0 at certain frequency, just cut it out and copy it till the end

    # Convert the numpy array to a sound sample
    # TODO: Change to work with the following
    '''
    Sound data is made of thousands of samples per second, and each sample
    is the amplitude of the wave at a particular moment in time. For
    example, in 22-kHz format, element number 5 of the array is the
    amplitude of the wave after 5/22000 seconds.
    '''
    # sound = pygame.sndarray.make_sound((output * 32767).astype(np.int16))
    #
    # num_samples = int(round(duration * sample_rate))
    # sound_buffer = np.zeros((num_samples, 2), dtype=np.int16)
    # amplitude = 2 ** (bits - 1) - 1
    # sound_buffer =


    # Play the sound
    # sound.play()
    # for index in range(5):
        # pygame.time.delay(int(duration * 1000))

    # Wait for the sound to finish
    # pygame.time.delay(int(duration * 1000))


# # Quit pygame
# pygame.quit()
#
# # Exit the program
# sys.exit()
