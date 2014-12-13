import pyPolyCSG as csg
import numpy 
import copy
import xml.etree.ElementTree as Et


default_color = (0.5, 0.5, 0.5, 1)
default_mat = ""
coplanarity_threshold = 1e-5


def _polyhedron_mult_numpy_matrix_4(polyhedron, matrix):
    # Multiply a numpy matrix for a pyPolyCSG polyhedron
    
    elements = numpy.hstack(numpy.asarray(matrix)).tolist()
    return polyhedron.mult_matrix_4(elements)


class CSGObject(object):
    """Represent a CSG constructed object or a primitive and keeps \
    material and color information."""
    
    def __init__(self, pos = (0, 0, 0), polyhedron = None, mat = None, 
                 color = None, transform = None):
        """Initialize a CSGObject with the given position, the \
        given polyhedron, material and color, and transform.
        """
        
        # The construction position
        self._pos = pos
        
        # The pyPolyCSG polyhedron
        if polyhedron is not None:
            self._polyhedron = polyhedron
        else:
            self._polyhedron = csg.polyhedron()
            
        if transform is not None:
            self.transform = transform
        else:
            self.transform = numpy.identity(4)
        
        if mat:
            self.mat = mat
        else:
            self.mat = default_mat
            
        if color:
            self.color = color
        else:    
            self.color = default_color
        
        self._global_polyhedron = None
    
    @property    
    def pos(self):
        """The construction position."""
        return self._pos
    
    @property
    def global_polyhedron(self):
        """The polyhedron in global space coordinates."""
        
        if not self._global_polyhedron:
            self._global_polyhedron = \
                _polyhedron_mult_numpy_matrix_4(self._polyhedron,
                                                self.transform)
        return self._global_polyhedron
    
        
    def translate(self, offset, local=False):
        """Translate by offset.
        
        If local is True, use local space coordinates.
        
        """
        
        translate_matrix = numpy.matrix([[1.0, 0.0, 0.0, offset[0]], 
                                         [0.0, 1.0, 0.0, offset[1]],
                                         [0.0, 0.0, 1.0, offset[2]],
                                         [0.0, 0.0, 0.0, 1.0]])
        if local:
            self.transform = self.transform * translate_matrix
        else:
            self.transform = translate_matrix * self.transform
        self._global_polyhedron = None
        
    def rotate(self, axis, origin, angle):
        """Rotate by angle degrees, around the axis starting at origin."""
        
        # Convert angle to radinas and calculate sin and cos
        angle_rad = numpy.radians(angle)
        cos = numpy.cos(angle_rad)
        sin = numpy.sin(angle_rad)
        
        # Store temporary variables of components
        np_axis = numpy.array(axis)
        np_axis = np_axis / numpy.linalg.norm(np_axis)
        ux, uy, uz = np_axis
        
        # Calculate rotation matrix
        rotation_matrix = numpy.matrix(
         [[cos + ux*ux*(1-cos), ux*uy*(1-cos) - uz*sin, ux*uz*(1-cos) + uy*sin, 0.0],
         [uy*ux*(1-cos) + uz*sin, cos + uy*uy*(1-cos), uy*uz*(1-cos) - ux*sin, 0.0],
         [uz*ux*(1-cos) - uy*sin, uz*uy*(1-cos) + ux*sin, cos + uz*uz*(1-cos), 0.0],
         [0.0, 0.0, 0.0, 1.0]])
         
        # Translate to negative origin, applay rotation ad retranslate
        # to origin
        self.translate((-origin[0], -origin[1], -origin[2]))
        self.transform = rotation_matrix * self.transform
        self.translate(origin)
        
        # Invalidate global polygon cache
        self._global_polyhedron = None
        
    def scale(self, factor, origin):
        """Scale by factor respect to origin"""
        
        scale_matrix = numpy.matrix([[factor[0], 0.0, 0.0, 0.0],
                                     [0.0, factor[1], 0.0, 0.0],
                                     [0.0, 0.0, factor[2], 0.0],
                                     [0.0, 0.0, 0.0, 1.0]])
        self.translate((-origin[0], -origin[1], -origin[2]))
        self.transform = scale_matrix * self.transform
        self.translate(origin)
        self._global_polyhedron = None
        
    def union(self, csg_object):
        """Return the object union of self and the csg_object.
        
        Attributes such as creation position, material, color are taken
        from the self object.
        
        """
        
        polyhedron = self.global_polyhedron + csg_object.global_polyhedron
        polyhedron = _polyhedron_mult_numpy_matrix_4(polyhedron,
                                            numpy.linalg.inv(self.transform))
        union_object = CSGObject(self.pos, polyhedron, self.mat, self.color, 
                                 self.transform)
        return union_object
    
    def intersection(self, csg_object):
        """Return the intersection object of self and the csg_object.
                
        Attributes such as creation position, material, color are taken
        from the self object.
        
        """
        
        polyhedron = self.global_polyhedron * csg_object.global_polyhedron
        polyhedron = _polyhedron_mult_numpy_matrix_4(polyhedron,
                                            numpy.linalg.inv(self.transform))
        intersection_object = CSGObject(self.pos, polyhedron, self.mat,
                                        self.color, self.transform)
        return intersection_object
    
    def difference(self, csg_object):
        """Return the difference object of self and the csg_object.
                
        Attributes such as creation position, material, color are taken
        from the self object.
        
        """
        
        polyhedron = self.global_polyhedron - csg_object.global_polyhedron
        polyhedron = _polyhedron_mult_numpy_matrix_4(polyhedron,
                                            numpy.linalg.inv(self.transform))
        difference_object = CSGObject(self.pos, polyhedron, self.mat,
                                      self.color, self.transform)
        return difference_object
    
    def symmetric_difference(self, csg_object):
        """Return the symmetric_difference object of self and the \
        csg_object.
        
        Attributes such as creation position, material, color are taken
        from the self object.
        
        """
        
        polyhedron = self.global_polyhedron ^ csg_object.global_polyhedron
        polyhedron = _polyhedron_mult_numpy_matrix_4(polyhedron,
                                            numpy.linalg.inv(self.transform))
        symmetric_difference_object = CSGObject(self.pos, polyhedron, self.mat,
                                                self.color, self.transform)
        return symmetric_difference_object
    
    def __add__(self, other):
        """Perform union of CSGObjects.
        
        Attributes such as creation position, material, color are taken
        from the first object.
        
        """
        
        return self.union(other)

    def __sub__(self, other):
        """Perform difference of CSGObjects.
        
        Attributes such as creation position, material, color are taken
        from the first object.
        
        """
        
        return self.difference(other)
    
    def __mul__(self, other):
        """Perform intersection of CSGObjects.
        
        Attributes such as creation position, material, color are taken
        from the first object.
        
        """
        
        return self.intersection(other)
    
    def __xor__(self, other):
        """Perform symmetric_difference of CSGObjects.
        
        Attributes such as creation position, material, color are taken
        from the first object.
        
        """
        
        return self.symmetric_difference(other)
    
    def __copy__(self):
        
        new_object = CSGObject(copy.copy(self._pos),
                               self._polyhedron,
                               self.mat,
                               copy.copy(self.color),
                               copy.copy(self.transform))
        return new_object
    
    def export(self, filename, **keywords):
        """Export the CSGObject of file.
        
        Currently only xml format is supported.
        Only the material, color, geometry and transform are exported.
        
        """
        
        if filename.endswith(".xml"):
            root_element = Et.Element("py_csg_script_data")
            mesh_filename = filename[:-4]
            if "mesh_format" in keywords.keys():
                mesh_filename += keywords["mesh_format"]
            else:
                mesh_filename += ".obj"
            self._polyhedron.save_mesh(mesh_filename)
            obj_element = self._make_xml_element(mesh_filename)
            root_element.append(obj_element)
            el_tree = Et.ElementTree(root_element)
            el_tree.write(filename)
    
    def import_(self, filename):
        """Import the CSGObject from file.
        
        Currently only xml format is supported.
        Only the material, color, geometry and transform are imported.
        
        """
        
        if filename.endswith(".xml"):
            e_tree = Et.parse(filename)
            obj_element = e_tree.getroot().find("csg_obj")
            if obj_element is None:
                return
            else:
                mesh_filename = obj_element.get("filename")
                self._polyhedron.load_mesh(mesh_filename)
                
                color_string = obj_element.get("color")
                r = int(color_string[1:3], 16) / 255.0
                g = int(color_string[3:5], 16) / 255.0
                b = int(color_string[5:7], 16) / 255.0
                a = int(color_string[7:9], 16) / 255.0
                self.color = (r, g, b, a)
                
                self.mat = obj_element.get("mat")
                
                transform_e = obj_element.find("transform")
                transform_list = []
                for row_e in list(transform_e):
                    row = []
                    for el_e in list(row_e):
                        row.append(float(el_e.text))
                    transform_list.append(row)
                self.transform = numpy.matrix(transform_list)
                    
    def _make_xml_element(self, filename):
        # Make an xml element that stores the color, mat and
        # the filename of the mesh
        
        e = Et.Element("csg_obj", filename = filename)
        
        r = int(self.color[0] * 255.0) 
        g = int(self.color[1] * 255.0)
        b = int(self.color[2] * 255.0) 
        a = int(self.color[3] * 255.0)
        color_string = "#{0:X}{1:X}{2:X}{3:X}".format(r, g, b, a)
        
        transform_e = Et.Element("transform")
        for row in self.transform:
            row_e = Et.Element("row")
            transform_e.append(row_e)
            for element in row.tolist()[0]:
                el_e = Et.Element("element")
                el_e.text = repr(element)
                row_e.append(el_e)
                
        e.set("color", color_string)
        e.set("mat", self.mat)
        e.append(transform_e)
        return e
        
        
