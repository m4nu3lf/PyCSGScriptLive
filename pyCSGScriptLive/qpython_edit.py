import string
import re
from PyQt4.QtCore import QTimer, QString, QPoint
from PyQt4 import Qsci
from PyQt4.Qsci import QsciScintilla, QsciLexerPython
from PyQt4.Qt import Qt
from PyQt4.QtGui import QPixmap, QToolTip, QPrintDialog



class QPythonEdit(QsciScintilla):
    """Adds functionality to the QsciSintilla class, for python code.
    
    Included addictions are:
        - Defaults for python lexer, folding, margin, and error
          markers/indicators
          
        - New block auto indentation based on keywords
        
        - Problems management, with marker, indicators, and tool tips
        
    """
    
    new_block_keywords = ["class",
                          "def",
                          "elif",
                          "else",
                          "except",
                          "for",
                          "if",
                          "try",
                          "while"]
    """Python keywords that start a new block."""
    
    def __init__(self, parent = None):
        QsciScintilla.__init__(self, parent)
        
        # Time that should enlapse for the tool tip to show
        self.tool_tip_delay = 1
        
        # Whether or not annotations should be displayed
        self.annotations_active = False
        
        # Set python as language
        lexer = QsciLexerPython()
        api = Qsci.QsciAPIs(lexer)
        self.setLexer(lexer)
        self.lexer = lexer # NOTE: For some reasone self.lexer() doesn't work
        
        # Addictional API
        api.prepare()
        
        lexer.setFoldComments(True)
        lexer.setFoldCompact(False)
        
        # QsciScintilla editing defaults
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(4)
        
        # QScintilla code guides
        self.setIndentationGuides(True)
        self.setEdgeMode(QsciScintilla.EDGE_LINE)
        
        # Margin 0 is used to display problem markers (errors and warnings)
        self.setMarginType(0, QsciScintilla.SymbolMargin)
        self.setMarginWidth(0, 16)
        self.setMarginMarkerMask(0, 8)
        
        # Margin 1 is used to display line numbers
        self.setMarginType(1, QsciScintilla.TextMarginRightJustified)
        self._adjust_margin_width()
        self.setMarginLineNumbers(1, True)
        self.setMarginMarkerMask(1, 0)
        
        # Margin 2 is used to display folding commands
        self.setMarginType(2, QsciScintilla.SymbolMargin)
        self.setFolding(QsciScintilla.CircledTreeFoldStyle)
        
        # Syntax errors highlight symbols
        crosscircle_icon = QPixmap("images/crosscircle.png")
        self._syntax_error_marker = self.markerDefine(crosscircle_icon, 3)
        self._syntax_error_indicator = self.indicatorDefine(
                                                QsciScintilla.SquiggleIndicator)
        self.setIndicatorForegroundColor(Qt.red, self._syntax_error_indicator)
        
        # SyntaxError list
        self._syntax_errors = []
        
        # Ensure the margin width is enough to show line numbers
        self.linesChanged.connect(self._adjust_margin_width)
        
        # Enable mouse tracking for tooltips
        QsciScintilla.setMouseTracking(self, True)
        
        # Line tool tip timer
        self._tool_tip_timer = QTimer(self)
        self._tool_tip_timer.setSingleShot(True)
        self._tool_tip_timer.timeout.connect(self._show_tool_tip)
        
        # Keep track of the mouse position
        self._mouse_position = None
        self._global_mouse_position = None
        
    def mouseMoveEvent(self, event):
        # This reimplementation adds support for tool tips
        
        QsciScintilla.mouseMoveEvent(self, event)
        QToolTip.hideText()
        self._global_mouse_position = event.globalPos()
        self._mouse_position = event.pos()
        self._tool_tip_timer.stop()
        self._tool_tip_timer.start(self.tool_tip_delay * 1000)
        
    def keyPressEvent(self, event):
        # This reimplementation add support for auto indentation
        # for blocks
        
        need_indent = (event.key() == Qt.Key_Return and
                       self._need_auto_indent_open())
              
        QsciScintilla.keyPressEvent(self, event)
        
        if need_indent:
            self._insert_indent()

        
    def addSyntaxErrors(self, errors):
        """Add syntax errors to show in the editor."""
        
        for error in errors:
            lineno = error.lineno - 1
            self.markerAdd(lineno, self._syntax_error_marker)
            if self.annotations_active:
                self.annotate(lineno, error.msg, 0)
                
            offset = error.offset if error.offset else self.lineLength(lineno)
            
            self.fillIndicatorRange(lineno, 0, lineno, offset,
                                    self._syntax_error_indicator)
          
        self._syntax_errors = errors
        
    def cleanSyntaxErrors(self):
        """Remove all syntax error shown in the editor."""
        
        self.markerDeleteAll()
        self.clearAnnotations()
        last_line = self.lines()
        last_offset = self.lineLength(last_line)
        self.clearIndicatorRange(0, 0, last_line, last_offset,
                                 self._syntax_error_indicator)
        self._syntax_errors = []
        
    def print_on_paper(self):
        """Print the document with a printer."""
        
        printer = Qsci.QsciPrinter()
        print_dialog = QPrintDialog(printer)
        print_dialog.setWindowTitle(self.tr("Print Document"))
        print_dialog.addEnabledOption(QPrintDialog.PrintSelection)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            printer.printRange(self)
        
        
    def _adjust_margin_width(self):
        # Margins are adjusted in width according to the numer of lines
        # in order to make sure the line number shows up propely
        
        margin_size = self.SendScintilla(QsciScintilla.SCI_TEXTWIDTH,
                    QsciScintilla.STYLE_LINENUMBER, str(self.lines()))
        self.setMarginWidth(1, margin_size)
        
    def _show_tool_tip(self):
        # Show a tool tip based on the mouse position
        
        mouse_line = self._mouse_margin_line()
        if mouse_line == -1:
            return
        for syntax_error in self._syntax_errors:
            if syntax_error.lineno - 1 == mouse_line:
                QToolTip.showText(self._global_mouse_position,
                                   QString(syntax_error.msg))
                
    def _mouse_margin_line(self):
        # Get the index of the line when the mouse cursor is onto
        # a margin.
        # If the mouse cursor is not onto a margin -1 is returned
        
        if (self._mouse_position.x() < self.marginWidth(0)):
            margin_total_width = 0
            for i in range(0, 5):
                margin_total_width += self.marginWidth(i)
            line_pos = QPoint(margin_total_width + 1, self._mouse_position.y())
            return self.lineAt(line_pos)
        return -1
        
    def _need_auto_indent_open(self):
        # Determins, based on the current cursor position, if
        # a new line will cause the code to be in a sub block
        # and thus a indentation is required
        
        cursor_pos = self.getCursorPosition()
        cursor_line_text = str(self.text(cursor_pos[0]))
        
        if QPythonEdit._is_pos_after_code(cursor_pos[1], cursor_line_text):
            for keyword in QPythonEdit.new_block_keywords:
                if re.match("\\s*" + keyword, cursor_line_text):
                    before_cursor_text = cursor_line_text[:cursor_pos[1]]
                    if re.match(".*:\\s*\\Z", before_cursor_text):
                        return True
                    else:
                        return False
        return False
    
    def _insert_indent(self):
        # Insert  an indentation where in the cursor positon and
        # moves the cursor after the inserted indentation, thus
        # having the same effect of hitting the tab button
        
        cursor_pos = self.getCursorPosition()
        if self.indentationsUseTabs():
            # FIXME: For some reason two tabs are inserted
            indent_string = "\t"
        else:
            indent_string = " " * self.indentationWidth()
        new_cursor_pos = cursor_pos[0], cursor_pos[1] + \
                         self.indentationWidth()
        self.insertAt(indent_string, cursor_pos[0], 0)

        self.setCursorPosition(*new_cursor_pos)
        
    @classmethod
    def _is_pos_after_code(cls, pos, text):
        # check if actual, non comment code appears after
        # the pos position in the text string
        
        after_pos_text = text[pos:]
        for ch in after_pos_text:
            if ch not in string.whitespace:
                if ch == "#":
                    return True
                else:
                    return False
        return True
            
        
        
