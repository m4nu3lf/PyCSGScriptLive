from PyQt4.QtGui import QDialog
from ui_preferencesdialog import Ui_PreferencesDialog


_scintilla_styles_names = ["default",
                           "comment",
                           "number",
                           "double quoted string",
                           "single quoted string",
                           "keyword",
                           "triple single quoted string",
                           "triple double quoted string",
                           "class name",
                           "function method name",
                           "operator",
                           "identifier",
                           "comment block",
                           "unclosed string",
                           "highligheted identifier",
                           "docorator"]

class PreferencesDialog(QDialog):
    
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        
        # Create the ui
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        
        self.editor = parent.editor
        
        # Temporany variables
        editor = self.editor
        ui = self.ui
        mainwindow = self.parent()
        
        # Initialize editor preferences        
        ui.annotationsCheckBox.setChecked(editor.annotations_active)
        ui.autoIndentCheckBox.setChecked(editor.autoIndent())
        autocompletion_threshold = editor.autoCompletionThreshold()
        ui.autoCompletionCheckBox.setChecked(autocompletion_threshold >= 0)
        ui.autoCompletionThresholdSpinBox.setValue(autocompletion_threshold)
        ui.indentWidthSpinBox.setValue(editor.indentationWidth())
        if editor.indentationsUseTabs():
            indent_mode = 1
        else:
            indent_mode = 0             
        ui.indentModeComboBox.setCurrentIndex(indent_mode)
        
        # Initialize code preferences
        ui.autoExecutionCheckBox.setChecked(mainwindow.auto_execution)
        ui.checkDelaySpinBox.setValue(parent.code_check_delay)
        
        
        # Signals and slots connections
        self.ui.buttonBox.accepted.connect(self.confirm)
        self.ui.buttonBox.rejected.connect(self.cancel)
        
    def confirm(self):
        editor = self.editor
        mainwindow = self.parent()
        ui = self.ui
        
        # Set editor preferences
        editor.annotations_active = ui.annotationsCheckBox.isChecked()
        editor.setAutoIndent(ui.autoIndentCheckBox.isChecked())
        
        if ui.autoCompletionCheckBox.isChecked():
            threshold = ui.autoCompletionThresholdSpinBox.value()
            editor.setAutoCompletionThreshold(threshold)
        else:
            editor.setAutoCompletionThreshold(-1)
        editor.setIndentationWidth(ui.indentWidthSpinBox.value())
        editor.setIndentationsUseTabs(ui.indentModeComboBox.currentIndex() == 1)
        
        # Set code preferences
        mainwindow.auto_execution = ui.autoExecutionCheckBox.isChecked()
        mainwindow.code_check_delay = ui.checkDelaySpinBox.value()
        
        self.hide()
        self.destroy()
        
    def cancel(self):
        self.hide()
        self.destroy()
        
        
        
    
