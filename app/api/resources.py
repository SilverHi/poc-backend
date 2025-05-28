import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.resource import Resource, ResourceUpdate, ResourceUploadResponse
from app.services.resource_service import ResourceService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
resource_service = ResourceService()


@router.post("/upload", response_model=ResourceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload file and create resource with comprehensive error handling"""
    logger.info(f"Upload request received: file={file.filename}, title={title}")
    
    try:
        # Validate input
        if not title or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required and cannot be empty"
            )
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is required"
            )
        
        resource = await resource_service.upload_file(db, file, title.strip(), description)
        
        logger.info(f"Successfully uploaded file: {file.filename} -> resource ID: {resource.id}")
        return ResourceUploadResponse(
            id=resource.id,
            title=resource.title,
            file_name=resource.file_name,
            file_size=resource.file_size,
            file_type=resource.file_type,
            message="File uploaded and parsed successfully"
        )
        
    except ValueError as e:
        # These are expected validation errors
        logger.warning(f"Upload validation error for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during upload of {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file upload. Please try again or contact support."
        )


@router.get("/", response_model=List[Resource])
def get_resources(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get resource list with optional search"""
    try:
        # Validate parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )
        
        if limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 1000"
            )
        
        if search:
            logger.debug(f"Searching resources with query: {search}")
            return resource_service.search_resources(db, search, skip=skip, limit=limit)
        else:
            logger.debug(f"Getting resources with skip={skip}, limit={limit}")
            return resource_service.get_resources(db, skip=skip, limit=limit)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resources"
        )


@router.get("/{resource_id}", response_model=Resource)
def get_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """Get resource by ID"""
    try:
        if not resource_id or not resource_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource ID is required"
            )
        
        resource = resource_service.get_resource(db, resource_id)
        if not resource:
            logger.warning(f"Resource not found: {resource_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with ID '{resource_id}' not found"
            )
        
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resource"
        )


@router.put("/{resource_id}", response_model=Resource)
def update_resource(
    resource_id: str,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """Update resource"""
    try:
        if not resource_id or not resource_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource ID is required"
            )
        
        resource = resource_service.update_resource(db, resource_id, resource_data)
        if not resource:
            logger.warning(f"Resource not found for update: {resource_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with ID '{resource_id}' not found"
            )
        
        logger.info(f"Successfully updated resource: {resource_id}")
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resource"
        )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """Delete resource"""
    try:
        if not resource_id or not resource_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource ID is required"
            )
        
        success = resource_service.delete_resource(db, resource_id)
        if not success:
            logger.warning(f"Resource not found for deletion: {resource_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with ID '{resource_id}' not found"
            )
        
        logger.info(f"Successfully deleted resource: {resource_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource"
        ) 