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


"""Handles a password change to be recorded in the parameters"""


from PyQt5.QtWidgets import QDialog

from editpassworddialog import EditPasswordDialog


class EditPassword():

    def __init__(self, parent, settings, title, settings_key):
        self._parent = parent
        self._settings = settings
        self._title = title
        self._key = settings_key


    def exec(self):

        if not self._settings.unlockMasterKeyInteractive(self._parent):
            return

        cur_value = self._settings.encryptedStrValue(self._key)
        dialog = EditPasswordDialog('SSH password:', cur_value, self._parent)
        if dialog.exec() == QDialog.Accepted:
            new_value = dialog.passwordLE.text()
            if new_value != cur_value:
                self._settings.setEncryptedStrValue(self._key, new_value)
