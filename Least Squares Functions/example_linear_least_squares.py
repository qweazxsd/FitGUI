def fit_function(x, a0, a1):
    """
    Fit data to this function.

    For the Least Square algorithm the function mus take x (the free variable) as the first argument
    and all the subsequent arguments need to be the fitting parameters.
    """
    return a1 * x + a0
