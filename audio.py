import numpy as np
import pygame


def audio_from_function(func, graph_width, fourier=False, n_terms=0, sample_rate=20000, duration=1):
    """
    Sound data is made of thousands of samples per second, and each sample
    is the amplitude of the wave at a particular moment in time. For
    example, in 22-kHz format, element number 5 of the array is the
    amplitude of the wave after 5/22000 seconds.
    """

    # Parameters for sound generation
    num_samples = int(sample_rate * duration)

    # Populate the sound buffer
    buf = np.zeros((num_samples, 2))
    current_index = 0
    for index in np.linspace(0, sample_rate, num_samples):
        value = func(index) * 1700_000  # Get the y value at frequency index
        buf[current_index][0] = value  # left
        buf[current_index][1] = value  # right
        current_index += 1
    buf = buf.astype(np.int16)
    sound = pygame.sndarray.make_sound(buf)
    return sound
