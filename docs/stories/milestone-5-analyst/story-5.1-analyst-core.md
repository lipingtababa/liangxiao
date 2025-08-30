# Story 5.1: Analyst Agent Core ✅ COMPLETED

## Story Details
- **ID**: 5.1
- **Title**: Implement Requirements Analyst Agent
- **Milestone**: Milestone 5 - Analyst Agent
- **Points**: 8
- **Priority**: P1 (Essential)
- **Dependencies**: Stories 2.1 (PM Agent), 3.1 (Navigator Agent)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/analyst/`

## Description

### Overview
Implement the Analyst Agent that performs thorough requirements gathering, codebase analysis, and documentation creation. The Analyst ensures developers have clear, complete requirements before coding, preventing ambiguity that leads to disasters like PR #23.

### Why This Is Important
- Prevents implementation disasters through clear requirements
- Analyzes existing codebase to understand context
- Creates specifications that developers can follow precisely
- Identifies dependencies and potential issues before coding
- Bridges the gap between issue description and implementation

### Context
PR #23 happened because no one read the existing README before "fixing" it. The Analyst Agent's job is to read, understand, and document what exists so other agents can make informed decisions.

## Acceptance Criteria

### Required
- [ ] Analyst Agent class implemented with LangChain
- [ ] Can read and analyze existing codebase files
- [ ] Extracts clear requirements from GitHub issues
- [ ] Creates detailed technical specifications
- [ ] Identifies file dependencies and relationships
- [ ] Documents current system behavior
- [ ] Provides context for other agents
- [ ] Creates implementation guidelines
- [ ] Handles various issue types (bugs, features, improvements)
- [ ] Returns structured analysis artifacts

## Technical Details

### Analyst Agent Implementation
```python
# agents/analyst/agent.py
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from services.github_service import github_service
import logging

logger = logging.getLogger(__name__)

class RequirementSpec(BaseModel):
    """Individual requirement specification."""
    id: str = Field(description="Unique requirement ID")
    description: str = Field(description="Clear requirement description")
    priority: Literal["critical", "high", "medium", "low"]
    acceptance_criteria: List[str] = Field(description="How to verify completion")
    dependencies: List[str] = Field(description="What this depends on")

class CodebaseAnalysis(BaseModel):
    """Analysis of existing codebase."""
    relevant_files: List[str] = Field(description="Files that need to be read/modified")
    current_behavior: str = Field(description="How system currently works")
    architecture_notes: str = Field(description="Relevant architectural patterns")
    dependencies: List[str] = Field(description="External dependencies identified")
    potential_impacts: List[str] = Field(description="What might be affected by changes")

class TechnicalSpecification(BaseModel):
    """Complete technical specification."""
    requirements: List[RequirementSpec]
    codebase_analysis: CodebaseAnalysis
    implementation_approach: str = Field(description="Recommended approach")
    testing_strategy: str = Field(description="How to test the changes")
    risk_assessment: List[str] = Field(description="Potential risks and mitigations")
    success_criteria: List[str] = Field(description="How to measure success")

