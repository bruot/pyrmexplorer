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


"""Base class for Qt dialogs with "OK" and "Cancel" buttons"""


from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QVBoxLayout


class OKCancelDialog(QDialog):

    def __init__(self, parent=None):

        super(OKCancelDialog, self).__init__(parent=parent)

        self.okButton = QPushButton('OK', self)
        self.cancelButton = QPushButton('Cancel', self)

        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.reject)


    def setLayout(self, layout):

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        super().setLayout(mainLayout)


    def ok(self):
        self.accept()
