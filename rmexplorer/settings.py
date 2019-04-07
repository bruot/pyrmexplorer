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


import base64
import Cryptodome.Cipher.AES
import Cryptodome.Random
import Cryptodome.Protocol.KDF

from PyQt5.QtCore import QSettings, QStandardPaths, QCoreApplication
from PyQt5.QtWidgets import QDialog, QMessageBox

import tools
from _version import __version__
import constants
import migrations
from askpassphrasedialog import AskPassphraseDialog


class Settings():

    def __init__(self, masterKey=None):

        self._settings = QSettings(QCoreApplication.applicationName(),
                                   QCoreApplication.organizationName())

        # Expose directly some methods of _settings
        self.value = self._settings.value
        self.setValue = self._settings.setValue
        self.sync = self._settings.sync
        self.beginGroup = self._settings.beginGroup
        self.endGroup = self._settings.endGroup

        # Load settings or set default parameters.  Keys are case-insensitive.
        #
        # Special treatment for _version
        if not self._settings.contains('version'):
            self._settings.setValue('version', __version__)
        else:
            settings_ver = tools.Version(self._settings.value('version'))
            if settings_ver > tools.Version(__version__):
                # Program older than settings: force the user to upgrade.
                raise Exception("Program version %s is lower than settings version (%s). Use rmExplorer's latest version." % (__version__,
                                                                                                                              self._settings.value('version')))
            else:
                # Program may be newer than settings.  Settings migrations go
                # here.
                #
                # Make sure version is updated in each migration.
                if settings_ver < tools.Version('1.1.0'):
                    migrations.settings_v1_1_0_migration(self)

        self._masterKey = masterKey
        self._set_defaults()


    def setEncryptedStrValue(self, key, value):
        """Writes a value in the settings in an encrypted form

        Master key must be unlocked.
        """

        if not self.isMasterKeyUnlocked():
            raise RuntimeError('Called setEncryptedStrValue while master key is locked.')

        # Encrypt value with the master key and a new IV
        cipher = Cryptodome.Cipher.AES.new(self._masterKey,
                                           Cryptodome.Cipher.AES.MODE_CFB)
        ct_bytes = cipher.encrypt(value.encode('utf-8'))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        self.setValue('Encrypted/%s.IV' % key, iv)
        self.setValue('Encrypted/%s.CipherText' % key, ct)


    def encryptedStrValue(self, key, crypto_key=None):

        if crypto_key is None:
            crypto_key = self._masterKey

        iv = self.value('Encrypted/%s.IV' % key)
        ct = self.value('Encrypted/%s.CipherText' % key)
        if ct == '':
            return ''
        try:
            iv_bytes = base64.b64decode(iv.encode('utf-8'))
            ct_bytes = base64.b64decode(ct.encode('utf-8'))
            cipher = Cryptodome.Cipher.AES.new(crypto_key,
                                               Cryptodome.Cipher.AES.MODE_CFB,
                                               iv=iv_bytes)
            value = cipher.decrypt(ct_bytes).decode('utf-8')
        except (ValueError, KeyError):
            raise tools.DecipherError()
        return value


    def unlockMasterKey(self, passphrase):
        """Unlocks and checks the master key from the given passphrase

        The passphrase must be set when this is called.
        """

        if not self.isPassphraseSet():
            raise RuntimeError('Called unlockMasterKey while passphrase is not set.')

        kdf_algo = self.value('KDF.Algorithm')
        salt_bytes = base64.b64decode(self.value('KDF.Salt').encode('utf-8'))
        iterations = int(self.value('KDF.Iterations'))
        hash_module = self.value('KDF.Hash')
        passphrase_bytes = passphrase.encode('utf-8')
        KDFAlgo = getattr(Cryptodome.Protocol.KDF, kdf_algo)
        master_key = KDFAlgo(passphrase_bytes,
                             salt_bytes,
                             dkLen=constants.MasterKeyLen,
                             count=iterations,
                             hmac_hash_module=getattr(Cryptodome.Hash, hash_module))
        try:
            value = self.encryptedStrValue('TestString', crypto_key=master_key)
        except tools.DecipherError:
            return False
        if value == constants.TestString:
            self._masterKey = master_key
            return True
        else:
            return False


    def unlockMasterKeyInteractive(self, parent):
        if not self.isPassphraseSet():
            QMessageBox.warning(parent, 'rMExplorer',
                                'No master passphrase set. Please set a master passphrase in the settings to enable the passwords saving feature.')
            return False

        if not self.isMasterKeyUnlocked():
            # Unlock master key
            while True:
                dialog = AskPassphraseDialog(parent)
                result = dialog.exec()
                if result != QDialog.Accepted:
                    return False
                if self.unlockMasterKey(dialog.passphraseLE.text()):
                    break

        return True


    def isPassphraseSet(self):
        return bool(self.value('Encrypted/TestString.CipherText'))


    def isMasterKeyUnlocked(self):
        return bool(self._masterKey is not None)


    def changeMasterKey(self, newPassphrase):
        """Changes the master key

        The old master key must be unlocked.
        """

        change = self.isPassphraseSet()
        if change and self._masterKey is None:
            raise RuntimeError('Called changeMasterKey while master key is locked.')

        oldMasterKey = self._masterKey

        # Set up new KDF parameters and master key
        kdf_algo = 'PBKDF2'
        salt_bytes = Cryptodome.Random.get_random_bytes(16)
        iterations = 100000
        hash_module = 'SHA256'
        self.setValue('KDF.Algorithm', kdf_algo)
        self.setValue('KDF.Salt', base64.b64encode(salt_bytes).decode('utf-8'))
        self.setValue('KDF.Iterations', iterations)
        self.setValue('KDF.Hash', hash_module)
        passphrase_bytes = newPassphrase.encode('utf-8')
        KDFAlgo = getattr(Cryptodome.Protocol.KDF, kdf_algo)
        self._masterKey = KDFAlgo(passphrase_bytes,
                                  salt_bytes,
                                  dkLen=constants.MasterKeyLen,
                                  count=iterations,
                                  hmac_hash_module=getattr(Cryptodome.Hash, hash_module))

        # Re-encrypt relevant settings
        self.beginGroup('Encrypted')
        keys = [k[:-len('.CipherText')] for k in self._settings.childKeys() if k.endswith('.CipherText')]
        keys.remove('TestString')
        self.endGroup()
        self.setEncryptedStrValue('TestString', constants.TestString)
        if change:
            for key in keys:
                value = self.encryptedStrValue(key, crypto_key=oldMasterKey)
                self.setEncryptedStrValue(key, value)


    def deleteMasterKey(self):
        """Deletes the master key and all encrypted data"""

        # Empty KDF parameters
        self.setValue('KDF.Algorithm', '')
        self.setValue('KDF.Salt', '')
        self.setValue('KDF.Iterations', '')
        self.setValue('KDF.Hash', '')
        self._masterKey = None

        # Erase encrypted data
        self.beginGroup('Encrypted')
        for elem in self._settings.childKeys():
            self.setValue(elem, '')
        self.endGroup()


    def _set_defaults(self):
        """Set settings default values for fields that do not already exist"""

        # Hidden settings
        self._get_or_set('lastDir',
                         QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
        self._get_or_set('lastSSHBackupDir',
                         QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
        self._get_or_set('lastSaveMode', 'pdf')
        self._get_or_set('KDF.Algorithm', '')
        self._get_or_set('KDF.Salt', '')
        self._get_or_set('KDF.Iterations', '')
        self._get_or_set('KDF.Hash', '')
        #
        # Settings on the Settings dialog
        self._get_or_set('downloadURL', 'http://10.11.99.1/download/%s/placeholder')
        self._get_or_set('listFolderURL', 'http://10.11.99.1/documents/%s')
        self._get_or_set('HTTPTimeout', 60)
        self._get_or_set('HTTPShortTimeout', 0.5)
        self._get_or_set('PNGResolution', 360)
        self._get_or_set('TabletHostname', '')
        self._get_or_set('SSHUsername', 'root')
        self._get_or_set('TabletDocumentsDir', '/home/root/.local/share/remarkable/xochitl')

        # Group containing all settings encrypted with the master key
        self.beginGroup('Encrypted')
        self._get_or_set('TestString.IV', '')
        self._get_or_set('TestString.CipherText', '')
        self._get_or_set('SSHPassword.IV', '')
        self._get_or_set('SSHPassword.CipherText', '')
        self.endGroup()


    def _get_or_set(self, key, defaultValue):
        """Retrieves a value from settings, setting a default value if non-existent"""

        if not self._settings.contains(key):
            self._settings.setValue(key, defaultValue)

        return self._settings.value(key)
