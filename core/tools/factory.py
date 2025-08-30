"""AI tool factory for creating configured tool instances."""

import logging
from typing import Optional, Dict, Any

from .ai_interface import AITool, OpenAITool, ClaudeCodeTool, AIToolError
from config import Settings

logger = logging.getLogger(__name__)


def create_ai_tool(agent_type: str, settings: Optional[Settings] = None) -> AITool:
    """
    Create AI tool instance based on agent type and configuration.
    
    Args:
        agent_type: Type of agent (developer, navigator, analyst)
        settings: Optional settings instance
        
    Returns:
        Configured AI tool instance
        
    Raises:
        AIToolError: If tool creation fails
    """
    if settings is None:
        settings = Settings()
    
    # Get tool type for this agent
    tool_type = settings.agent_tools.get(agent_type)
    if not tool_type:
        raise AIToolError(f"No tool configured for agent type: {agent_type}", "unknown")
    
    logger.info(f"Creating {tool_type} tool for {agent_type} agent")
    
    try:
        if tool_type == "openai":
            # Create OpenAI tool with settings
            openai_config = settings.openai_settings.copy()
            openai_config["api_key"] = settings.openai_api_key
            return OpenAITool(**openai_config)
            
        elif tool_type == "claude":
            # Create Claude Code tool with settings
            claude_config = settings.claude_settings.copy()
            return ClaudeCodeTool(**claude_config)
            
        else:
            raise AIToolError(f"Unknown tool type: {tool_type}", tool_type)
            
    except Exception as e:
        logger.error(f"Failed to create {tool_type} tool for {agent_type}: {e}")
        raise AIToolError(
            f"Tool creation failed: {e}", 
            tool_type, 
            {"agent_type": agent_type, "error": str(e)}
        )


def get_tool_info(agent_type: str, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """
    Get information about the tool configured for an agent.
    
    Args:
        agent_type: Type of agent
        settings: Optional settings instance
        
    Returns:
        Tool information dictionary
    """
    if settings is None:
        settings = Settings()
    
    tool_type = settings.agent_tools.get(agent_type, "unknown")
    
    return {
        "agent_type": agent_type,
        "tool_type": tool_type,
        "configured": tool_type in ["openai", "claude"]
    }


# Export functions
__all__ = [
    "create_ai_tool",
    "get_tool_info"
]