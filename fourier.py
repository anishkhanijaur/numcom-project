import numpy as np
import scipy
import matplotlib.pyplot as plt


def integrate_complex_function(f, a, b):
    def real_function(x):
        return np.real(f(x))

    def imaginary_function(x):
        return np.imag(f(x))

    # Trap function takes too long
    # real_integrated = trap(real_function, a, b, h)
    # imaginary_integrated = trap(imaginary_function, a, b, h)
    real_integrated = scipy.integrate.quad(real_function, a, b)[0]
    imaginary_integrated = scipy.integrate.quad(imaginary_function, a, b)[0]
    result = real_integrated + 1j * imaginary_integrated
    return result


def get_fourier_coefficients(f, n_coefficient, period):
    result = []
    for n in range(-n_coefficient, n_coefficient + 1):
        def integrate_func(t):
            if f(t) == 0:
                return 0
            return f(t) * np.exp(-1j * 2 * np.pi * n * t / period)

        cn = (1. / period) * integrate_complex_function(integrate_func, 0, period)
        result.append(cn)
    return np.array(result)


def produce_fourier_func(f, n_coefficient, period):
    coefficients = get_fourier_coefficients(f, n_coefficient, period)

    def fourier_func(t):
        total = 0. + 0.j
        sum_dimension_magnitude = int((len(coefficients) - 1) / 2)
        for n in range(-sum_dimension_magnitude, sum_dimension_magnitude + 1):
            total += coefficients[n + sum_dimension_magnitude] * np.exp(1j * 2. * np.pi * n * t / period)
        return total

    return fourier_func


def f(x):
    return x ** 2 + x ** 9 + 3


# period = 10
# fourier = produce_fourier_func(f, 50, period)
# xs = np.linspace(0, period, 1000)
# ys = [f(x) for x in xs]
# ys1 = [fourier(x) for x in xs]
# plt.plot(xs, ys)
# plt.plot(xs, ys1)


def fourier_approximation(func, x_values, num_terms):
    T = x_values[-1] - x_values[0]
    a0 = (1/T) * np.trapz([func(x) for x in x_values], x=x_values)

    def a_n(n):
        integrand = lambda x: func(x) * np.cos(2 * np.pi * n * x / T)
        return (2/T) * np.trapz([integrand(x) for x in x_values], x=x_values)

    def b_n(n):
        integrand = lambda x: func(x) * np.sin(2 * np.pi * n * x / T)
        return (2/T) * np.trapz([integrand(x) for x in x_values], x=x_values)

    def fourier_series(x):
        series_sum = a0/2
        for n in range(1, num_terms + 1):
            series_sum += a_n(n) * np.cos(2 * np.pi * n * x / T) + b_n(n) * np.sin(2 * np.pi * n * x / T)
        return series_sum+1

    return fourier_series

# Example usage:
# Define a function to approximate
def original_function(x):
    return x**3+x**2-x

# # Define x values
# x_values = np.linspace(0, 2, 1000)
#
# # Create Fourier approximation function
# num_terms = 101
# approximation = fourier_approximation(original_function, x_values, num_terms)
#
# # Plot the original function and its Fourier approximation
# plt.plot(x_values, original_function(x_values), label='Original Function')
# plt.plot(x_values, approximation(x_values), label=f'Fourier Approximation (Terms={num_terms})')
# plt.legend()
# plt.show()
