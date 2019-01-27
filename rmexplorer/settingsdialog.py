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
                             QGridLayout, QVBoxLayout)
from PyQt5.QtGui import QIntValidator

from okcanceldialog import OKCancelDialog


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
        self.httpTimeoutLE.setValidator(QIntValidator(0, 999, self))
        self.pngResolutionLE = QLineEdit(str(self.settings.value('PNGResolution', type=int)), self)
        self.pngResolutionLE.setValidator(QIntValidator(36, 4800, self))
        miscLayout = QGridLayout()
        miscLayout.addWidget(QLabel('HTTP timeout (s):'), 0, 0)
        miscLayout.addWidget(self.httpTimeoutLE, 0, 1)
        miscLayout.addWidget(QLabel('PNG export resolution (dpi):'), 1, 0)
        miscLayout.addWidget(self.pngResolutionLE, 1, 1)
        miscGroupBox.setLayout(miscLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(urlGroupBox)
        mainLayout.addWidget(miscGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle('Settings')

        self.accepted.connect(self.updateSettings)


    def updateSettings(self):

        self.settings.setValue('listFolderURL',
                               str(self.listFolderUrlLE.text()))
        self.settings.setValue('downloadURL',
                               str(self.downloadUrlLE.text()))
        self.settings.setValue('HTTPTimeout',
                               int(self.httpTimeoutLE.text()))
        self.settings.setValue('PNGResolution',
                               int(self.pngResolutionLE.text()))
