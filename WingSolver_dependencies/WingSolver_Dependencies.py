import shutil
import os
import numpy as np
import scipy as sp

def empty_directory(directory):
    try:
        shutil.rmtree(directory)  # Remove all contents
        os.makedirs(directory)  # Recreate the empty directory
    except Exception as e:
        print(f"Failed to empty directory. Reason: {e}")

def main():
    # Example usage
    empty_directory('/path/to/your/directory')

def quadratic(x,a,b,c):
	return a* x**2 +b* x+ c

def drag_curve(lift_coefficient, drag_coeffcient):
	#c_w(c_a)=a*c_a�+b*c_a+d
	initial_guess = [1, -1, 1]
	bounds = ([0, -np.inf, 0], [np.inf, 0, np.inf])
	if len(lift_coefficient) != len(drag_coeffcient):
		return 0
	params, _ = sp.optimize.curve_fit(quadratic, lift_coefficient, drag_coeffcient, p0=initial_guess, bounds=bounds)
	#a,b,d= np.polyfit(lift_coefficient,drag_coeffcient,2)
	a,b,d= params
	return [a,b,d]

def calculate_function(reference,coefficients):
    # Define the polynomial coefficients as a tuple
    #coefficients = (-0.00601809876176738, -0.0602287380735399, 7.39222409124886, 44.7487686030506)  # Example: x^2 - 3x + 2

    # Generate the polynomial function from the coefficients
    polynomial = np.poly1d(coefficients)

    # Generate x values for plotting
    x = reference  

    # Evaluate the polynomial for the x valuesa
    y = polynomial(x)

    return y

if __name__=="__main__":
    main()