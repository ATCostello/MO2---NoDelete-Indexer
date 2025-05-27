# ----------------------------------------------------------------
# Author: Alfthebigheaded
# ----------------------------------------------------------------
import ast
from datetime import date
import datetime
from functools import partial
import json
import sys
import traceback
from typing import List
from json import JSONDecoder
from pathlib import Path

try:
    from PyQt6 import QtCore
    from PyQt6.QtCore import Qt
    from PyQt6 import QtGui
    from PyQt6 import QtWidgets
except:
    from PyQt5 import QtCore
    from PyQt5.QtCore import Qt
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets
import mobase
import os
import re

class Ui_RestoreBackup(object):
    def setupUi(self, RestoreBackupUI, _organizer, _parent):        
        self._translate = QtCore.QCoreApplication.translate
        self._organizer = _organizer
        self._parent = _parent
        
        self.red = QtGui.QBrush(QtGui.QColor(255, 0, 0, 50))
        self.green = QtGui.QBrush(QtGui.QColor(0, 255, 0, 50))
        self.grey = QtGui.QBrush(QtGui.QColor(150, 150, 150, 50))
        self.blue = QtGui.QBrush(QtGui.QColor(0, 0, 255, 50))
        self.winningIcon = "+"
        self.losingIcon = "-"
        self.notFoundIcon = "~"
        
        # Main Window        
        RestoreBackupUI.setObjectName("RestoreBackupUI")
        RestoreBackupUI.resize(942, 807)
        RestoreBackupUI.setSizeGripEnabled(False)
        RestoreBackupUI.setWindowTitle(
            self._translate("RestoreBackupUI", "Restore Backup")
        )
        
        self.verticalLayout = QtWidgets.QVBoxLayout(RestoreBackupUI)
        self.verticalLayout.setObjectName("verticalLayout")
            
        # List Widget (Available Backups)
        self.setup_available_backups_list_widget(RestoreBackupUI)
        
        # Tree Widget (Backup contents)
        self.setup_backup_content_tree_widget(RestoreBackupUI)

        # Buttons
        self.setup_buttons_widget(RestoreBackupUI)

        QtCore.QMetaObject.connectSlotsByName(RestoreBackupUI)

    def setup_available_backups_list_widget(self, RestoreBackupUI):
        # List Widget Label
        self.label = QtWidgets.QLabel(RestoreBackupUI)
        self.label.setGeometry(QtCore.QRect(9, 9, 500, 16))
        self.label.setScaledContents(False)
        self.label.setObjectName("label")
        self.label.setText(
            self._translate("RestoreBackupUI", "1. Pick a backup to view")
        )
        self.verticalLayout.addWidget(self.label)

        # List Widget (Available Backups)
        self.listWidget = QtWidgets.QListWidget(RestoreBackupUI)
        self.listWidget.setGeometry(QtCore.QRect(9, 31, 891, 251))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setMaximumSize(QtCore.QSize(16777215, 200))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.listWidget.setWordWrap(True)
        self.verticalLayout.addWidget(self.listWidget)

        # Set paths
        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
        backup_path = str(profilefolder_Path + "/[NoDelete] Indexer Backups/")

        # Add items
        if os.path.isdir(backup_path):
            files = [f for f in os.listdir(backup_path) if re.match("modlist_BACKUP_", f)]

            for f in reversed(files):
                item = QtWidgets.QListWidgetItem()
                self.listWidget.addItem(item)

                newdatestr = (
                    f.replace(backup_path, "")
                    .replace("modlist_BACKUP_", "")
                    .replace(".txt", "")
                )

                newdate = datetime.datetime.strptime(
                    newdatestr, "%Y-%m-%dT%H_%M_%SZ"
                ).strftime("%d %B %Y, %H:%M:%S")

                item.setData(69, newdatestr)
                item.setText(self._translate("RestoreBackupUI", newdate))

            self.listWidget.itemClicked.connect(self.itemClicked_event)

    def itemClicked_event(self, item):
        self.fill_tree_widget(item)

    def toggleClicked_event(self):
        if self.selected_item is not None:
            self.fill_tree_widget(self.selected_item)

    # Override drag drop events for moving items
    class TreeWidget(QtWidgets.QTreeWidget):

        itemDropped=QtCore.pyqtSignal()

        def __init__(self):
            QtWidgets.QTreeWidget.__init__(self)
            
        def dropEvent(self, event):
            super().dropEvent(event)
        
    def setup_backup_content_tree_widget(self, RestoreBackupUI):
        self.splitter = QtWidgets.QSplitter(RestoreBackupUI)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        
        # Tree Widget Label
        self.label_2 = QtWidgets.QLabel(self.splitter)
        self.label_2.setGeometry(QtCore.QRect(10, 290, 500, 16))
        self.label_2.setObjectName("label_2")
        self.label_2.setText(
            self._translate("RestoreBackupUI", "2. Check the backup contents")
        )

        # Legend Label
        self.legend_green_icon = QtWidgets.QLabel(self.splitter)
        self.legend_green_icon.setGeometry(QtCore.QRect(610, 290, 21, 20))
        self.legend_green_icon.setAutoFillBackground(True)
        self.legend_green_icon.setText("")
        self.legend_green_icon.setObjectName("legend_green_icon")
        self.legend_green = QtWidgets.QLabel(self.splitter)
        self.legend_green.setGeometry(QtCore.QRect(640, 290, 61, 16))
        self.legend_green.setObjectName("legend_green")
        
        self.legend_red_icon = QtWidgets.QLabel(self.splitter)
        self.legend_red_icon.setGeometry(QtCore.QRect(510, 290, 21, 20))
        self.legend_red_icon.setAutoFillBackground(True)
        self.legend_red_icon.setText("")
        self.legend_red_icon.setObjectName("legend_red_icon")
        self.legend_red = QtWidgets.QLabel(self.splitter)
        self.legend_red.setGeometry(QtCore.QRect(540, 290, 61, 16))
        self.legend_red.setObjectName("legend_red")
        
        self.legend_grey_icon = QtWidgets.QLabel(self.splitter)
        self.legend_grey_icon.setGeometry(QtCore.QRect(710, 290, 21, 20))
        self.legend_grey_icon.setAutoFillBackground(True)
        self.legend_grey_icon.setText("")
        self.legend_grey_icon.setObjectName("legend_grey_icon")
        self.legend_grey = QtWidgets.QLabel(self.splitter)
        self.legend_grey.setGeometry(QtCore.QRect(740, 290, 81, 16))
        self.legend_grey.setObjectName("legend_grey")
        
        self.legend_blue_icon = QtWidgets.QLabel(self.splitter)
        self.legend_blue_icon.setGeometry(QtCore.QRect(410, 290, 21, 20))
        self.legend_blue_icon.setAutoFillBackground(True)
        self.legend_blue_icon.setText("")
        self.legend_blue_icon.setObjectName("legend_blue_icon")
        self.legend_blue = QtWidgets.QLabel(self.splitter)
        self.legend_blue.setGeometry(QtCore.QRect(440, 290, 61, 16))
        self.legend_blue.setObjectName("legend_blue")

        self.legend_grey_icon.setStyleSheet("background-color: rgba(150, 150, 150, 50)")
        self.legend_blue_icon.setStyleSheet("background-color: rgba(0, 0, 255, 50)")
        self.legend_red_icon.setStyleSheet("background-color: rgba(255, 0, 0, 50)")
        self.legend_green_icon.setStyleSheet("background-color: rgba(0, 255, 0, 50)")

        self.legend_red.setText(self._translate("RestoreBackupUI", "Losing"))
        self.legend_blue.setText(self._translate("RestoreBackupUI", "Not Found"))
        self.legend_green.setText(self._translate("RestoreBackupUI", "Winning"))
        self.legend_grey.setText(self._translate("RestoreBackupUI", "No Change"))

        self.verticalLayout.addWidget(self.splitter)
        
        # Tree Widget (Available Backups)
        self.treeWidget = QtWidgets.QTreeWidget(RestoreBackupUI)
        self.treeWidget.setGeometry(QtCore.QRect(10, 320, 891, 311))
        self.treeWidget.setObjectName("treeWidget")
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.treeWidget.setWordWrap(True)
        self.treeWidget.setDragEnabled(False)
        self.treeWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.NoDragDrop)
        self.treeWidget.setDefaultDropAction(Qt.DropAction.IgnoreAction)

        # Tree Widget (Available Backups)
        self.treeWidget.headerItem().setText(
            0, self._translate("RestoreBackupUI", "File")
        )
        self.treeWidget.headerItem().setText(
            1, self._translate("RestoreBackupUI", "Current")
        )
        self.treeWidget.headerItem().setText(
            2, self._translate("RestoreBackupUI", "Backup")
        )
        self.treeWidget.setColumnWidth(0, 150)
        self.treeWidget.setColumnWidth(1, 350)
        self.treeWidget.setColumnWidth(2, 350)

        self.verticalLayout.addWidget(self.treeWidget)
    
    def setup_buttons_widget(self, RestoreBackupUI):
        
        self.splitter_2 = QtWidgets.QSplitter(RestoreBackupUI)
        self.splitter_2.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        
        # No Change Toggle
        self.HideNoChangeCheckbox = QtWidgets.QCheckBox(self.splitter_2)
        self.HideNoChangeCheckbox.setGeometry(QtCore.QRect(10, 640, 291, 20))
        self.HideNoChangeCheckbox.setObjectName("HideNoChangeCheckbox")
        self.HideNoChangeCheckbox.setText(
            self._translate("RestoreBackupUI", 'Hide "No Change" Items')
        )
        self.HideNoChangeCheckbox.stateChanged.connect(self.toggleClicked_event)
        
        # Restore Button
        self.restoreButton = QtWidgets.QPushButton(self.splitter_2)
        self.restoreButton.setGeometry(QtCore.QRect(730, 660, 75, 24))
        self.restoreButton.setObjectName("restoreButton")
        self.restoreButton.setText(self._translate("RestoreBackupUI", "Restore"))
        self.restoreButton.clicked.connect(self.on_restore_clicked)

        # Cancel Button
        self.cancelButton = QtWidgets.QPushButton(self.splitter_2)
        self.cancelButton.setGeometry(QtCore.QRect(820, 660, 75, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setText(self._translate("RestoreBackupUI", "Cancel"))
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
        
        self.verticalLayout.addWidget(self.splitter_2)
        
    def fill_tree_widget(self, selected_item):
        self.selected_item = selected_item
        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
        backup_path = str(profilefolder_Path + "/[NoDelete] Indexer Backups/")

        self.treeWidget.clear()

        files = [
            f
            for f in os.listdir(backup_path)
            if selected_item.data(69) in f and "PluginsObjects" not in f
        ]

        # Create top level items (Files)
        for f in files:
            if "pluginsObjects" not in f:

                # Create title item
                QtWidgets.QTreeWidgetItem(self.treeWidget)

                filename = f
                readablename = f

                topLevelCount = self.treeWidget.topLevelItemCount() - 1
                parentItem = self.treeWidget.topLevelItem(topLevelCount)

                # Create nice readable text for file type
                if "modfolders_BACKUP" in f:
                    readablename = "Mod Names"
                    parentItem.setText(
                        0, self._translate("RestoreBackupUI", readablename)
                    )
                    self.setupModFoldersTree(filename, parentItem)
                    parentItem.setExpanded(True)
                elif "modlist_BACKUP" in f:
                    readablename = "Mod Load Order"
                    parentItem.setText(
                        0, self._translate("RestoreBackupUI", readablename)
                    )
                    self.setupModLoadOrderTree(filename, parentItem)
                    parentItem.setExpanded(True)
                elif "plugins_BACKUP" in f:
                    readablename = "Plugin Load Order"
                    parentItem.setText(
                        0, self._translate("RestoreBackupUI", readablename)
                    )
                    self.setupPluginLoadOrderTree(filename, parentItem)
                    parentItem.setExpanded(True)

    def stripPreviousIndex(self, oldFolderName):
        newFolderName = re.sub("\[[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\[[0-9]*\.[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\s+", " ", newFolderName)
        return newFolderName

    def checkNoDeleteModName(self, modname, backupmodname, parentTreeItem):
        modname_stripped = self.stripPreviousIndex(modname)
        modsfolder_Path = self._organizer.modsPath()
        currentmodsfolder_List = os.listdir(modsfolder_Path)
        currentmodsfolder_List_stripped = []
        currModFolder = ""

        if parentTreeItem is not None:
            childCount = parentTreeItem.childCount() - 1

        for folder in currentmodsfolder_List:
            if "[NoDelete]" in folder or "[No Delete]" in folder:
                oldFolderName = folder
                folder = self.stripPreviousIndex(oldFolderName)
            currentmodsfolder_List_stripped.append(folder.rstrip())

        if modname in currentmodsfolder_List:
            i = currentmodsfolder_List.index(modname)
            if currentmodsfolder_List[i] == backupmodname:
                currModFolder = currentmodsfolder_List[i]
                if parentTreeItem is not None:
                    parentTreeItem.child(childCount).setBackground(1, self.grey)
                    parentTreeItem.child(childCount).setBackground(2, self.grey)
            else:
                currModFolder = currentmodsfolder_List[i]
                if parentTreeItem is not None:
                    parentTreeItem.child(childCount).setBackground(1, self.red)
                    parentTreeItem.child(childCount).setBackground(2, self.green)
                    parentTreeItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)
        elif modname_stripped in currentmodsfolder_List_stripped:
            i = currentmodsfolder_List_stripped.index(modname_stripped)
            if currentmodsfolder_List_stripped[i] == backupmodname:
                currModFolder = currentmodsfolder_List[i]
                if parentTreeItem is not None:
                    parentTreeItem.child(childCount).setBackground(1, self.red)
                    parentTreeItem.child(childCount).setBackground(2, self.green)
                    parentTreeItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)
            else:
                currModFolder = currentmodsfolder_List[i]
                if parentTreeItem is not None:
                    parentTreeItem.child(childCount).setBackground(1, self.red)
                    parentTreeItem.child(childCount).setBackground(2, self.green)
                    parentTreeItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)
        else:
            currModFolder = modname
            self.missing_items = True
            if parentTreeItem is not None:
                parentTreeItem.child(childCount).setBackground(1, self.blue)
                parentTreeItem.child(childCount).setBackground(2, self.grey)
                parentTreeItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)


        return currModFolder        
        
    def setupModFoldersTree(self, filename, parentItem):
        oldToNewDictionary = {}

        profilefolder_Path = self._organizer.profilePath()
        backup_path = str(
            profilefolder_Path + "/[NoDelete] Indexer Backups/" + filename
        )
        modsfolder_Path = self._organizer.modsPath()

        currentmodsfolder_List = os.listdir(modsfolder_Path)
        currentmodsfolder_List_stripped = []
        for folder in currentmodsfolder_List:
            if "[NoDelete]" in folder or "[No Delete]" in folder:
                oldFolderName = folder
                #folder = self.stripPreviousIndex(oldFolderName)
            currentmodsfolder_List_stripped.append(folder.rstrip())

        # Read file
        with open(backup_path, "r", encoding="utf-8") as backupfoldersfile:
            oldToNewDictionary = ast.literal_eval(backupfoldersfile.read())

        self.modFoldersOldToNewDictionary = oldToNewDictionary

        self.missing_items = False
        for folder in oldToNewDictionary:

            # Old folder in oldToNewDictionary which will be replaced
            folderToReplace = (
                oldToNewDictionary[folder].replace(modsfolder_Path + "/", "").rstrip()
            )
            # Strip indexes from old folder if needed
            folderToReplace_stripped = self.stripPreviousIndex(folderToReplace)
            # New folder name from backup which will replace
            backupFolder = folder.replace(modsfolder_Path + "/", "").rstrip()
            # Equivalent current folder in current mods folder (if any)
            currModFolder = ""
            currModFolder = self.checkNoDeleteModName(
                folderToReplace, backupFolder, None
            )

            if not (
                self.HideNoChangeCheckbox.isChecked() and currModFolder == backupFolder
            ):
                # Create new entry
                QtWidgets.QTreeWidgetItem(parentItem)
                childCount = parentItem.childCount() - 1

                currModFolder = self.checkNoDeleteModName(
                    folderToReplace, backupFolder, parentItem
                )
                parentItem.child(childCount).setText(
                    0, self._translate("RestoreBackupUI", str(childCount))
                )

                parentItem.child(childCount).setText(
                    1,
                    self._translate("RestoreBackupUI", currModFolder),
                )

                parentItem.child(childCount).setText(
                    2,
                    self._translate("RestoreBackupUI", backupFolder),
                )

    def setupModLoadOrderTree(self, filename, parentItem):
        profilefolder_Path = self._organizer.profilePath()
        backup_path = str(
            profilefolder_Path + "/[NoDelete] Indexer Backups/" + filename
        )
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")

        backupModOrderContent = []
        currentModOrderContent = []
        if os.path.exists(backup_path):
            # open backup modlist txt
            with open(backup_path, "r", encoding="utf-8") as backupfile:
                for line in backupfile:
                    if (
                        line.rstrip()
                        != "# This file was automatically generated by Mod Organizer."
                    ):
                        backupModOrderContent.append(line.rstrip())
            # open current modlist txt
            with open(modlisttxt_Path, "r", encoding="utf-8") as modlisttxt:
                for line in modlisttxt:
                    if (
                        line.rstrip()
                        != "# This file was automatically generated by Mod Organizer."
                    ):
                        currentModOrderContent.append(line.rstrip())

        backupModOrderContent.reverse()
        currentModOrderContent.reverse()

        largestList = []
        if len(backupModOrderContent) > len(currentModOrderContent):
            largestList = backupModOrderContent
        else:
            largestList = currentModOrderContent

        for i, x in enumerate(largestList):
            currBackupItem = ""
            currItem = ""
            try:
                currBackupItem = backupModOrderContent[i].rstrip()
            except IndexError:
                currBackupItem = ""
            try:
                currItem = currentModOrderContent[i].rstrip()
            except IndexError:
                currItem = ""

            if self.HideNoChangeCheckbox.isChecked() and currBackupItem == currItem:
                print("")
            else:
                # Create new entry
                QtWidgets.QTreeWidgetItem(parentItem)
                childCount = parentItem.childCount() - 1

                parentItem.child(childCount).setText(
                    0, self._translate("RestoreBackupUI", str(childCount))
                )

                parentItem.child(childCount).setText(
                    1,
                    self._translate(
                        "RestoreBackupUI",
                        currItem,
                    ),
                )

                parentItem.child(childCount).setText(
                    2,
                    self._translate("RestoreBackupUI", currBackupItem),
                )

                if currBackupItem != currItem:
                    parentItem.child(childCount).setBackground(1, self.red)
                    parentItem.child(childCount).setBackground(2, self.green)
                    parentItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)
                else:
                    parentItem.child(childCount).setBackground(1, self.grey)
                    parentItem.child(childCount).setBackground(2, self.grey)

    def setupPluginLoadOrderTree(self, filename, parentItem):
        profilefolder_Path = self._organizer.profilePath()
        backup_path = str(
            profilefolder_Path + "/[NoDelete] Indexer Backups/" + filename
        )
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")

        backupModOrderContent = []
        currentModOrderContent = []
        if os.path.exists(backup_path):
            # open backup modlist txt
            with open(backup_path, "r", encoding="utf-8") as backupfile:
                for line in backupfile:
                    if (
                        line.rstrip()
                        != "# This file was automatically generated by Mod Organizer."
                    ):
                        backupModOrderContent.append(line.rstrip())
            # open current modlist txt
            with open(pluginstxt_Path, "r", encoding="utf-8") as modlisttxt:
                for line in modlisttxt:
                    if (
                        line.rstrip()
                        != "# This file was automatically generated by Mod Organizer."
                    ):
                        currentModOrderContent.append(line.rstrip())

        largestList = []
        if len(backupModOrderContent) > len(currentModOrderContent):
            largestList = backupModOrderContent
        else:
            largestList = currentModOrderContent

        for i, x in enumerate(largestList):

            currBackupItem = ""
            currItem = ""
            try:
                currBackupItem = backupModOrderContent[i].rstrip()
            except IndexError:
                currBackupItem = ""
            try:
                currItem = currentModOrderContent[i].rstrip()
            except IndexError:
                currItem = ""

            if self.HideNoChangeCheckbox.isChecked() and currBackupItem == currItem:
                print("")
            else:
                # Create new entry
                QtWidgets.QTreeWidgetItem(parentItem)
                childCount = parentItem.childCount() - 1

                parentItem.child(childCount).setText(
                    0, self._translate("RestoreBackupUI", str(childCount))
                )

                parentItem.child(childCount).setText(
                    1,
                    self._translate(
                        "RestoreBackupUI",
                        currItem,
                    ),
                )

                parentItem.child(childCount).setText(
                    2,
                    self._translate("RestoreBackupUI", currBackupItem),
                )

                if currBackupItem != currItem:
                    parentItem.child(childCount).setBackground(1, self.red)
                    parentItem.child(childCount).setBackground(2, self.green)
                    parentItem.child(childCount).setCheckState(1, Qt.CheckState.Checked)
                else:
                    parentItem.child(childCount).setBackground(1, self.grey)
                    parentItem.child(childCount).setBackground(2, self.grey)

    # ----------------------------------------------------------------
    # Backup the plugins.txt incase failure.
    # ----------------------------------------------------------------
    def backupPluginstxt(self, pluginstxt_Path, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(pluginstxt_Path, "r", encoding="utf-8") as pluginstxt:
            with open(backup_path, "w", encoding="utf-8") as backupfile:
                backupfile.write(pluginstxt.read())

        print("Made backup of plugins.txt to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Backup the modlist.txt incase failure.
    # ----------------------------------------------------------------
    def backupModlisttxt(self, modlisttxt_Path, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/modlist_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(modlisttxt_Path, "r", encoding="utf-8") as modlisttxt:
            with open(backup_path, "w", encoding="utf-8") as backupfile:
                backupfile.write(modlisttxt.read())

        print("Made backup of modlist.txt to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Backup the plugins objects so that they may be sorted AFTER wabbajack usage.
    # ----------------------------------------------------------------
    def backupPluginsObjects(self, pluginsObjects, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/pluginsObjects_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(backup_path, "w", encoding="utf-8") as backupfile:
            for plugin in pluginsObjects.items():
                json.dump(plugin, backupfile)
                backupfile.write("\n")

        print("Made backup of plugin objects to '" + backup_path + "'")

    def backupModFolders(self, profilefolder_Path, oldToNewDictionary, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/modfolders_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        # For each separator, rename folders appropriately.
        with open(backup_path, "w", encoding="utf-8") as backupfile:
            backupfile.write(str(oldToNewDictionary))

        print("Made backup of mod folders to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Restore the modlist.txt, plugins.txt and folder names incase failure.
    # ----------------------------------------------------------------
    def restoreBackup(self, date_format):
        date = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")


        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")

        self.backupModFolders(
            profilefolder_Path, self.modFoldersOldToNewDictionary, date
        )
        self.backupModlisttxt(modlisttxt_Path, profilefolder_Path, date)
        self.backupPluginstxt(pluginstxt_Path, profilefolder_Path, date)

        modsWithLoadorder = {}
        with open(modlisttxt_Path, "r", encoding="UTF-8") as infile:
            for i, modname in reversed(list(enumerate(infile))):
                if "[NoDelete]" in modname or "[No Delete]" in modname:
                    modname = modname[1:]
                    modsWithLoadorder[len(modsWithLoadorder)] = modname

        modlistname_list = list(modsWithLoadorder.values())

        pluginObjects = {}
        # make list of all plugins for easier traversal
        pluginstxt_list = {}
        with open(pluginstxt_Path, "r", encoding="UTF-8") as pluginsfile:
            for i, pluginname in list(enumerate(pluginsfile)):
                pluginname = pluginname[0:]
                pluginstxt_list[len(pluginstxt_list)] = pluginname.rstrip()

        # Go through mod folders and make plugin objects
        for folder in modlistname_list:
            for file in os.listdir(modsfolder_Path.rstrip() + "/" + folder.rstrip()):
                for i, pluginName in pluginstxt_list.items():
                    if pluginName.rstrip().replace("*", "") in file.rstrip():
                        print(str(i) + " : " + pluginName.rstrip())
                        modName = folder.rstrip()
                        pluginName = pluginName.rstrip()
                        previousPlugins = []
                        # grab previous 10 plugins
                        for j in range(10):
                            j = j + 1
                            x = 0
                            if i - j > 0:
                                x = i - j
                            if len(previousPlugins) == 0:
                                previousPlugins.append(pluginstxt_list[x])
                            elif previousPlugins[-1] != pluginstxt_list[x]:
                                previousPlugins.append(pluginstxt_list[x])
                        nextPlugins = []
                        # grab next 10 plugins
                        for j in range(10):
                            j = j + 1
                            x = len(pluginstxt_list) - 1
                            if i + j < len(pluginstxt_list):
                                x = i + j
                            if len(nextPlugins) == 0:
                                nextPlugins.append(pluginstxt_list[x])
                            elif nextPlugins[-1] != pluginstxt_list[x]:
                                nextPlugins.append(pluginstxt_list[x])
                        pluginObjects[pluginName.replace("*", "").rstrip()] = {
                            "modName": modName,
                            "pluginName": pluginName,
                            "previousPlugins": previousPlugins,
                            "nextPlugins": nextPlugins,
                        }

        self.backupPluginsObjects(pluginObjects, profilefolder_Path, date)

        try:
            backupmodlisttxt_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/modlist_BACKUP_"
                + date_format
                + ".txt"
            )

            backuppluginstxt_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
                + date_format
                + ".txt"
            )

            backupfolders_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/modfolders_BACKUP_"
                + date_format
                + ".txt"
            )

            if os.path.exists(backupmodlisttxt_path):
                # restore modlist.txt
                with open(backupmodlisttxt_path, "r", encoding="utf-8") as backupfile:
                    with open(modlisttxt_Path, "w", encoding="utf-8") as modlisttxt:
                        modlisttxt.write(backupfile.read())

            pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
            if os.path.exists(backuppluginstxt_path):
                # restore plugins.txt
                with open(backuppluginstxt_path, "r", encoding="utf-8") as backupfile:
                    with open(pluginstxt_Path, "w", encoding="utf-8") as pluginstxt:
                        pluginstxt.write(backupfile.read())

            if os.path.exists(backupfolders_path):
                # restore mod folder names
                oldToNewDictionary = {}
                with open(
                    backupfolders_path, "r", encoding="utf-8"
                ) as backupfoldersfile:
                    oldToNewDictionary = ast.literal_eval(backupfoldersfile.read())

                for brokenFolder in oldToNewDictionary:
                    my_file = Path(oldToNewDictionary[brokenFolder].rstrip())
                    if my_file.exists():
                        os.rename(
                            "" + oldToNewDictionary[brokenFolder].rstrip(),
                            "" + brokenFolder.rstrip(),
                        )

            QtWidgets.QMessageBox.information(
                self,
                self._translate("RestoreBackupUI","Backup Restored!"),
                self._translate("RestoreBackupUI",
                    "MO2 Backup from "
                    + date_format
                    + " has successfully been restored!"
                ),
            )
            self._organizer.refresh(True)
        except Exception as error:
            print(str(error))

            error_message = error
            e_type, e_object, e_traceback = sys.exc_info()
            e_line_number = e_traceback.tb_lineno
                
            print(f'exception type: {e_type}')

            print(f'exception line number: {e_line_number}')
            
            if len(error.args) > 1:
                if "file already exists" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        fname2 = str(error).split("'")[3]
                        error_message = (
                            "Duplicated file name, please rename one of the following mods: \n"
                            + fname1
                            + " \n"
                            + fname2
                        )
                    except:
                        error_message = (
                            "Duplicated file name,\n"
                            + str(error)
                        )
                if "Access is denied" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        error_message = (
                            "Access denied, please check that no files are open from the following mod and try again: \n"
                            + fname1
                        )
                    except:
                        error_message = (
                            "Access denied, \n" 
                            + str(error)
                        )

            QtWidgets.QMessageBox.information(
                self,
                self._translate("RestoreBackupUI","[NoDelete] Indexer has encountered an issue"),
                self._translate(
                    "RestoreBackupUI","Failed to restore requested backup. Reverting to previous state. \nError: \n"
                    + str(error_message)
                ),
            )

            self.restoreBackup(date)
            self._organizer.refresh(True)

    def on_restore_clicked(self):
        if self.missing_items is not None and self.missing_items == True:
            QtWidgets.QMessageBox.information(
                self,
                self._translate("RestoreBackupUI","Cannot restore this backup"),
                self._translate("RestoreBackupUI",
                    "This backup cannot be restored, as some mods cannot be found. \nPlease check for any 'Not Found' mods, and either disable the checkbox next to them in the backup contents list, or reinstall the mod and try again."
                ),
            )
        else:
            if self.selected_item is not None:
                date = self.selected_item.data(69)
                if date is not None:
                    self.restoreBackup(date)

    def on_cancel_clicked(self):
        self.close()


class MainWindow(QtWidgets.QDialog, Ui_RestoreBackup):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

    def showWindow(self, _organizer, _parent):
        self.setupUi(self, _organizer, _parent)
        self.show()


class RestoreBackup(
    mobase.IPluginTool
):  # The base class depends on the actual type of plugin

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self._organizer = None
        self._parent = None

    def __tr(self, str_):
        return QtCore.QCoreApplication.translate("WabbajackNoDeleteSaver", str_)

    # IPlugin
    def init(self, organizer):
        self._organizer = organizer
        return True

    def name(self):
        return "Restore Backup"

    def author(self):
        return "Alf"

    def description(self):
        return self.__tr(
            "Automatically adds index numbers to your [NoDelete] tags to keep your mod order saved when updating via Wabbajack"
        )

    def version(self):
        return mobase.VersionInfo(1, 0, 0, 0)

    def settings(self):
        return []

    # IPluginTool
    def displayName(self):
        return self.__tr("[NoDelete] Indexer/4. Restore Backup")

    def tooltip(self):
        return self.description()

    def icon(self):
        return QtGui.QIcon()

    def setParentWidget(self, widget):
        self._parent = widget

    def display(self):
        self.window = MainWindow()
        self.window.showWindow(self._organizer, self._parent)


class RemoveIndexingNumbers(
    mobase.IPluginTool
):  # The base class depends on the actual type of plugin

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self._organizer = None
        self._parent = None
        self.window = MainWindow()

    def __tr(self, str_):
        return QtCore.QCoreApplication.translate("WabbajackNoDeleteSaver", str_)

    # IPlugin
    def init(self, organizer):
        self._organizer = organizer
        return True

    def name(self):
        return "Remove Indexing Numbers"

    def author(self):
        return "Alf"

    def description(self):
        return self.__tr(
            "Automatically adds index numbers to your [NoDelete] tags to keep your mod order saved when updating via Wabbajack"
        )

    def version(self):
        return mobase.VersionInfo(1, 0, 0, 0)

    def settings(self):
        return []

    # IPluginTool
    def displayName(self):
        return self.__tr("[NoDelete] Indexer/2. Remove Indexing Numbers")

    def tooltip(self):
        return self.description()

    def icon(self):
        return QtGui.QIcon()

    def setParentWidget(self, widget):
        self._parent = widget

    def display(self):
        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
        self.stripPreviousIndexes(modlisttxt_Path, modsfolder_Path, modsfolder_List)
        QtWidgets.QMessageBox.information(
            self._parent,
            self.__tr("[NoDelete] Indexes Removed"),
            self.__tr("All mods with the [NoDelete] tag's indexes have been removed."),
        )
        self._organizer.refresh(True)

    # ----------------------------------------------------------------
    # Remove all previous [index] values from both the modlist.txt file and the mods folders.
    #
    # modlisttxt_Path: path to the modlist.txt file
    # modsfolder_Path: path to the mods folder
    # modsfolder_List: List containing all the mods folders
    # ----------------------------------------------------------------
    def stripPreviousIndexes(self, modlisttxt_Path, modsfolder_Path, modsfolder_List):
        print("Removing previous [indexes] from /mods folder and modlist.txt")
        # Strip from mods folders
        for folder in modsfolder_List:
            if "[NoDelete]" in folder or "[No Delete]" in folder:
                oldFolderName = modsfolder_Path + "/" + folder
                newFolderName = self.stripPreviousIndex(oldFolderName)
                
                my_file = Path(oldFolderName.rstrip())
                if my_file.exists():
                    os.rename("" + oldFolderName.rstrip(), "" + newFolderName.rstrip())

        # Strip from modlist.txt
        lines = []
        with open(modlisttxt_Path, "r", encoding="UTF-8") as infile:
            for line in infile:
                line = re.sub("\[[0-9]+\]", "", line)
                line = re.sub("\[[0-9]*\.[0-9]+\]\s", "", line)
                lines.append(line)
        with open(modlisttxt_Path, "w", encoding="UTF-8") as outfile:
            for line in lines:
                outfile.write(line)

    # ----------------------------------------------------------------
    # Strip a string of any [index] values and return the new value
    # ----------------------------------------------------------------
    def stripPreviousIndex(self, oldFolderName):
        newFolderName = re.sub("\[[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\[[0-9]*\.[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\s+", " ", newFolderName)
        return newFolderName


class SortPlugins(
    mobase.IPluginTool
):  # The base class depends on the actual type of plugin

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self._organizer = None
        self._parent = None

    def __tr(self, str_):
        return QtCore.QCoreApplication.translate("WabbajackNoDeleteSaver", str_)

    # IPlugin
    def init(self, organizer):
        self._organizer = organizer
        return True

    def name(self):
        return "Sort [NoDelete] Plugins"

    def author(self):
        return "Alf"

    def description(self):
        return self.__tr(
            "Automatically adds index numbers to your [NoDelete] tags to keep your mod order saved when updating via Wabbajack"
        )

    def version(self):
        return mobase.VersionInfo(1, 0, 0, 0)

    def settings(self):
        return []

    # IPluginTool
    def displayName(self):
        return self.__tr("[NoDelete] Indexer/3. Order Plugins")

    def tooltip(self):
        return self.description()

    def icon(self):
        return QtGui.QIcon()

    def setParentWidget(self, widget):
        self._parent = widget

    def display(self):
        self.restorePluginsObjects()

    # ----------------------------------------------------------------
    # Backup the plugins.txt incase failure.
    # ----------------------------------------------------------------
    def backupPluginstxt(self, pluginstxt_Path, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(pluginstxt_Path, "r", encoding="utf-8") as pluginstxt:
            with open(backup_path, "w", encoding="utf-8") as backupfile:
                backupfile.write(pluginstxt.read())

        print("Made backup of plugins.txt to '" + backup_path + "'")

    def restorePluginsBackup(self, profilefolder_Path, date_format):

        backuppluginstxt_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
            + date_format
            + ".txt"
        )

        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
        if os.path.exists(backuppluginstxt_path):
            # restore plugins.txt
            with open(backuppluginstxt_path, "r", encoding="utf-8") as backupfile:
                with open(pluginstxt_Path, "w", encoding="utf-8") as pluginstxt:
                    pluginstxt.write(backupfile.read())

    def restorePluginsObjects(self):
        try:
            print("----------------------------------------------------------------")
            print("             Wabbajack - MO2 [NoDelete] Indexer")
            print("----------------------------------------------------------------")
            print("\nOrdering Plugins from [NoDelete] Mods")

            profilefolder_Path = self._organizer.profilePath()
            pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
            backupFolderPath = str(profilefolder_Path + "/[NoDelete] Indexer Backups")

            # def date for this runthrough
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")

            # Make backup of plugins.txt
            self.backupPluginstxt(pluginstxt_Path, profilefolder_Path, date)

            pluginObjectFiles = []
            for file in os.listdir(backupFolderPath):
                if "pluginsObjects" in file.rstrip():
                    pluginObjectFiles.append(
                        backupFolderPath.rstrip() + "/" + file.rstrip()
                    )

            latestPluginObjectFile = ""
            for file in pluginObjectFiles:
                newdatestr = (
                    file.replace(backupFolderPath + "/", "")
                    .replace("pluginsObjects_", "")
                    .replace(".txt", "")
                )
                newdate = datetime.datetime.strptime(newdatestr, "%Y-%m-%dT%H_%M_%SZ")

                if latestPluginObjectFile != "":
                    latestdatestr = (
                        latestPluginObjectFile.replace(backupFolderPath + "/", "")
                        .replace("pluginsObjects_", "")
                        .replace(".txt", "")
                    )
                    latestdate = datetime.datetime.strptime(
                        latestdatestr, "%Y-%m-%dT%H_%M_%SZ"
                    )

                    if newdate > latestdate:
                        latestPluginObjectFile = file
                else:
                    latestPluginObjectFile = file

            pluginFilePath = latestPluginObjectFile

            print("Loading plugin objects from '" + pluginFilePath + "'")
            pluginObjects = []
            temp = []
            with open(pluginFilePath, "r", encoding="utf-8") as f:
                for jsonObj in f:
                    data = json.loads(jsonObj)
                    temp.append(data)

            for pluginObject in temp:
                pluginObjects.append(pluginObject)

            print("Plugin Objects:")
            for pluginObject in pluginObjects:
                print(pluginObject[1].get("pluginName"))
                print(pluginObject)

            lines = []
            with open(pluginstxt_Path, "r", encoding="UTF-8") as pluginsfilein:
                # Read each line in plugin txt and add to lines
                for line in pluginsfilein:
                    lines.append(line)

            # Go through each plugin and find the position of [NoDelete] plugins
            for pluginObject in pluginObjects:
                found = False
                print("\n----------------\n" + pluginObject[1].get("pluginName"))
                print(pluginObject[1].get("previousPlugins"))
                print("----------------")
                for plugin in pluginObject[1].get("previousPlugins"):
                    if found == True:
                        break
                    for i, pluginname in reversed(list(enumerate(lines))):
                        if found == True:
                            break
                        # print(plugin.rstrip())
                        plugin = plugin.rstrip()
                        pluginname = pluginname.rstrip()

                        if pluginname.replace("*", "") == plugin.replace("*", ""):
                            print(
                                "FOUND PREVIOUS PLUGIN: "
                                + pluginname
                                + " for plugin: "
                                + pluginObject[1].get("pluginName")
                            )

                            # Remove old plugin position from lines
                            if (
                                lines.count(pluginObject[1].get("pluginName") + "\n")
                                > 0
                            ):
                                lines.remove(pluginObject[1].get("pluginName") + "\n")
                                print(
                                    "Removed old plugin position: "
                                    + pluginObject[1].get("pluginName")
                                    + "\n"
                                )
                            elif (
                                lines.count(
                                    pluginObject[1].get("pluginName").replace("*", "")
                                    + "\n"
                                )
                                > 0
                            ):
                                lines.remove(
                                    pluginObject[1].get("pluginName").replace("*", "")
                                    + "\n"
                                )
                                print(
                                    "Removed old plugin position: "
                                    + pluginObject[1].get("pluginName")
                                    + "\n"
                                )

                            # edit lines to include new position of plugin
                            lines.insert(
                                i + 1, pluginObject[1].get("pluginName") + "\n"
                            )
                            found = True
                            break

            print("LINES:")
            print(lines)
            # Write new lines to plugins fileout
            with open(pluginstxt_Path, "w", encoding="UTF-8") as pluginsfileout:
                for line in lines:
                    pluginsfileout.write(line)

            print("----------------------------------------------------------------")
            print("             Plugins Ordered")
            print("----------------------------------------------------------------")

            QtWidgets.QMessageBox.information(
                self._parent,
                self.__tr("Success!"),
                self.__tr(
                    "Plugins within [NoDelete] mods have been ordered according to your previous list. "
                ),
            )
            self._organizer.refresh(True)

        except OSError as error:
            self.restorePluginsBackup(profilefolder_Path, date)
            print(error)
            QtWidgets.QMessageBox.information(
                self._parent,
                self.__tr("[NoDelete] Indexer Encountered an Issue"),
                self.__tr(
                    "Failed to complete ordering of [NoDelete] plugins \nError: "
                    + str(error)
                ),
            )
            self._organizer.refresh(True)


class NoDeleteIndexer(
    mobase.IPluginTool
):  # The base class depends on the actual type of plugin

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self._organizer = None
        self._parent = None

    def __tr(self, str_):
        return QtCore.QCoreApplication.translate("WabbajackNoDeleteSaver", str_)

    # IPlugin
    def init(self, organizer):
        self._organizer = organizer
        return True

    def name(self):
        return "Run Indexer"

    def author(self):
        return "Alf"

    def description(self):
        return self.__tr(
            "Automatically adds index numbers to your [NoDelete] tags to keep your mod order saved when updating via Wabbajack"
        )

    def version(self):
        return mobase.VersionInfo(1, 0, 0, 0)

    def settings(self):
        return []

    # IPluginTool
    def displayName(self):
        return self.__tr("[NoDelete] Indexer/1. Run Indexer")

    def tooltip(self):
        return self.description()

    def icon(self):
        return QtGui.QIcon()

    def setParentWidget(self, widget):
        self._parent = widget

    def display(self):
        self.rename()

    # ----------------------------------------------------------------
    # Add the new index values to the provided modlist.txt file.
    #
    # txtfilepath: the absolute path to the txt file
    # replacementDict: a dictionary of "old name : new name" replacements
    # modsfolder_Path: the path to the mods folder
    # ----------------------------------------------------------------
    def addNewIndexToFile(self, txtfilepath, replacementDict, modsfolder_Path):
        lines = []
        nodellines = []

        with open(txtfilepath, "r", encoding="UTF-8") as infile:
            for line in infile:
                if "[NoDelete]" in line or "[No Delete]" in line:
                    searchLine = modsfolder_Path + "/" + line[1:].rstrip()
                    line = line.replace(
                        self.getJustFolderName(str(searchLine)),
                        self.getJustFolderName(str(replacementDict.get(searchLine))),
                    )

                    nodellines.append(line)
                lines.append(line)

        with open(txtfilepath, "w", encoding="UTF-8") as outfile:
            for line in lines:
                outfile.write(line)

    # ----------------------------------------------------------------
    # Remove all previous [index] values from both the modlist.txt file and the mods folders.
    #
    # modlisttxt_Path: path to the modlist.txt file
    # modsfolder_Path: path to the mods folder
    # modsfolder_List: List containing all the mods folders
    # ----------------------------------------------------------------
    def stripPreviousIndexes(self, modlisttxt_Path, modsfolder_Path, modsfolder_List):
        print("Removing previous [indexes] from /mods folder and modlist.txt")
        # Strip from mods folders
        for folder in modsfolder_List:
            if "[NoDelete]" in folder or "[No Delete]" in folder:
                oldFolderName = modsfolder_Path + "/" + folder
                newFolderName = self.stripPreviousIndex(oldFolderName)
                
                my_file = Path(oldFolderName.rstrip())
                if my_file.exists():
                    os.rename("" + oldFolderName.rstrip(), "" + newFolderName.rstrip())

        # Strip from modlist.txt
        lines = []
        with open(modlisttxt_Path, "r", encoding="UTF-8") as infile:
            for line in infile:
                line = re.sub("\[[0-9]+\]", "", line)
                line = re.sub("\[[0-9]*\.[0-9]+\]\s", "", line)
                lines.append(line)
        with open(modlisttxt_Path, "w", encoding="UTF-8") as outfile:
            for line in lines:
                outfile.write(line)

    # ----------------------------------------------------------------
    # Strip a string of any [index] values and return the new value
    # ----------------------------------------------------------------
    def stripPreviousIndex(self, oldFolderName):
        newFolderName = re.sub("\[[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\[[0-9]*\.[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\s+", " ", newFolderName)
        return newFolderName

    # ----------------------------------------------------------------
    # From a full path, return just the end folder name
    # ----------------------------------------------------------------
    def getJustFolderName(self, fullpath):
        foldername = fullpath.split("/")
        foldername = foldername[len(foldername) - 1]
        return foldername

    # ----------------------------------------------------------------
    # Backup the plugins.txt incase failure.
    # ----------------------------------------------------------------
    def backupPluginstxt(self, pluginstxt_Path, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(pluginstxt_Path, "r", encoding="utf-8") as pluginstxt:
            with open(backup_path, "w", encoding="utf-8") as backupfile:
                backupfile.write(pluginstxt.read())

        print("Made backup of plugins.txt to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Backup the modlist.txt incase failure.
    # ----------------------------------------------------------------
    def backupModlisttxt(self, modlisttxt_Path, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/modlist_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(modlisttxt_Path, "r", encoding="utf-8") as modlisttxt:
            with open(backup_path, "w", encoding="utf-8") as backupfile:
                backupfile.write(modlisttxt.read())

        print("Made backup of modlist.txt to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Backup the plugins objects so that they may be sorted AFTER wabbajack usage.
    # ----------------------------------------------------------------
    def backupPluginsObjects(self, pluginsObjects, profilefolder_Path, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/pluginsObjects_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        with open(backup_path, "w", encoding="utf-8") as backupfile:
            for plugin in pluginsObjects.items():
                json.dump(plugin, backupfile)
                backupfile.write("\n")

        print("Made backup of plugin objects to '" + backup_path + "'")

    def backupModFolders(self, profilefolder_Path, oldToNewDictionary, date_format):
        backup_path = str(
            profilefolder_Path
            + "/[NoDelete] Indexer Backups/modfolders_BACKUP_"
            + date_format
            + ".txt"
        )

        if not os.path.exists(profilefolder_Path + "/[NoDelete] Indexer Backups"):
            os.makedirs(profilefolder_Path + "/[NoDelete] Indexer Backups")

        # For each separator, rename folders appropriately.
        with open(backup_path, "w", encoding="utf-8") as backupfile:
            backupfile.write(str(oldToNewDictionary))

        print("Made backup of mod folders to '" + backup_path + "'")

    # ----------------------------------------------------------------
    # Restore the modlist.txt, plugins.txt and folder names incase failure.
    # ----------------------------------------------------------------
    def restoreBackup(self, date_format):
        date = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")

        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)
        pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")

        #self.backupModFolders(
        #    profilefolder_Path, self.oldToNewDictionary, date
        #)
        self.backupModlisttxt(modlisttxt_Path, profilefolder_Path, date)
        self.backupPluginstxt(pluginstxt_Path, profilefolder_Path, date)

        self.stripPreviousIndexes(modlisttxt_Path, modsfolder_Path, modsfolder_List)

        modsWithLoadorder = {}
        with open(modlisttxt_Path, "r", encoding="UTF-8") as infile:
            for i, modname in reversed(list(enumerate(infile))):
                if "[NoDelete]" in modname or "[No Delete]" in modname:
                    modname = modname[1:]
                    modsWithLoadorder[len(modsWithLoadorder)] = modname

        modlistname_list = list(modsWithLoadorder.values())

        pluginObjects = {}
        # make list of all plugins for easier traversal
        pluginstxt_list = {}
        with open(pluginstxt_Path, "r", encoding="UTF-8") as pluginsfile:
            for i, pluginname in list(enumerate(pluginsfile)):
                pluginname = pluginname[0:]
                pluginstxt_list[len(pluginstxt_list)] = pluginname.rstrip()

        # Go through mod folders and make plugin objects
        for folder in modlistname_list:
            for file in os.listdir(modsfolder_Path.rstrip() + "/" + folder.rstrip()):
                for i, pluginName in pluginstxt_list.items():
                    if pluginName.rstrip().replace("*", "") in file.rstrip():
                        print(str(i) + " : " + pluginName.rstrip())
                        modName = folder.rstrip()
                        pluginName = pluginName.rstrip()
                        previousPlugins = []
                        # grab previous 10 plugins
                        for j in range(10):
                            j = j + 1
                            x = 0
                            if i - j > 0:
                                x = i - j
                            if len(previousPlugins) == 0:
                                previousPlugins.append(pluginstxt_list[x])
                            elif previousPlugins[-1] != pluginstxt_list[x]:
                                previousPlugins.append(pluginstxt_list[x])
                        nextPlugins = []
                        # grab next 10 plugins
                        for j in range(10):
                            j = j + 1
                            x = len(pluginstxt_list) - 1
                            if i + j < len(pluginstxt_list):
                                x = i + j
                            if len(nextPlugins) == 0:
                                nextPlugins.append(pluginstxt_list[x])
                            elif nextPlugins[-1] != pluginstxt_list[x]:
                                nextPlugins.append(pluginstxt_list[x])
                        pluginObjects[pluginName.replace("*", "").rstrip()] = {
                            "modName": modName,
                            "pluginName": pluginName,
                            "previousPlugins": previousPlugins,
                            "nextPlugins": nextPlugins,
                        }

        self.backupPluginsObjects(pluginObjects, profilefolder_Path, date)

        try:
            backupmodlisttxt_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/modlist_BACKUP_"
                + date_format
                + ".txt"
            )

            backuppluginstxt_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/plugins_BACKUP_"
                + date_format
                + ".txt"
            )

            backupfolders_path = str(
                profilefolder_Path
                + "/[NoDelete] Indexer Backups/modfolders_BACKUP_"
                + date_format
                + ".txt"
            )

            if os.path.exists(backupmodlisttxt_path):
                # restore modlist.txt
                with open(backupmodlisttxt_path, "r", encoding="utf-8") as backupfile:
                    with open(modlisttxt_Path, "w", encoding="utf-8") as modlisttxt:
                        modlisttxt.write(backupfile.read())

            pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")
            if os.path.exists(backuppluginstxt_path):
                # restore plugins.txt
                with open(backuppluginstxt_path, "r", encoding="utf-8") as backupfile:
                    with open(pluginstxt_Path, "w", encoding="utf-8") as pluginstxt:
                        pluginstxt.write(backupfile.read())

            if os.path.exists(backupfolders_path):
                # restore mod folder names
                oldToNewDictionary = {}
                with open(
                    backupfolders_path, "r", encoding="utf-8"
                ) as backupfoldersfile:
                    oldToNewDictionary = ast.literal_eval(backupfoldersfile.read())

                for brokenFolder in oldToNewDictionary:
                    my_file = Path(oldToNewDictionary[brokenFolder].rstrip())
                    if my_file.exists():
                        os.rename(
                            "" + oldToNewDictionary[brokenFolder].rstrip(),
                            "" + brokenFolder.rstrip(),
                        )

            self._organizer.refresh(True)
        except Exception as error:
            print(str(error))

            error_message = error
            e_type, e_object, e_traceback = sys.exc_info()
            e_line_number = e_traceback.tb_lineno
                
            print(f'exception type: {e_type}')

            print(f'exception line number: {e_line_number}')
            
            if len(error.args) > 1:
                if "file already exists" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        fname2 = str(error).split("'")[3]
                        error_message = (
                            "Duplicated file name, please rename one of the following mods: \n"
                            + fname1
                            + " \n"
                            + fname2
                        )
                    except:
                        error_message = (
                            "Duplicated file name,\n"
                            + str(error)
                        )
                if "Access is denied" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        error_message = (
                            "Access denied, please check that no files are open from the following mod and try again: \n"
                            + fname1
                        )
                    except:
                        error_message = (
                            "Access denied, \n" 
                            + str(error)
                        )

            QtWidgets.QMessageBox.information(
                self._parent,
                self.__tr("[NoDelete] Indexer has encountered an issue"),
                self.__tr("Failed to restore requested backup. Reverting to previous state. \nError: \n"
                    + str(error_message)
                ),
            )

            self.restoreBackup(date)
            self._organizer.refresh(True)
            
    # ----------------------------------------------------------------
    # Sort mods in MO2/mods folder by their current order in Mod Organizer.
    # Will categorise by their current separator.
    # ----------------------------------------------------------------
    def rename(self):
        print("----------------------------------------------------------------")
        print("             Wabbajack - MO2 [NoDelete] Saver")
        print("----------------------------------------------------------------")
        print("\nRenaming MO2 [NoDelete] Mods")

        try:

            # def date for this runthrough
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")

            # Load paths
            modsfolder_Path = self._organizer.modsPath()
            profilefolder_Path = self._organizer.profilePath()
            modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
            modsfolder_List = os.listdir(modsfolder_Path)
            pluginstxt_Path = str(profilefolder_Path + "/plugins.txt")

            # Make backup of modlist.txt
            self.backupModlisttxt(modlisttxt_Path, profilefolder_Path, date)

            # Make backup of plugins.txt
            self.backupPluginstxt(pluginstxt_Path, profilefolder_Path, date)

            # Remove any order tagging from previous
            self.stripPreviousIndexes(modlisttxt_Path, modsfolder_Path, modsfolder_List)

            # Find all mods with [NoDelete] and add to dictionary as "index : modname"
            modsWithLoadorder = {}
            with open(modlisttxt_Path, "r", encoding="UTF-8") as infile:
                for i, modname in reversed(list(enumerate(infile))):
                    if "[NoDelete]" in modname or "[No Delete]" in modname:
                        modname = modname[1:]
                        modsWithLoadorder[len(modsWithLoadorder)] = modname

            modlistindex_list = list(modsWithLoadorder.keys())
            modlistname_list = list(modsWithLoadorder.values())

            pluginObjects = {}
            # make list of all plugins for easier traversal
            pluginstxt_list = {}
            with open(pluginstxt_Path, "r", encoding="UTF-8") as pluginsfile:
                for i, pluginname in list(enumerate(pluginsfile)):
                    pluginname = pluginname[0:]
                    pluginstxt_list[len(pluginstxt_list)] = pluginname.rstrip()
            print("Plugin list")
            print(pluginstxt_list)

            # Go through mod folders and make plugin objects
            for folder in modlistname_list:
                print("FOLDER: " + folder.rstrip())
                for file in os.listdir(
                    modsfolder_Path.rstrip() + "/" + folder.rstrip()
                ):
                    for i, pluginName in pluginstxt_list.items():
                        if pluginName.rstrip().replace("*", "") in file.rstrip():
                            print(str(i) + " : " + pluginName.rstrip())
                            modName = folder.rstrip()
                            pluginName = pluginName.rstrip()
                            previousPlugins = []
                            # grab previous 10 plugins
                            for j in range(10):
                                j = j + 1
                                x = 0
                                if i - j > 0:
                                    x = i - j
                                if len(previousPlugins) == 0:
                                    previousPlugins.append(pluginstxt_list[x])
                                elif previousPlugins[-1] != pluginstxt_list[x]:
                                    previousPlugins.append(pluginstxt_list[x])
                            nextPlugins = []
                            # grab next 10 plugins
                            for j in range(10):
                                j = j + 1
                                x = len(pluginstxt_list) - 1
                                if i + j < len(pluginstxt_list):
                                    x = i + j
                                if len(nextPlugins) == 0:
                                    nextPlugins.append(pluginstxt_list[x])
                                elif nextPlugins[-1] != pluginstxt_list[x]:
                                    nextPlugins.append(pluginstxt_list[x])
                            pluginObjects[pluginName.replace("*", "").rstrip()] = {
                                "modName": modName,
                                "pluginName": pluginName,
                                "previousPlugins": previousPlugins,
                                "nextPlugins": nextPlugins,
                            }

            # Make backup of plugins objects (For restoration after wabbajack usage)
            self.backupPluginsObjects(pluginObjects, profilefolder_Path, date)

            print("Processing " + str(len(modlistname_list)) + " [NoDelete] mods")

            # Make list of separators with a list of their mods
            separatorDirectory = {}
            isInSeparator = False
            currentSeparator = ""
            prevSeparator = ""

            for folder in modlistname_list:
                
                if "_separator" in folder:
                    isCurrentSeparator = True
                    currentSeparator = folder
                    separatorDirectory[currentSeparator] = []
                else:
                    isCurrentSeparator = False

                if currentSeparator == "":
                    isInSeparator = False
                else:
                    isInSeparator = True

                print("f " + str(folder) + " currsep " + str(currentSeparator))

                if isInSeparator == True and isCurrentSeparator == False:
                    separatorDirectory[currentSeparator].append(folder)
                if isInSeparator == False and isCurrentSeparator == False:
                    separatorDirectory[folder] = []
                
            # dictionary of old -> new filenames
            oldToNewDictionary = {}

            print(str(separatorDirectory))
            
            # For each separator, rename folders appropriately.
            for separator in separatorDirectory:
                if "_separator" in separator:
                    print(
                        "Processing separator: %s"
                        % separator.replace("_separator", "").rstrip()
                    )
                currentSeparatorMods = separatorDirectory.get(separator)

                # Calculate separator index
                separatorIndex = list(separatorDirectory.keys()).index(separator) + 1
                separatorIndex = "%03d" % (separatorIndex,)

                # Rename separator folders
                newIndex = "%05d" % (0,)
                newFolderName = separator.replace(
                    "[NoDelete]",
                    "[NoDelete] "
                    + "["
                    + str(separatorIndex)
                    + "."
                    + str(newIndex)
                    + "]",
                ).replace(
                    "[No Delete]",
                    "[No Delete] "
                    + "["
                    + str(separatorIndex)
                    + "."
                    + str(newIndex)
                    + "]",
                )
                oldFolderName = modsfolder_Path + "/" + separator
                newFolderName = modsfolder_Path + "/" + newFolderName

                self.backupModFolders(profilefolder_Path, oldToNewDictionary, date)
                my_file = Path(oldFolderName.rstrip())
                print("old seperator: " + "" + oldFolderName.rstrip() + str(my_file.exists()))
                print("new seperator: " + "" + newFolderName.rstrip())

                if my_file.exists():
                    oldToNewDictionary[oldFolderName.rstrip()] = newFolderName.rstrip()
                    os.rename("" + oldFolderName.rstrip(), "" + newFolderName.rstrip())

                # Rename mod folders
                for folder in currentSeparatorMods:

                    # Calculate position in separator directory index
                    position = currentSeparatorMods.index(folder) + 1
                                   
                    if len(modlistindex_list) > position:
                        newIndex = "%05d" % (modlistindex_list[position],)

                        newFolderName = folder.replace(
                            "[NoDelete]",
                            "[NoDelete] "
                            + "["
                            + str(separatorIndex)
                            + "."
                            + str(newIndex)
                            + "]",
                        ).replace(
                            "[No Delete]",
                            "[No Delete] "
                            + "["
                            + str(separatorIndex)
                            + "."
                            + str(newIndex)
                            + "]",
                        )

                        oldFolderName = modsfolder_Path + "/" + folder
                        newFolderName = modsfolder_Path + "/" + newFolderName
                        
                        my_file = Path(oldFolderName.rstrip())
                        print("old folder: " + "" + oldFolderName.rstrip() + str(my_file.exists()))
                        print("new folder: " + "" + newFolderName.rstrip())

                        if my_file.exists():
                            oldToNewDictionary[oldFolderName.rstrip()] = newFolderName.rstrip()
                            os.rename("" + oldFolderName.rstrip(), "" + newFolderName.rstrip())

            # Update modlist.txt file to use the new indexes
            self.addNewIndexToFile(modlisttxt_Path, oldToNewDictionary, modsfolder_Path)
            
            print("Processed " + str(len(oldToNewDictionary)) + " [NoDelete] mods")
            print("\n----------------------------------------------------------------")

            QtWidgets.QMessageBox.information(
                self._parent,
                self.__tr("[NoDelete] Tags Indexed"),
                self.__tr(
                    str(len(oldToNewDictionary))
                    + " mods with the [NoDelete] tag have been indexed."
                ),
            )
            self._organizer.refresh(True)
        except Exception as error:
            print(str(error))

            error_message = error
            e_type, e_object, e_traceback = sys.exc_info()
            e_line_number = e_traceback.tb_lineno
                
            print(f'exception type: {e_type}')

            print(f'exception line number: {e_line_number}')
    
            ########
            if len(error.args) > 1:
                if "file already exists" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        fname2 = str(error).split("'")[3]
                        error_message = (
                            "Duplicated file name, please rename one of the following mods: \nLine number" + str({e_line_number}) + "\n"
                            + fname1
                            + " \n"
                            + fname2
                        )
                    except:
                        error_message = (
                            "Duplicated file name,\n"
                            + str(error)
                        )
                if "Access is denied" in error.args[1]:
                    try:
                        fname1 = str(error).split("'")[1]
                        error_message = (
                            "Access denied, please check that no files are open from the following mod and try again: \nLine number" + str({e_line_number}) + "\n"
                            + fname1
                        )
                    except:
                        error_message = (
                            "Access denied, \n" 
                            + str(error)
                        )
            QtWidgets.QMessageBox.information(
                self._parent,
                self.__tr("[NoDelete] Indexer has encountered an issue"),
                self.__tr(
                    "Failed to complete indexing of [NoDelete] Tags. \nLine number" + str({e_line_number}) + "\nError: \n"
                    + str(error_message)
                ),
            )
            
            self.restoreBackup(date)
            self._organizer.refresh(True)

# SortPlugins(), RestoreBackup()
def createPlugins():
    return [NoDeleteIndexer(), RemoveIndexingNumbers()]
