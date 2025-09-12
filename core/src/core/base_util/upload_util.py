"""
File upload utilities for test artifacts and reports.
"""

import os
import boto3
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .logger import get_logger
from .exception_handler import TestConfigError

logger = get_logger(__name__)


class UploadUtil:
    """Utility class for uploading files to various storage services."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def upload_to_s3(self, 
                     local_file_path: str,
                     s3_bucket: str,
                     s3_key: str,
                     aws_access_key_id: Optional[str] = None,
                     aws_secret_access_key: Optional[str] = None,
                     region_name: str = 'us-east-1') -> str:
        """
        Upload file to AWS S3.
        
        Args:
            local_file_path: Path to local file
            s3_bucket: S3 bucket name
            s3_key: S3 object key (path in bucket)
            aws_access_key_id: AWS access key (optional, can use env vars)
            aws_secret_access_key: AWS secret key (optional, can use env vars)
            region_name: AWS region
            
        Returns:
            S3 URL of uploaded file
        """
        try:
            # Use provided credentials or fall back to environment/IAM
            session_kwargs = {}
            if aws_access_key_id and aws_secret_access_key:
                session_kwargs = {
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                }
            
            s3_client = boto3.client('s3', region_name=region_name, **session_kwargs)
            
            # Upload file
            s3_client.upload_file(local_file_path, s3_bucket, s3_key)
            
            # Generate URL
            s3_url = f"https://{s3_bucket}.s3.{region_name}.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded {local_file_path} to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            error_msg = f"Failed to upload {local_file_path} to S3: {str(e)}"
            logger.error(error_msg)
            raise TestConfigError(error_msg)
    
    def upload_directory_to_s3(self,
                              local_dir_path: str,
                              s3_bucket: str,
                              s3_prefix: str = "",
                              **s3_kwargs) -> Dict[str, str]:
        """
        Upload entire directory to S3.
        
        Args:
            local_dir_path: Path to local directory
            s3_bucket: S3 bucket name
            s3_prefix: Prefix for S3 keys
            **s3_kwargs: Additional arguments for S3 upload
            
        Returns:
            Dictionary mapping local paths to S3 URLs
        """
        local_path = Path(local_dir_path)
        if not local_path.is_dir():
            raise TestConfigError(f"Directory not found: {local_dir_path}")
        
        uploaded_files = {}
        
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                # Calculate relative path and S3 key
                relative_path = file_path.relative_to(local_path)
                s3_key = f"{s3_prefix}/{relative_path}".replace("\\", "/").lstrip("/")
                
                # Upload file
                s3_url = self.upload_to_s3(
                    str(file_path),
                    s3_bucket,
                    s3_key,
                    **s3_kwargs
                )
                uploaded_files[str(file_path)] = s3_url
        
        logger.info(f"Uploaded {len(uploaded_files)} files from {local_dir_path} to S3")
        return uploaded_files
    
    def upload_test_report(self,
                          report_path: str,
                          storage_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Upload test report to configured storage.
        
        Args:
            report_path: Path to test report
            storage_config: Storage configuration
            
        Returns:
            URL of uploaded report or None if upload disabled
        """
        config = storage_config or self.config.get('upload', {})
        
        if not config.get('enabled', False):
            logger.info("File upload is disabled")
            return None
        
        storage_type = config.get('type', 's3').lower()
        
        if storage_type == 's3':
            return self._upload_report_to_s3(report_path, config)
        else:
            logger.warning(f"Unsupported storage type: {storage_type}")
            return None
    
    def _upload_report_to_s3(self, report_path: str, config: Dict[str, Any]) -> str:
        """Upload report to S3 using configuration."""
        s3_config = config.get('s3', {})
        
        bucket = s3_config.get('bucket')
        if not bucket:
            raise TestConfigError("S3 bucket not configured for upload")
        
        # Generate S3 key with timestamp
        report_name = Path(report_path).name
        timestamp = Path(report_path).stat().st_mtime
        s3_key = f"{s3_config.get('prefix', 'test-reports')}/{timestamp}_{report_name}"
        
        return self.upload_to_s3(
            report_path,
            bucket,
            s3_key,
            aws_access_key_id=s3_config.get('access_key_id'),
            aws_secret_access_key=s3_config.get('secret_access_key'),
            region_name=s3_config.get('region', 'us-east-1')
        )