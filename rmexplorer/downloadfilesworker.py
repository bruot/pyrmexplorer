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


"""Qt worker that downloads files"""


import os

from PyQt5.QtCore import QObject
# Renaming below is to prepare for switch from PyQt5 to PySide2 when it will be
# mature enough.
from PyQt5.QtCore import pyqtSignal as Signal

from rmexplorer.settings import Settings
import rmexplorer.tools as tools


class DownloadFilesWorker(QObject):

    notifyProgress = Signal(int)
    warning = Signal(str)
    finished = Signal()


    def __init__(self, folder, dlList, mode):

        super().__init__()

        self._settings = Settings()
        self._folder = folder
        self._dlList = dlList
        self._mode = mode


    def start(self):

        if not os.path.isdir(self._folder):
            self.warning.emit('Not a directory: %s. Aborted.' % self._folder)
            self.finished.emit()
            return

        warnings = []
        for i, elem in enumerate(self._dlList):
            self.notifyProgress.emit(i)
            fid, destRelPath = elem
            try:
                tools.downloadFile(fid, self._folder, destRelPath, self._mode,
                                   self._settings)
            except Exception as e:
                warnings.append('%s: %s' % (destRelPath, str(e)))

        if warnings:
            msg = 'Some errors were encountered:\n%s' % '\n'.join(warnings)
            self.warning.emit(msg)
        self.finished.emit()
