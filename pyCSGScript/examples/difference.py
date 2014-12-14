from pyCSGScript import *

cylinder = Cylinder([0, 0, 0], 1, 3, "MAT02", [0, 1, 0, 1])
cone = Cone([0, 0, 0], 1, 4, "MAT03", [0, 0, 1, 1])

difference = cone - cylinder

del cylinder, cone