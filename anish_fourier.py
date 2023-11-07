import numpy as np
import scipy


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


period = 10
fourier = produce_fourier_func(f, 50, period)
xs = np.linspace(0, period, 1000)
ys = [f(x) for x in xs]
ys1 = [fourier(x) for x in xs]
plt.plot(xs, ys)
plt.plot(xs, ys1)
