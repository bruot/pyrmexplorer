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


"""Qt worker that backups all types of documents through SSH"""


import os
import stat
from datetime import datetime
import socket
import paramiko

from PyQt5.QtCore import QObject
# Renaming below is to prepare for switch from PyQt5 to PySide2 when it will be
# mature enough.
from PyQt5.QtCore import pyqtSignal as Signal

import constants
from settings import Settings


class BackupDocsWorker(QObject):

    notifyProgress = Signal(int)
    warning = Signal(str)
    finished = Signal()


    def __init__(self, destFolder, masterKey):

        super().__init__()

        self._settings = Settings(masterKey)
        self._destFolder = destFolder


    def _recursiveDownload(self, sftpClient, root, destRoot, count=0):

        for name in sftpClient.listdir(root):
            count += 1
            self.notifyProgress.emit(count)
            path = os.path.join(root, name)
            destPath = os.path.join(destRoot, name)
            lstat = sftpClient.lstat(path)
            if stat.S_ISDIR(lstat.st_mode):
                os.mkdir(destPath)
                count = self._recursiveDownload(sftpClient,
                                                path, destPath,
                                                count)
            else:
                sftpClient.get(path, destPath)

        return count


    def start(self):

        if not os.path.isdir(self._destFolder):
            self.warning.emit('Not a directory: %s. Aborted.' % self._destFolder)
            self.finished.emit()
            return

        warnings = []

        try:
            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self._settings.value('TabletHostname', type=str),
                            username=self._settings.value('SSHUsername', type=str),
                            password=self._settings.encryptedStrValue('SSHPassword'),
                            timeout=constants.SSHTimeout,
                            banner_timeout=constants.SSHTimeout,
                            allow_agent=False)

                with ssh.open_sftp() as sftp:
                    destFolder = os.path.join(self._destFolder,
                                              datetime.strftime(datetime.now(), 'remarkable_bak_%Y%m%d_%H%M%S'))
                    try:
                        os.mkdir(destFolder)
                    except FileExistsError:
                        warnings.append('Path "%s" already exists.' % destFolder)
                    else:
                        self._recursiveDownload(sftp,
                                                self._settings.value('TabletDocumentsDir', type=str),
                                                destFolder)
        except socket.timeout:
            warnings.append('SSH timeout.')
        except socket.error:
            warnings.append('Socket error. Check that tablet is turned on, Wifi is enabled and that the hostname setting is correct.')
        except paramiko.SSHException as e:
            warnings.append('SSH error: %s' % e)
        except Exception as e:
            warnings.append('Error: %s' % e)

        if warnings:
            msg = '\n'.join(warnings)
            self.warning.emit(msg)
        self.finished.emit()
