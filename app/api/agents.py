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
    """Create new Agent"""
    try:
        service = AgentService()
        return service.create_agent(db, agent_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create Agent: {str(e)}"
        )


@router.get("/", response_model=List[Agent])
def get_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get Agent list"""
    service = AgentService()
    return service.get_agents(db, skip, limit)


@router.get("/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Get Agent by ID"""
    service = AgentService()
    agent = service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=Agent)
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update Agent"""
    service = AgentService()
    updated_agent = service.update_agent(db, agent_id, agent_data)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return updated_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Delete Agent"""
    service = AgentService()
    success = service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute Agent"""
    try:
        # Add debug logging
        print(f"🔍 Execute agent request:")
        print(f"   Agent ID: {agent_id}")
        print(f"   Request input type: {type(request.input)}")
        print(f"   Request input length: {len(request.input) if request.input else 0}")
        print(f"   Request input preview: {request.input[:100] if request.input else 'None'}...")
        
        service = AgentService()
        output, logs = await service.execute_agent(db, agent_id, request.input)
        return AgentExecuteResponse(output=output, logs=logs)
    except ValueError as e:
        print(f"❌ ValueError in execute_agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Exception in execute_agent: {str(e)}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute Agent: {str(e)}"
        )


@router.post("/optimize-prompt")
async def optimize_prompt(request: dict):
    """Optimize system prompt"""
    try:
        original_prompt = request.get("prompt", "")
        if not original_prompt.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt cannot be empty")
        
        ai_service = AIService()
        
        # Check if OpenAI is configured
        if not ai_service.is_configured():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="OpenAI API is not configured. Please set OPENAI_API_KEY in environment variables."
            )
        
        # System prompt for optimization
        optimization_system_prompt = """You are a professional AI prompt optimization expert. Your task is to help users improve their system prompts to make them clearer, more specific, and more effective.

Optimization principles:
1. Clear role definition: Ensure the AI's role and professional domain are clearly defined
2. Specific instructions: Convert vague instructions into specific, actionable steps
3. Structured output: Specify expected output format and structure
4. Add constraints: Clearly define rules and limitations the AI should follow
5. Provide examples: Provide output examples when appropriate
6. Optimize language: Use clear, professional language

Please analyze the original prompt provided by the user, then provide an optimized version. The optimized prompt should be more professional, specific, and effective.

Please output the complete optimized prompt directly without adding any other content.
"""

        user_input = f"Please help me optimize the following system prompt:\n\n{original_prompt}"
        
        optimized_result, logs = await ai_service.execute_agent(
            system_prompt=optimization_system_prompt,
            user_input=user_input,
            model="gpt-4o-mini",
            temperature=0.3,  # Use lower temperature for more consistent results
            max_tokens=2000
        )
        
        return {
            "optimized_prompt": optimized_result,
            "logs": logs
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Optimization failed: {str(e)}") 