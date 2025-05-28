import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.ai_service import AIService


class AgentService:
    """Agent服务，处理Agent的CRUD操作"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def create_agent(self, db: Session, agent_data: AgentCreate) -> Agent:
        """创建新的Agent"""
        agent_id = str(uuid.uuid4())
        
        db_agent = Agent(
            id=agent_id,
            name=agent_data.name,
            description=agent_data.description,
            icon=agent_data.icon,
            category=agent_data.category,
            color=agent_data.color,
            system_prompt=agent_data.system_prompt,
            model=agent_data.model,
            temperature=agent_data.temperature,
            max_tokens=agent_data.max_tokens
        )
        
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent
    
    def get_agent(self, db: Session, agent_id: str) -> Optional[Agent]:
        """根据ID获取Agent"""
        return db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agents(self, db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
        """获取Agent列表"""
        return db.query(Agent).offset(skip).limit(limit).all()
    
    def update_agent(self, db: Session, agent_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
        """更新Agent"""
        db_agent = self.get_agent(db, agent_id)
        if not db_agent:
            return None
        
        # 更新字段
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # 将schema字段名转换为数据库字段名
            if field == "system_prompt":
                field = "system_prompt"
            elif field == "max_tokens":
                field = "max_tokens"
            
            setattr(db_agent, field, value)
        
        db.commit()
        db.refresh(db_agent)
        return db_agent
    
    def delete_agent(self, db: Session, agent_id: str) -> bool:
        """删除Agent"""
        db_agent = self.get_agent(db, agent_id)
        if not db_agent:
            return False
        
        db.delete(db_agent)
        db.commit()
        return True
    
    async def execute_agent(self, db: Session, agent_id: str, user_input: str) -> tuple[str, List[str]]:
        """执行Agent"""
        db_agent = self.get_agent(db, agent_id)
        if not db_agent:
            raise ValueError(f"Agent {agent_id} 不存在")
        
        # 根据是否配置了OpenAI API选择执行方式
        if self.ai_service.is_configured():
            return await self.ai_service.execute_agent(
                system_prompt=db_agent.system_prompt,
                user_input=user_input,
                model=db_agent.model,
                temperature=db_agent.temperature,
                max_tokens=db_agent.max_tokens
            )
        else:
            return await self.ai_service.mock_execute_agent(
                system_prompt=db_agent.system_prompt,
                user_input=user_input,
                model=db_agent.model,
                temperature=db_agent.temperature,
                max_tokens=db_agent.max_tokens
            ) 