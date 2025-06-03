from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    ConversationMessage, 
    ConversationMessageCreate, 
    SaveConversationRequest,
    ConversationSummary,
    Conversation
)

router = APIRouter()
conversation_service = ConversationService()


@router.post("/", response_model=ConversationSummary)
def save_conversation(
    conversation_data: SaveConversationRequest,
    db: Session = Depends(get_db)
):
    """Save a complete conversation"""
    try:
        return conversation_service.save_conversation(db, conversation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save conversation: {str(e)}"
        )


@router.get("/", response_model=List[ConversationSummary])
def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get conversation summaries"""
    try:
        return conversation_service.get_conversations(db, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get complete conversation with all messages"""
    try:
        conversation = conversation_service.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete conversation and all its messages"""
    try:
        if not conversation_service.delete_conversation(db, conversation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.post("/messages", response_model=ConversationMessage)
def create_conversation_message(
    message_data: ConversationMessageCreate,
    db: Session = Depends(get_db)
):
    """Create a single conversation message"""
    try:
        return conversation_service.create_conversation_message(db, message_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )


@router.post("/messages/batch", response_model=List[ConversationMessage])
def create_conversation_messages_batch(
    messages_data: List[ConversationMessageCreate],
    db: Session = Depends(get_db)
):
    """Create multiple conversation messages in batch"""
    try:
        return conversation_service.create_conversation_messages_batch(db, messages_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create messages: {str(e)}"
        )


@router.get("/messages/{conversation_id}", response_model=List[ConversationMessage])
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get all messages for a conversation"""
    try:
        return conversation_service.get_conversation_messages(db, conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        ) 