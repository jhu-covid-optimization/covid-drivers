import numpy as np
from numpy.linalg import eig
import pandas as pd

def ac_pca(X, Y, lam):
    X_rows, X_cols = X.shape

    column_names = ['PC' + str(i) for i in range(1, X_cols + 1)]

    # Center data
    X_mean = X.T.mean(axis=1)
    X = X - X_mean
    Y_mean = Y.T.mean(axis=1)
    Y = Y - Y_mean

    # AC-PCA
#     lam = 20  # lambda
#     lam = 100
    K = Y @ Y.T
    cov_1 = X.T @ X 
    cov_2 = lam * X.T @ K @ X
#     print('cov_1:\n', cov_1)
#     print('cov_2:\n', cov_2)
    cov = cov_1 - cov_2
    eigenvals, eigenvecs = eig(cov.T)
    P = eigenvecs.T.dot(X.T)
    P = P.T

    projected = pd.DataFrame(data=P, columns=column_names)
    PCs = pd.DataFrame(data=eigenvecs, columns=column_names)
    eigenvalues = pd.DataFrame(data=eigenvals.reshape(1, X_cols), columns=column_names)

    return projected, PCs, eigenvalues