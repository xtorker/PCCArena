from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def glob_filename(src_dir, pattern):
    '''
    Recursively glob the relative filename to the src_dir with input pattern.

    Parameters:
        src_dir (str or PosixPath): The top directory to glob the files.
        pattern (str or PosixPath): The pattern to glob the files.
    
    Returns:
        list (PosixPath): Files that match the glob pattern.
    '''
    filenames = list(path.relative_to(src_dir) for path in Path(src_dir).rglob(pattern))
    assert len(filenames) > 0
    logger.info(f"Found {len(filenames)} files with pattern: {pattern} in {Path(src_dir).resolve(True)}")

    return filenames

def glob_filepath(src_dir, pattern):
    '''
    Recursively glob the absolute path of files with input pattern.

    Parameters:
        src_dir (str or PosixPath): The top directory to glob the files.
        pattern (str or PosixPath): The pattern to glob the files.
    
    Returns:
        list (PosixPath): Full path of files that match the glob pattern.
    '''
    filepaths = list(path.resolve(True) for path in Path(src_dir).rglob(pattern))
    assert len(filepaths) > 0
    logger.info(f"Found {len(filepaths)} files with pattern: {pattern} in {Path(src_dir).resolve(True)}")

    return filepaths