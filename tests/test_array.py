import numpy as np

A = np.asarray(((1, 2),
                (3, 4),
                (5, 6)))
# print((A%1).sum())
print(A.sum(axis=0)[0])
np.sum(A)
np.sum(A, axis=0)
np.array([9, 12])
np.sum(A, axis=1)
np.array([3, 7, 11])


