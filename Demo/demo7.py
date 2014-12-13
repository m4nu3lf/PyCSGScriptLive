from pyCSGScript import*

sphere = Sphere([0, 1, 0], 3, "MAT05", [1, 0.5, 0.5, 1])
torus = Torus([10, 1, 0], 4, 1, "MAT06", [0.5, 0.5, 1, 1])

planet = sphere + torus

