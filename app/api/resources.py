from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.resource import Resource, ResourceUpdate, ResourceUploadResponse
from app.services.resource_service import ResourceService

router = APIRouter()
resource_service = ResourceService()


@router.post("/upload", response_model=ResourceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload file and create resource"""
    try:
        resource = await resource_service.upload_file(db, file, title, description)
        return ResourceUploadResponse(
            id=resource.id,
            title=resource.title,
            file_name=resource.file_name,
            file_size=resource.file_size,
            file_type=resource.file_type,
            message="File uploaded successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/", response_model=List[Resource])
def get_resources(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get resource list"""
    if search:
        return resource_service.search_resources(db, search, skip=skip, limit=limit)
    return resource_service.get_resources(db, skip=skip, limit=limit)


@router.get("/{resource_id}", response_model=Resource)
def get_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """Get resource by ID"""
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource


@router.put("/{resource_id}", response_model=Resource)
def update_resource(
    resource_id: str,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """Update resource"""
    resource = resource_service.update_resource(db, resource_id, resource_data)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """Delete resource"""
    success = resource_service.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        ) 