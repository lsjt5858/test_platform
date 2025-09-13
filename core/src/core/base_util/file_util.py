"""
File operations and utilities.
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logger import get_logger
from .exception_handler import TestDataError

logger = get_logger(__name__)


class FileUtil:
    """Utility class for file operations."""
    
    @staticmethod
    def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read and parse JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TestDataError(f"Failed to read JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def write_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> None:
        """Write data to JSON file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise TestDataError(f"Failed to write JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def read_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read and parse YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise TestDataError(f"Failed to read YAML file {file_path}: {str(e)}")
    
    @staticmethod
    def write_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """Write data to YAML file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise TestDataError(f"Failed to write YAML file {file_path}: {str(e)}")
    
    @staticmethod
    def read_text(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read text file content."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError as e:
            raise TestDataError(f"File not found: {file_path}")
        except Exception as e:
            raise TestDataError(f"Failed to read text file {file_path}: {str(e)}")
    
    @staticmethod
    def write_text(content: str, file_path: Union[str, Path], encoding: str = 'utf-8') -> None:
        """Write text to file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise TestDataError(f"Failed to write text file {file_path}: {str(e)}")
    
    @staticmethod
    def ensure_directory(dir_path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if not."""
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy file from src to dst."""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            logger.debug(f"Copied file from {src} to {dst}")
        except Exception as e:
            raise TestDataError(f"Failed to copy file from {src} to {dst}: {str(e)}")
    
    @staticmethod
    def copy_directory(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy entire directory."""
        try:
            if Path(dst).exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            logger.debug(f"Copied directory from {src} to {dst}")
        except Exception as e:
            raise TestDataError(f"Failed to copy directory from {src} to {dst}: {str(e)}")
    
    @staticmethod
    def remove_path(path: Union[str, Path]) -> None:
        """Remove file or directory."""
        path = Path(path)
        try:
            if path.is_file():
                path.unlink()
                logger.debug(f"Removed file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.debug(f"Removed directory: {path}")
        except Exception as e:
            raise TestDataError(f"Failed to remove path {path}: {str(e)}")
    
    @staticmethod
    def list_files(directory: Union[str, Path], 
                   pattern: str = "*", 
                   recursive: bool = False) -> List[Path]:
        """List files in directory matching pattern."""
        try:
            dir_path = Path(directory)
            if recursive:
                return list(dir_path.rglob(pattern))
            else:
                return list(dir_path.glob(pattern))
        except Exception as e:
            raise TestDataError(f"Failed to list files in {directory}: {str(e)}")
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except FileNotFoundError:
            raise TestDataError(f"File not found: {file_path}")
        except Exception as e:
            raise TestDataError(f"Failed to get file size for {file_path}: {str(e)}")
    
    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()