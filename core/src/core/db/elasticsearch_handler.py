"""
Elasticsearch handler for log analysis and search operations in tests.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ApiError, TransportError, ConnectionError

from .base_db_handler import BaseDBHandler, DatabaseError
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig

logger = get_logger(__name__)


class ElasticsearchHandler(BaseDBHandler):
    """Elasticsearch handler for search and analytics operations."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.client = None
    
    def connect(self) -> None:
        """Establish Elasticsearch connection."""
        try:
            hosts = self.config.get('hosts', ['localhost:9200'])
            
            client_params = {
                'hosts': hosts,
                'timeout': self.config.get('timeout', 30),
                'max_retries': self.config.get('max_retries', 3),
                'retry_on_timeout': self.config.get('retry_on_timeout', True)
            }
            
            # Add authentication if provided
            if self.config.get('username') and self.config.get('password'):
                client_params['http_auth'] = (
                    self.config['username'], 
                    self.config['password']
                )
            
            # SSL configuration
            if self.config.get('use_ssl', False):
                client_params['use_ssl'] = True
                client_params['verify_certs'] = self.config.get('verify_certs', True)
                
                if self.config.get('ca_certs'):
                    client_params['ca_certs'] = self.config['ca_certs']
            
            self.client = Elasticsearch(**client_params)
            
            # Test connection
            if not self.client.ping():
                raise DatabaseError("Elasticsearch cluster is not available")
                
            self._connected = True
            logger.info(f"Connected to Elasticsearch: {hosts}")
            
        except Exception as e:
            error_msg = f"Failed to connect to Elasticsearch: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def disconnect(self) -> None:
        """Close Elasticsearch connection."""
        if self.client:
            try:
                # Elasticsearch client doesn't have explicit close method
                self.client = None
                self._connected = False
                logger.debug("Elasticsearch connection closed")
            except Exception as e:
                logger.warning(f"Error closing Elasticsearch connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Elasticsearch connection is active."""
        if not self.client:
            return False
        
        try:
            return self.client.ping()
        except:
            self._connected = False
            return False
    
    @retry(RetryConfig(max_attempts=3, exceptions=(ApiError, TransportError, ConnectionError)))
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute Elasticsearch query (JSON string or dict)."""
        if not self.is_connected():
            self.connect()
        
        try:
            if isinstance(query, str):
                query_dict = json.loads(query)
            else:
                query_dict = query
            
            index = params.get('index', '_all') if params else '_all'
            
            result = self.client.search(index=index, body=query_dict)
            logger.debug(f"Elasticsearch query executed on index '{index}'")
            return result
            
        except Exception as e:
            error_msg = f"Elasticsearch query execution failed: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, {'query': query, 'params': params})
    
    def index_document(self, 
                      index: str, 
                      document: Dict[str, Any],
                      doc_id: Optional[str] = None,
                      doc_type: str = '_doc') -> Dict[str, Any]:
        """Index a document in Elasticsearch."""
        if not self.is_connected():
            self.connect()
        
        try:
            # Add timestamp if not present
            if '@timestamp' not in document:
                document['@timestamp'] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.index(
                index=index,
                doc_type=doc_type,
                id=doc_id,
                body=document
            )
            
            logger.debug(f"Document indexed in '{index}' with ID: {result.get('_id')}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to index document: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def bulk_index(self, 
                   index: str,
                   documents: List[Dict[str, Any]],
                   doc_type: str = '_doc') -> Dict[str, Any]:
        """Bulk index multiple documents."""
        if not self.is_connected():
            self.connect()
        
        try:
            actions = []
            for doc in documents:
                if '@timestamp' not in doc:
                    doc['@timestamp'] = datetime.now(timezone.utc).isoformat()
                
                action = {
                    '_index': index,
                    '_type': doc_type,
                    '_source': doc
                }
                actions.append(action)
            
            result = self.client.bulk(body=actions)
            
            logger.info(f"Bulk indexed {len(documents)} documents in '{index}'")
            return result
            
        except Exception as e:
            error_msg = f"Failed to bulk index documents: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def search(self, 
               index: str,
               query: Dict[str, Any] = None,
               size: int = 10,
               from_: int = 0,
               sort: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Search documents in index."""
        if not self.is_connected():
            self.connect()
        
        try:
            search_body = {
                'size': size,
                'from': from_
            }
            
            if query:
                search_body['query'] = query
            else:
                search_body['query'] = {'match_all': {}}
            
            if sort:
                search_body['sort'] = sort
            
            result = self.client.search(index=index, body=search_body)
            logger.debug(f"Search completed in '{index}', found {result['hits']['total']['value']} documents")
            return result
            
        except Exception as e:
            error_msg = f"Search failed in index '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def get_document(self, index: str, doc_id: str, doc_type: str = '_doc') -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.client.get(index=index, doc_type=doc_type, id=doc_id)
            return result.get('_source')
            
        except Exception as e:
            if 'not found' in str(e).lower():
                return None
            
            error_msg = f"Failed to get document '{doc_id}' from '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def delete_document(self, index: str, doc_id: str, doc_type: str = '_doc') -> Dict[str, Any]:
        """Delete document by ID."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.client.delete(index=index, doc_type=doc_type, id=doc_id)
            logger.debug(f"Document '{doc_id}' deleted from '{index}'")
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete document '{doc_id}' from '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def create_index(self, 
                     index: str,
                     mapping: Optional[Dict[str, Any]] = None,
                     settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create index with optional mapping and settings."""
        if not self.is_connected():
            self.connect()
        
        try:
            body = {}
            if mapping:
                body['mappings'] = mapping
            if settings:
                body['settings'] = settings
            
            result = self.client.indices.create(index=index, body=body)
            logger.info(f"Index '{index}' created successfully")
            return result
            
        except Exception as e:
            error_msg = f"Failed to create index '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def delete_index(self, index: str) -> Dict[str, Any]:
        """Delete index."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.client.indices.delete(index=index)
            logger.info(f"Index '{index}' deleted successfully")
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete index '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def index_exists(self, index: str) -> bool:
        """Check if index exists."""
        if not self.is_connected():
            self.connect()
        
        try:
            return self.client.indices.exists(index=index)
        except Exception as e:
            error_msg = f"Failed to check if index '{index}' exists: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def get_index_info(self, index: str) -> Dict[str, Any]:
        """Get index information."""
        if not self.is_connected():
            self.connect()
        
        try:
            return self.client.indices.get(index=index)
        except Exception as e:
            error_msg = f"Failed to get info for index '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def refresh_index(self, index: str) -> Dict[str, Any]:
        """Refresh index to make recent changes searchable."""
        if not self.is_connected():
            self.connect()
        
        try:
            result = self.client.indices.refresh(index=index)
            logger.debug(f"Index '{index}' refreshed")
            return result
        except Exception as e:
            error_msg = f"Failed to refresh index '{index}': {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)