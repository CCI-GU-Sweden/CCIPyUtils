#from operator import index
#import signal
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QFileSystemModel
#from watchdog.observers.polling import PollingObserver
from pathlib import Path
#from ccipy.utils.CCILogger import CCILogger
#import ImgFileEventHandler
#import logger
import os

DIR_PATH_ROLE = Qt.ItemDataRole.DisplayRole + 1

class CCISessionFilesModel(QSortFilterProxyModel):
    
    directoryLoaded = Signal(str)
    
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.fsm = QFileSystemModel()
        self.setSourceModel(self.fsm)
        self.dataSets = []
        self.dir_watcher = None
 #       self.fsm.directoryLoaded.connect(self.logDirLoaded)
        self.fsm.directoryLoaded.connect(self.directoryLoaded)
 #       CCILogger.setup_logger()
        
    # def setRootPath(self, rootPath):
    #     return self.mapFromSource(self.fsm.setRootPath(rootPath))
    
    
    
    def indexForPath(self, pathStr):
        idx =  self.mapFromSource(self.fsm.index(pathStr))
        return idx

    def setRootAndDataSets(self, rootPath, orderedDataSets):
        self.dataSets = orderedDataSets
        
        if self.dir_watcher:
                self.dir_watcher.stop()
            
        #self.dir_watcher = ImgFileEventHandler.SessionDirWatcher(rootPath,self.addIfSDirectory)
        
        idx = self.mapFromSource(self.fsm.setRootPath(rootPath))
        return idx

#    def logDirLoaded(self, path):
#        CCILogger.info(f"Dir {path} loaded")

    def addIfSDirectory(self, path : Path):
        return

    # def filterAcceptsRow(self, source_row, source_parent):
    #     model = self.sourceModel()
    #     index = model.index(source_row, 0, source_parent)

    #     # Only interested in directories
    #     if not model.isDir(index):
    #         return False

    #     dir_path = os.path.abspath(model.filePath(index))

    #     # Always accept the root directory
    #     if dir_path == model.rootPath():
    #         return True

    #     # Only accept directories that are descendants of root_path
    #     if not dir_path.startswith(model.rootPath() + os.sep):
    #         return False
        
    #     if model.rowCount(index) == 0:
    #         return True
        

    #     # If the directory can't be listed (not loaded yet), accept it so it can be expanded
    #     if not os.path.exists(dir_path):
    #         return True

    #     try:
    #         for entry in os.listdir(dir_path):
    #             full_entry = os.path.join(dir_path, entry)
    #             if os.path.isdir(full_entry) and entry.startswith("S_"):
    #                 return True
    #     except Exception:
    #         # If we can't list the directory (permissions, etc.), accept it so the user can try to expand
    #         return True

    #     return False


    def filterAcceptsRow(self, source_row, source_parent):
        index = self.fsm.index(source_row, 0, source_parent)

        # Only interested in directories
        if not self.fsm.isDir(index):
            return False

        # Get the absolute path for the directory
        dir_path = self.fsm.filePath(index)
        if dir_path == self.fsm.rootPath():
            return True
                
        # Reject if not a descendant of root_path
        # (os.path.commonpath returns the shared prefix path)
        if not dir_path.startswith(self.fsm.rootPath() + os.sep):
            return False
        
        if Path(dir_path).name in self.dataSets:
            return True
        
        dirPath = Path(dir_path)
        if dirPath.name.startswith("S_"):
            return True
        
        
        return False
        # try:
        #     # List all entries in the directory
        #     for entry in os.listdir(dir_path):
        #         full_entry = os.path.join(dir_path, entry)
        #         if os.path.isdir(full_entry) and entry.startswith("S_"):
        #             return True  # At least one subdirectory starts with "S_"
        # except PermissionError:
        #     pass  # Ignore directories we can't access

        # return False  # No matching subdirectory found

# class DirItem:
    
#     def __init__(self, dir : Path, parentDirItem, row):
#         self.childDirList = []
#         self.dir = dir
#         self.parent = parentDirItem
#         self.row = row
        
#     def childCount(self):
#         return len(self.childDirList)
    
#     def addChildDir(self, dir : Path):
#         self.childDirList.append(DirItem(dir,self, self.childCount()))
         
#     def child(self, row):
#         return self.childDirList[row]
         
#     def name(self):
#         return self.dir.name
    
#     def parent(self):
#         return self.parent
    
