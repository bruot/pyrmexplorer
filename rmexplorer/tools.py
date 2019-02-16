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


"""Tools for rMExplorer"""


import os
import io
import socket
import functools
import urllib.request
import wand.image


@functools.total_ordering
class Version(object):
    """Represents a program version"""

    def __init__(self, version_str):
        self._version = tuple([int(val) for val in version_str.split('.')])


    def __eq__(self, v):
        return self._version == v._version


    def __gt__(self, v):
        return self._version > v._version


def downloadFile(fid, basePath, destRelPath, mode, settings):

    destPath = os.path.join(basePath, destRelPath)
    if mode == 'png':
        # We rewrite the path to add an intermediate folder with the visible name:
        parts = os.path.split(destPath)
        destPath = os.path.join(parts[0], parts[1][:-4] + '_pages', parts[1])
    parts = os.path.split(destPath)
    url = settings.value('downloadURL', type=str) % fid
    if not os.path.isdir(parts[0]):
        os.makedirs(parts[0])
    socket.setdefaulttimeout(settings.value('HTTPTimeout', type=int))
    data = urllib.request.urlopen(url).read() # PDF data
    socket.setdefaulttimeout(settings.value('HTTPShortTimeout', type=float))
    if mode == 'pdf':
        with open(destPath, 'bw') as f:
            f.write(data)
    else: # mode = png
        with wand.image.Image(file=io.BytesIO(data),
                              resolution=settings.value('PNGResolution', type=int)) as img:
            with img.convert('png') as converted:
                converted.save(filename=destPath)
