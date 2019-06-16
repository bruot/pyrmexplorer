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


"""Qt dialog to ask for master passphrase"""


from PyQt5.QtWidgets import QLabel, QLineEdit, QVBoxLayout

import rmexplorer.constants as constants
from rmexplorer.okcanceldialog import OKCancelDialog


class AskPassphraseDialog(OKCancelDialog):

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.passphraseLE = QLineEdit(self)
        self.passphraseLE.setEchoMode(QLineEdit.Password)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel('Enter your %s passphrase:' % constants.AppName))
        mainLayout.addWidget(self.passphraseLE)
        self.setLayout(mainLayout)

        self.passphraseLE.setFocus()

        self.setWindowTitle('rMExplorer passphrase')
