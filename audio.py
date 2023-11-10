import time

import numpy as np
import pygame
import fourier_file
import sys

def audio_from_function(func, graph_width, fourier=False, n_terms=0):
    '''
    Sound data is made of thousands of samples per second, and each sample
    is the amplitude of the wave at a particular moment in time. For
    example, in 22-kHz format, element number 5 of the array is the
    amplitude of the wave after 5/22000 seconds.
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
    # sound.play(loops=-1) #, maxtime=int(duration * one_sec))
    return sound
    # If the value of the sound ends up being 0 at certain frequency, just cut it out and copy it till the end
