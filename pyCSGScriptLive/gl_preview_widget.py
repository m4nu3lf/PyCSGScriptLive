import numpy
from PyQt4.QtGui import QColor, QApplication
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import Qt
from PyQt4.QtOpenGL import QGLWidget 
from OpenGL import GL, GLU


class GLPreviewWidget(QGLWidget):
    """Show a preview of the CSG scene by rendering the objects \
    provided within the render_objects list."""
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        
        # An array with all the objects prepared for rendering
        self.render_objects = []
        
        # If the perspective view is active
        self.perspective = True
        
        # Sensitivity mouse parameters
        self.rot_sensitivity = 0.1
        self.zoom_sensitivity = 0.001
        
        # The last position where mouse was pressed
        self._mouse_last_pos = QPoint()
        
        # Viewport size
        self._viewport_size = (1, 1)
        
        # XZ plane grid
        self._grid_vertices = None
        self.buildGrid(1, 100)
        
        # Initialize camera defaults
        self._init_camera_defaults()
        
    def _init_camera_defaults(self):
        # Initialize camera defaults
        
        # Perspective clipping planes
        self.near_clip = 1
        self.far_clip = 1e5
        
        # Camera target position and camera distance form it
        self.camera_distance = 10.0
        self.camera_target = numpy.array([0.0, 0.0, 0.0])
        
        # Camera X and Y rotations
        self._x_rotation = 30.0
        self._y_rotation = 0.0
        
        # Camera zoom factor
        self.zoom_factor = 10
        
    def setRenderObjects(self, render_objects):
        """Set the objects used for renderig"""
        
        self.render_objects = render_objects
        self.updateGL()
        
    def buildGrid(self, step, lines):
        """Build a grid geometry on the xz plane."""
        
        grid_vertices = []
        width = lines * step
        
        # Axsis lines
        grid_vertices.append([width, 0.0, 0.0])
        grid_vertices.append([-width, 0.0, 0.0])
        grid_vertices.append([0.0, 0.0, width])
        grid_vertices.append([0.0, 0.0, -width])
        
        for i in xrange(-lines, lines):
            if i:
                grid_vertices.append([i * step, 0.0, width])
                grid_vertices.append([i * step, 0.0, -width])
                grid_vertices.append([width, 0.0, i * step])
                grid_vertices.append([-width, 0.0, i * step])
        self._grid_vertices = numpy.array(grid_vertices)
        
    def renderGrid(self):
        """Paint an already build grid."""
        
        GL.glDisable(GL.GL_LIGHTING)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        GL.glVertexPointerd(self._grid_vertices)
        
        GL.glColor4f(1.0, 0.0, 0.0, 0.5)
        GL.glDrawArrays(GL.GL_LINES, 0, 2)
        GL.glColor4f(0.0, 0.0, 1.0, 0.5)
        GL.glDrawArrays(GL.GL_LINES, 2, 4)
        GL.glColor4f(0.5, 0.5, 0.5, 0.5)
        GL.glDrawArrays(GL.GL_LINES, 4, len(self._grid_vertices))
        
    def initializeGL(self):
        """Initialize opengl with some default settings."""
    
        self.qglClearColor(QColor(64, 64,128))
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        
    def mousePressEvent(self, event):
        """Intercept the mouse press event to keep track of the mouse \
        position for rotation and panning."""
        
        self._mouse_last_pos = QPoint(event.pos())
        
    def mouseMoveEvent(self, event):
        """Intercept the mouse move event to perform view rotation \
        and panning."""
        
        dx = event.x() - self._mouse_last_pos.x()
        dy = event.y() - self._mouse_last_pos.y()

        if (event.buttons() & Qt.MidButton and
            QApplication.keyboardModifiers() & Qt.ShiftModifier):
            # Perform panning
            self._pann(dx, dy)

        elif event.buttons() & Qt.MidButton:
            # Perform camera rotation
            self._x_rotation += self.rot_sensitivity * dy
            self._y_rotation += self.rot_sensitivity * dx
            
        self.updateGL()

        self._mouse_last_pos = QPoint(event.pos())
        
    def _pann(self, dx, dy):
        # Helper function for panning
        
        prev_obj_pos = numpy.array(list(
                            GLU.gluUnProject(self._mouse_last_pos.x(),
                                             - self._mouse_last_pos.y(),
                                             0.0)))
        curr_obj_pos = numpy.array(list(
                            GLU.gluUnProject(self._mouse_last_pos.x() + dx,
                                             - self._mouse_last_pos.y() - dy,
                                             0.0)))
        
        near_offset = curr_obj_pos - prev_obj_pos
        
        if self.perspective:
            target_offset = near_offset * self.camera_distance / self.near_clip
        else:
            target_offset = near_offset
            
        self.camera_target += target_offset
        
        
    def wheelEvent(self, event):
        """Intercept the mouse wheel event to update the zoom factor
        and the fovy."""
        
        # Update the zoom factor, zoom factor cannot be less than 0.001
        self.zoom_factor *= 1 + event.delta() * self.zoom_sensitivity
        self.zoom_factor = max(0.001, self.zoom_factor)
                
        # Update the camera position so that the plane parallel to the camera
        # plane and passing from the camera_target point has the same height
        # and width of the ortho view size            
        self.camera_distance = \
            self.near_clip * self._viewport_size[1] / self.zoom_factor / 4
        

        self._update_projection_matrix()
        self.updateGL()
        
    def paintGL(self):
        """Paint the geomtries stored in the render_objects list."""
        
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0.0, 0.0, - self.camera_distance)
        GL.glRotated(self._x_rotation, 1.0, 0.0, 0.0)
        GL.glRotated(self._y_rotation, 0.0, 1.0, 0.0)
        GL.glTranslated(self.camera_target[0],
                        self.camera_target[1],
                        self.camera_target[2])
        GL.glLight(GL.GL_LIGHT0, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        GL.glLight(GL.GL_LIGHT0, GL.GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
        GL.glLight(GL.GL_LIGHT0, GL.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        GL.glEnable(GL.GL_LIGHT0)
        
        self.renderGrid()
        
        for obj in self.render_objects:
            if len(obj.vertices) == 0:
                continue
            
            GL.glEnable(GL.GL_LIGHTING)
            GL.glMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT, obj.ambient)
            GL.glMaterial(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, obj.diffuse)
            GL.glMaterial(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, obj.specular)
            GL.glMaterial(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, obj.shininess)
            
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
            GL.glNormalPointerf(obj.normals)
            GL.glVertexPointerf(obj.vertices)

            GL.glShadeModel(GL.GL_SMOOTH)
            GL.glDrawElementsui(GL.GL_TRIANGLES, obj.indices)
        
    def resizeGL(self, width, height):
        """Adjust the camera aspect ratio to match the view one."""
        
        GL.glViewport(0, 0, width, height)
        self._viewport_size = (width, height)
        self._update_projection_matrix()
        
    def _update_projection_matrix(self):
        """Update the projection matrix.
        
        The matrix is updated to match the view aspect ratio and the
        internal view parameters.
        
        """
        
        width = self._viewport_size[0]
        height = self._viewport_size[1]
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        if self.perspective:                
            GL.glFrustum(-width/float(height), width/float(height), -1.0, 1.0, 
                         self.near_clip, self.far_clip)
        else:
            GL.glOrtho(-width/self.zoom_factor/2,
                       width/self.zoom_factor/2,
                       -height/self.zoom_factor/2,
                       height/self.zoom_factor/2,
                       -1e5, 1e5)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        
    def togglePerspective(self):
        """Toggle from perspective ad orhtographic view."""
        
        self.perspective = not self.perspective
        self._update_projection_matrix()
        self.updateGL()
        
    def resetCamera(self):
        """Reset camera postion and view settings to default."""

        self._init_camera_defaults()
        self._update_projection_matrix()
        self.updateGL()
        