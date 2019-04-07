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


"""Qt dialog that presents saving options to the user"""


from PyQt5.QtWidgets import QVBoxLayout, QRadioButton

from okcanceldialog import OKCancelDialog


class SaveOptsDialog(OKCancelDialog):

    def __init__(self, settings, parent=None):

        super().__init__(parent=parent)

        self.settings = settings
        self.pdfRB = QRadioButton('Save as PDF', self)
        self.pngRB = QRadioButton('Save as stack of PNG', self)

        lastMode = self.settings.value('lastSaveMode', type=str)
        if lastMode == 'pdf':
            self.pdfRB.setChecked(True)
        else:
            self.pngRB.setChecked(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.pdfRB)
        mainLayout.addWidget(self.pngRB)

        self.setLayout(mainLayout)

        self.setWindowTitle('Save options')


    def __del__(self):

        if self.pdfRB.isChecked():
            self.settings.setValue('lastSaveMode', 'pdf')
        else:
            self.settings.setValue('lastSaveMode', 'png')


    def getSaveMode(self):

        return 'pdf' if self.pdfRB.isChecked() else 'png'
