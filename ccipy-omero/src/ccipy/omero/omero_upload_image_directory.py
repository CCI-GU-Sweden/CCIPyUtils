from pathlib import Path
import platform
import locale
import hashlib
import omero.model
import omero.grid
from omero.callbacks import CmdCallbackI
from omero_version import omero_version
from omero.model.enums import ChecksumAlgorithmSHA1160
from omero.rtypes import rstring, rbool
from ccipy.omero.cci_omero_progress_call_back import ProgressCallback
from ccipy.omero.exceptions.exceptions import OmeroConnectionError, AssertImportError, ImportError
from ccipy.omero.cci_omero_connection import OmeroConnection
from ccipy.omero.omero_getter_ctx import OmeroGetterCtx
from ccipy.utils.cci_logger import CCILogger


def create_fileset_from_directory(image_directory: Path) -> list[omero.model.FilesetI]: # type: ignore
    """Create a new Fileset from local files."""
    file_path_list = [f for f in image_directory.iterdir() if f.is_file()]
    return create_filset_from_file_list(file_path_list)


def create_filesets_from_directory(image_directory: Path) -> list[omero.model.FilesetI]: # type: ignore
    """Create a new Fileset from local files."""
    file_path_list = [f for f in image_directory.iterdir() if f.is_file()]
    return create_filsets_from_file(file_path_list)


def create_settings(datasset_id: int, description: str, annotations: list[omero.model.Annotation]) -> omero.grid.ImportSettings: # type: ignore
    """Create ImportSettings and set some values."""
    settings = omero.grid.ImportSettings() # type: ignore
    settings.doThumbnails = rbool(True)
    settings.noStatsInfo = rbool(False)

    dataset = omero.model.DatasetI(datasset_id, False) # type: ignore
    settings.userSpecifiedTarget = dataset

    settings.userSpecifiedName = None  # For images, this is the name if the image
    settings.userSpecifiedDescription = rstring(description)
    
    settings.userSpecifiedAnnotationList = annotations
    settings.userSpecifiedPixels = None
    settings.checksumAlgorithm = omero.model.ChecksumAlgorithmI() # type: ignore
    s = rstring(ChecksumAlgorithmSHA1160)
    settings.checksumAlgorithm.value = s

    return settings


def create_filset_from_file_list(file_path_list: list[Path]) -> omero.model.FilesetI:  # type: ignore
    
    system, node, release, version, machine, processor = platform.uname()
    client_version_info = [
        omero.model.NamedValue('omero.version', omero_version),  # type: ignore
        omero.model.NamedValue('os.name', system),  # type: ignore
        omero.model.NamedValue('os.version', release),  # type: ignore
        omero.model.NamedValue('os.architecture', machine)  # type: ignore
        ]
    try:
        client_version_info.append(
            omero.model.NamedValue('locale', locale.getdefaultlocale()[0]))  # type: ignore
    except Exception:  # pragma: no cover
        pass

    fileset = omero.model.FilesetI()  # type: ignore
    for f in file_path_list:
        entry = omero.model.FilesetEntryI()  # type: ignore
        entry.setClientPath(rstring(f))
        fileset.addFilesetEntry(entry)

    upload = omero.model.UploadJobI()  # type: ignore
    upload.setVersionInfo(client_version_info)
    fileset.linkJob(upload)
    return fileset


def create_filsets_from_file(file_path_list: list[Path]) -> list[omero.model.FilesetI]: # type: ignore
    filesets = []
    
    system, node, release, version, machine, processor = platform.uname()
    client_version_info = [
        omero.model.NamedValue('omero.version', omero_version), # type: ignore
        omero.model.NamedValue('os.name', system), # type: ignore
        omero.model.NamedValue('os.version', release), # type: ignore
        omero.model.NamedValue('os.architecture', machine) # type: ignore
        ]
    try:
        client_version_info.append(
            omero.model.NamedValue('locale', locale.getdefaultlocale()[0])) #type: ignore
    except Exception:  # pragma: no cover
        pass

    for f in file_path_list:
        fileset = omero.model.FilesetI() # type: ignore
        entry = omero.model.FilesetEntryI() # type: ignore
        entry.setClientPath(rstring(f))
        fileset.addFilesetEntry(entry)
        upload = omero.model.UploadJobI() #type: ignore
        upload.setVersionInfo(client_version_info)
        fileset.linkJob(upload)
        filesets.append(fileset)
        
    return filesets


