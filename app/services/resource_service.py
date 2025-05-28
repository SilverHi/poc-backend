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
    """Resource服务，处理资源的CRUD操作和文件上传"""
    
    def __init__(self):
        self.file_parser = FileParser()
    
    async def upload_file(self, db: Session, file: UploadFile, title: str, description: str = None) -> Resource:
        """上传文件并创建资源"""
        # 检查文件大小
        if file.size > settings.max_file_size:
            raise ValueError(f"文件大小超过限制 ({settings.max_file_size} bytes)")
        
        # 生成唯一ID和文件路径
        resource_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{resource_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # 读取文件内容
        file_content = await file.read()
        
        # 解析文件内容
        try:
            file_type, parsed_content = self.file_parser.parse_file(file.filename, file_content)
        except ValueError as e:
            raise ValueError(f"文件解析失败: {str(e)}")
        
        # 保存文件到磁盘
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # 创建数据库记录
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
        """创建新的Resource"""
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
        """根据ID获取Resource"""
        return db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_resources(self, db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
        """获取Resource列表"""
        return db.query(Resource).offset(skip).limit(limit).all()
    
    def update_resource(self, db: Session, resource_id: str, resource_data: ResourceUpdate) -> Optional[Resource]:
        """更新Resource"""
        db_resource = self.get_resource(db, resource_id)
        if not db_resource:
            return None
        
        # 更新字段
        update_data = resource_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_resource, field, value)
        
        db.commit()
        db.refresh(db_resource)
        return db_resource
    
    def delete_resource(self, db: Session, resource_id: str) -> bool:
        """删除Resource"""
        db_resource = self.get_resource(db, resource_id)
        if not db_resource:
            return False
        
        # 删除文件
        try:
            if os.path.exists(db_resource.file_path):
                os.remove(db_resource.file_path)
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        # 删除数据库记录
        db.delete(db_resource)
        db.commit()
        return True
    
    def search_resources(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Resource]:
        """搜索资源"""
        return db.query(Resource).filter(
            Resource.title.contains(query) |
            Resource.description.contains(query) |
            Resource.parsed_content.contains(query)
        ).offset(skip).limit(limit).all() 