class AnalystAgent:
    """
    Analyst agent that gathers requirements and analyzes codebase.
    
    Responsible for thorough analysis before implementation begins.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1  # Very low temperature for consistent analysis
        )
        self.parser = PydanticOutputParser(pydantic_object=TechnicalSpecification)
    
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis task.
        
        Args:
            task: Task definition from PM
            context: Issue and repository context
            
        Returns:
            Analysis artifacts
        """
        logger.info(f"Analyst executing task: {task['id']}")
        
        try:
            # Extract issue information
            issue = context.get("issue", {})
            repository = context.get("repository", "")
            
            # Perform comprehensive analysis
            spec = await self._analyze_issue_thoroughly(
                issue=issue,
                repository=repository,
                task_description=task.get("description", "")
            )
            
            # Create documentation
            documentation = await self._create_documentation(spec, issue)
            
            return {
                "success": True,
                "artifacts": [
                    {
                        "type": "requirements",
                        "path": f"analysis/requirements-{issue['number']}.md",
                        "content": documentation,
                        "specification": spec.model_dump()
                    }
                ],
                "summary": f"Analyzed {len(spec.requirements)} requirements, {len(spec.codebase_analysis.relevant_files)} files"
            }
            
        except Exception as e:
            logger.error(f"Analyst execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "artifacts": []
            }
    
    async def _analyze_issue_thoroughly(
        self,
        issue: Dict[str, Any],
        repository: str,
        task_description: str
    ) -> TechnicalSpecification:
        """Perform thorough issue analysis."""
        
        # First, read relevant files from the repository
        relevant_files = await self._identify_relevant_files(issue, repository)
        codebase_content = await self._read_relevant_files(relevant_files)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert Business Analyst and System Analyst.
                
                Your job is to thoroughly analyze requirements and existing codebase
                to create clear, unambiguous specifications for developers.
                
                Key principles:
                1. READ FIRST - Always understand what exists before proposing changes
                2. BE SPECIFIC - Vague requirements lead to wrong implementations  
                3. IDENTIFY DEPENDENCIES - What might be affected by changes?
                4. THINK ABOUT TESTING - How will we verify success?
                5. ASSESS RISKS - What could go wrong?
                
                Remember: You're preventing disasters like PR #23 where an agent
                deleted an entire README instead of removing one phrase because
                they didn't read the existing content first!
                
                {format_instructions}
                """
            ),
            ("human", """Issue to analyze:
            Title: {title}
            Body: {body}
            Repository: {repository}
            
            Task Description: {task_description}
            
            Existing Codebase Analysis:
            {codebase_content}
            
            Create a comprehensive technical specification:""")
        ])
        
        formatted_prompt = prompt.format_messages(
            format_instructions=self.parser.get_format_instructions(),
            title=issue.get("title", ""),
            body=issue.get("body", ""),
            repository=repository,
            task_description=task_description,
            codebase_content=codebase_content
        )
        
        response = await self.llm.ainvoke(formatted_prompt)
        specification = self.parser.parse(response.content)
        
        return specification
    
    async def _identify_relevant_files(
        self,
        issue: Dict[str, Any],
        repository: str
    ) -> List[str]:
        """Identify files that need to be analyzed."""
        
        # Use LLM to identify relevant files based on issue
        prompt = f"""
        Based on this issue, identify which files in the repository should be analyzed:
        
        Issue: {issue.get('title', '')}
        Description: {issue.get('body', '')}
        
        Consider:
        - Files mentioned in the issue
        - Files that might be affected by changes
        - Configuration files that might be relevant
        - Test files that might need updates
        
        Return a list of specific file paths (e.g., README.md, src/components/Button.tsx)
        """
        
        # Get file tree first
        file_tree = github_service.get_file_tree()
        
        # Use LLM to identify relevant files from tree
        identification_prompt = f"""
        {prompt}
        
        Available files in repository:
        {chr(10).join(file_tree[:100])}  # First 100 files
        
        Return relevant file paths:
        """
        
        response = await self.llm.ainvoke([("human", identification_prompt)])
        
        # Parse response to extract file paths
        relevant_files = self._parse_file_paths_from_response(response.content)
        
        return relevant_files[:10]  # Limit to 10 files to avoid overwhelming
    
    async def _read_relevant_files(self, file_paths: List[str]) -> str:
        """Read content of relevant files."""
        
        file_contents = []
        
        for file_path in file_paths:
            try:
                content = github_service.read_file(file_path)
                if content:
                    file_contents.append(f"=== {file_path} ===\n{content}\n")
                else:
                    file_contents.append(f"=== {file_path} === (File not found)\n")
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                file_contents.append(f"=== {file_path} === (Error reading file)\n")
        
        return "\n".join(file_contents)
    
    async def _create_documentation(
        self,
        specification: TechnicalSpecification,
        issue: Dict[str, Any]
    ) -> str:
        """Create comprehensive documentation."""
        
        doc = f"""# Requirements Analysis - Issue #{issue.get('number', 'Unknown')}

## Issue Summary
**Title**: {issue.get('title', 'No title')}
**Description**: {issue.get('body', 'No description')}

## Requirements

"""
        
        for i, req in enumerate(specification.requirements, 1):
            doc += f"""### Requirement {i}: {req.description}
- **Priority**: {req.priority}
- **Acceptance Criteria**:
{chr(10).join(f"  - {criteria}" for criteria in req.acceptance_criteria)}
- **Dependencies**: {', '.join(req.dependencies) if req.dependencies else 'None'}

"""
        
        doc += f"""## Codebase Analysis

### Relevant Files
{chr(10).join(f"- `{file}`" for file in specification.codebase_analysis.relevant_files)}

### Current Behavior
{specification.codebase_analysis.current_behavior}

### Architecture Notes
{specification.codebase_analysis.architecture_notes}

### Dependencies
{chr(10).join(f"- {dep}" for dep in specification.codebase_analysis.dependencies)}

### Potential Impacts
{chr(10).join(f"- {impact}" for impact in specification.codebase_analysis.potential_impacts)}

## Implementation Approach
{specification.implementation_approach}

## Testing Strategy
{specification.testing_strategy}

## Risk Assessment
{chr(10).join(f"- {risk}" for risk in specification.risk_assessment)}

## Success Criteria
{chr(10).join(f"- {criteria}" for criteria in specification.success_criteria)}

