from pathlib import Path
from PySide6.QtXml import QDomDocument, QDomNode
from PySide6.QtCore import QModelIndex
from typing import Self, List
from ccipy.atlas.cci_atlas_xml_model import CCIAtlasXmlModel

SESSION_TAG_NAME = "BioSemSession"
NAME_TAG_NAME = "Name"
UID_TAG_NAME = "UID"
DATA_FOLDER_TAG_NAME = "DataFolder"
ORDERED_DATASET_TAG_NAME = "OrderedDataSet"


class CCIAtlasDomModel(CCIAtlasXmlModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_folder: Path = Path()

    def load_from_dom(self, atlas_dom_document: QDomDocument, base_folder: str):  # pyright: ignore[reportIncompatibleMethodOverride]
        super().load_from_dom(atlas_dom_document)
        self.base_folder = Path(base_folder)
        self.data_folder_idx = self.find_index_by_name("DataFolder", store_anchor=True)

    #####################################################################
    # cool methods below
    #####################################################################
    def update_name(self, proj_name: str):
        biosem_idx = self.find_index_by_name("BioSemProject")
        if not biosem_idx.isValid():
            return
         
        proj_name_idx = self.find_index_by_name("Name", parent=biosem_idx)
        xml_file_idx = self.find_index_by_name("XMLFile", parent=biosem_idx)
        #data_folder_idx = self.find_index_by_name("DataFolder", parent=biosem_idx)
        
        if proj_name_idx.isValid():
            self.setData(self.index(proj_name_idx.row(), 1, biosem_idx), proj_name)
        
        if xml_file_idx.isValid():
            self.setData(self.index(xml_file_idx.row(), 1, biosem_idx), proj_name)
        
        if self.data_folder_idx.isValid():
            self.setData(self.index(self.data_folder_idx.row(), 1, biosem_idx), proj_name.split('.')[0] + "_data")
        
    def add_atlas_region(self, node: QDomNode) -> bool:
        atlas_index = self.find_index_by_name("RegionSet", store_anchor=True)
        if not atlas_index.isValid():
            return False

        return self.insert_node(atlas_index, node)

    def get_region_set_index(self):
        return self.find_index_by_name("RegionSet", store_anchor=True)
    
    def get_data_set_index(self):
        return self.find_index_by_name("DataSet", store_anchor=True)
    
    def get_atlas_region_indices(self)-> List[QModelIndex]:
        
        rs_idx = self.get_region_set_index()
        return self.find_indices_by_name("AtlasRegion",rs_idx)
    
    # def getSessionByName()

    def get_base_folder(self) -> Path:
        return self.base_folder

    def get_imported_folder(self) -> Path:
        data_folder_name = self.data_by_index_and_column(self.data_folder_idx, 1)
        return self.base_folder / data_folder_name / "imported"

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
