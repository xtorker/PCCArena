import ast
import logging
from pathlib import Path
from typing import Union

import yaml

logger = logging.getLogger(__name__)

def get_logging_config(cfg_file: Union[str, Path]) -> dict:
    """Get the loggging config dictionary from file.

    Parameters
    ----------
    cfg_file : `Union[str, Path]`
        The logging config file.

    Returns
    -------
    `dict`
        The dictionary for the input of dictConfig()
    """
    with open(cfg_file, 'r') as f:
        ret = f.read()
        logging_config = ast.literal_eval(ret)
    
    return logging_config

def load_cfg(cfg_file: Union[str, Path]) -> dict:
    """Load the PCC algs config file in YAML format with custom tag 
    !join.

    Parameters
    ----------
    cfg_file : `Union[str, Path]`
        The YAML config file.

    Returns
    -------
    `dict`
        A dictionary object loaded from the YAML config file.
    """
    # [ref.] https://stackoverflow.com/a/23212524
    ## define custom tag handler
    def join(loader, node):
        seq = loader.construct_sequence(node)
        return ''.join([str(i) for i in seq])

    ## register the tag handler
    yaml.add_constructor('!join', join)
    
    with open(cfg_file, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    
    return cfg

def glob_file(
        src_dir: Union[str, Path],
        pattern: str,
        fullpath: bool = False,
        verbose: bool = False
    ) -> list[Path]:
    """Recursively glob the files in ``src_dir`` with input ``pattern``.

    Parameters
    ----------
    src_dir : `Union[str, Path]`
        The root directory to glob the files.
    pattern : `str`
        The pattern to glob the files.
    fullpath : `bool`, optional
        True for full path of files, False for filename only, 
        by default False
    verbose : `bool`, optional
        True to log message, False otherwise, by default False

    Returns
    -------
    `list[Path]`
        Files that match the glob pattern.

    Raises
    ------
    `ValueError`
        No any file match pattern in `src_dir`.
    """
    if fullpath is True:
        files = list(p.resolve(True) for p in Path(src_dir).rglob(pattern))
    else:
        files = list(
            p.relative_to(src_dir) for p in Path(src_dir).rglob(pattern)
        )
    
    if len(files) <= 0:
        logger.error(
            f"Not found any files "
            f"with pattern: {pattern} in {Path(src_dir).resolve(True)}")
        raise ValueError
    
    if verbose is True:
        logger.info(
            f"Found {len(files)} files "
            f"with pattern: {pattern} in {Path(src_dir).resolve(True)}")

    return files