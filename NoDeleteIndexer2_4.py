#----------------------------------------------------------------
# Author: A. Costello
#----------------------------------------------------------------
from typing import List
from PyQt5.QtCore import QCoreApplication, qCritical, QDir, qDebug
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

import mobase
import os
import re

class MyPlugin(mobase.IPluginTool):  # The base class depends on the actual type of plugin

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self._organizer = None
        self._parent = None

    def __tr(self, str_):
        return QCoreApplication.translate("WabbajackNoDeleteSaver", str_)
    
     # IPlugin
    def init(self, organizer):
        self._organizer = organizer
        return True

    def name(self):
        return "Wabbajack [NoDelete] Indexer"

    def author(self):
        return "Alf"

    def description(self):
        return self.__tr("Automatically adds index numbers to your [NoDelete] tags to keep your mod order saved when updating via Wabbajack")

    def version(self):
        return mobase.VersionInfo(1, 0, 0, 0)

    def settings(self):
        return []
        
    # IPluginTool
    def displayName(self):
        return self.__tr("[NoDelete] Indexer")

    def tooltip(self):
        return self.description()

    def icon(self):
        return QIcon()
    
    def setParentWidget(self, widget):
        self._parent = widget

    def display(self):
        self.rename()
        
    #----------------------------------------------------------------
    # Add the new index values to the provided modlist.txt file.
    #
    # txtfilepath: the absolute path to the txt file
    # replacementDict: a dictionary of "old name : new name" replacements
    # modsfolder_Path: the path to the mods folder
    #----------------------------------------------------------------
    def addNewIndexToFile(self, txtfilepath, replacementDict, modsfolder_Path):      
            lines = []
            nodellines = []

            with open(txtfilepath,'r', encoding='UTF-8') as infile:
                for line in infile:
                    if '[NoDelete]' in line:
                        searchLine = modsfolder_Path + "/" + line[1:].rstrip()
                        line = line.replace(self.getJustFolderName(str(searchLine)), self.getJustFolderName(str(replacementDict.get(searchLine))))
                        
                        nodellines.append(line)
                    lines.append(line)
                
            with open(txtfilepath, 'w', encoding='UTF-8') as outfile:
                for line in lines:
                    outfile.write(line)
            
    #----------------------------------------------------------------
    # Remove all previous [index] values from both the modlist.txt file and the mods folders.
    #
    # modlisttxt_Path: path to the modlist.txt file
    # modsfolder_Path: path to the mods folder
    # modsfolder_List: List containing all the mods folders
    #----------------------------------------------------------------
    def stripPreviousIndexes(self, modlisttxt_Path, modsfolder_Path, modsfolder_List):
        print("Removing previous [indexes] from /mods folder and modlist.txt")
        # Strip from mods folders
        for folder in modsfolder_List:
            if '[NoDelete]' in folder:
                oldFolderName = (modsfolder_Path + "/" + folder)
                newFolderName = self.stripPreviousIndex(oldFolderName)
                os.rename(""+oldFolderName.rstrip(),""+newFolderName.rstrip())
                
        # Strip from modlist.txt
        lines = []
        with open(modlisttxt_Path, 'r', encoding='UTF-8') as infile:
            for line in infile:
                line = re.sub("\[[0-9]+\]", "", line)
                line = re.sub("\[[0-9]*\.[0-9]+\]\s", "", line)
                lines.append(line)
        with open(modlisttxt_Path, 'w', encoding='UTF-8') as outfile:
            for line in lines:
                outfile.write(line)
                
    #----------------------------------------------------------------
    # Strip a string of any [index] values and return the new value
    #----------------------------------------------------------------   
    def stripPreviousIndex(self, oldFolderName):
        newFolderName = re.sub("\[[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\[[0-9]*\.[0-9]+\]", "", oldFolderName)
        newFolderName = re.sub("\s+", " ", newFolderName)
        return newFolderName

    #----------------------------------------------------------------
    # From a full path, return just the end folder name
    #----------------------------------------------------------------   
    def getJustFolderName(self, fullpath):
        foldername = fullpath.split('/')
        foldername = foldername[len(foldername)-1] 
        return foldername

    #----------------------------------------------------------------
    # Backup the modlist.txt incase failure.
    #----------------------------------------------------------------
    def backupModlisttxt(self, modlisttxt_Path, profilefolder_Path):
        lines = []
        with open(modlisttxt_Path, 'r', encoding='UTF-8') as infile:
            for line in infile:
                lines.append(line)
                
        with open(str(profilefolder_Path + "modlist_BACKUP.txt"), 'w', encoding='UTF-8') as outfile:
            for line in lines:
                outfile.write(line)
        print("Made backup of modlist.txt to '" + str(profilefolder_Path + "modlist_BACKUP.txt") + "'")
    #----------------------------------------------------------------
    # Sort mods in MO2/mods folder by their current order in Mod Organizer.
    # Will categorise by their current separator.
    #----------------------------------------------------------------   
    def rename(self):
        print("----------------------------------------------------------------")
        print("             Wabbajack - MO2 [NoDelete] Saver")
        print("----------------------------------------------------------------")
        print("\nRenaming MO2 [NoDelete] Mods")
        
        # Load paths 
        modsfolder_Path = self._organizer.modsPath()
        profilefolder_Path = self._organizer.profilePath()
        modlisttxt_Path = str(profilefolder_Path + "/modlist.txt")
        modsfolder_List = os.listdir(modsfolder_Path)

        # Make backup of modlist.txt
        self.backupModlisttxt(modlisttxt_Path, profilefolder_Path)
        
        # Remove any order tagging from previous
        self.stripPreviousIndexes(modlisttxt_Path, modsfolder_Path, modsfolder_List)
        
        # Find all mods with [NoDelete] and add to dictionary as "index : modname"
        modsWithLoadorder = {}
        with open(modlisttxt_Path, 'r', encoding='UTF-8') as infile:
            for i, line in reversed(list(enumerate(infile))):
                if '[NoDelete]' in line:
                    #print(i, line)
                    line=line[1:]
                    modsWithLoadorder[len(modsWithLoadorder)] = line

        key_list = list(modsWithLoadorder.keys())
        val_list = list(modsWithLoadorder.values())
        
        print("Processing " + str(len(val_list)) + " [NoDelete] mods")
        
        # Make list of separators with a list of their mods
        separatorDirectory = {}
        separatorModList = []
        isInSeparator = False
        currentSeparator = ""
        prevSeparator = ""
        
        for folder in val_list:       

            if folder.endswith("_separator\n"):
                isCurrentSeparator = True
                prevSeparator = currentSeparator
                currentSeparator = folder
            else:
                isCurrentSeparator = False
                
            if(prevSeparator == "" and currentSeparator == ""):
                isInSeparator = False
            else:
                isInSeparator = True
                
            # If last one, then add
            if modsWithLoadorder.get(len(modsWithLoadorder)-1) == folder:
                if(currentSeparator != ""):
                    separatorModList.append(folder)
                    separatorDirectory[currentSeparator] = separatorModList
                    separatorModList = []
                
            # If current mod is in separator and is not itself a separator, needs to be added to previous separator.
            # Else if it is not a separator, add to it's own index
            # Else if it IS a separator, then add previous modlist and start new index
            if isInSeparator == True and isCurrentSeparator == False:
                separatorModList.append(folder)
            if isInSeparator == False and isCurrentSeparator == False:
                separatorDirectory[folder] = []
                separatorModList = []
            if isCurrentSeparator == True:
                if(prevSeparator != ""):
                    separatorDirectory[prevSeparator] = separatorModList
                    separatorModList = []

        
        # dictionary of old -> new filenames
        oldToNewDictionary = {}
            
        # For each separator, rename folders appropriately.
        for separator in separatorDirectory:
            if("_separator" in separator):
                print("Processing separator: %s" % separator.replace("_separator", "").rstrip())
            currentSeparatorMods = separatorDirectory.get(separator)
            
            # Calculate separator index
            separatorIndex = list(separatorDirectory.keys()).index(separator) + 1
            separatorIndex = "%03d" % (separatorIndex,)
                    
            # Rename separator folders
            newIndex = "%05d" % (0,)
            newFolderName = separator.replace("[NoDelete]", "[NoDelete] " + "[" + str(separatorIndex) + "." + str(newIndex) + "]")
            oldFolderName = (modsfolder_Path + "/" + separator)
            newFolderName = (modsfolder_Path + "/" + newFolderName)
            try: 
                oldToNewDictionary[oldFolderName.rstrip()] = newFolderName.rstrip()
                os.rename(""+oldFolderName.rstrip(),""+newFolderName.rstrip())
            except OSError as error: 
                print(error) 
                    
            # Rename mod folders
            for folder in currentSeparatorMods:
                try:
                    # Calculate position in separator directory index
                    position = currentSeparatorMods.index(folder) + 1
                    newIndex = "%05d" % (key_list[position],)
                    
                    newFolderName = folder.replace("[NoDelete]", "[NoDelete] " + "[" + str(separatorIndex) + "." + str(newIndex) + "]")
                    
                    oldFolderName = (modsfolder_Path + "/" + folder)
                    newFolderName = (modsfolder_Path + "/" + newFolderName)
                    
                    try : 
                        oldToNewDictionary[oldFolderName.rstrip()] = newFolderName.rstrip()
                        os.rename(""+oldFolderName.rstrip(),""+newFolderName.rstrip())
                    except OSError as error: 
                        print(error)  
                except OSError as error: 
                    print(error) 

        # Update modlist.txt file to use the new indexes            
        self.addNewIndexToFile(modlisttxt_Path, oldToNewDictionary, modsfolder_Path)
        print("Processed " + str(len(oldToNewDictionary)) + " [NoDelete] mods")
        print("\n----------------------------------------------------------------")
        QMessageBox.information(self._parent, self.__tr("[NoDelete] Tags Indexed"), self.__tr(str(len(oldToNewDictionary)) + " mods with the [NoDelete] tag have been indexed."))
        self._organizer.refresh(True)

def createPlugin() -> mobase.IPlugin:
    return MyPlugin()