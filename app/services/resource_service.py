import os
import uuid
import aiofiles
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.utils.file_parser import FileParser
from config import settings


class ResourceService:
    """Resource service for handling resource CRUD operations and file uploads"""
    
    def __init__(self):
        self.file_parser = FileParser()
    
    async def upload_file(self, db: Session, file: UploadFile, title: str, description: str = None) -> Resource:
        """Upload file and create resource"""
        # Check file size
        if file.size > settings.max_file_size:
            raise ValueError(f"File size exceeds limit ({settings.max_file_size} bytes)")
        
        # Generate unique ID and file path
        resource_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{resource_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # Read file content
        file_content = await file.read()
        
        # Parse file content
        try:
            file_type, parsed_content = self.file_parser.parse_file(file.filename, file_content)
        except ValueError as e:
            raise ValueError(f"File parsing failed: {str(e)}")
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Create database record
        resource_data = ResourceCreate(
            title=title,
            description=description,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_type,
            file_path=file_path,
            parsed_content=parsed_content
        )
        
        return self.create_resource(db, resource_id, resource_data)
    
    def create_resource(self, db: Session, resource_id: str, resource_data: ResourceCreate) -> Resource:
        """Create new Resource"""
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
    
    def get_resource(self, db: Session, resource_id: str) -> Optional[Resource]:
        """Get Resource by ID"""
        return db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_resources(self, db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
        """Get Resource list"""
        return db.query(Resource).offset(skip).limit(limit).all()
    
    def update_resource(self, db: Session, resource_id: str, resource_data: ResourceUpdate) -> Optional[Resource]:
        """Update Resource"""
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
    
    def delete_resource(self, db: Session, resource_id: str) -> bool:
        """Delete Resource"""
        db_resource = self.get_resource(db, resource_id)
        if not db_resource:
            return False
        
        # Delete file
        try:
            if os.path.exists(db_resource.file_path):
                os.remove(db_resource.file_path)
        except Exception as e:
            print(f"Failed to delete file: {e}")
        
        # Delete database record
        db.delete(db_resource)
        db.commit()
        return True
    
    def search_resources(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Resource]:
        """Search resources"""
        return db.query(Resource).filter(
            Resource.title.contains(query) |
            Resource.description.contains(query) |
            Resource.parsed_content.contains(query)
        ).offset(skip).limit(limit).all() 