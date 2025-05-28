import asyncio
from typing import List, Optional
import openai
from config import settings


class AIService:
    """AI服务，处理OpenAI API调用"""
    
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def is_configured(self) -> bool:
        """检查OpenAI是否已配置"""
        return self.client is not None and settings.openai_api_key is not None
    
    def get_available_models(self) -> List[dict]:
        """获取可用的模型列表"""
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "max_tokens": 4000,
                "description": "快速高效的模型"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "max_tokens": 8000,
                "description": "最强大的模型"
            },
            {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo",
                "max_tokens": 128000,
                "description": "最新的GPT-4模型"
            }
        ]
    
    def _combine_prompts(self, system_prompt: str, user_input: str) -> str:
        """
        将系统提示词和用户输入合并为单一提示词
        
        Args:
            system_prompt: 系统提示词
            user_input: 用户输入
            
        Returns:
            str: 合并后的提示词
        """
        combined_prompt = f"""你是一个AI助手，请严格按照以下角色设定和指令来回答用户的问题：

【角色设定和指令】
{system_prompt}

【用户问题】
{user_input}

请根据上述角色设定，对用户问题给出专业的回答："""
        
        return combined_prompt

    async def execute_agent(
        self,
        system_prompt: str,
        user_input: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> tuple[str, List[str]]:
        """
        执行AI代理
        
        Args:
            system_prompt: 系统提示词
            user_input: 用户输入
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            tuple[output, logs]: 输出结果和执行日志
        """
        if not self.is_configured():
            raise ValueError("OpenAI API未配置")
        
        # 使用默认值
        model = model or settings.openai_default_model
        temperature = temperature if temperature is not None else settings.openai_default_temperature
        max_tokens = max_tokens or settings.openai_default_max_tokens
        
        logs = [
            f"启动AI代理...",
            f"使用模型: {model}",
            f"温度参数: {temperature}",
            f"最大tokens: {max_tokens}",
            "合并系统提示词和用户输入...",
            "调用OpenAI API...",
        ]
        
        try:
            # 模拟异步处理
            await asyncio.sleep(0.5)
            
            # 将系统提示词合并到用户输入中
            combined_prompt = self._combine_prompts(system_prompt, user_input)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": combined_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            output = response.choices[0].message.content
            logs.extend([
                "API调用成功",
                f"生成tokens: {response.usage.completion_tokens}",
                "处理完成"
            ])
            
            return output, logs
            
        except Exception as e:
            error_msg = f"AI执行失败: {str(e)}"
            logs.append(error_msg)
            raise ValueError(error_msg)
    
    async def mock_execute_agent(
        self,
        system_prompt: str,
        user_input: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> tuple[str, List[str]]:
        """
        模拟执行AI代理（用于测试或无API key时）
        """
        model = model or settings.openai_default_model
        temperature = temperature if temperature is not None else settings.openai_default_temperature
        max_tokens = max_tokens or settings.openai_default_max_tokens
        
        logs = [
            f"启动模拟AI代理...",
            f"使用模型: {model}",
            f"温度参数: {temperature}",
            f"最大tokens: {max_tokens}",
            "合并系统提示词和用户输入...",
            "应用处理逻辑...",
            "生成输出结果...",
        ]
        
        # 模拟处理时间
        await asyncio.sleep(2)
        
        # 生成模拟输出
        output = f"""基于系统提示词的处理结果：

输入内容分析：
{user_input[:200]}{'...' if len(user_input) > 200 else ''}

处理结果：
这是一个模拟的AI代理执行结果。在实际环境中，这里会是根据系统提示词和用户输入生成的智能回复。

使用的参数：
- 模型: {model}
- 温度: {temperature}
- 最大tokens: {max_tokens}

请配置有效的OpenAI API密钥以获得真实的AI响应。"""
        
        logs.append("模拟执行完成")
        return output, logs 