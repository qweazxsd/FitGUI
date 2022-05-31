def fit_function(a, x):
    """
    Fit data to this function.

    For the ODR algorithm the function must take a vector containing the fitting parameters as the first argument
    and x (the free variable) as the second.
    """
    return a[0] * x + a[1]