# def get_managed_repo(omero_connection: OmeroConnection) -> omero.grid.ManagedRepositoryPrx:  # type: ignore
#     """Get the managed repository proxy from the OMERO connection."""

#     try:
#         session = omero_connection.conn.c.getSession()  # Access the underlying client session
#         if not session:
#             raise OmeroConnectionError("No session available in the client connection.")
#     except Exception as e:
#         raise OmeroConnectionError(f"Failed to get session from OMERO connection: {str(e)}")

#     shared_resources = session.sharedResources()

#     repos = shared_resources.repositories()
#     repo_map = list(zip(repos.proxies, repos.descriptions))
#     prx = None
#     for (prx, _) in repo_map:
#         if not prx:
#             continue
#         prx = omero.grid.ManagedRepositoryPrx.checkedCast(prx)  # type: ignore
#         if prx is not None:
#             break
        
#     return prx


def upload_fileset_and_calculate_hash(proc, fileset: omero.model.FilesetI, show_log: bool = False, progress_callback: ProgressCallback = None) -> list[str]:
    """Upload files to OMERO from local filesystem.
    Returns the SHA1 hash of the file for verification.
    """
    hashes = []
    # tot_size: int = 5000000#fileset.getTotalSize().getValue()
    # tot_read: int = 0
    # tot_percentage: int = -1
    # if fileset.sizeOfUsedFiles() > 1:
    #     raise ImportError("Uploading multiple files in a single fileset is not supported in this function. Create separate filesets for each file.")

    entry = fileset.getFilesetEntry(0)
    fobj = entry.getClientPath().val
    digest = hashlib.sha1() 
    rfs = proc.getUploader(0)
    try:
        with open(fobj, 'rb') as f:
            offset = 0
            while (block := f.read(1_000_000)):
                
                rfs.write(block, offset, len(block))
                digest.update(block)
                
                # read_size = len(block)
                # tot_read += read_size
                offset += len(block)
                # if show_log:
                #     CCILogger.debug(f"Uploaded {read_size} bytes from {fobj}, total uploaded: {tot_read} bytes.")
                # if progress_callback:
                #     prog_percentage = int((tot_read / tot_size) * 100)
                #     if prog_percentage > tot_percentage:
                #         tot_percentage = prog_percentage
                #         progress_callback(tot_percentage)
                        
    except FileNotFoundError as fnf:
        error_msg = f"File not found during upload: {fnf.filename}"
        CCILogger.error(error_msg)
        raise OmeroConnectionError(error_msg)
    finally:
        hashes.append(digest.hexdigest())
        rfs.close()  # Ensure cleanup even if errors occur
    
    return hashes



def assert_import(omero_connection: OmeroConnection, proc, hashes, index):
    """Wait and check that we imported an image correctly."""
    handle = proc.verifyUpload(hashes)
    cb = CmdCallbackI(omero_connection.conn.c, handle)
    while not cb.block(2000):
        CCILogger.info(f"Waiting for import to finish for id: {index}...")
    rsp = cb.getResponse()
    if isinstance(rsp, omero.cmd.ERR): # type: ignore
        raise AssertImportError(message=str(rsp))
    cb.close(handle)
    return rsp

def upload_image_directory(omero_connection: OmeroConnection, directory_path: Path, project_name: str, dataset_name: str, description: str, annotations: list[omero.model.Annotation]):
    
    with OmeroGetterCtx(omero_connection) as getter:
        proj_id = getter.get_or_create_project(project_name, omero_connection.get_user_id())
        dataset_id = getter.get_or_create_dataset(proj_id, dataset_name)

    file_sets = create_filesets_from_directory(directory_path)
    settings = create_settings(dataset_id, description, annotations)

    managed_repo = get_managed_repo(omero_connection)

    for fileset in file_sets:
        proc = managed_repo.importFileset(fileset, settings)
        hashes = upload_fileset_and_calculate_hash(proc, fileset)
        assert_import(omero_connection, proc, hashes)
