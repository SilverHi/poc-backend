from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    Conversation, ConversationCreate, ConversationUpdate, ConversationSummary,
    SaveConversationRequest
)

router = APIRouter()


@router.post("/", response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    return ConversationService.create_conversation(db, conversation)


@router.get("/", response_model=List[ConversationSummary])
def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all conversations with summary info"""
    return ConversationService.get_conversations(db, skip=skip, limit=limit)


@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation


@router.put("/{conversation_id}", response_model=Conversation)
def update_conversation(
    conversation_id: str,
    conversation: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update a conversation"""
    updated_conversation = ConversationService.update_conversation(
        db, conversation_id, conversation
    )
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return updated_conversation


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    success = ConversationService.delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"message": "Conversation deleted successfully"}


@router.post("/save", response_model=Conversation)
def save_conversation(
    request: SaveConversationRequest,
    db: Session = Depends(get_db)
):
    """Save a conversation from frontend conversation nodes"""
    return ConversationService.save_conversation_from_nodes(db, request)


@router.get("/{conversation_id}/nodes")
def get_conversation_nodes(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation as frontend-compatible nodes"""
    nodes = ConversationService.get_conversation_nodes(db, conversation_id)
    if not nodes:
        # Check if conversation exists
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    return {"nodes": nodes} 