class CSGGroup(object):
    """Represent a group of CSGObject that can be manipulated at once."""
    
    def __init__(self, csg_objects = None):
        
        if csg_objects is not None:
            self._csg_objects = set(csg_objects)
        else:
            self._csg_objects = set([]) 
        
    
    def add(self, csg_object):
        """Add an object to the group."""
        self._csg_objects.add(csg_object)
        
    def remove(self, csg_object):
        """Remove an object to the group."""
        self._csg_objects.remove(csg_object)
        
    def translate(self, offset):
        """Translate the group by offset."""
        for obj in self._csg_objects:
            obj.translate(offset)
    
    def rotate(self, axis, origin, angle):
        """Rotate the group by angle degrees around the axis starting \
        at origin."""
        for obj in self._csg_objects:
            obj.rotate(axis, origin, angle)
    
    def scale(self, factor, origin):
        """Scale by factor relative to origin."""
        for obj in self._csg_objects:
            obj.scale(factor, origin)
            
    def __copy__(self):
        """Copy the group and each element of the group."""
        csg_group = CSGGroup()
        for csg_object in self.csg_objects:
            csg_copy = copy.copy(csg_object)
            csg_group.add(csg_copy)
        
        return csg_group
    
    
class Box(CSGObject):
    """Box CSG primitive."""
    
    def __init__(self, pos, dim, mat = None, color = None):
        polyhedron = csg.box(*dim)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        self._dim = dim
        
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._dim = self._dim
        return new_obj
        
    
    @property
    def dim(self):
        return self._dim
    
    
