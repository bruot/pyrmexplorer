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


"""Qt dialog showing a progress bar"""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QProgressBar, QHBoxLayout


class ProgressWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent,
                         Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.progressBar)
        self.setLayout(mainLayout)

        self.step = 0
        self.nSteps = 1


    def refresh(self):

        self.progressBar.setMaximum(int(self.nSteps))
        self.progressBar.setValue(int(self.step))


    def open(self):

        self.refresh()
        super().open()


    def closeEvent(event):

        event.ignore()


    def keyPressEvent(event):

        # Disables key events
        pass


    def updateStep(self, step):

        self.step = step
        self.refresh()
