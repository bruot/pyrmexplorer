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


def settings_new_timeouts(settings):
    """Splits timeouts into two settings

    v1.1.0 migration.
    """

    # Overwrite HTTPTimeout
    settings.setValue('HTTPTimeout', 60)
    # Add HTTPShortTimeout
    settings.setValue('HTTPShortTimeout', 0.5)

    # Update version
    settings.setValue('version', '1.1.0')
