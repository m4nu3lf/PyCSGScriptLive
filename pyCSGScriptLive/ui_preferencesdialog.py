# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferencesdialog.ui'
#
# Created: Wed Oct  2 13:50:28 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName(_fromUtf8("PreferencesDialog"))
        PreferencesDialog.resize(540, 266)
        self.gridLayout = QtGui.QGridLayout(PreferencesDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(PreferencesDialog)
        self.groupBox.setFlat(True)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.annotationsCheckBox = QtGui.QCheckBox(self.groupBox)
        self.annotationsCheckBox.setObjectName(_fromUtf8("annotationsCheckBox"))
        self.verticalLayout.addWidget(self.annotationsCheckBox)
        self.autoCompletionCheckBox = QtGui.QCheckBox(self.groupBox)
        self.autoCompletionCheckBox.setObjectName(_fromUtf8("autoCompletionCheckBox"))
        self.verticalLayout.addWidget(self.autoCompletionCheckBox)
        self.autoIndentCheckBox = QtGui.QCheckBox(self.groupBox)
        self.autoIndentCheckBox.setObjectName(_fromUtf8("autoIndentCheckBox"))
        self.verticalLayout.addWidget(self.autoIndentCheckBox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.autoCompletionThresholdSpinBox = QtGui.QSpinBox(self.groupBox)
        self.autoCompletionThresholdSpinBox.setObjectName(_fromUtf8("autoCompletionThresholdSpinBox"))
        self.horizontalLayout_3.addWidget(self.autoCompletionThresholdSpinBox)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_3.addWidget(self.label_4)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.indentWidthSpinBox = QtGui.QSpinBox(self.groupBox)
        self.indentWidthSpinBox.setObjectName(_fromUtf8("indentWidthSpinBox"))
        self.horizontalLayout.addWidget(self.indentWidthSpinBox)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.indentModeComboBox = QtGui.QComboBox(self.groupBox)
        self.indentModeComboBox.setObjectName(_fromUtf8("indentModeComboBox"))
        self.indentModeComboBox.addItem(_fromUtf8(""))
        self.indentModeComboBox.addItem(_fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.indentModeComboBox)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 2, 1)
        self.groupBox_2 = QtGui.QGroupBox(PreferencesDialog)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_5.addWidget(self.label_3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.frame = QtGui.QFrame(self.groupBox_2)
        self.frame.setMinimumSize(QtCore.QSize(16, 16))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_5.addWidget(self.frame)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.checkBox = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout_3.addWidget(self.checkBox)
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(PreferencesDialog)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.autoExecutionCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.autoExecutionCheckBox.setObjectName(_fromUtf8("autoExecutionCheckBox"))
        self.verticalLayout_2.addWidget(self.autoExecutionCheckBox)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.checkDelaySpinBox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.checkDelaySpinBox.setObjectName(_fromUtf8("checkDelaySpinBox"))
        self.horizontalLayout_4.addWidget(self.checkDelaySpinBox)
        self.label_5 = QtGui.QLabel(self.groupBox_4)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_4.addWidget(self.label_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.gridLayout.addWidget(self.groupBox_4, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(PreferencesDialog)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences", None))
        self.groupBox.setTitle(_translate("PreferencesDialog", "Editor", None))
        self.annotationsCheckBox.setText(_translate("PreferencesDialog", "Annotations", None))
        self.autoCompletionCheckBox.setText(_translate("PreferencesDialog", "Auto Completion", None))
        self.autoIndentCheckBox.setText(_translate("PreferencesDialog", "Auto Indentation", None))
        self.label_4.setText(_translate("PreferencesDialog", "Auto Completion Threshold", None))
        self.label.setText(_translate("PreferencesDialog", "Indentation Width", None))
        self.indentModeComboBox.setItemText(0, _translate("PreferencesDialog", "Spaces", None))
        self.indentModeComboBox.setItemText(1, _translate("PreferencesDialog", "Tab", None))
        self.label_2.setText(_translate("PreferencesDialog", "Indentation Mode", None))
        self.groupBox_2.setTitle(_translate("PreferencesDialog", "Preview", None))
        self.label_3.setText(_translate("PreferencesDialog", "Background", None))
        self.checkBox.setText(_translate("PreferencesDialog", "Show Grid", None))
        self.checkBox_2.setText(_translate("PreferencesDialog", "Show Axes", None))
        self.groupBox_4.setTitle(_translate("PreferencesDialog", "Code", None))
        self.autoExecutionCheckBox.setText(_translate("PreferencesDialog", "Auto Execution", None))
        self.label_5.setText(_translate("PreferencesDialog", "Check Delay", None))

