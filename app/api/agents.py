from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentExecuteRequest, AgentExecuteResponse
from app.services.agent_service import AgentService
from app.services.ai_service import AIService

router = APIRouter()
agent_service = AgentService()


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """创建新的Agent"""
    try:
        service = AgentService()
        return service.create_agent(db, agent_data)
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
    service = AgentService()
    return service.get_agents(db, skip, limit)


@router.get("/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """根据ID获取Agent"""
    service = AgentService()
    agent = service.get_agent(db, agent_id)
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
    service = AgentService()
    updated_agent = service.update_agent(db, agent_id, agent_data)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    return updated_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """删除Agent"""
    service = AgentService()
    success = service.delete_agent(db, agent_id)
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
        service = AgentService()
        output, logs = await service.execute_agent(db, agent_id, request.input)
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


@router.post("/optimize-prompt")
async def optimize_prompt(request: dict):
    """优化系统提示词"""
    try:
        original_prompt = request.get("prompt", "")
        if not original_prompt.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt cannot be empty")
        
        ai_service = AIService()
        
        # 优化提示词的系统提示
        optimization_system_prompt = """你是一个专业的AI提示词优化专家。你的任务是帮助用户改进他们的系统提示词，使其更加清晰、具体、有效。

优化原则：
1. 明确角色定位：确保AI的角色和专业领域清晰明确
2. 具体化指令：将模糊的指令转换为具体、可操作的步骤
3. 结构化输出：指定期望的输出格式和结构
4. 添加约束条件：明确AI应该遵循的规则和限制
5. 提供示例：在适当时候提供输出示例
6. 优化语言：使用清晰、专业的语言表达

请分析用户提供的原始提示词，然后提供一个优化后的版本。优化后的提示词应该更加专业、具体、有效。

请按以下格式回复：
## 原始提示词分析
[分析原始提示词的优缺点]

## 优化建议
[说明主要的优化方向和改进点]

## 优化后的提示词
[提供完整的优化后提示词]"""

        user_input = f"请帮我优化以下系统提示词：\n\n{original_prompt}"
        
        if ai_service.is_configured():
            optimized_result, logs = await ai_service.execute_agent(
                system_prompt=optimization_system_prompt,
                user_input=user_input,
                model="gpt-3.5-turbo",
                temperature=0.3,  # 使用较低的温度以获得更一致的结果
                max_tokens=2000
            )
        else:
            # 如果没有配置OpenAI，使用模拟优化
            optimized_result = f"""## 原始提示词分析
原始提示词："{original_prompt}"

分析：这是一个需要优化的提示词。

## 优化建议
建议增加更具体的角色定位、明确的任务描述和输出格式要求。

## 优化后的提示词
你是一个专业的{original_prompt}专家。请按照以下要求完成任务：

1. 仔细分析用户的需求
2. 提供专业、准确的建议
3. 确保回答结构清晰、逻辑性强
4. 使用专业术语，但保持易懂

输出格式：
- 使用清晰的段落结构
- 重要信息用要点列出
- 必要时提供具体示例

请注意：始终保持专业态度，确保信息的准确性和实用性。

注意：这是模拟优化结果，请配置OpenAI API以获得真实的优化效果。"""
            logs = ["模拟优化完成"]
        
        return {
            "optimized_prompt": optimized_result,
            "logs": logs
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Optimization failed: {str(e)}") 