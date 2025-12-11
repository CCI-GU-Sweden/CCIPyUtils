from pathlib import Path
from PySide6.QtXml import QDomDocument, QDomNode
from typing import Self
from ccipy.atlas.cci_atlas_xml_model import CCIAtlasXmlModel

SESSION_TAG_NAME = "BioSemSession"
NAME_TAG_NAME = "Name"
UID_TAG_NAME = "UID"
DATA_FOLDER_TAG_NAME = "DataFolder"
ORDERED_DATASET_TAG_NAME = "OrderedDataSet"


# class CCIAtlasDomItem:
#     """Wrapper for QDomNode that tracks parent/child relationships"""
#     def __init__(self, node: QDomNode, row: int = -10, parent=None):
#         self.node: QDomNode = node
#         self.parent = parent
#         self.row_number = row
#         self.children = []
#         self.text = ""

#         if node is None:
#             return
#         # Preload children
#         child = node.firstChild()
#         if child.nodeType() == QDomNode.TextNode:
#             self.text = child.toText().data()
#             return

#         while not child.isNull():
#             self.children.append(CCIAtlasDomItem(child, len(self.children), self))
#             child = child.nextSibling()

#     def insert_child_node_tree(self, child_node: QDomNode, add_node_to_dom: bool = False):

#         if child_node is None:
#             return

#         if add_node_to_dom:
#             self.node.appendChild(child_node)
            
#         self.children.append(CCIAtlasDomItem(child_node, len(self.children), self))
        
#         # child = child_node.firstChild()
#         # if child.nodeType() == QDomNode.TextNode:  # type: ignore
#         #     self.text = child.toText().data()
#         #     return

#         # while not child.isNull():
#         #     self.children.append(CCIAtlasDomItem(child, len(self.children), self))
#         #     child = child.nextSibling()

#     # def insert_child_item_tree(self, root: Self, add_node_to_dom: bool = False):  # type: ignore # noqa: F821
#     #     self.insert_child_node_tree(root.node)

#     def child(self, row: int):
#         if row < 0 or row >= len(self.children):
#             return None
#         return self.children[row]

#     def row(self):
#         return self.row_number

#     def get_node_name(self) -> str:
#         return self.node.nodeName()

#     def get_node_text(self) -> str:
#         return self.text
    
#     def get_nr_of_children(self) -> int:
#         return len(self.children)


class CCIAtlasDomModel(CCIAtlasXmlModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_folder: Path = Path()

    def load_from_dom(self, atlas_dom_document: QDomDocument, base_folder: str):  # pyright: ignore[reportIncompatibleMethodOverride]
        super().load_from_dom(atlas_dom_document)
        self.base_folder = Path(base_folder)

    #####################################################################
    # cool methods below
    #####################################################################
    def get_document(self) -> QDomDocument:
        return self.dom_document

    def add_atlas_region(self, node: QDomNode) -> bool:
        atlas_index = self.find_index_by_name("RegionSet", store_anchor=True)
        if not atlas_index.isValid():
            return False

        return self.insert_node(atlas_index, node)

    def get_region_set_index(self):
        return self.find_index_by_name("RegionSet", store_anchor=True)

    # def getSessionByName()

    def get_base_folder(self):
        return self.base_folder

    def get_data_dir(self):
        # error handling?
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
    
    def add_protocol(self, protocol_node: QDomNode) -> bool:
        protocols_index = self.find_index_by_name("ProtocolCache", store_anchor=False)
        if not protocols_index.isValid():
            return False

        return self.insert_node(protocols_index, protocol_node)
