from pyCSGScript import *

# Create a sphere
sphere = Sphere([0, 0, 0], 2, "SOME_MAT", [1, 0.5, 0, 1])

# Create a cube
cube = Box([0, 0, 0], [2, 2, 2], "SOME_MAT2")

# Intersection between sphere and cube
slice = sphere * cube

# Remove cube volume from sphere
sphere -= cube

# Delete the cube
del cube               

# Translate the intersection
slice.translate([.5, .5, .5])

# Create a cylinder
cylinder = Cylinder([5, 0, 0], 1, 2, "SOME_MAT3", [0.5, 0.5, 1, 1])

# Create a cone
cone = Cone([5, 0, 0], 2, 3, "SOME_MAT4")

# Intersection between cylinder and cone
cylinder *= cone

# Delete the cone
del cone



