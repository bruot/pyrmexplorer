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
from PyQt5.QtCore import QCommandLineParser, QCommandLineOption

from rmexplorer.rmexplorerwindow import RmExplorerWindow

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def main(use_resources=False):

    parser = QCommandLineParser()
    geometryOpt = QCommandLineOption('geometry', 'Main window geometry', 'geometry')
    parser.addOption(geometryOpt)
    parser.process(sys.argv)
    if parser.isSet('geometry'):
        try:
            geometry = tuple(int(val) for val in parser.value('geometry').split('x'))
            if len(geometry) != 4:
                raise
            if any(val < 1 for val in geometry):
                raise
        except:
            print('The --geometry argument value must have a format such as 1x1x640x320 (x, y, width, height).')
            exit(0)
    else:
        geometry = None

    app = QApplication(sys.argv)
    app.setApplicationName('pyrMExplorer')
    app.setOrganizationName('rMTools')
    if use_resources:
        icon_path = resource_path('icon.ico')
    else:
        icon_path =os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'icon.ico')
    app.setWindowIcon(QIcon(icon_path))
    mainWindow = RmExplorerWindow()
    if geometry:
        mainWindow.setGeometry(*geometry)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':

    main()