class Cylinder(CSGObject):
    """Cylinder CSG primitive."""
    
    def __init__(self, pos, radius, height, mat = None, color = None):
        polyhedron = csg.cylinder(radius, height, True)
        polyhedron = polyhedron.translate(0, height/2.0, 0)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        self._radius = radius
        self._height = height
     
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._radius = self._radius
        new_obj._height = self._height
        return new_obj
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def height(self):
        return self._height


class Sphere(CSGObject):
    """Sphere CSG primitive."""
    
    def __init__(self, pos, radius, mat = None, color = None):
        polyhedron = csg.sphere(radius, True)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        self._radius = radius
    
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._radius = self._radius
        return new_obj
        
    @property
    def radius(self):
        return self._radius
    
    
class Cone(CSGObject):
    """Cone CSG primitive """
    
    def __init__(self, pos, radius, height, mat = None, color = None):
        polyhedron = csg.cone(radius, height, True)
        polyhedron = polyhedron.translate(0, height/2.0, 0)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        self._radius = radius
        self._height = height
     
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._radius = self._radius
        new_obj._height = self._height
        return new_obj
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def height(self):
        return self._height


class Torus(CSGObject):
    """ Torus CSG primitive """
    
    def __init__(self, pos, radius_major, radius_minor, mat = None, color = None):
        polyhedron = csg.torus(radius_major, radius_minor, True)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        self._radius_major = radius_major
        self._radius_minor = radius_minor
        
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._radius_major = self._radius_major
        new_obj._radius_minor = self._radius_minor
        return new_obj
    
    @property
    def radius_major(self):
        return self._radius_major
    
    @property
    def radius_minor(self):
        return self._radius_minor


class CoplanarityError(Exception):
    pass
  
  
class Polyline(CSGObject):
    """Polyline CSG primitive."""
    
    def __init__(self, pos, vertices, mat = None, color = None):
        self._vertices = vertices
        
        if not self._check_coplanarity():
            raise CoplanarityError()
        
        polyhedron = csg.extrusion(vertices, 0, 0, 0)
        CSGObject.__init__(self, pos, polyhedron, mat, color)
        self.translate(pos)
        
    def extrude(self, vector):
        """Extrude the polyline by vector."""
        
        self._polyhedron = csg.extrusion(self._vertices, vector[0], vector[1], 
                                       vector[2])
        
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        return new_obj
       
    @property
    def vertices(self):
        return copy.copy(self._vertices)
    
    def _check_coplanarity(self):
        # Check if vertices are coplanary, if not raise a
        # CoplanaryError exception
        
        if len(self._vertices) <= 3:
            return True
        
        # First 3 vertices determin the plane
        v0 = self._vertices[0]
        v1 = self._vertices[1]
        v2 = self._vertices[2]
        vertices = self._vertices[3:]
        
        # Check for other vertices in the same plane of the first 3
        for v in vertices:
            m = numpy.matrix([[v0[0], v0[1], v0[2], 1],
                              [v1[0], v1[1], v2[2], 1],
                              [v2[0], v2[1], v2[2], 1],
                              [v[0], v[1], v[2], 1]])
            det = numpy.linalg.det(m)
            if det < - coplanarity_threshold or det > coplanarity_threshold:
                return False
            
        return True
    
    
class Trapeze(Polyline):
    """Trapeze CSG primitive."""
    
    def __init__(self, pos, width, height, top, mat = None, color = None):
        self._width = width
        self._height = height
        self._top = top
        vertices = [(-width/2, -height/2, 0),
                    (-top/2, height/2, 0),
                    (top/2, height/2, 0),
                    (width/2, -height/2, 0)]
        Polyline.__init__(self, pos, vertices, mat, color)
    
    def __copy__(self):
        new_obj = CSGObject.__copy__(self)
        new_obj._width = self._width
        new_obj._height = self._height
        new_obj._top = self._top
        return new_obj
        
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    @property
    def top(self):
        return self._top
    
        