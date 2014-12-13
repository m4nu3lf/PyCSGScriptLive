import numpy
from PyQt4.QtCore import QObject, pyqtSignal
from dynamic_code_execution import BaseCodeChecker, BaseCodeExecutor
import pyCSGScript as csg


class GLReadyObject:
    def __init__(self, vertices, indices, normals, name, color):
        """A prepared object stores the same information of a CSG \
        object pluse the name.
        
        This class is used for optimizzation purposes since the
        get_vertices() method of a polyedron require data copy.
        
        """
        self.vertices = vertices
        self.indices = indices
        self.normals = normals         
        self.ambient = color
        self.diffuse = color
        self.specular = color
        self.shininess = 50.0


def _calculate_vertex_normals(vertices, indices):
    # NOTE: this function should be implemented in C/C++
    
    # Calculate the normal of each face
    face_normals = numpy.array(len(indices)//3 * [[0.0, 0.0, 0.0]])
    for i in xrange(0, len(indices), 3):
        side1 = vertices[indices[i + 1]] - vertices[indices[i + 0]]
        side2 = vertices[indices[i + 2]] - vertices[indices[i + 0]]
        normal = numpy.cross(side1, side2)
        normal /= numpy.linalg.norm(normal)
        face_normals[i//3] = normal
    
    normals = numpy.array(len(vertices)* [[0.0, 0.0, 0.0]])
        
    # For each vertex compute and average of the normals of the
    # faces it belongs
    faces_per_vertex = numpy.array(len(vertices)* [0])
    for i in xrange(0, len(indices), 3):
        faces_per_vertex[indices[i + 0]] += 1
        faces_per_vertex[indices[i + 1]] += 1
        faces_per_vertex[indices[i + 2]] += 1
        normals[indices[i + 0]] += face_normals[i//3]
        normals[indices[i + 1]] += face_normals[i//3]
        normals[indices[i + 2]] += face_normals[i//3]
    for i in xrange(0, len(normals)):
        normals[i] /= faces_per_vertex[i]
        
    return normals


def _csg_object_to_glready_object(csg_object, name):
    """Translate a csg_object with the given name to a GLReadyObject."""
    
    vertices = csg_object.global_polyhedron.get_vertices()
    triangles = csg_object.global_polyhedron.get_triangles().astype('uint16')
    indices = triangles.flatten()
    normals = _calculate_vertex_normals(vertices, indices)
    return GLReadyObject(vertices,
                         indices,
                         normals,
                         name,
                         csg_object.color)


def _extract_geometries_info(dict_):
    """Extract the csg objects contained into a dictionary and \
    convert them to GLReadyObjects"""
    
    processed_objects = set([])
    prepared_objects = []
    for name, csg_obj in dict_.iteritems():
        if (isinstance(csg_obj, csg.CSGObject) and
                        csg_obj not in processed_objects):
            # Ensure there is only one entry for object
            processed_objects.add(csg_obj)
            prepared_objects.append(_csg_object_to_glready_object(csg_obj,
                                                                    name))
            
    return prepared_objects


class CodeChecker(BaseCodeChecker, QObject):
    """Adds Qt signals to the BaseCodeChecker."""
    
    # This signal is emitted when the parsing process starts
    parseStart = pyqtSignal()
    
    # This signal is emitted when the parsing process ends and
    # the list of SyntaxError(s) is passed as argument
    parseEnd = pyqtSignal(list)
    
    def __init__(self, code_executor):
        BaseCodeChecker.__init__(self, code_executor)
        QObject.__init__(self)
        
    def on_parse_start(self):
        """Emits a parseStart signal."""
        self.parseStart.emit()
        
    def on_parse_end(self):
        """Emits a parseEnd signal with the list of syntaxErrors as \
        argument."""
        self.parseEnd.emit(self.syntax_errors)


class CodeExecutor(BaseCodeExecutor, QObject):
    """Adds Qt signals to the BaseCodeExecutor and csg_data \
    conversion."""
    
    # This signal is emitted when the execution ends.
    # Execution stdout and stderr files, locals and globals dict
    # are passed as argumets
    executionEnd = pyqtSignal(object, object, dict, dict)
    
    # This signal is emitted when the csg geomtries changed.
    # A list of GLReadyObjects is passed as argument.
    csgDataChanged = pyqtSignal(list)
    
    def __init__(self):
        BaseCodeExecutor.__init__(self)
        QObject.__init__(self)
        
    def on_execution_end(self):
        """Emits an executionEnd signal, extract csg objects \
        data and emit a csgDataChanged signal."""
        self.executionEnd.emit(self.exec_stdout,
                               self.exec_stderr,
                               self.exec_globals,
                               self.exec_locals)
        
        render_ready_objects = _extract_geometries_info(self.exec_locals)
        self.csgDataChanged.emit(render_ready_objects)
        
        