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
import json
import contextlib
import re
import urllib.request
import paramiko
import wand.image

import rmexplorer.constants as constants


class OperationCancelled(Exception):
    pass


class DecipherError(Exception):
    pass


@functools.total_ordering
class Version():
    """Represents a program version"""

    def __init__(self, version_str):
        self._version = tuple([int(val) for val in version_str.split('.')])


    def __eq__(self, v):
        return self._version == v._version


    def __gt__(self, v):
        return self._version > v._version


@contextlib.contextmanager
def openSftp(settings):
    """Defines a context manager that opens an SFTP session with parameters from `settings`"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(settings.value('TabletHostname', type=str),
                    username=settings.value('SSHUsername', type=str),
                    password=settings.encryptedStrValue('SSHPassword'),
                    timeout=constants.SSHTimeout,
                    banner_timeout=constants.SSHTimeout,
                    allow_agent=False)
        try:
            sftp = ssh.open_sftp()
            yield sftp
        finally:
            sftp.close()
    finally:
        ssh.close()


def listDir(dirId, settings):
    """Obtain from a HTTP request the list of collections and documents of a collection"""

    url = settings.value('listFolderURL', type=str) % dirId
    res = urllib.request.urlopen(url)
    encoding = res.info().get_content_charset() or constants.HttpDefaultEncoding
    data = res.read().decode(encoding)

    data = json.loads(data)

    collections = []
    docs = []
    for elem in data:
        id_ = elem['ID']
        name = elem['VissibleName'] # yes, "Vissible"
        if elem['Type'] == 'CollectionType':
            collections.append((id_, name))
        elif elem['Type'] == 'DocumentType':
            docs.append((id_, name))
    # Sort by name:
    collections = sorted(collections, key=lambda elem: elem[1])
    docs = sorted(docs, key=lambda elem: elem[1])

    return collections, docs


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


def isValidBackupDir(folder):
    """Checks if a folder looks like a backup by looking at the structure of filenames"""

    filenames = os.listdir(folder)

    if len(filenames) == 0:
        return (False, 'Folder is empty.')

    regexp = '^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}(\.[a-z0-9]+)*$'
    for filename in filenames:
        m = re.match(regexp, filename)
        if m is None:
            return (False, 'Folder contains file or folder "%s" that does not seem to be part of a reMarkable document according its name.' % filename)

    return (True, None)
