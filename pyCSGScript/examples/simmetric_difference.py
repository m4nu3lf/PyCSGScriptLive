from pyCSGScript import *

cylinder = Cylinder([0, 0, 0], 1, 3, "MAT01",
    [0, 1, 0, 1])
box = Box([0, 0, 0], [2, 3, 2], "MAT02",
    [1, 0, 0, 1])
    
symm_diff = cylinder ^ box

del cylinder, box

