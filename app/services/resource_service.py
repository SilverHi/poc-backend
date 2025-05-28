import os
import uuid
import logging
import aiofiles
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.utils.file_parser import FileParser
from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class ResourceService:
    """Resource service for handling resource CRUD operations and file uploads"""
    
    def __init__(self):
        self.file_parser = FileParser()
    
    async def upload_file(self, db: Session, file: UploadFile, title: str, description: str = None) -> Resource:
        """Upload file and create resource with improved error handling"""
        logger.info(f"Starting file upload: {file.filename}, size: {file.size} bytes")
        
        # Validate file
        if not file.filename:
            raise ValueError("File name is required")
        
        if file.size is None or file.size == 0:
            raise ValueError("File appears to be empty")
        
        if file.size > settings.max_file_size:
            raise ValueError(
                f"File size ({file.size} bytes) exceeds maximum limit "
                f"({settings.max_file_size} bytes = {settings.max_file_size // (1024*1024)}MB)"
            )
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.pdf', '.md', '.markdown', '.txt', '.text']
        if file_extension not in allowed_extensions:
            raise ValueError(
                f"Unsupported file type '{file_extension}'. "
                f"Supported types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique ID and file path
        resource_id = str(uuid.uuid4())
        safe_filename = f"{resource_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Read file content
        try:
            file_content = await file.read()
            logger.debug(f"Successfully read file content: {len(file_content)} bytes")
        except Exception as e:
            logger.error(f"Failed to read file content: {e}")
            raise ValueError(f"Failed to read file: {str(e)}")
        
        # Validate file content
        if not file_content:
            raise ValueError("File content is empty")
        
        # Parse file content
        try:
            file_type, parsed_content = self.file_parser.parse_file(file.filename, file_content)
            logger.info(f"Successfully parsed file, extracted {len(parsed_content)} characters")
        except ValueError as e:
            logger.error(f"File parsing failed for {file.filename}: {e}")
            # Re-raise with more context
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error during file parsing: {e}")
            raise ValueError(f"Unexpected error during file parsing: {str(e)}")
        
        # Save file to disk
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            logger.debug(f"File saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file to disk: {e}")
            raise ValueError(f"Failed to save file: {str(e)}")
        
        # Create database record
        try:
            resource_data = ResourceCreate(
                title=title,
                description=description,
                file_name=file.filename,
                file_size=file.size,
                file_type=file_type,
                file_path=file_path,
                parsed_content=parsed_content
            )
            
            resource = self.create_resource(db, resource_id, resource_data)
            logger.info(f"Successfully created resource with ID: {resource_id}")
            return resource
            
        except Exception as e:
            # Clean up file if database operation fails
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up file after database error: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up file after error: {cleanup_error}")
            
            logger.error(f"Failed to create database record: {e}")
            raise ValueError(f"Failed to save resource to database: {str(e)}")
    
    def create_resource(self, db: Session, resource_id: str, resource_data: ResourceCreate) -> Resource:
        """Create new Resource"""
        try:
            db_resource = Resource(
                id=resource_id,
                title=resource_data.title,
                description=resource_data.description,
                file_name=resource_data.file_name,
                file_size=resource_data.file_size,
                file_type=resource_data.file_type,
                file_path=resource_data.file_path,
                parsed_content=resource_data.parsed_content
            )
            
            db.add(db_resource)
            db.commit()
            db.refresh(db_resource)
            return db_resource
        except Exception as e:
            db.rollback()
            logger.error(f"Database error creating resource: {e}")
            raise
    
    def get_resource(self, db: Session, resource_id: str) -> Optional[Resource]:
        """Get Resource by ID"""
        try:
            return db.query(Resource).filter(Resource.id == resource_id).first()
        except Exception as e:
            logger.error(f"Database error getting resource {resource_id}: {e}")
            raise
    
    def get_resources(self, db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
        """Get Resource list"""
        try:
            return db.query(Resource).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Database error getting resources: {e}")
            raise
    
    def update_resource(self, db: Session, resource_id: str, resource_data: ResourceUpdate) -> Optional[Resource]:
        """Update Resource"""
        try:
            db_resource = self.get_resource(db, resource_id)
            if not db_resource:
                return None
            
            # Update fields
            update_data = resource_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_resource, field, value)
            
            db.commit()
            db.refresh(db_resource)
            return db_resource
        except Exception as e:
            db.rollback()
            logger.error(f"Database error updating resource {resource_id}: {e}")
            raise
    
    def delete_resource(self, db: Session, resource_id: str) -> bool:
        """Delete Resource"""
        try:
            db_resource = self.get_resource(db, resource_id)
            if not db_resource:
                return False
            
            # Delete file
            try:
                if os.path.exists(db_resource.file_path):
                    os.remove(db_resource.file_path)
                    logger.debug(f"Deleted file: {db_resource.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {db_resource.file_path}: {e}")
            
            # Delete database record
            db.delete(db_resource)
            db.commit()
            logger.info(f"Successfully deleted resource: {resource_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Database error deleting resource {resource_id}: {e}")
            raise
    
    def search_resources(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Resource]:
        """Search resources"""
        try:
            return db.query(Resource).filter(
                Resource.title.contains(query) |
                Resource.description.contains(query) |
                Resource.parsed_content.contains(query)
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Database error searching resources: {e}")
            raise 