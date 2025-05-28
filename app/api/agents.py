from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentExecuteRequest, AgentExecuteResponse
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """创建新的Agent"""
    try:
        return agent_service.create_agent(db, agent_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建Agent失败: {str(e)}"
        )


@router.get("/", response_model=List[Agent])
def get_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取Agent列表"""
    return agent_service.get_agents(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """根据ID获取Agent"""
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    return agent


@router.put("/{agent_id}", response_model=Agent)
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """更新Agent"""
    agent = agent_service.update_agent(db, agent_id, agent_data)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """删除Agent"""
    success = agent_service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: Session = Depends(get_db)
):
    """执行Agent"""
    try:
        output, logs = await agent_service.execute_agent(db, agent_id, request.input)
        return AgentExecuteResponse(output=output, logs=logs)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行Agent失败: {str(e)}"
        ) 