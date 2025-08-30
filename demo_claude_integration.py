#!/usr/bin/env python3
"""
Demo script for Claude Code integration with SyntheticCodingTeam.

This demonstrates the new unified AI tool interface that supports both
Claude Code CLI and OpenAI API through a clean `execute` method.
"""

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.tools.ai_interface import ClaudeCodeTool, OpenAITool
from core.tools.factory import create_ai_tool, get_tool_info
from config import Settings


async def demo_claude_integration():
    """Demonstrate Claude Code integration with unified interface."""
    print("🤖 CLAUDE CODE INTEGRATION DEMO")
    print("=" * 60)
    print("Testing unified AI tool interface with both Claude Code and OpenAI")
    print()
    
    try:
        # Load configuration
        settings = Settings()
        print("✅ Configuration loaded")
        print(f"   Agent tools: {settings.agent_tools}")
        print(f"   Claude settings: {settings.claude_settings}")
        print(f"   OpenAI settings: {settings.openai_settings}")
        print()
        
        # Test tool creation for each agent type
        agent_types = ["developer", "navigator", "analyst"]
        
        for agent_type in agent_types:
            print(f"🔧 Testing {agent_type.upper()} agent tool:")
            
            # Get tool info
            tool_info = get_tool_info(agent_type, settings)
            print(f"   Tool type: {tool_info['tool_type']}")
            print(f"   Configured: {tool_info['configured']}")
            
            # Create tool
            try:
                ai_tool = create_ai_tool(agent_type, settings)
                print(f"   ✅ {ai_tool.tool_type} tool created successfully")
                
                # Test basic execution
                test_prompt = f"Hello from {agent_type} agent using {ai_tool.tool_type}"
                context = {"timeout": 30, "agent_type": agent_type}
                
                # Simple test (just to verify interface works)
                if ai_tool.tool_type == "claude":
                    print(f"   🎯 Would execute: claude -p '{test_prompt[:50]}...'")
                    print(f"   ✅ Claude Code interface ready")
                else:
                    print(f"   🎯 Would call OpenAI API with prompt")
                    print(f"   ✅ OpenAI interface ready")
                
            except Exception as e:
                print(f"   ❌ Tool creation failed: {e}")
            
            print()
        
        print("🎯 INTERFACE COMPARISON:")
        print("-" * 40)
        print("UNIFIED INTERFACE - All agents use same method:")
        print()
        print("# Developer Agent")
        print("result = await ai_tool.execute(")
        print("    prompt='Implement authentication feature',")
        print("    context={'timeout': 120, 'files': existing_files},")
        print("    system_prompt='You are a senior developer'")
        print(")")
        print()
        print("# Navigator Agent")
        print("review = await ai_tool.execute(")
        print("    prompt='Review this code for quality issues',")
        print("    context={'timeout': 60, 'code': code_to_review}")
        print(")")
        print()
        print("# Analyst Agent") 
        print("analysis = await ai_tool.execute(")
        print("    prompt='Analyze requirements for this issue',")
        print("    context={'timeout': 90, 'issue': issue_data}")
        print(")")
        print()
        
        print("🔄 BEHIND THE SCENES:")
        print("-" * 40)
        print("OpenAI Tool:")
        print("  → Converts to chat messages")
        print("  → Uses LangChain ChatOpenAI")
        print("  → API call with temperature/tokens")
        print()
        print("Claude Code Tool:")
        print("  → Formats as single prompt")
        print("  → Executes: claude -p 'prompt' --output-format text") 
        print("  → Direct CLI subprocess call")
        print()
        
        print("✅ BENEFITS:")
        print("• Clean, unified interface for all agents")
        print("• No kwargs - explicit parameters only")
        print("• Timeout in context (per-request control)")
        print("• Easy switching between Claude/OpenAI per agent")
        print("• Each tool uses its natural paradigm")
        print("• Configuration-driven tool selection")
        print()
        
        print("🎉 Claude Code integration demo COMPLETED!")
        print("Ready to replace OpenAI with Claude Code in all agents!")
        
    except Exception as e:
        print(f"❌ Demo FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_claude_integration())