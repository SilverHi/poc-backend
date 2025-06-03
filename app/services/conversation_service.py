import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.conversation import ConversationSummary, ConversationMessage
from app.schemas.conversation import (
    ConversationMessageCreate, 
    SaveConversationRequest,
    ConversationSummary as ConversationSummarySchema,
    Conversation as ConversationSchema
)


class ConversationService:
    """Conversation service for handling conversation CRUD operations"""
    
    def create_conversation_message(self, db: Session, message_data: ConversationMessageCreate) -> ConversationMessage:
        """Create new ConversationMessage"""
        message_id = str(uuid.uuid4())
        
        db_message = ConversationMessage(
            id=message_id,
            conversation_id=message_data.conversation_id,
            node_type=message_data.node_type,
            content=message_data.content,
            sort=message_data.sort,
            agent_id=message_data.agent_id
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def create_conversation_messages_batch(self, db: Session, messages_data: List[ConversationMessageCreate]) -> List[ConversationMessage]:
        """Create multiple ConversationMessages in batch"""
        db_messages = []
        
        for message_data in messages_data:
            message_id = str(uuid.uuid4())
            db_message = ConversationMessage(
                id=message_id,
                conversation_id=message_data.conversation_id,
                node_type=message_data.node_type,
                content=message_data.content,
                sort=message_data.sort,
                agent_id=message_data.agent_id
            )
            db_messages.append(db_message)
        
        db.add_all(db_messages)
        db.commit()
        
        for db_message in db_messages:
            db.refresh(db_message)
        
        return db_messages
    
    def get_conversation_message(self, db: Session, message_id: str) -> Optional[ConversationMessage]:
        """Get ConversationMessage by ID"""
        return db.query(ConversationMessage).filter(ConversationMessage.id == message_id).first()
    
    def get_conversation_messages(self, db: Session, conversation_id: str) -> List[ConversationMessage]:
        """Get all messages for a conversation, ordered by sort"""
        return db.query(ConversationMessage)\
            .filter(ConversationMessage.conversation_id == conversation_id)\
            .order_by(ConversationMessage.sort)\
            .all()
    
    def save_conversation(self, db: Session, conversation_data: SaveConversationRequest) -> ConversationSummarySchema:
        """Save a complete conversation with summary and messages"""
        conversation_id = str(uuid.uuid4())
        
        # Create conversation summary
        db_summary = ConversationSummary(
            id=conversation_id,
            title=conversation_data.title
        )
        db.add(db_summary)
        
        # Create messages with conversation_id
        db_messages = []
        for message_data in conversation_data.messages:
            message_id = str(uuid.uuid4())
            db_message = ConversationMessage(
                id=message_id,
                conversation_id=conversation_id,
                node_type=message_data.node_type,
                content=message_data.content,
                sort=message_data.sort,
                agent_id=message_data.agent_id
            )
            db_messages.append(db_message)
        
        db.add_all(db_messages)
        db.commit()
        db.refresh(db_summary)
        
        # Return conversation summary with message count
        message_count = len(db_messages)
        return ConversationSummarySchema(
            id=db_summary.id,
            title=db_summary.title,
            created_at=db_summary.created_at,
            updated_at=db_summary.updated_at,
            message_count=message_count
        )
    
    def get_conversations(self, db: Session, skip: int = 0, limit: int = 100) -> List[ConversationSummarySchema]:
        """Get conversation summaries with message count"""
        # Get summaries with message count
        results = db.query(
            ConversationSummary,
            func.count(ConversationMessage.id).label('message_count')
        ).outerjoin(
            ConversationMessage, 
            ConversationSummary.id == ConversationMessage.conversation_id
        ).group_by(
            ConversationSummary.id
        ).order_by(
            desc(ConversationSummary.updated_at)
        ).offset(skip).limit(limit).all()
        
        return [
            ConversationSummarySchema(
                id=summary.id,
                title=summary.title,
                created_at=summary.created_at,
                updated_at=summary.updated_at,
                message_count=message_count or 0
            )
            for summary, message_count in results
        ]
    
    def get_conversation(self, db: Session, conversation_id: str) -> Optional[ConversationSchema]:
        """Get complete conversation with all messages"""
        # Get summary
        db_summary = db.query(ConversationSummary).filter(ConversationSummary.id == conversation_id).first()
        if not db_summary:
            return None
        
        # Get messages
        db_messages = self.get_conversation_messages(db, conversation_id)
        
        return ConversationSchema(
            id=db_summary.id,
            title=db_summary.title,
            created_at=db_summary.created_at,
            updated_at=db_summary.updated_at,
            messages=[
                msg for msg in db_messages
            ]
        )
    
    def delete_conversation(self, db: Session, conversation_id: str) -> bool:
        """Delete conversation and all its messages"""
        # Delete messages first
        db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conversation_id).delete()
        
        # Delete summary
        db_summary = db.query(ConversationSummary).filter(ConversationSummary.id == conversation_id).first()
        if not db_summary:
            return False
        
        db.delete(db_summary)
        db.commit()
        return True 