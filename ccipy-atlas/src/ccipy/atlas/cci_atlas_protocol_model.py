from PySide6.QtXml import QDomDocument, QDomNode
from ccipy.atlas.cci_atlas_xml_model import CCIAtlasXmlModel
from typing import List, Tuple


class CCIAtlasProtocolModel(CCIAtlasXmlModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def load_from_dom(self, atlas_dom_document: QDomDocument):
        return super().load_from_dom(atlas_dom_document)
    
    def get_protocols(self) -> List[Tuple[str, str]] | None:
        """Retrieve a list of protocols from the atlas XML model.
        
        Returns:
            A list of tuples, each containing the protocol name and UID.
            Returns None if no protocols are found.
        """
        protocols: List[Tuple[str, str]] = []
        protocol_index = self.find_index_by_name("Protocols")
        if not protocol_index.isValid():
            return None
        
        row_count = self.rowCount(protocol_index)
        for row in range(row_count):
            protocol_item_index = self.index(row, 0, protocol_index)
            # name_node = self.get_node(inde=protocol_item_index)
            # uid_node = self.get_node(parent=protocol_item_index)
            
            name_index = self.find_index_by_name("Name", parent=protocol_item_index)
            uid_index = self.find_index_by_name("UID", parent=protocol_item_index)
            
            if name_index.isValid() and uid_index.isValid():
                name = self.data(self.index(name_index.row(), 1, protocol_item_index))
                uid = self.data(self.index(uid_index.row(), 1, protocol_item_index))
                if name and uid:
                    protocols.append((name, uid))
        
        return protocols if protocols else None
    
    def get_protocol_node_by_uid(self, uid: str) -> QDomNode | None:
        
        protocol_index = self.find_index_by_name("Protocols")
        if not protocol_index.isValid():
            return None
        
        row_count = self.rowCount(protocol_index)
        for row in range(row_count):
            protocol_item_index = self.index(row, 0, protocol_index)
            #name_index = self.find_index_by_name("Name", parent=protocol_item_index)
            # uid_index = self.find_index_by_name("UID", parent=protocol_item_index)
            uid_value_index = self.find_index_by_data(uid, protocol_item_index)
            
            if uid_value_index.isValid():
                return self.get_node(index=protocol_item_index)
            
        return None
