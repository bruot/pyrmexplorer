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


"""rmExplorer main window"""


import os
import socket
import json
import urllib.request
import urllib.error

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (qApp, QWidget, QMainWindow, QMenu, QAction,
                             QLabel, QListWidget, QGridLayout, QDialog,
                             QFileDialog, QMessageBox)

from _version import __version__
from saveoptsdialog import SaveOptsDialog
from settingsdialog import SettingsDialog
from downloadfilesworker import DownloadFilesWorker
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

        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel('Folders:'), 0, 0)
        mainLayout.addWidget(QLabel('Files:'), 0, 1)
        mainLayout.addWidget(self.dirsList, 1, 0)
        mainLayout.addWidget(self.filesList, 1, 1)

        centralWidget = QWidget(self)
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.curDir = ''
        self.curDirParents = []
        self.dirIds = []
        self.fileIds = []
        self.goToDir('')

        self.currentWarning = ''

        self.progressWindow = None
        self.downloadFilesWorker = None
        self.taskThread = None

        self.setWindowTitle('rMExplorer')


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
        settingsAct.setStatusTip('rMExplorer settings')
        settingsAct.triggered.connect(self.editSettings)
        #
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit rMExplorer.')
        exitAct.triggered.connect(qApp.quit)
        #
        explorerMenu = menubar.addMenu('&Explorer')
        explorerMenu.addAction(dlAllAct)
        explorerMenu.addAction(refreshAct)
        explorerMenu.addAction(settingsAct)
        explorerMenu.addAction(exitAct)

        # About menu
        aboutAct = QAction('rMExplorer', self)
        aboutAct.setStatusTip("Show rMExplorer's About box.")
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


    def goToDir(self, dirId):

        url = self.settings.value('listFolderURL', type=str) % dirId
        try:
            data = urllib.request.urlopen(url).read()
        except urllib.error.URLError as e:
            errorBox = QMessageBox(self)
            errorBox.setText('Could not go to directory "%s": URL error:\n%s' % (dirId, e.reason))
            errorBox.setIcon(QMessageBox.Critical)
            errorBox.exec()
            return

        data = json.loads(data)

        if dirId != self.curDir:
            # We are either moving up or down one level
            if len(self.curDirParents) == 0 or self.curDirParents[-1] != dirId:
                # Moving down
                self.curDirParents += [self.curDir]
            else:
                # Moving up
                self.curDirParents.pop()
            self.curDir = dirId

        # Update dirsList and filesList
        self.dirsList.clear()
        self.filesList.clear()

        if dirId != '':
            self.dirIds = [self.curDirParents[-1]]
            self.dirsList.addItem('..')
        else:
            self.dirIds = []
        self.fileIds = []

        for elem in data:
            if elem['Type'] == 'CollectionType':
                self.dirIds.append(elem['ID'])
                self.dirsList.addItem(elem['VissibleName']) # yes, "Vissible"
            elif elem['Type'] == 'DocumentType':
                self.fileIds.append(elem['ID'])
                self.filesList.addItem(elem['VissibleName'])


    def downloadFile(self, basePath, fileDesc, mode):

        if not os.path.isdir(basePath):
            raise OSError('Not a directory: %s' % basePath)

        fid, destRelPath = fileDesc
        self.statusBar().showMessage('Downloading %s...' % os.path.split(destRelPath)[1])
        try:
            tools.downloadFile(fid, basePath, destRelPath, mode, self.settings)
        except urllib.error.URLError as e:
            warningBox = QMessageBox(self)
            warningBox.setText('URL error: %s. Aborted.' % e.reason)
            warningBox.setIcon(QMessageBox.Warning)
            warningBox.exec()
            self.statusBar().showMessage('Download error.', 5000)
        else:
            self.statusBar().showMessage('Download finished.', 5000)


    def downloadDir(self, directory, rootName):

        def listFiles(ext, baseFolderId, baseFolderPath, filesList):
            url = self.settings.value('listFolderURL', type=str) % baseFolderId
            try:
                data = urllib.request.urlopen(url).read()
            except urllib.error.URLError as e:
                warningBox = QMessageBox(self)
                warningBox.setText('URL error: %s. Aborted.' % e.reason)
                warningBox.setIcon(QMessageBox.Warning)
                warningBox.exec()
                self.statusBar().showMessage('Download error.', 5000)
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
                self.statusBar().showMessage('Cancelled.', 5000)


    #########
    # Slots #
    #########

    def refreshLists(self):

        self.goToDir(self.curDir)


    def dirsListItemDoubleClicked(self, item):

        dirId = self.dirIds[self.dirsList.currentRow()]
        self.goToDir(dirId)


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
                self.statusBar().showMessage('Cancelled.', 5000)
        else:
            self.statusBar().showMessage('Cancelled.', 5000)


    def downloadDirClicked(self):

        dirId = self.dirIds[self.dirsList.currentRow()]
        dirName = self.dirsList.selectedItems()[0].text()
        self.downloadDir(dirId, dirName)


    def downloadAll(self):

        self.downloadDir('', '')


    def warningRaised(self, msg):

        self.currentWarning = msg


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
            warningBox = QMessageBox(self)
            warningBox.setText('Errors were encountered:\n%s' % self.currentWarning)
            warningBox.setIcon(QMessageBox.Warning)
            warningBox.exec()
        self.statusBar().showMessage('Finished downloading files.', 5000)


    def editSettings(self):

        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            self.updateFromSettings()
            self.statusBar().showMessage('Settings updated.', 5000)


    def about(self):

        msg = """pyrmexplorer: Explorer for Remarkable tablets<br/><br/>
Version %s<br/><br/>
Copyright (C) 2019 Nicolas Bruot (<a href="https://www.bruot.org/hp/">https://www.bruot.org/hp/</a>)<br/><br/>
pyrmexplorer is released under the terms of the GNU General Public License (GPL) v3.<br/>
The source code is available at <a href=\"https://github.com/bruot/pyrmexplorer/\">https://github.com/bruot/pyrmexplorer/</a>.<br/><br/>
"""
        msg = msg % __version__
        msgBox = QMessageBox(self)
        msgBox.setText(msg)
        msgBox.exec()
