import numpy as np
import concurrent.futures

def fourier_approximation(func, x_values, num_terms):
    T = x_values[-1] - x_values[0]
    a0 = (1/T) * np.trapz([func(x) for x in x_values], x=x_values)

    def a_n(n):
        integrand = lambda x: func(x) * np.cos(2 * np.pi * n * x / T)
        return (2/T) * np.trapz([integrand(x) for x in x_values], x=x_values)

    def b_n(n):
        integrand = lambda x: func(x) * np.sin(2 * np.pi * n * x / T)
        return (2/T) * np.trapz([integrand(x) for x in x_values], x=x_values)

    a_values = [a_n(n) for n in range(1, num_terms + 1)]
    b_values = [b_n(n) for n in range(1, num_terms + 1)]

    def fourier_series(x):
        cos_terms = np.cos(2 * np.pi * np.arange(1, num_terms + 1) * x / T)
        sin_terms = np.sin(2 * np.pi * np.arange(1, num_terms + 1) * x / T)
        # Matrix multiplication
        result = a_values @ cos_terms + b_values @ sin_terms
        return result + 1 + a0 / 2

    return fourier_series

"""
# Example usage:
# Define a function to approximate
def original_function(x):
    return x**3+x**2-x

# Define x values
x_values = np.linspace(0, 2, 1000)

# Create Fourier approximation function
num_terms = 101
approximation = fourier_approximation(original_function, x_values, num_terms)

# Plot the original function and its Fourier approximation
plt.plot(x_values, original_function(x_values), label='Original Function')
plt.plot(x_values, approximation(x_values), label=f'Fourier Approximation (Terms={num_terms})')
plt.legend()
plt.show()
"""