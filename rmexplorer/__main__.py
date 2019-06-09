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


"""GUI explorer for Remarkable tablets"""


import os
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from rmexplorerwindow import RmExplorerWindow


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName('pyrMExplorer')
    app.setOrganizationName('rMTools')
    thisDir = os.path.dirname(os.path.abspath(__file__))
    app.setWindowIcon(QIcon(os.path.join(thisDir, 'icon.png')))
    mainWindow = RmExplorerWindow()
    mainWindow.show()
    sys.exit(app.exec_())
