from pyCSGScript import *

box = Box([0, 0, 0], [2, 2, 2], "MAT01", [1, 0, 0, 1])
cylinder = Cylinder([5, 0, 0], 1, 3, "MAT02", [0, 1, 0, 1])
torus = Torus([-5, 0, 0], 2, 0.5, "MAT03", [0.5, 0.5, 1, 1])

group = CSGGroup([box, cylinder, torus])

group.translate([3, 0, -2])
group.scale([0.5, 0.5, 0.5], [0, 0, 0])





