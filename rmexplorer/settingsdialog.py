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


from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QGroupBox,
                             QGridLayout, QVBoxLayout, QMessageBox, QDialog)
from PyQt5.QtGui import QValidator, QIntValidator, QDoubleValidator

from rmexplorer.okcanceldialog import OKCancelDialog
from rmexplorer.changepassphrasedialog import ChangePassphraseDialog
from rmexplorer.editpassword import EditPassword
import rmexplorer.constants as constants


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
        locale = QLocale()
        val = locale.toString(self.settings.value('HTTPTimeout', type=int))
        self.httpTimeoutLE = QLineEdit(val, self)
        self.httpTimeoutLE.setValidator(QIntValidator(constants.HttpTimeoutMin,
                                                      constants.HttpTimeoutMax,
                                                      self))
        val = locale.toString(self.settings.value('HTTPShortTimeout', type=float),
                              precision=constants.HttpShortTimeoutMaxDecimals)
        self.httpShortTimeoutLE = QLineEdit(val, self)
        self.httpShortTimeoutLE.setValidator(QDoubleValidator(constants.HttpShortTimeoutMin,
                                                              constants.HttpShortTimeoutMax,
                                                              constants.HttpShortTimeoutMaxDecimals,
                                                              self))
        val = locale.toString(self.settings.value('PNGResolution', type=int))
        self.pngResolutionLE = QLineEdit(val, self)
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

        securityGroupBox = QGroupBox('Security', self)
        self.changePassphraseBtn = QPushButton("Set/change", self)
        self.changePassphraseBtn.clicked.connect(self.changePassphrase)
        self.deletePassphraseBtn = QPushButton("Delete", self)
        self.deletePassphraseBtn.clicked.connect(self.deletePassphrase)
        securityLayout = QGridLayout()
        securityLayout.addWidget(QLabel('Set or change the master passphrase:'), 0, 0)
        securityLayout.addWidget(self.changePassphraseBtn, 0, 1)
        securityLayout.addWidget(QLabel('Delete the master passphrase:'), 1, 0)
        securityLayout.addWidget(self.deletePassphraseBtn, 1, 1)
        securityGroupBox.setLayout(securityLayout)

        sshGroupBox = QGroupBox('SSH', self)
        self.sshHostLE = QLineEdit(self.settings.value('TabletHostname', type=str), self)
        self.sshUsernameLE = QLineEdit(self.settings.value('SSHUsername', type=str), self)
        self.changeSSHPasswordBtn = QPushButton("Set/change", self)
        self.changeSSHPasswordBtn.clicked.connect(self.changeSSHPassword)
        self.tabletDocsDirLE = QLineEdit(self.settings.value('TabletDocumentsDir', type=str), self)
        sshLayout = QGridLayout()
        sshLayout.addWidget(QLabel('Hostname or IP address:'), 0, 0)
        sshLayout.addWidget(self.sshHostLE, 0, 1)
        sshLayout.addWidget(QLabel('Username:'), 1, 0)
        sshLayout.addWidget(self.sshUsernameLE, 1, 1)
        sshLayout.addWidget(QLabel('Password:'), 2, 0)
        sshLayout.addWidget(self.changeSSHPasswordBtn, 2, 1)
        sshLayout.addWidget(QLabel('Documents directory:'), 3, 0)
        sshLayout.addWidget(self.tabletDocsDirLE, 3, 1)
        sshGroupBox.setLayout(sshLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(urlGroupBox)
        mainLayout.addWidget(miscGroupBox)
        mainLayout.addWidget(securityGroupBox)
        mainLayout.addWidget(sshGroupBox)
        self.setLayout(mainLayout)

        self.updateWindowState()

        self.setWindowTitle('Settings')

        self.accepted.connect(self.updateSettings)


    def updateWindowState(self):
        self.deletePassphraseBtn.setEnabled(self.settings.isPassphraseSet())


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


    def changePassphrase(self):

        dialog = ChangePassphraseDialog(self.settings, self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.settings.changeMasterKey(dialog.newPassphraseLE.text())
            self.updateWindowState()


    def deletePassphrase(self):

        # Ask confirmation
        reply = QMessageBox.question(self, constants.AppName,
                                     'Are you sure you want to delete the passphrase and all the encrypted parameters?')
        if reply == QMessageBox.No:
            return

        # Delete encrypted parameters
        self.settings.deleteMasterKey()
        self.updateWindowState()
        QMessageBox.information(self, constants.AppName,
                                'All encrypted data have been erased.')


    def changeSSHPassword(self):

        ep = EditPassword(self, self.settings, 'SSH password', 'SSHPassword')
        ep.exec()


    def updateSettings(self):

        locale = QLocale()
        self.settings.setValue('listFolderURL',
                               str(self.listFolderUrlLE.text()))
        self.settings.setValue('downloadURL',
                               str(self.downloadUrlLE.text()))
        self.settings.setValue('HTTPTimeout',
                               locale.toUInt(self.httpTimeoutLE.text())[0])
        self.settings.setValue('HTTPShortTimeout',
                               str(locale.toDouble(self.httpShortTimeoutLE.text())[0]))
        self.settings.setValue('PNGResolution',
                               locale.toUInt(self.pngResolutionLE.text())[0])
        self.settings.setValue('TabletHostname',
                               str(self.sshHostLE.text()))
        self.settings.setValue('SSHUsername',
                               str(self.sshUsernameLE.text()))
        self.settings.setValue('TabletDocumentsDir',
                               str(self.tabletDocsDirLE.text()))
