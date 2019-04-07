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


"""Qt dialog to change a password"""


from PyQt5.QtWidgets import QLabel, QLineEdit, QVBoxLayout

from okcanceldialog import OKCancelDialog


class EditPasswordDialog(OKCancelDialog):

    def __init__(self, prompt, value, parent=None):

        super().__init__(parent=parent)

        self.passwordLE = QLineEdit(self)
        self.passwordLE.setEchoMode(QLineEdit.Password)
        self.passwordLE.setText(value)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(prompt))
        mainLayout.addWidget(self.passwordLE)
        self.setLayout(mainLayout)

        self.setWindowTitle('rMExplorer')
