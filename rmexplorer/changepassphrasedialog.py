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


"""Qt dialog to change or set the master passphrase"""


import password_strength

from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QMessageBox

import rmexplorer.constants as constants
from rmexplorer.okcanceldialog import OKCancelDialog


class ChangePassphraseDialog(OKCancelDialog):

    def __init__(self, settings, parent=None):

        super().__init__(parent=parent)

        self.settings = settings

        self.oldPassphraseLE = QLineEdit(self)
        self.oldPassphraseLE.setEchoMode(QLineEdit.Password)
        self.newPassphraseLE = QLineEdit(self)
        self.newPassphraseLE.setEchoMode(QLineEdit.Password)
        self.repeatPassphraseLE = QLineEdit(self)
        self.repeatPassphraseLE.setEchoMode(QLineEdit.Password)
        mainLayout = QGridLayout()
        oldPassphraseLabel = QLabel('Old passphrase:', self)
        mainLayout.addWidget(oldPassphraseLabel, 0, 0)
        mainLayout.addWidget(self.oldPassphraseLE, 0, 1)
        oldPassphraseLabel.setEnabled(self.settings.isPassphraseSet())
        self.oldPassphraseLE.setEnabled(self.settings.isPassphraseSet())
        mainLayout.addWidget(QLabel('New passphrase:'), 1, 0)
        mainLayout.addWidget(self.newPassphraseLE, 1, 1)
        mainLayout.addWidget(QLabel('Repeat new passphrase:'), 2, 0)
        mainLayout.addWidget(self.repeatPassphraseLE, 2, 1)
        mainLayout.addWidget(self.repeatPassphraseLE)
        self.setLayout(mainLayout)

        self.setWindowTitle('%s passphrase settings' % constants.AppName)


    def validationWarning(self, message):
        QMessageBox.warning(self, constants.AppName, message)


    def ok(self):

        # Data validation
        #
        # Check old password:
        if self.oldPassphraseLE.isEnabled():
            if not self.settings.unlockMasterKey(self.oldPassphraseLE.text()):
                self.validationWarning('The old passphrase is not correct.')
                return
        # Match between old and new
        if self.newPassphraseLE.text() != self.repeatPassphraseLE.text():
            self.validationWarning('The new passphrases do not match.')
            return

        # Password complexity
        new_password = self.newPassphraseLE.text()
        if new_password == '' or password_strength.PasswordStats(new_password).strength() < constants.PassphraseMinStrength:
            self.validationWarning('Passphrase is not complex enough.')
            return
        elif len(new_password) > constants.PassphraseMaxLen:
            self.validationWarning('Passphrase should contain at most %d characters.' % constants.PassphraseMaxLen)
            return

        super().ok()
