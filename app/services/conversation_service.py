import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationSummary,
    SaveConversationRequest, ConversationMessageCreate
)


class ConversationService:
    
    @staticmethod
    def create_conversation(db: Session, conversation: ConversationCreate) -> Conversation:
        """Create a new conversation"""
        db_conversation = Conversation(
            id=str(uuid.uuid4()),
            title=conversation.title
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID with all messages"""
        return db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
    
    @staticmethod
    def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[ConversationSummary]:
        """Get all conversations with summary info"""
        conversations = db.query(
            Conversation.id,
            Conversation.title,
            Conversation.created_at,
            Conversation.updated_at,
            func.count(ConversationMessage.id).label('message_count')
        ).outerjoin(ConversationMessage).group_by(
            Conversation.id
        ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
        
        return [
            ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=conv.message_count or 0
            )
            for conv in conversations
        ]
    
    @staticmethod
    def update_conversation(db: Session, conversation_id: str, conversation: ConversationUpdate) -> Optional[Conversation]:
        """Update a conversation"""
        db_conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if db_conversation:
            if conversation.title is not None:
                db_conversation.title = conversation.title
            db.commit()
            db.refresh(db_conversation)
        return db_conversation
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        db_conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if db_conversation:
            db.delete(db_conversation)
            db.commit()
            return True
        return False
    
    @staticmethod
    def save_conversation_from_nodes(db: Session, request: SaveConversationRequest) -> Conversation:
        """Save a conversation from frontend conversation nodes"""
        # Create conversation
        conversation = ConversationService.create_conversation(
            db, ConversationCreate(title=request.title)
        )
        
        # Convert and save conversation nodes as messages
        for node in request.conversation_nodes:
            message_data = ConversationMessageCreate(
                conversation_id=conversation.id,
                node_type=node.get('type', 'input'),
                content=node.get('content', ''),
                agent_id=node.get('agentId'),
                agent_name=node.get('agentName'),
                resources=json.dumps(node.get('resources', [])) if node.get('resources') else None,
                execution_logs=json.dumps(node.get('executionLogs', [])) if node.get('executionLogs') else None,
                is_current_input=node.get('isCurrentInput', False),
                is_editable=node.get('isEditable', False)
            )
            
            db_message = ConversationMessage(
                id=str(uuid.uuid4()),
                **message_data.dict()
            )
            db.add(db_message)
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_conversation_nodes(db: Session, conversation_id: str) -> List[dict]:
        """Get conversation as frontend-compatible nodes"""
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            return []
        
        nodes = []
        for message in conversation.messages:
            node = {
                'id': message.id,
                'type': message.node_type,
                'content': message.content,
                'timestamp': message.created_at,
                'isCurrentInput': message.is_current_input,
                'isEditable': message.is_editable
            }
            
            if message.agent_id:
                node['agentId'] = message.agent_id
            if message.agent_name:
                node['agentName'] = message.agent_name
            if message.resources:
                node['resources'] = json.loads(message.resources)
            if message.execution_logs:
                node['executionLogs'] = json.loads(message.execution_logs)
            
            nodes.append(node)
        
        return nodes 