---
*Generated by Analyst Agent*
"""
        
        return doc
    
    def _parse_file_paths_from_response(self, response: str) -> List[str]:
        """Parse file paths from LLM response."""
        # Simple parsing - look for lines that look like file paths
        lines = response.split('\n')
        file_paths = []
        
        for line in lines:
            line = line.strip()
            # Look for common file patterns
            if any(line.endswith(ext) for ext in ['.md', '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yml', '.yaml']):
                # Remove markdown formatting if present
                line = line.replace('`', '').replace('-', '').strip()
                if line:
                    file_paths.append(line)
        
        return file_paths
```

### Example Analysis Output
```markdown
# Requirements Analysis - Issue #21

## Issue Summary
**Title**: remove "解释文化细节" from readme
**Description**: Remove the phrase "解释文化细节" from README.md

## Requirements

### Requirement 1: Remove specific phrase from README
- **Priority**: high
- **Acceptance Criteria**:
  - Phrase "解释文化细节" is completely removed from README.md
  - All other content in README.md is preserved exactly as-is
  - File structure and formatting remain unchanged
  - No other text is modified or deleted
- **Dependencies**: None

## Codebase Analysis

### Relevant Files
- `README.md`

### Current Behavior
The README.md file contains comprehensive project documentation including:
- Project overview in Chinese
- Setup instructions  
- Architecture details
- The phrase "解释文化细节" appears in the translation section

### Architecture Notes
This is a documentation-only change with no impact on code functionality.

### Dependencies
- None identified

### Potential Impacts
- Documentation will be slightly shorter
- Translation guidance section will be updated
- No functional code changes required

## Implementation Approach
1. Read current README.md content
2. Locate the exact phrase "解释文化细节"  
3. Remove ONLY that phrase, preserving all surrounding text
4. Maintain original formatting and structure
5. Verify no other content was accidentally modified

## Testing Strategy
1. Compare before/after file content
2. Verify phrase is completely removed
3. Verify all other content is identical
4. Check file renders correctly in GitHub

## Risk Assessment
- Low risk: Documentation change only
- Risk: Accidentally removing more content than intended
- Mitigation: Careful text replacement, not wholesale file replacement

## Success Criteria
- README.md no longer contains "解释文化细节"
- All other README content is preserved
- File structure and formatting unchanged
- Change is minimal and targeted

---
*Generated by Analyst Agent*
```

## Testing Requirements

### Unit Tests
```python
# tests/test_analyst.py
import pytest
from agents.analyst.agent import AnalystAgent

@pytest.mark.asyncio
async def test_analyst_identifies_relevant_files():
    """Test that analyst identifies correct files to analyze."""
    analyst = AnalystAgent()
    
    issue = {
        "title": "Fix button component",
        "body": "The submit button is not working properly"
    }
    
    files = await analyst._identify_relevant_files(issue, "test-repo")
    
    # Should identify button-related files
    assert any("button" in f.lower() for f in files)

@pytest.mark.asyncio  
async def test_analyst_prevents_pr_23():
    """Test analyst creates proper requirements for README changes."""
    analyst = AnalystAgent()
    
    task = {
        "id": "test-1",
        "description": "Remove phrase from README"
    }
    
    context = {
        "issue": {
            "number": 21,
            "title": "remove phrase from readme", 
            "body": "Remove '解释文化细节' from README.md"
        }
    }
    
    result = await analyst.execute(task, context)
    
    # Should create specific requirements
    assert result["success"]
    assert len(result["artifacts"]) > 0
    
    # Check requirements are specific
    spec = result["artifacts"][0]["specification"]
    requirements = spec["requirements"]
    assert any("preserve" in r["description"].lower() for r in requirements)
    assert any("only" in r["description"].lower() for r in requirements)
```

## Dependencies & Risks

### Prerequisites
- GitHub service for reading files
- LangChain configured
- Understanding of requirements analysis

### Risks
- **Incomplete analysis**: Missing important files or requirements
- **Over-analysis**: Too much detail overwhelming other agents
- **File access failures**: Cannot read repository files
- **Ambiguous requirements**: Requirements still unclear after analysis

### Mitigations
- Structured analysis templates
- File reading error handling
- Requirements validation
- Clear acceptance criteria format

## Definition of Done

1. ✅ Analyst Agent class implemented
2. ✅ Can read and analyze codebase files
3. ✅ Creates clear technical specifications
4. ✅ Identifies dependencies and impacts
5. ✅ Provides implementation guidance
6. ✅ Integration with task pair system
7. ✅ Unit tests passing
8. ✅ Prevents PR #23 type disasters
9. ✅ Documentation generation working

## Implementation Notes for AI Agents

### DO
- Always read existing files before analyzing
- Be specific about requirements
- Include acceptance criteria for everything
- Identify what should NOT be changed
- Consider testing implications

### DON'T
- Don't make assumptions about codebase
- Don't create vague requirements
- Don't skip reading relevant files
- Don't ignore dependencies
- Don't rush the analysis

### Common Pitfalls to Avoid
1. Not reading existing code (PR #23 root cause!)
2. Vague requirements that confuse developers
3. Missing file dependencies
4. Ignoring impact on other components
5. Not specifying what to preserve

## Success Example

Analyst preventing PR #23:
```
Issue: "Remove phrase from README"

Bad Analysis: "Remove the phrase" (Vague!)

Good Analysis: 
"Remove ONLY the phrase '解释文化细节' from README.md
- Preserve ALL other content exactly as-is
- Maintain file structure and formatting  
- Target only the specific phrase, nothing else
- Verify by comparing before/after content"

Result: Developer makes targeted change, not wholesale deletion ✅
```

## Next Story
Once this story is complete, proceed to [Story 5.2: Analyst-Navigator Pair](story-5.2-analyst-pair.md)