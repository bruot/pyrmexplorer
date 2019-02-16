#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This file is part of the pyrmexplorer software that allows exploring
# and downloading content stored on Remarkable tablets.
#
# Copyright 2019 Nicolas Bruot (https://www.bruot.org/hp/)
#
#
# pyrmexplorer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyrmexplorer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyrmexplorer.  If not, see <http://www.gnu.org/licenses/>.


"""Qt dialog to edit settings"""


from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGroupBox,
                             QGridLayout, QVBoxLayout, QMessageBox)
from PyQt5.QtGui import QValidator, QIntValidator, QDoubleValidator

from okcanceldialog import OKCancelDialog
import constants


class SettingsDialog(OKCancelDialog):

    def __init__(self, settings, parent=None):

        super().__init__(parent=parent)

        self.settings = settings

        urlGroupBox = QGroupBox('Query URLs', self)
        self.listFolderUrlLE = QLineEdit(self.settings.value('listFolderURL', type=str), self)
        self.downloadUrlLE = QLineEdit(self.settings.value('downloadURL', type=str), self)
        urlLayout = QGridLayout()
        urlLayout.addWidget(QLabel('Download URL:'), 0, 0)
        urlLayout.addWidget(self.downloadUrlLE, 0, 1)
        urlLayout.addWidget(QLabel('List folder URL:'), 1, 0)
        urlLayout.addWidget(self.listFolderUrlLE, 1, 1)
        urlLayout.setColumnMinimumWidth(1, 300)
        urlGroupBox.setLayout(urlLayout)

        miscGroupBox = QGroupBox('Miscellaneous', self)
        self.httpTimeoutLE = QLineEdit(str(self.settings.value('HTTPTimeout', type=int)), self)
        self.httpTimeoutLE.setValidator(QIntValidator(constants.HttpTimeoutMin,
                                                      constants.HttpTimeoutMax,
                                                      self))
        self.httpShortTimeoutLE = QLineEdit(str(self.settings.value('HTTPShortTimeout', type=float)), self)
        self.httpShortTimeoutLE.setValidator(QDoubleValidator(constants.HttpShortTimeoutMin,
                                                              constants.HttpShortTimeoutMax,
                                                              constants.HttpShortTimeoutMaxDecimals,
                                                              self))
        self.pngResolutionLE = QLineEdit(str(self.settings.value('PNGResolution', type=int)), self)
        self.pngResolutionLE.setValidator(QIntValidator(constants.PngExportDpiMin,
                                                        constants.PngExportDpiMax,
                                                        self))
        miscLayout = QGridLayout()
        miscLayout.addWidget(QLabel('HTTP timeout (s):'), 0, 0)
        miscLayout.addWidget(self.httpTimeoutLE, 0, 1)
        miscLayout.addWidget(QLabel('HTTP short timeout (s):'), 1, 0)
        miscLayout.addWidget(self.httpShortTimeoutLE, 1, 1)
        miscLayout.addWidget(QLabel('PNG export resolution (dpi):'), 2, 0)
        miscLayout.addWidget(self.pngResolutionLE, 2, 1)
        miscGroupBox.setLayout(miscLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(urlGroupBox)
        mainLayout.addWidget(miscGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle('Settings')

        self.accepted.connect(self.updateSettings)


    def ok(self):
        # Validate fields
        msgBox = QMessageBox(self)
        if self.listFolderUrlLE.text() == '':
            msgBox.setText("List folder URL cannot be empty.")
            msgBox.exec()
            return
        elif not '%s' in self.listFolderUrlLE.text():
            msgBox.setText("List folder URL must contain a \"%s\" placeholder.")
            msgBox.exec()
            return
        #
        if self.downloadUrlLE.text() == '':
            msgBox.setText("Download URL cannot be empty.")
            msgBox.exec()
            return
        elif not '%s' in self.downloadUrlLE.text():
            msgBox.setText("Download URL must contain a \"%s\" placeholder.")
            msgBox.exec()
            return
        #
        pos = self.pngResolutionLE.cursorPosition()
        if self.pngResolutionLE.validator().validate(self.pngResolutionLE.text(), pos)[0] != QValidator.Acceptable:
            msgBox.setText("PNG resolution outside integer range (%d-%d)." % (constants.PngExportDpiMin,
                                                                              constants.PngExportDpiMax))
            msgBox.exec()
            return
        #
        pos = self.httpTimeoutLE.cursorPosition()
        if self.httpTimeoutLE.validator().validate(self.httpTimeoutLE.text(), pos)[0] != QValidator.Acceptable:
            msgBox.setText("HTTP timeout outside integer range (%d-%d)." % (constants.HttpTimeoutMin,
                                                                            constants.HttpTimeoutMax))
            msgBox.exec()
            return
        #
        pos = self.httpShortTimeoutLE.cursorPosition()
        if self.httpShortTimeoutLE.validator().validate(self.httpShortTimeoutLE.text(), pos)[0] != QValidator.Acceptable:
            msgBox.setText("HTTP short timeout outside range (%f-%f)." % (constants.HttpShortTimeoutMin,
                                                                          constants.HttpShortTimeoutMax))
            msgBox.exec()
            return

        # All validations succeeded
        super().ok()


    def updateSettings(self):

        self.settings.setValue('listFolderURL',
                               str(self.listFolderUrlLE.text()))
        self.settings.setValue('downloadURL',
                               str(self.downloadUrlLE.text()))
        self.settings.setValue('HTTPTimeout',
                               int(self.httpTimeoutLE.text()))
        self.settings.setValue('HTTPShortTimeout',
                               float(self.httpShortTimeoutLE.text()))
        self.settings.setValue('PNGResolution',
                               int(self.pngResolutionLE.text()))
