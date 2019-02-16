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


"""Wrapper for rMExplorer QSettings"""


import os.path

from PyQt5.QtCore import QSettings, QStandardPaths, QCoreApplication

from tools import Version
from _version import __version__
import migrations


class Settings(object):

    def __init__(self):

        self._settings = QSettings(QCoreApplication.applicationName(),
                                   QCoreApplication.organizationName())

        # Expose directly some methods of _settings
        self.value = self._settings.value
        self.setValue = self._settings.setValue
        self.sync = self._settings.sync

        # Load settings or set default parameters.  Keys are case-insensitive.
        #
        # Special treatment for _version
        if not self._settings.contains('version'):
            self._settings.setValue('version', __version__)
        else:
            settings_ver = Version(self._settings.value('version'))
            if settings_ver > Version(__version__):
                # Program older than settings: force the user to upgrade.
                raise Exception("Program version %s is lower than settings version (%s). Use rmExplorer's latest version." % (__version__,
                                                                                                                              self._settings.value('version')))
            else:
                # Program may be newer than settings.  Settings migrations go
                # here.
                #
                # Make sure version is updated in each migration.
                if settings_ver < Version('1.1.0'):
                    migrations.settings_new_timeouts(self)

        self._set_defaults()


    def _set_defaults(self):
        """Set settings default values for fields that do not already exist"""

        # Hidden settings
        self._get_or_set('lastDir',
                          QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
        self._get_or_set('lastSaveMode', 'pdf')
        #
        # Settings on the Settings dialog
        self._get_or_set('downloadURL', 'http://10.11.99.1/download/%s/placeholder')
        self._get_or_set('listFolderURL', 'http://10.11.99.1/documents/%s')
        self._get_or_set('HTTPTimeout', 60)
        self._get_or_set('HTTPShortTimeout', 0.5)
        self._get_or_set('PNGResolution', 360)


    def _get_or_set(self, key, defaultValue):
        """Retrieves a value from settings, setting a default value if non-existent"""

        if not self._settings.contains(key):
            self._settings.setValue(key, defaultValue)

        return self._settings.value(key)
