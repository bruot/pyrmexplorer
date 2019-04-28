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


"""Qt worker that restores all types of documents through SSH"""


import os
import errno
import stat
import posixpath
from datetime import datetime
import socket
import paramiko

from PyQt5.QtCore import QObject
# Renaming below is to prepare for switch from PyQt5 to PySide2 when it will be
# mature enough.
from PyQt5.QtCore import pyqtSignal as Signal

import constants
from settings import Settings


class RestoreDocsWorker(QObject):

    notifyProgress = Signal(int)
    error = Signal(str)
    finished = Signal()


    def __init__(self, srcFolder, masterKey):

        super().__init__()

        self._settings = Settings(masterKey)
        self._srcFolder = srcFolder


    def _rmDir(self, sftpClient, dirPath):
        """Deletes remote directory `path`"""

        for f in sftpClient.listdir_attr(dirPath):
            path = posixpath.join(dirPath, f.filename)
            if stat.S_ISDIR(f.st_mode):
                self._rmDir(sftpClient, path)
            else:
                sftpClient.remove(path)
        sftpClient.rmdir(dirPath)


    def _recursiveUpload(self, sftpClient, root, destRoot, count=0):
        """Recursively copies a local folder to a remote location"""

        for name in os.listdir(root):
            count += 1
            self.notifyProgress.emit(count)
            path = os.path.join(root, name)
            destPath = posixpath.join(destRoot, name)
            if os.path.isdir(path):
                sftpClient.mkdir(destPath)
                count = self._recursiveUpload(sftpClient,
                                              path,
                                              destPath,
                                              count)
            else:
                sftpClient.put(path, destPath)

        return count


    def start(self):

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
                    destDir = self._settings.value('TabletDocumentsDir', type=str)
                    try:
                        attr = sftp.lstat(destDir)
                    except FileNotFoundError:
                        # Change the error raised so that it contains path info.
                        raise FileNotFoundError(errno.ENOENT,
                                                os.strerror(errno.ENOENT),
                                                destDir)
                    if not stat.S_ISDIR(attr.st_mode):
                        raise Exception('Remote path "%s" is not a folder.' % destDir)
                    self._rmDir(sftp, destDir)
                    sftp.mkdir(destDir)
                    self._recursiveUpload(sftp,
                                          self._srcFolder,
                                          destDir)
        except FileNotFoundError as e:
            self.error.emit(str(e))
        except socket.timeout:
            self.error.emit('SSH timeout.')
        except socket.error:
            self.error.emit('Socket error. Check that tablet is turned on, Wifi is enabled and that the hostname setting is correct.')
        except paramiko.SSHException as e:
            self.error.emit('SSH error: %s' % str(e))
        except Exception as e:
            self.error.emit(str(e))

        self.finished.emit()
