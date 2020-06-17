import numpy as np
from numpy.linalg import eig
import pandas as pd

def ac_pca(X, Y):
    X_rows, X_cols = X.shape

    column_names = ['PC' + str(i) for i in range(1, X_cols + 1)]

    # Center data
    X_mean = X.T.mean(axis=1)
    X = X - X_mean
    Y_mean = Y.T.mean(axis=1)
    Y = Y - Y_mean

    # AC-PCA
    lam = 20  # lambda
    K = Y @ Y.T
    cov = X.T @ X - lam * X.T @ K @ X
    eigenvals, eigenvecs = eig(cov.T)
    P = eigenvecs.T.dot(X.T)
    P = P.T

    projected = pd.DataFrame(data=P, columns=column_names)
    PCs = pd.DataFrame(data=eigenvecs, columns=column_names)
    eigenvalues = pd.DataFrame(data=eigenvals.reshape(1, X_cols), columns=column_names)

    return projected, PCs, eigenvalues