from pathlib import Path
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtXml import QDomDocument, QDomNode, QDomElement
from typing import Self

# SESSION_TAG_NAME = "BioSemSession"
# NAME_TAG_NAME = "Name"
# UID_TAG_NAME = "UID"
# DATA_FOLDER_TAG_NAME = "DataFolder"
# ORDERED_DATASET_TAG_NAME = "OrderedDataSet"


class CCIAtlasXmlItem:
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
            self.children.append(CCIAtlasXmlItem(child, len(self.children), self))
            child = child.nextSibling()

    def insert_child_node_tree(self, child_node: QDomNode, add_node_to_dom: bool = False):

        if child_node is None:
            return

        if add_node_to_dom:
            self.node.appendChild(child_node)
            
        self.children.append(CCIAtlasXmlItem(child_node, len(self.children), self))
        
        # child = child_node.firstChild()
        # if child.nodeType() == QDomNode.TextNode:  # type: ignore
        #     self.text = child.toText().data()
        #     return

        # while not child.isNull():
        #     self.children.append(CCIAtlasDomItem(child, len(self.children), self))
        #     child = child.nextSibling()

    # def insert_child_item_tree(self, root: Self, add_node_to_dom: bool = False):  # type: ignore # noqa: F821
    #     self.insert_child_node_tree(root.node)

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
    
    def set_node_text(self, val):
        self.text = val
        self.node.setNodeValue(val)
    
    def get_nr_of_children(self) -> int:
        return len(self.children)


class CCIAtlasXmlModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dom_document: QDomDocument = QDomDocument()
        self.root_item: CCIAtlasXmlItem | None = None
        self.root_element: QDomElement = QDomElement()
        self._anchors: dict[str, QPersistentModelIndex] = {}

    def load_from_dom(self, atlas_dom_document: QDomDocument):
        self.dom_document: QDomDocument = atlas_dom_document
        self.root_item = CCIAtlasXmlItem(atlas_dom_document.documentElement(), 0)
        self.root_element = atlas_dom_document.documentElement()
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))

    def parent(self, child: QModelIndex | QPersistentModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        parent_item = child_item.parent

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        return 2

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

    def data(self, index: QModelIndex | QPersistentModelIndex = QModelIndex(), role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        item: CCIAtlasXmlItem = index.internalPointer()

        if index.column() == 0:
            return item.get_node_name()
        elif index.column() == 1:
            return item.get_node_text()

        return None

    def setData(self, index: QModelIndex | QPersistentModelIndex, value, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return None

        item: CCIAtlasXmlItem = index.internalPointer()

        if index.column() == 1:
            item.set_node_text(value)
        
        self.dataChanged.emit(index, index, [value])

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # pyright: ignore[reportIncompatibleMethodOverride]  # noqa: N802
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ["Name", "Value"][section]
        return None

    #####################################################################
    # cool methods below
    #####################################################################
    def get_document(self) -> QDomDocument:
        return self.dom_document

    def find_index_by_name(self, name: str, parent=QModelIndex(), store_anchor: bool = False) -> QModelIndex:
        if name in self._anchors:
            return self.anchor_index(name)

        idx = self.find_index_by_column_data(name, 0, parent)

        if store_anchor and idx.isValid():
            self.set_anchor(name, idx)

        return idx

    def find_index_by_data(self, name: str, parent=QModelIndex()) -> QModelIndex:

        idx = self.find_index_by_column_data(name, 1, parent)
        return idx

    def find_index_by_column_data(self, data: str, column: int, parent=QModelIndex()) -> QModelIndex:

        if column < 0 or column >= self.columnCount(parent):
            return QModelIndex()

        the_index = parent
        if self.rowCount(the_index) == 0:
            return QModelIndex()

        # Start from the very first root index; MatchRecursive walks the whole tree
        start = self.index(0, column, the_index)
        hits = self.match(start, Qt.DisplayRole, data, hits=1,
                        flags=Qt.MatchExactly | Qt.MatchRecursive)

        if hits:
            return hits[0]
        
        return QModelIndex()

    def find_indices_by_name(self, name: str, parent=QModelIndex(), store_anchor: bool = False) -> list[QModelIndex]:
        return self.find_indices_by_column_data(name,0,parent)

    def find_indices_by_column_data(self, data: str, column: int, parent=QModelIndex()) -> list[QModelIndex]:

        hits = []

        if column < 0 or column >= self.columnCount(parent):
            return []

        the_index = parent
        if self.rowCount(the_index) == 0:
            return []

        # Start from the very first root index; MatchRecursive walks the whole tree
        start = self.index(0, column, the_index)
        hits = self.match(start, Qt.DisplayRole, data, hits=-1,
                        flags=Qt.MatchExactly | Qt.MatchRecursive)

        return hits
        


    def data_by_index_and_column(self, index: QModelIndex | QPersistentModelIndex = QModelIndex(), column: int = 0, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        item: CCIAtlasXmlItem = index.internalPointer()

        if column == 0:
            return item.get_node_name()
        elif column == 1:
            return item.get_node_text()

        return None


    def insert_node(self, parent_index: QModelIndex, dom_node: QDomNode) -> bool:
        """Insert an existing QDomNode (with its children) under parent_index at row."""
        parent_item = parent_index.internalPointer()

        # Ensure node belongs to this document
        if dom_node.ownerDocument() != self.dom_document:
            dom_node = self.dom_document.importNode(dom_node, True)  # deep copy, keeps children

        row = parent_item.get_nr_of_children()

        self.beginInsertRows(parent_index, row, row)

        parent_item.insert_child_node_tree(dom_node, True)

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

    def get_node(self, index: QModelIndex | QPersistentModelIndex) -> QDomNode | None:

        if not index.isValid():
            return None

        item: CCIAtlasXmlItem = index.internalPointer()
        return item.node

    def get_item(self, index: QModelIndex | QPersistentModelIndex) -> CCIAtlasXmlItem | None:

        if not index.isValid():
            return None

        item: CCIAtlasXmlItem = index.internalPointer()
        return item