#     def childRow(self, dir):
#         row = -1
#         for i,d in enumerate(self.childDirList):
#             if d.name() == dir.name:
#                 row = i
                    
#         return row
        
#     def row(self):
#         return self.row
    
#     def data(self, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole:
#             d = self.dir.name
#             return d
#         elif role == DIR_PATH_ROLE:
#             d = self.dir
#             return d
#         else:
#             return None

#     def clear(self):
#         for i in self.childDirList:
#             i.clear()
            
#         self.childDirList = []


# class SessionFilesModel(QAbstractTableModel):
#     def __init__(self,  parent=None):
#         super().__init__(parent)
        
#         #self.parentDirList = []
#         self.dir_watcher = None
#         self.root = DirItem(Path(),None,0)
        
#     def startMonitoring(self, projectBasePath, dataDir, orderedDataSets, sessionUID):
        
#         self.clear()
        
#         sessionDirName = "session_" + str(sessionUID)
#         sessionDirPath = Path(projectBasePath) / Path(dataDir) / Path(sessionDirName)
        
#         for ods_dir in sessionDirPath.iterdir():
#             if ods_dir.is_dir() and ods_dir.name in orderedDataSets:
#                 for s_dir in ods_dir.iterdir():
#                     if not s_dir.parent == sessionDirPath:
#                         self.addIfSDirectory(s_dir, s_dir.parent)
#                     else:
#                         self.addIfSDirectory(s_dir)
                        
#         if self.dir_watcher:
#             self.dir_watcher.stop()
            
#         self.dir_watcher = ImgFileEventHandler.SessionDirWatcher(sessionDirPath,self.addIfSDirectory)
        
#     def clear(self):
#         self.beginRemoveRows(QModelIndex(),0,self.rowCount()-1)
#         self.root.clear()
#         self.endRemoveRows()

#     def indexForParentDir(self, dir):
#         row = self.root.childRow(dir)
#         if row == -1:
#             return QModelIndex()
#         return self.index(row,0)

#     def addIfSDirectory(self, dir : Path, parentDir = None):
#         if dir.is_dir() and dir.name.startswith("S_"):
#             pid = QModelIndex()
#             #check it parent dir is valid
#             if parentDir:
#                 pid = self.indexForParentDir(parentDir)
#                 if not pid.isValid():
#                     logger.info(f"adding parent dir: {parentDir.name}")
#                     pid = self.addParentDir(parentDir)
            
#             self.beginInsertRows(pid,self.rowCount(), self.rowCount())
#             if pid.isValid():
#                 pid.internalPointer().addChildDir(dir)
#             else:
#                 self.root.addChildDir(dir)
#             self.endInsertRows()


#     def addParentDir(self, parentDir):
#         self.root
#         self.beginInsertRows(QModelIndex(),self.rowCount(), self.rowCount())
#         self.root.addChildDir(parentDir)
#         self.endInsertRows()
#         return self.index(self.rowCount()-1,0)


#     def index(self, row, column, parent = QModelIndex()):
#         if not self.hasIndex(row, column, parent):
#             return QModelIndex()

#         if not parent.isValid():
#             parent_node = self.root
#         else:
#             parent_node = parent.internalPointer()

#         child_node = parent_node.child(row)
#         if child_node:
#             return self.createIndex(row, column, child_node)
#         else:
#             return QModelIndex()
    
#     def parent(self, index = QModelIndex()):
#         if not index.isValid():
#             return QModelIndex()

#         node = index.internalPointer()
#         parent_node = node.parent()

#         if parent_node is None or parent_node == self.root:
#             return QModelIndex()

#         return self.createIndex(parent_node.row(), 0, parent_node)

#     def columnCount(self, parent=QModelIndex()):
#         return 2

#     def rowCount(self, parent=QModelIndex()):
#         if not parent.isValid():
#             return self.root.childCount()
#         else:
#             return parent.internalPointer().childCount()

#     def data(self, index: QModelIndex, role=Qt.DisplayRole):
        
#         parent = index.parent()
#         if not parent.isValid():
#             child = self.root.child(index.row())
#         else:
#             child = parent.internalPointer().child(index.row())
            
#         return child.data(role)
            
#         #     if role == Qt.DisplayRole:
#         #         return self.root.child(index.row()).data(role)
#         #     else:
#         #         return None
#         # else:
#         #         d = parent.internalPointer().child(index.row()).data(role)
#         #         #d = p.data(index.row, role)
#         #         return d

#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         return "Directory"
     