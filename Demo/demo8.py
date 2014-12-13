from pyCSGScript import *

box = Box([-1, 0, -1], [2, 2, 2], "MAT01", [1, 0, 0, 1])
cone = Cone([-5, 0, 0], 1, 3, "MAT02", [0, 0, 1, 1])

obj = box * cone