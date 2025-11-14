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
        self._anchors: dict[str, QPersistentModelIndex] = {}

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
    def get_document(self) -> QDomDocument:
        return self.dom_document

    def add_atlas_region(self, node: QDomNode)-> bool:
        atlas_index = self.find_index_by_name("RegionSet", store_anchor=True)
        if not atlas_index.isValid():
            return False
        
        return self.insert_node(atlas_index, node)
    
    def get_region_set_index(self):
        return self.find_index_by_name("RegionSet", store_anchor=True)

    def find_index_by_name(self, name: str, store_anchor: bool = False, column=0) -> QModelIndex:
        if self.rowCount(QModelIndex()) == 0:
            return QModelIndex()
        
        if name in self._anchors:
            return self.anchor_index(name)

        # Start from the very first root index; MatchRecursive walks the whole tree
        start = self.index(0, column, QModelIndex())
        hits = self.match(start, Qt.DisplayRole, name, hits=1,
                        flags=Qt.MatchExactly | Qt.MatchRecursive)
        if store_anchor and hits:
            self.set_anchor(name, hits[0])
        return hits[0] if hits else QModelIndex()

    def node_from_index(self, index: QModelIndex) -> QDomNode:
        """Get the QDomNode for a given QModelIndex."""
        if not index.isValid():
            return self.dom_document.documentElement()
        
        item: CCIAtlasDomItem = index.internalPointer()
        return item.node

    def insert_node(self, parent_index: QModelIndex, dom_node: QDomNode) -> bool:
        """Insert an existing QDomNode (with its children) under parent_index at row."""
        parent_node = self.node_from_index(parent_index)

        # Ensure node belongs to this document
        if dom_node.ownerDocument() != self.dom_document:
            dom_node = self.dom_document.importNode(dom_node, True)  # deep copy, keeps children

        row = parent_node.childNodes().length()

        self.beginInsertRows(parent_index, row, row)

        parent_node.appendChild(dom_node)

        self.endInsertRows()
        return True

    def set_anchor(self, name: str, index: QModelIndex) -> None:
        """
        Store a persistent index under the given name.
        If index is invalid, remove the anchor for that name.
        """
        if not index.isValid():
            # Treat setting an invalid index as "remove this anchor"
            self._anchors.pop(name, None)
            return

        self._anchors[name] = QPersistentModelIndex(index)

    def anchor_index(self, name: str) -> QModelIndex:
        """
        Return the (normal) QModelIndex for a stored anchor name,
        or an invalid QModelIndex if not found / no longer valid.
        """
        pidx = self._anchors.get(name)
        if pidx is None or not pidx.isValid():
            # Clean up dead anchor if needed
            self._anchors.pop(name, None)
            return QModelIndex()

        # In PySide/PyQt, QPersistentModelIndex is usually usable directly
        # as a QModelIndex, but returning it as QModelIndex is explicit:
        return QModelIndex(pidx)

    def remove_anchor(self, name: str) -> None:
        self._anchors.pop(name, None)


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