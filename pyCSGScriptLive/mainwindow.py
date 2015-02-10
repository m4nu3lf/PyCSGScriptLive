import sys
import os
import subprocess
from copy import deepcopy
from threading import Timer
from PyQt4.QtGui import QMainWindow, QFileDialog, QMessageBox
from PyQt4.QtCore import QFileInfo, QSettings, QStringList
from PyQt4.QtCore import QCoreApplication
from ui_mainwindow import Ui_MainWindow
from preferencesdialog import PreferencesDialog
from csg_code_execution import CodeChecker, CodeExecutor


_app_name = "PyCSGScriptLive"
_app_version_str = "0.1"
_app_version = 0

        
class MainWindow(QMainWindow):
    """The main window class.
    
        This class auto setup the ui and initialize all the needed
        objects, for the windows logic.
        
     """
    def __init__(self):
        QMainWindow.__init__(self)
        
        # Window ui setup
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(_app_name)
        self.editor = self.ui.pythonEdit
        
        # File menu signals and slots connections
        self.ui.actionNew_File.triggered.connect(self.newFile)
        self.ui.actionOpen_File.triggered.connect(self.openFiles)
        self.ui.actionClear_All.triggered.connect(self._clearRecents)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionSave_as.triggered.connect(self.saveFileAs)
        self.ui.actionPrint.triggered.connect(self.editor.print_on_paper)
        self.ui.actionExit.triggered.connect(self.close)
        
        # Edit menu signals and slots connections
        self.ui.actionUndo.triggered.connect(self.editor.undo)
        self.ui.actionRedo.triggered.connect(self.editor.redo)
        self.ui.actionCut.triggered.connect(self.editor.cut)
        self.ui.actionCopy.triggered.connect(self.editor.copy)
        self.ui.actionPaste.triggered.connect(self.editor.paste)
        self.ui.actionDelete.triggered.connect(
                                        self.editor.removeSelectedText)
        self.ui.actionSelect_All.triggered.connect(self.editor.selectAll)
        
        # Run menu signals and slots connections
        self.ui.actionRun_From_Start.triggered.connect(self.runFromStart)
        self.ui.actionRun_From_Last_Statement.triggered.connect(
                                                            self.runFromLast)
        
        # Find/Replace menu signals and slots connections
        self.ui.actionFind_Replace.triggered.connect(self._toggleFindAndReplace)
        self.ui.actionFind_Next.triggered.connect(self._findNext)
        self.ui.actionFind_Previous.triggered.connect(self._findPrevious)
        self.ui.actionReplace.triggered.connect(self._replace)
        self.ui.actionReplace_All.triggered.connect(self._replaceAll)
        
        # Window menu signals and slots connections
        self.ui.actionFull_Screen.triggered.connect(self._toggleFullScreen)
        self.ui.actionPreferences.triggered.connect(self._showPreferences)
        
        # 3D View menu signals and slots connections
        self.ui.actionPerspective.triggered.connect(
                                    self.ui.glPreviewWidget.togglePerspective)
        self.ui.actionReset_Camera.triggered.connect(
                                    self.ui.glPreviewWidget.resetCamera)
        
        # Help menu signals and slots connections
        self.ui.actionAbout.triggered.connect(self.showAbout)
        
        # Find and Replace widget signals and slots connections
        self.ui.findButton.pressed.connect(self._findNext)
        self.ui.replaceButton.pressed.connect(self._replace)
        self.ui.replaceAllButton.pressed.connect(self._replaceAll)
        
        # Other signals and slots
        self.editor.modificationChanged.connect(self._updateWindowTitle)
        
        # Recents file management
        self.recent_file_names = []
        self.recent_files_limit = 5
        
        # Dynamic code execution
        self._auto_execution = True
        self.code_check_delay = 1.0
        self.code_executor = CodeExecutor()
        self.code_checker = CodeChecker(self.code_executor)
        self.editor.textChanged.connect(self._resetCheckTimer)

        self._code_check_timer = Timer(0, None)
        
        # Dynamic code execution signals
        self.code_checker.parseStart.connect(self.editor.cleanSyntaxErrors)
        self.code_checker.parseEnd.connect(self.editor.addSyntaxErrors)
        self.code_executor.csgDataChanged.connect(
            self.ui.glPreviewWidget.setRenderObjects)
        self.code_executor.executionEnd.connect(self.updateConsole)
        
        # Application settings
        self.settings = QSettings(_app_name, _app_name + " " + _app_version_str)
        self.restoreSettings()
        
        # Open file if provided
        self._file_name = None
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r") as f:
                self.file_name = sys.argv[1]
                self.editor.setText(f.read())
                self.editor.setModified(False)
        else:
            self._file_name = "Untitled"
        self._updateWindowTitle(False)

    @property
    def file_name(self):
        """The current file name, if changed, the title of the window \
        and the current working directory are chenged accordigly"""
        
        return self._file_name
    
    @file_name.setter
    def file_name(self, value):
        self._file_name = value
        os.chdir(os.path.dirname(value))
        self._updateWindowTitle(self.editor.isModified())
        
    @property
    def auto_execution(self):
        """Whether auto execution is enabled or not."""
        
        return self._auto_execution
    
    @auto_execution.setter
    def auto_execution(self, value):
        if value and not self._auto_execution:
            self._auto_execution = value
            self._requestCheck()
        else:
            self._auto_execution = value
        
    def updateConsole(self, exec_stdout, exec_stderr, exec_globals,
                      exec_locals):
        """Updates the console with the execution output."""
        
        self.ui.consoleTextEdit.setText("")
        self.ui.consoleTextEdit.append(exec_stdout.getvalue())
        
    def closeEvent(self,event):
        """Overwrites the QMainWindow closeEvent. Check for file
        modfications and ask to save."""
        
        if self.editor.isModified():
            if not self._askForAndSave():
                event.ignore()
                return
        self.code_checker.send_request(CodeChecker.TermRequest())
        self.code_executor.send_request(CodeExecutor.TermRequest())
        self.saveSettings()
        event.accept()
        
    def newFile(self):
        """Creates a new file, actually launches a new instance of \
        the program."""
        
        subprocess.call(["python",  "./pyCSGScriptLive.py"])
    
    def openFiles(self):
        """Opens existing files.
        
        The user is asked for the file target, if here is specified the
        first file will replace the current, otherwise a new instance is
        fired.
        For each file from the second there on, a new instance is fired.
        
        """
        
        dialog_caption = self.tr("Open Files")
        file_names = QFileDialog.getOpenFileNames(caption=dialog_caption,
                                                filter="python script (*py)")
        if len(file_names) == 0:
            return
        else:
            selection = self._askForOpenTarget()
            
        if selection == 2:
            return
        elif selection == 0:
            self.openFileByName(file_names[0], True)
            file_names = file_names[1:]
        
        for file_name in file_names:
            self.openFileByName(str(file_name))
        
    def openFileByName(self, file_name, here = False):
        """Opens the file with the provided name.
        
        If here is specified the opened file will replace the current,
        else a new instance is fired.
        
        """
        
        self._addToRecents(file_name)
        if here:
            if self.editor.isModified():
                if not self._askForAndSave():
                    return False
            with open(file_name, "r") as f:
                self.editor.setText(f.read())
                self.editor.setModified(False)
                self.file_name = str(file_name)
        else:
            subprocess.call(["python", "./pyCSGScriptLive.py", file_name])
            return True
        return False

    def saveFile(self):
        """Save the file with its current file name."""
        
        with open(self.file_name, "w") as f:
            f.write(self.editor.text())
            self.editor.setModified(False)
            self._addToRecents(self.file_name)
        
    def saveFileAs(self):
        """Asks the user for a new file name and save the file with \
        that name."""
        
        file_name = QFileDialog.getSaveFileName(caption="Save File As",
                                             filter="python script (*.py)")
        if file_name:
            self.file_name = str(file_name)
            self.saveFile()
        
    def saveSettings(self):
        """Saves settigns such as the window state and geometry, \
        and user preferences."""
        
        # Widgets state and geometry
        self.settings.beginGroup("widgets")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitter1_state", self.ui.splitter.saveState())
        self.settings.setValue("splitter2_state",
                               self.ui.splitter_2.saveState())
        self.settings.setValue("window_state", self.saveState(_app_version))
        self.settings.endGroup()
        
        # User preferences
        self.settings.beginGroup("preferences")
        self.settings.setValue("annotations", self.editor.annotations_active)
        self.settings.setValue("autoindent", self.editor.autoIndent())
        self.settings.setValue("autocomp_thresh",
                               self.editor.autoCompletionThreshold())
        self.settings.setValue("indent_width", self.editor.indentationWidth())
        self.settings.setValue("indent_use_tabs",
                               self.editor.indentationsUseTabs())
        
        self.settings.setValue("autoexecution", self._auto_execution)
        self.settings.setValue("code_check_delay", self.code_check_delay)
        self.settings.endGroup()
        
        # 3D View state
        self.settings.beginGroup("view_state")
        self.settings.setValue("perspective",
                               self.ui.glPreviewWidget.perspective)
        self.settings.endGroup()
        
    
    def restoreSettings(self):
        """Restore the previous saved settings such as window
        state/geometry and recent files."""
        
        # Check for exsisting settings
        if len(self.settings.allKeys()) == 0:
            return
        
        # Widgets state and geometry
        self.settings.beginGroup("widgets")
        geometry = self.settings.value("geometry").toByteArray()
        splitter1_state = self.settings.value("splitter1_state").toByteArray()
        splitter2_state = self.settings.value("splitter2_state").toByteArray()
        window_state = self.settings.value("window_state").toByteArray()
        self.restoreGeometry(geometry)
        self.restoreState(window_state, _app_version)
        self.ui.splitter.restoreState(splitter1_state)
        self.ui.splitter_2.restoreState(splitter2_state)
        self.settings.endGroup()
        
        # Recent files
        recents_data = self.settings.value("recent_file_names")
        recents_file_names = recents_data.toStringList()
        for recent_file_name in recents_file_names:
            self.recent_file_names.append(str(recent_file_name))
        self._updateRecentsMenu()
        
        # User preferences
        self.settings.beginGroup("preferences")
        annotations_active = self.settings.value("annotations").toBool()
        autoindent = self.settings.value("autoindent").toBool()
        autocomp_thresh = self.settings.value("autocomp_thresh").toInt()[0]
        indent_width = self.settings.value("indent_width").toInt()[0]
        indent_use_tabs = self.settings.value("indent_use_tabs").toBool()
        self._auto_execution = self.settings.value("autoexecution").toBool()
        self.code_check_delay = \
            self.settings.value("code_check_delay").toFloat()[0]
        self.settings.endGroup()
             
        self.editor.annotations_active = annotations_active
        self.editor.setAutoIndent(autoindent)
        self.editor.setAutoCompletionThreshold(autocomp_thresh)
        self.editor.setIndentationWidth(indent_width)
        self.editor.setIndentationsUseTabs(indent_use_tabs)
        
        # 3D View state
        self.settings.beginGroup("view_state")
        persp = self.settings.value("perspective").toBool()
        self.ui.glPreviewWidget.perspective = persp
        self.settings.endGroup()
        
    def showAbout(self):
        """Shows the about dialog."""
        
        with open("about") as f:
            text = f.read().format(_app_version_str)
            QMessageBox.about(self, "About PyCSGScriptLive", text)
            
    def runFromStart(self):
        self.code_executor.send_request(CodeExecutor.StopRequest())
        request = CodeChecker.CheckRequest(unicode(self.editor.text()),
                                               unicode(self.file_name),
                                               True)
        self.code_checker.send_request(request)
        
    def runFromLast(self):
        request = CodeChecker.CheckRequest(unicode(self.editor.text()),
                                               unicode(self.file_name),
                                               True)
        self.code_checker.send_request(request)
        
    def _askForAndSave(self):
        # Asks the user for save the current file, and if the user
        # confirms, save the file.
        # Returns False if the Cancel button is pressed, True otherwise.
 
        file_name = QFileInfo(self.file_name).fileName()
        selection = QMessageBox.warning(self, self.tr("Save File"),
                                        file_name + \
                                        self.tr(" has been modified."),
                                        self.tr("Save"),
                                        self.tr("Ignore"),
                                        self.tr("Cancel"))
        
        if selection == 0:
            self.saveFile()
        
        return selection != 2
    
    def _askForOpenTarget(self):
        # Asks the user for the open target of a file, and return
        # the index of the button pressed.
        
        return QMessageBox.information(self, self.tr("Open Target"),
                                                  self.tr("Open In:"),
                                                  self.tr("Here"),
                                                  self.tr("New Window"),
                                                  self.tr("Cancel"))
        
    def _updateWindowTitle(self, modified):
        # Updates the window title according to the current file name
        # and state.
        if modified:
            modified_note = QCoreApplication.translate("MainWindow",
                                                       "[modified]")
        else:
            modified_note = ""
        file_name = QFileInfo(self.file_name).fileName()
        title = _app_name + " - " + file_name + " " + modified_note
        self.setWindowTitle(title)
        
    def _genRecentOpenSlot(self, file_name):
        # Generates a function that calls the openFileByName with
        # binded with the provided file_name.
        # Used to generate slots for the recents files.

        def open_slot():
            selection = self._askForOpenTarget()
            if selection == 2:
                return
            self.openFileByName(file_name, selection == 0)
          
        return open_slot
    
    def _updateRecentsMenu(self):
        # Ensures the recent files menu matches the recent file names
        # into the recent_file_names attribute.
        # This shoud be called each time the recent_file_names is modified.
        
        self.ui.menuRecent_Files.clear()
        for recent_file_name in self.recent_file_names:
            recent_file_info = QFileInfo(recent_file_name)
            action_text = recent_file_info.baseName() + " ["
            action_text += recent_file_info.canonicalFilePath() + "]"
            file_action = self.ui.menuRecent_Files.addAction(action_text)
            file_name = recent_file_info.canonicalFilePath()
            file_action.triggered.connect(self._genRecentOpenSlot(file_name))
        
        self.ui.menuRecent_Files.addSeparator()
        self.ui.menuRecent_Files.addAction(self.ui.actionClear_All)
    
    def _clearRecents(self):
        # Remove all the recent file names and update the menu
        
        self.recent_file_names = []
        self._updateRecentsMenu()
        
    def _addToRecents(self, file_name):
        # Add a file tot he recents and update the menu
        
        # Removes the file if already into the list of recent file names
        try:
            self.recent_file_names.remove(file_name)
        except ValueError:
            pass
        
        # Insert the element on top of the recent file names
        self.recent_file_names.insert(0, file_name)
        
        # Drops any exeeding entry of the recent file names 
        if len(self.recent_file_names) > self.recent_files_limit:
            self.recent_file_names.pop()
            
        # Save the recent file names in settings
        qrecent_file_names = QStringList()
        for recent_file_name in self.recent_file_names:
            qrecent_file_names.append(recent_file_name)
        self.settings.setValue("recent_file_names", qrecent_file_names)
        
        # Update the Ui
        self._updateRecentsMenu()
        
    def _toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def _toggleFindAndReplace(self):
        if self.ui.findAndReplacedockWidget.isVisible():
            self.ui.findAndReplacedockWidget.hide()
        else:
            self.ui.findAndReplacedockWidget.show()
        
    def _findNext(self):
        expr = self.ui.findTextEdit.toPlainText()
        case_sensitive = self.ui.findCaseSensitiveCheckBox.isChecked()
        is_regex = self.ui.findRegexCheckBox.isChecked()
        whole_word = self.ui.findWholeWordCheckBox.isChecked()
        return self.editor.findFirst(expr, is_regex, case_sensitive, whole_word,
                                     True)
        
    def _findPrevious(self):
        expr = self.ui.findTextEdit.toPlainText()
        case_sensitive = self.ui.findCaseSensitiveCheckBox.isChecked()
        is_regex = self.ui.findRegexCheckBox.isChecked()
        whole_word = self.ui.findWholeWordCheckBox.isChecked()
        cursor_pos = self.editor.getCursorPosition()
        
        # We need to search by a positione before the acutal cursor
        # position otherwise the search will find the same item again and
        # again in the item is located immediately on le left of the cursor.
        pos = cursor_pos[0], max(cursor_pos[1] - 1, 0)
        return self.editor.findFirst(expr, is_regex, case_sensitive, whole_word,
                                     True, False, pos[0], pos[1])
        
    def _replace(self):
        if self.editor.selectedText() == self.ui.findTextEdit.toPlainText():
            self.editor.replace(self.ui.replaceTextEdit.toPlainText())
        elif self._findNext():
            self.editor.replace(self.ui.replaceTextEdit.toPlainText())
            return True
        else:
            return False
        
    def _replaceAll(self):
        self.editor.beginUndoAction()
        while self._replace():
            pass
        self.editor.endUndoAction()
        
    def _showPreferences(self):
        pref_dialog = PreferencesDialog(self)
        pref_dialog.show()
        
    def _requestCheck(self):
        request = CodeChecker.CheckRequest(unicode(self.editor.text()),
                                               unicode(self.file_name),
                                               self._auto_execution)
        self.code_checker.send_request(request)
                
    def _resetCheckTimer(self):
        self._code_check_timer.cancel()
        self._code_check_timer = Timer(self.code_check_delay,
                                       self._requestCheck)
        self._code_check_timer.start()
        
