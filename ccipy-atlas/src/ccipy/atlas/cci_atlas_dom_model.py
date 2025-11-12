from pathlib import Path
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtXml import QDomDocument, QDomNode, QDomElement


SESSION_TAG_NAME = "BioSemSession"
NAME_TAG_NAME = "Name"
UID_TAG_NAME = "UID"
DATA_FOLDER_TAG_NAME = "DataFolder"
ORDERED_DATASET_TAG_NAME = "OrderedDataSet"


class CCIAtlasDomItem:
    """Wrapper for QDomNode that tracks parent/child relationships"""
    def __init__(self, node: QDomNode, row: int = -10, parent=None):
        self.node: QDomNode = node
        self.parent = parent
        self.row_number = row
        self.children = []
        self.text = ""
        
        if node is None:
            return
        # Preload children
        child = node.firstChild()
        if child.nodeType() == QDomNode.TextNode:
            self.text = child.toText().data()
            return

        while not child.isNull():
            self.children.append(CCIAtlasDomItem(child, len(self.children), self))
            child = child.nextSibling()

    def child(self, row: int):
        if row < 0 or row >= len(self.children):
            return None
        return self.children[row]

    def row(self):
        return self.row_number

    def get_node_name(self) -> str:
        return self.node.nodeName()
    
    def get_node_text(self) -> str:
        return self.text


class CCIAtlasDomModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dom_document: QDomDocument = QDomDocument()
        self.root_item: CCIAtlasDomItem | None = None
        self.root_element: QDomElement = QDomElement()
        self.base_folder: Path = Path()

    def load_from_dom(self, atlas_dom_document: QDomDocument, base_folder: str):
        self.dom_document: QDomDocument = atlas_dom_document
        self.root_item = CCIAtlasDomItem(atlas_dom_document.documentElement(), 0)
        self.root_element = atlas_dom_document.documentElement()
        self.base_folder = Path(base_folder)
        self.dataChanged.emit(self.index(0,0), self.index(self.rowCount()-1, self.columnCount()-1))
        
    def parent(self, child: QModelIndex | QPersistentModelIndex = QModelIndex()) -> QModelIndex: # pyright: ignore[reportIncompatibleMethodOverride]
        if not child.isValid():
            return QModelIndex()
        
        child_item = child.internalPointer()
        parent_item = child_item.parent
        
        if parent_item == self.root_item or not parent_item:
            return QModelIndex()
            
        return self.createIndex(parent_item.row(), 0, parent_item)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        return 2  # Name, Attributes, Value

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        if not parent_item:
            return 0
        
        return len(parent_item.children)

    def index(self, row: int, column: int, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        parent_item = self.root_item if not parent.isValid() else parent.internalPointer()
        if not parent_item:
            return QModelIndex()
        
        child_item = parent_item.child(row)
        
        if child_item:
            return self.createIndex(row, column, child_item)
        
        return QModelIndex()

    def data(self, index: QModelIndex | QPersistentModelIndex = QModelIndex(), role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole): # pyright: ignore[reportIncompatibleMethodOverride]
        
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        
        item: CCIAtlasDomItem = index.internalPointer()
        
        
        if index.column() == 0:
            return item.get_node_name()
        elif index.column() == 1:
            #     if node.isElement():
            #         attrs = node.toElement().attributes()
            #         return ' '.join([f'{attrs.item(i).nodeName()}="{attrs.item(i).nodeValue()}"' 
            #                        for i in range(attrs.count())])
            #        elif index.column() == 2:
            return item.get_node_text()
        
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole): # pyright: ignore[reportIncompatibleMethodOverride]
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ["Name", "Value"][section]
        return None
    
    #####################################################################
    # cool methods below
    #####################################################################

    #def getSessionByName()

    def get_base_folder(self):
        return self.base_folder

    def get_data_dir(self):
        #error handling?
        dds = self.root_element.elementsByTagName(DATA_FOLDER_TAG_NAME)
        dd = dds.at(0)
        dde = dd.toElement()
        return dde.text()

    def get_sessions(self):
        session_names = []
        session_nodes = self.root_element.elementsByTagName(SESSION_TAG_NAME)
        for sn in range(session_nodes.length()):
            name = session_nodes.at(sn).firstChildElement(NAME_TAG_NAME)
            uid = session_nodes.at(sn).firstChildElement(UID_TAG_NAME)
            session_string = name.text()
            session_uid = uid.text()
            
            session_names.append((session_string, session_uid))
            
        return session_names
    
    def get_ordered_data_sets_for_session(self, session_uid):
        ods = []
        session_nodes = self.root_element.elementsByTagName(SESSION_TAG_NAME)
        for sn in range(session_nodes.length()):
            session = session_nodes.at(sn)
            uid = session.firstChildElement(UID_TAG_NAME)
            if not uid.text() == session_uid:
                continue
            session_elem = session.toElement()
            ods_nodes = session_elem.elementsByTagName(ORDERED_DATASET_TAG_NAME)
            for od in range(ods_nodes.length()):
                od_name = ods_nodes.at(od).firstChildElement(NAME_TAG_NAME)
                ods.append(od_name.text())
                
        return ods