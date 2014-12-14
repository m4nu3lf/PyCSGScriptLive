from pyCSGScript import *

box = Box([-1, 0, -1], [2, 2, 2], "MAT01", [1, 0, 0, 1])
cylinder = Cylinder([5, 0, 0], 1, 3, "MAT02", [0 , 1, 0, 1])
cone = Cone([-5, 0, 0], 1, 3, "MAT03", [0, 0.0, 1, 1])
torus = Torus([0, 0, 5], 2, 0.5, "MAT04", [0.5, 0.5, 1, 1])
sphere = Sphere([0, 0, -5], 2, "MAT05", [1, 0.5, 0.5, 1])
trapeze = Trapeze([-5, 1, 5], 2, 1, 1, "MAT06", [2, 2, 0, 1])

vertices = [[0, 0, 0],
                  [2, 0, 0],
                  [2, 2, 0],
                  [1, 3, 0],
                  [0, 2, 0]]

poly = Polyline([5, 0, 5], vertices, "MAT07", [2, 1, 0.1, 1])