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


"""Migration scripts"""


from PyQt5.QtCore import QStandardPaths


def settings_v1_1_0_migration(settings):
    """Settings upgrade to v1.1.0

    This includes:

        - Splitting HTTP timeouts into two settings

        - Adding master password feature

        - SSH password storage
    """

    # Overwrite HTTPTimeout
    settings.setValue('HTTPTimeout', 60)
    # Add HTTPShortTimeout
    settings.setValue('HTTPShortTimeout', 0.5)

    # Add master password feature
    settings.setValue('KDF.Algorithm', '')
    settings.setValue('KDF.Salt', '')
    settings.setValue('KDF.Iterations', '')
    settings.setValue('KDF.Hash', '')
    settings.beginGroup('Encrypted')
    settings.setValue('TestString.IV', '')
    settings.setValue('TestString.CipherText', '')
    settings.endGroup()

    # Add SSH backup feature
    settings.setValue('TabletHostname', '')
    settings.setValue('SSHUsername', 'root')
    settings.setValue('TabletDocumentsDir', '/home/root/.local/share/remarkable/xochitl')
    settings.beginGroup('Encrypted')
    settings.setValue('SSHPassword.IV', '')
    settings.setValue('SSHPassword.CipherText', '')
    settings.endGroup()
    settings.setValue('lastSSHBackupDir',
                      QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))

    # Update version
    settings.setValue('version', '1.1.0')


def settings_v1_2_0_migration(settings):
    """Settings upgrade to v1.2.0

    This includes:

        - Increasing HTTPShortTimeout to 1 s if the user left it to the old
          default value of 0.5 s.
    """

    if settings.value('HTTPShortTimeout', type=float) == 0.5:
        # Increase HTTPShortTimeout
        settings.setValue('HTTPShortTimeout', 1.0)

    # Update version
    settings.setValue('version', '1.2.0')


def settings_v1_3_0_migration(settings):
    """Settings upgrade to v1.3.0

    This includes:

        - Adding uploadURL setting
    """

    settings.setValue('uploadURL', 'http://10.11.99.1/upload')

    # Update version
    settings.setValue('version', '1.3.0')
