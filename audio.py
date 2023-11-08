import numpy as np
import pygame
import fourier
import sys

def audio_from_function(my_function, graph_width):
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
    bits = 16
    sample_rate = 44100  # The number of samples per second (standard for audio)
    duration = 1  # Duration of the sound in seconds
    num_samples = int(sample_rate * duration)
    amplitude = 0.5  # Amplitude of the sound

    # Create a time array
    # TODO: Convert this so that the time_arr can be used on the graph
    time_arr = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Calculate the function's output for each time point
    output = np.array([my_function(2 * np.pi * t * 280) for t in time_arr])
    output = np.repeat(output.reshape(num_samples, 1), 2, axis=1)
    print(output[20000:20020])

    # Initialize the pygame mixer
    pygame.mixer.pre_init(sample_rate, bits)
    pygame.mixer.set_num_channels(1)
    print(f"Pygame mixer init: {pygame.mixer.get_init()}")

    # Calculate the function's output from one end to the other
    time_arr = np.linspace(0, graph_width, int(sample_rate * duration), endpoint=False)
    output = np.array([my_function(t) for t in time_arr])

    # Normalize the output to be in the range [-1, 1]
    # max_value = np.max(np.abs(output))
    # if max_value != 0:
    #     output /= max_value

    # Create the sound buffer
    sound_buffer = np.zeros((num_samples, 2), dtype=np.int16)
    for index in range(len(output)):
        sound_buffer[index][0] = int(round(output[index]))
        sound_buffer[index][1] = int(round(output[index]))

    # Play the sound
    sound = pygame.sndarray.make_sound(sound_buffer)
    sound.play()

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
