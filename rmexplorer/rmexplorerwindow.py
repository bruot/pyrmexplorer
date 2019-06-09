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


"""rMExplorer main window"""


import os
import socket
import json
import urllib.request
import urllib.error

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (qApp, QWidget, QMainWindow, QMenu, QAction,
                             QLabel, QListWidget, QGridLayout, QVBoxLayout,
                             QDialog, QFileDialog, QMessageBox)

import constants
from _version import __version__
from saveoptsdialog import SaveOptsDialog
from settingsdialog import SettingsDialog
from downloadfilesworker import DownloadFilesWorker
from backupdocsworker import BackupDocsWorker
from restoredocsworker import RestoreDocsWorker
from progresswindow import ProgressWindow
from settings import Settings
import tools


class RmExplorerWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.settings = Settings()
        self.updateFromSettings()

        self.statusBar()
        self.makeMenus()

        self.dirsList = QListWidget(self)
        self.dirsList.itemDoubleClicked.connect(self.dirsListItemDoubleClicked)
        self.dirsList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dirsList.customContextMenuRequested.connect(self.dirsListContextMenuRequested)

        self.filesList = QListWidget(self)
        self.filesList.itemDoubleClicked.connect(self.filesListItemDoubleClicked)

        self.curDirLabel = QLabel(self)

        browserLayout = QGridLayout()
        browserLayout.addWidget(QLabel('Folders:'), 0, 0)
        browserLayout.addWidget(QLabel('Files:'), 0, 1)
        browserLayout.addWidget(self.dirsList, 1, 0)
        browserLayout.addWidget(self.filesList, 1, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(browserLayout)
        mainLayout.addWidget(self.curDirLabel)

        centralWidget = QWidget(self)
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.curDir = ''
        self.curDirName = ''
        self.curDirParents = []
        self.curDirParentsNames = []
        self.dirIds = []
        self.dirNames = []
        self.fileIds = []
        self.goToDir('', '')

        self.currentWarning = ''
        self.hasRaised = None

        self.progressWindow = None
        self.downloadFilesWorker = None
        self.backupDocsWorker = None
        self.restoreDocsWorker = None
        self.taskThread = None

        self._masterKey = None

        self.setWindowTitle(constants.AppName)


    ###################
    # General methods #
    ###################

    def updateFromSettings(self):
        """Call this whenever settings are changed"""

        socket.setdefaulttimeout(self.settings.value('HTTPShortTimeout', type=float))


    def makeMenus(self):

        menubar = self.menuBar()

        # Explorer menu
        dlAllAct = QAction('&Download all', self)
        dlAllAct.setShortcut('Ctrl+D')
        dlAllAct.setStatusTip('Download all files to a local folder.')
        dlAllAct.triggered.connect(self.downloadAll)
        #
        refreshAct = QAction('&Refresh', self)
        refreshAct.setShortcut('Ctrl+R')
        refreshAct.setStatusTip('Refresh folders and files lists.')
        refreshAct.triggered.connect(self.refreshLists)
        #
        settingsAct = QAction('&Settings', self)
        settingsAct.setShortcut('Ctrl+S')
        settingsAct.setStatusTip('%s settings' % constants.AppName)
        settingsAct.triggered.connect(self.editSettings)
        #
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit %s.' % constants.AppName)
        exitAct.triggered.connect(qApp.quit)
        #
        explorerMenu = menubar.addMenu('&Explorer')
        explorerMenu.addAction(dlAllAct)
        explorerMenu.addAction(refreshAct)
        explorerMenu.addAction(settingsAct)
        explorerMenu.addAction(exitAct)

        # SSH menu
        backupDocsAct = QAction('&Backup documents', self)
        backupDocsAct.setStatusTip('Backup all notebooks, documents, ebooks and bookmarks to a folder on this computer.')
        backupDocsAct.triggered.connect(self.backupDocs)
        #
        restoreDocsAct = QAction('&Restore documents', self)
        restoreDocsAct.setStatusTip('Restore documents on the tablet from a backup on this computer.')
        restoreDocsAct.triggered.connect(self.restoreDocs)
        #
        sshMenu = menubar.addMenu('&SSH')
        sshMenu.addAction(backupDocsAct)
        sshMenu.addAction(restoreDocsAct)

        # About menu
        aboutAct = QAction(constants.AppName, self)
        aboutAct.setStatusTip("Show %s's About box." % constants.AppName)
        aboutAct.triggered.connect(self.about)
        #
        aboutQtAct = QAction('Qt', self)
        aboutQtAct.setStatusTip("Show Qt's About box.")
        aboutQtAct.triggered.connect(qApp.aboutQt)
        #
        explorerMenu = menubar.addMenu('&About')
        explorerMenu.addAction(aboutAct)
        explorerMenu.addAction(aboutQtAct)

        # Context menu of the directories QListWidget
        self.dirsListContextMenu = QMenu(self)
        downloadDirAct = self.dirsListContextMenu.addAction('&Download')
        downloadDirAct.triggered.connect(self.downloadDirClicked)


    def goToDir(self, dirId, dirName):

        try:
            collections, docs = tools.listDir(dirId, self.settings)
        except urllib.error.URLError as e:
            QMessageBox.critical(self, constants.AppName,
                                 'Could not go to directory "%s": URL error:\n%s' % (dirId, e.reason))
            return

        if dirId != self.curDir:
            # We are either moving up or down one level
            if len(self.curDirParents) == 0 or self.curDirParents[-1] != dirId:
                # Moving down
                self.curDirParents.append(self.curDir)
                self.curDirParentsNames.append(self.curDirName)
            else:
                # Moving up
                self.curDirParents.pop()
                self.curDirParentsNames.pop()
            self.curDir = dirId
            self.curDirName = dirName
        if self.curDirParents:
            path = '%s/%s' % ('/'.join(self.curDirParentsNames), self.curDirName)
        else:
            path = '/'
        self.curDirLabel.setText(path)

        # Update dirsList and filesList
        self.dirsList.clear()
        self.filesList.clear()

        if dirId != '':
            self.dirIds = [self.curDirParents[-1]]
            self.dirNames = [self.curDirParentsNames[-1]]
            self.dirsList.addItem('..')
        else:
            self.dirIds = []
            self.dirNames = []
        self.fileIds = []

        for id_, name in collections:
            self.dirIds.append(id_)
            self.dirNames.append(name)
            self.dirsList.addItem(name)
        for id_, name in docs:
            self.fileIds.append(id_)
            self.filesList.addItem(name)


    def downloadFile(self, basePath, fileDesc, mode):

        if not os.path.isdir(basePath):
            raise OSError('Not a directory: %s' % basePath)

        fid, destRelPath = fileDesc
        self.statusBar().showMessage('Downloading %s...' % os.path.split(destRelPath)[1])
        try:
            tools.downloadFile(fid, basePath, destRelPath, mode, self.settings)
        except urllib.error.URLError as e:
            QMessageBox.error(self, constants.AppName,
                                'URL error: %s. Aborted.' % e.reason)
            self.statusBar().showMessage('Download error.',
                                         constants.StatusBarMsgDisplayDuration)
        else:
            self.statusBar().showMessage('Download finished.',
                                         constants.StatusBarMsgDisplayDuration)


    def downloadDir(self, directory, rootName):

        def listFiles(ext, baseFolderId, baseFolderPath, filesList):
            url = self.settings.value('listFolderURL', type=str) % baseFolderId
            try:
                res = urllib.request.urlopen(url)
                data = res.read().decode(res.info().get_content_charset())
            except urllib.error.URLError as e:
                warningBox = QMessageBox(self)
                warningBox.setText('URL error: %s. Aborted.' % e.reason)
                warningBox.setIcon(QMessageBox.Warning)
                warningBox.exec()
                self.statusBar().showMessage('Download error.',
                                             constants.StatusBarMsgDisplayDuration)
                return
            data = json.loads(data)
            for elem in data:
                if elem['Type'] == 'DocumentType':
                    path = '%s.%s' % (os.path.join(baseFolderPath, elem['VissibleName']), ext) # yes, "Vissible"
                    filesList.append((elem['ID'], path))
                elif elem['Type'] == 'CollectionType':
                    listFiles(ext, elem['ID'],
                              os.path.join(baseFolderPath, elem['VissibleName']),
                              filesList)

        dialog = SaveOptsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            mode = dialog.getSaveMode()
            ext = mode
            # Ask for destination folder
            folder = QFileDialog.getExistingDirectory(self,
                                                      'Save directory',
                                                      self.settings.value('lastDir', type=str),
                                                      QFileDialog.ShowDirsOnly
                                                      | QFileDialog.DontResolveSymlinks)
            if folder:
                self.settings.setValue('lastDir', os.path.split(folder)[0])
                # Construct files list
                dlList = []
                listFiles(ext, directory, rootName, dlList)

                self.progressWindow = ProgressWindow(self)
                self.progressWindow.setWindowTitle("Downloading...")
                self.progressWindow.nSteps = len(dlList)
                self.progressWindow.open()

                self.settings.sync()
                self.currentWarning = ''
                self.downloadFilesWorker = DownloadFilesWorker(folder,
                                                               dlList,
                                                               mode)
                self.taskThread = QThread()
                self.downloadFilesWorker.moveToThread(self.taskThread)
                self.taskThread.started.connect(self.downloadFilesWorker.start)
                self.downloadFilesWorker.notifyProgress.connect(self.progressWindow.updateStep)
                self.downloadFilesWorker.finished.connect(self.onDownloadFilesFinished)
                self.downloadFilesWorker.warning.connect(self.warningRaised)
                self.taskThread.start()
            else:
                self.statusBar().showMessage('Cancelled.',
                                             constants.StatusBarMsgDisplayDuration)


    def backupDocs(self):

        # Destination folder
        defaultDir = (self.settings.value('lastSSHBackupDir', type=str)
                      or self.settings.value('lastDir', type=str))
        folder = QFileDialog.getExistingDirectory(self,
                                                  'Save directory',
                                                  defaultDir,
                                                  QFileDialog.ShowDirsOnly
                                                  | QFileDialog.DontResolveSymlinks)
        if not folder:
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        self.settings.setValue('lastSSHBackupDir', os.path.split(folder)[0])

        if not self.settings.unlockMasterKeyInteractive(self):
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        self.progressWindow = ProgressWindow(self)
        self.progressWindow.setWindowTitle("Downloading backup...")
        self.progressWindow.open()

        self.settings.sync()
        self.currentWarning = ''
        self.backupDocsWorker = BackupDocsWorker(folder, self.settings._masterKey)

        self.taskThread = QThread()
        self.backupDocsWorker.moveToThread(self.taskThread)
        self.taskThread.started.connect(self.backupDocsWorker.start)
        self.backupDocsWorker.notifyNSteps.connect(self.progressWindow.updateNSteps)
        self.backupDocsWorker.notifyProgress.connect(self.progressWindow.updateStep)
        self.backupDocsWorker.finished.connect(self.onBackupDocsFinished)
        self.backupDocsWorker.warning.connect(self.warningRaised)
        self.taskThread.start()


    def restoreDocs(self):

        # Confirm user has a backup folder
        tabletDir = self.settings.value('TabletDocumentsDir')
        msg = "To restore a backup, you need a previous copy on your computer of the tablet's \"%s\" folder. Ensure the backup you select was made with a tablet having the same software version as the device on which you want to restore the files.\n\n" % tabletDir
        msg += "Do you have such a backup and want to proceed to the restoration?"
        reply = QMessageBox.question(self, constants.AppName, msg)
        if reply == QMessageBox.No:
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        # Source folder
        defaultDir = (self.settings.value('lastSSHBackupDir', type=str)
                      or self.settings.value('lastDir', type=str))
        folder = QFileDialog.getExistingDirectory(self,
                                                  'Backup directory',
                                                  defaultDir,
                                                  QFileDialog.ShowDirsOnly
                                                  | QFileDialog.DontResolveSymlinks)
        if not folder:
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return
        self.settings.setValue('lastSSHBackupDir', os.path.split(folder)[0])

        # Basic check that the folder contents looks like a backup
        success, msg = tools.isValidBackupDir(folder)
        if not success:
            QMessageBox.warning(self, constants.AppName, '%s\nAborting.' % msg)
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        if not self.settings.unlockMasterKeyInteractive(self):
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        # Last chance to cancel!
        msg = "%s is now ready to restore the documents. Please check that the tablet is turned on, unlocked and that Wifi is enabled. Make sure no file is open and do not use the tablet during the upload.\n\n" % constants.AppName
        msg += "When the upload finishes, please reboot the tablet.\n\n"
        msg += "To restore documents, contents on the tablet will first be deleted. By continuing, you acknowledge that you take the sole responsibility for any possible data loss or damage caused to the tablet that may result from using %s.\n\n" % constants.AppName
        msg += "Do you want to continue?"
        reply = QMessageBox.question(self, constants.AppName, msg)
        if reply == QMessageBox.No:
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)
            return

        self.progressWindow = ProgressWindow(self)
        self.progressWindow.setWindowTitle("Restoring backup...")
        self.progressWindow.open()

        self.settings.sync()
        self.hasRaised = False
        self.restoreDocsWorker = RestoreDocsWorker(folder, self.settings._masterKey)

        self.taskThread = QThread()
        self.restoreDocsWorker.moveToThread(self.taskThread)
        self.taskThread.started.connect(self.restoreDocsWorker.start)
        self.restoreDocsWorker.notifyNSteps.connect(self.progressWindow.updateNSteps)
        self.restoreDocsWorker.notifyProgress.connect(self.progressWindow.updateStep)
        self.restoreDocsWorker.finished.connect(self.onRestoreDocsFinished)
        self.restoreDocsWorker.error.connect(self.errorRaised)
        self.taskThread.start()


    #########
    # Slots #
    #########

    def refreshLists(self):

        self.goToDir(self.curDir, self.curDirName)


    def dirsListItemDoubleClicked(self, item):

        idx = self.dirsList.currentRow()
        self.goToDir(self.dirIds[idx], self.dirNames[idx])


    def dirsListContextMenuRequested(self, pos):

        if self.dirsList.count() > 0:
            self.dirsListContextMenu.exec(self.dirsList.mapToGlobal(pos))


    def filesListItemDoubleClicked(self, item):

        fid = self.fileIds[self.filesList.currentRow()]
        dialog = SaveOptsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            mode = dialog.getSaveMode()
            ext = mode
            filename = '%s.%s' % (item.text(), ext)

            # Ask for file destination
            result = QFileDialog.getSaveFileName(self,
                                                 'Save %s' % ext.upper(),
                                                 os.path.join(self.settings.value('lastDir', type=str),
                                                              filename),
                                                 '%s file (*.%s)' % (ext.upper(), ext))
            if result[0]:
                dest_path = result[0] if result[0].endswith('.%s' % ext) else '%s.%s' % (result[0], ext)
                parts = os.path.split(dest_path)
                self.settings.setValue('lastDir', parts[0])
                self.downloadFile(parts[0], (fid, parts[1]), ext)
            else:
                self.statusBar().showMessage('Cancelled.',
                                             constants.StatusBarMsgDisplayDuration)
        else:
            self.statusBar().showMessage('Cancelled.',
                                         constants.StatusBarMsgDisplayDuration)


    def downloadDirClicked(self):

        idx = self.dirsList.currentRow()
        self.downloadDir(self.dirIds[idx], self.dirNames[idx])


    def downloadAll(self):

        self.downloadDir('', '')


    def warningRaised(self, msg):

        self.currentWarning = msg


    def errorRaised(self, msg):

        self.hasRaised = True
        QMessageBox.critical(self, constants.AppName,
                             'Error:\n%s\nAborted.' % msg)


    def onDownloadFilesFinished(self):

        self.progressWindow.hide()

        self.taskThread.started.disconnect(self.downloadFilesWorker.start)
        self.downloadFilesWorker.warning.disconnect(self.warningRaised)
        self.downloadFilesWorker.finished.disconnect(self.onDownloadFilesFinished)

        # Not sure that the following is entirely safe.  For example, what if a
        # new thread is created before the old objects are actually deleted?
        self.taskThread.quit()
        self.downloadFilesWorker.deleteLater()
        self.taskThread.deleteLater()
        self.taskThread.wait()

        if self.currentWarning:
            QMessageBox.warning(self, constants.AppName,
                                'Errors were encountered:\n%s' % self.currentWarning)
        self.statusBar().showMessage('Finished downloading files.',
                                     constants.StatusBarMsgDisplayDuration)


    def editSettings(self):

        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            self.updateFromSettings()
            self.statusBar().showMessage('Settings updated.',
                                         constants.StatusBarMsgDisplayDuration)


    def onBackupDocsFinished(self):

        self.progressWindow.hide()

        self.taskThread.started.disconnect(self.backupDocsWorker.start)
        self.backupDocsWorker.warning.disconnect(self.warningRaised)
        self.backupDocsWorker.finished.disconnect(self.onBackupDocsFinished)
        self.backupDocsWorker.notifyNSteps.disconnect(self.progressWindow.updateNSteps)
        self.backupDocsWorker.notifyProgress.disconnect(self.progressWindow.updateStep)

        self.taskThread.quit()
        self.backupDocsWorker.deleteLater()
        self.taskThread.deleteLater()
        self.taskThread.wait()

        if self.currentWarning:
            QMessageBox.warning(self, constants.AppName,
                                'Errors were encountered:\n%s' % self.currentWarning)
        else:
            QMessageBox.information(self, constants.AppName,
                                    'Backup was created successfully!')
        self.statusBar().showMessage('Finished downloading backup.',
                                     constants.StatusBarMsgDisplayDuration)


    def onRestoreDocsFinished(self):

        self.progressWindow.hide()

        self.taskThread.started.disconnect(self.restoreDocsWorker.start)
        self.restoreDocsWorker.error.disconnect(self.errorRaised)
        self.restoreDocsWorker.finished.disconnect(self.onRestoreDocsFinished)
        self.restoreDocsWorker.notifyNSteps.disconnect(self.progressWindow.updateNSteps)
        self.restoreDocsWorker.notifyProgress.disconnect(self.progressWindow.updateStep)

        self.taskThread.quit()
        self.restoreDocsWorker.deleteLater()
        self.taskThread.deleteLater()
        self.taskThread.wait()

        if not self.hasRaised:
            QMessageBox.information(self, constants.AppName,
                                    'Backup was restored successfully! Please reboot the tablet now.')

            self.statusBar().showMessage('Finished restoring backup.',
                                         constants.StatusBarMsgDisplayDuration)


    def about(self):

        msg = """<b>pyrmexplorer: Explorer for Remarkable tablets</b><br/><br/>
Version %s<br/><br/>
Copyright (C) 2019 Nicolas Bruot (<a href="https://www.bruot.org/hp/">https://www.bruot.org/hp/</a>)<br/><br/>

Some parts of this software are copyright other contributors. Refer to the individual source files for details.<br/><br/>

pyrmexplorer is released under the terms of the GNU General Public License (GPL) v3.<br/><br/>

The source code is available at <a href=\"https://github.com/bruot/pyrmexplorer/\">https://github.com/bruot/pyrmexplorer/</a>.<br/><br/>
"""
        msg = msg % __version__
        msgBox = QMessageBox(self)
        msgBox.setText(msg)
        msgBox.exec()
