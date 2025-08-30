# Story 5.2: Analyst-Navigator Pair ✅ COMPLETED

## Story Details
- **ID**: 5.2
- **Title**: Implement Analyst Review Cycle
- **Milestone**: Milestone 5 - Analyst Agent
- **Points**: 5
- **Priority**: P1 (Essential)
- **Dependencies**: Story 5.1 (Analyst Core), Story 3.1 (Navigator Agent)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/pairs/` and `services/orchestrator/agents/navigator/requirements_reviewer.py`

## Description

### Overview
Integrate the Analyst Agent with the Navigator Agent to form an Analyst-Navigator pair that ensures requirements are thorough, clear, and actionable before development begins. The Navigator reviews requirements for completeness and clarity, providing feedback for improvement.

### Why This Is Important
- Ensures requirements are comprehensive before development
- Catches unclear or incomplete specifications early
- Prevents implementation mistakes due to poor requirements
- Validates that requirements are testable and measurable
- Creates feedback loop for requirements improvement

### Context
Even the best Analyst might miss details or create unclear requirements. The Navigator provides a second set of eyes to review requirements documents, ensuring they're clear enough for the Developer Agent to implement correctly.

## Acceptance Criteria

### Required
- [ ] Navigator Agent configured for requirements review mode
- [ ] Can review requirements documents and identify gaps
- [ ] Provides specific feedback on requirement clarity
- [ ] Identifies missing acceptance criteria
- [ ] Validates requirements are testable and measurable
- [ ] Suggests improvements for ambiguous requirements
- [ ] Iteration cycle between Analyst and Navigator works
- [ ] Final requirements approved by Navigator before development
- [ ] Clear feedback format that Analyst can act on
- [ ] Integration with Task Pair execution system

## Technical Details

### Navigator Requirements Review Configuration
```python
# agents/navigator/requirements_reviewer.py
from agents.navigator.agent import NavigatorAgent, ReviewFeedback
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RequirementsIssue(BaseModel):
    """Issue found in requirements."""
    category: Literal["clarity", "completeness", "testability", "specificity", "consistency"]
    severity: Literal["critical", "major", "minor"] 
    location: str = Field(description="Where in requirements document")
    description: str = Field(description="What's wrong")
    suggestion: str = Field(description="How to improve")

class RequirementsReviewFeedback(ReviewFeedback):
    """Specialized feedback for requirements review."""
    requirements_issues: List[RequirementsIssue] = Field(description="Specific requirements problems")
    missing_elements: List[str] = Field(description="What's missing from requirements")
    completeness_score: int = Field(ge=0, le=10, description="How complete 0-10")
    clarity_score: int = Field(ge=0, le=10, description="How clear 0-10")
    testability_score: int = Field(ge=0, le=10, description="How testable 0-10")

class RequirementsNavigator(NavigatorAgent):
    """Navigator specialized for requirements review."""
    
    def __init__(self):
        super().__init__(specialty="requirements_review")
    
    async def review_requirements(
        self,
        task: Dict[str, Any],
        requirements_output: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int = 1
    ) -> RequirementsReviewFeedback:
        """
        Review requirements documentation for quality.
        
        Args:
            task: The analysis task
            requirements_output: Output from Analyst Agent
            context: Additional context
            iteration_number: Which iteration this is
            
        Returns:
            Specialized requirements feedback
        """
        
        logger.info(f"Navigator reviewing requirements (iteration {iteration_number})")
        
        # Extract requirements document
        artifacts = requirements_output.get("artifacts", [])
        requirements_doc = None
        specification = None
        
        for artifact in artifacts:
            if artifact.get("type") == "requirements":
                requirements_doc = artifact.get("content", "")
                specification = artifact.get("specification", {})
                break
        
        if not requirements_doc:
            return RequirementsReviewFeedback(
                decision=ReviewDecision.REJECTED,
                overall_assessment="No requirements document found",
                requirements_issues=[],
                missing_elements=["Requirements document"],
                completeness_score=0,
                clarity_score=0,
                testability_score=0,
                issues=[],
                required_changes=["Generate requirements document"],
                suggestions=[],
                positive_aspects=[],
                quality_score=0,
                reasoning="Cannot review without requirements document"
            )
        
        # Perform detailed review
        feedback = await self._perform_detailed_requirements_review(
            requirements_doc,
            specification,
            task,
            iteration_number
        )
        
        logger.info(f"Requirements review complete: {feedback.decision}, Completeness: {feedback.completeness_score}/10")
        
        return feedback
    
    async def _perform_detailed_requirements_review(
        self,
        requirements_doc: str,
        specification: Dict[str, Any],
        task: Dict[str, Any],
        iteration_number: int
    ) -> RequirementsReviewFeedback:
        """Perform detailed requirements review."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are reviewing requirements documentation for quality and completeness.
            
            Review the requirements document and check for:
            
            CLARITY:
            - Are requirements unambiguous?
            - Would a developer understand exactly what to implement?
            - Are technical terms defined?
            
            COMPLETENESS:
            - All aspects of the issue covered?
            - Edge cases considered?
            - Dependencies identified?
            - Error scenarios addressed?
            
            TESTABILITY:
            - Can each requirement be tested?
            - Are acceptance criteria specific and measurable?
            - Is success criteria clear?
            
            SPECIFICITY:
            - Are requirements specific rather than vague?
            - Are constraints and limits defined?
            - Are interfaces and data formats specified?
            
            CONSISTENCY:
            - Do requirements contradict each other?
            - Is terminology consistent?
            - Are priorities aligned?
            
            This is iteration {iteration} - be {strictness} in your review.
            
            Focus on preventing implementation disasters like PR #23 where vague
            requirements led to deleting entire files instead of making targeted changes.
            
            {format_instructions}
            """),
            ("human", """Task: {task_description}
            
            Requirements Document:
            {requirements_doc}
            
            Specification Data:
            {specification}
            
            Please review and provide detailed feedback:""")
        ])
        
        # Adjust strictness based on iteration
        strictness = "strict" if iteration_number == 1 else ("moderate" if iteration_number == 2 else "lenient")
        
        formatted_prompt = prompt.format_messages(
            iteration=iteration_number,
            strictness=strictness,
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", ""),
            requirements_doc=requirements_doc,
            specification=json.dumps(specification, indent=2)
        )
        
        response = await self.llm.ainvoke(formatted_prompt)
        feedback = self.parser.parse(response.content)
        
        return feedback
```

### Analyst-Navigator Pair Integration
```python
# agents/pairs/analyst_navigator_pair.py
from agents.analyst.agent import AnalystAgent
from agents.navigator.requirements_reviewer import RequirementsNavigator
from agents.pairs.task_pair import TaskPair
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AnalystNavigatorPair(TaskPair):
    """Specialized pair for requirements analysis."""
    
    def __init__(self):
        analyst = AnalystAgent()
        navigator = RequirementsNavigator()
        super().__init__(
            tasker_agent=analyst,
            navigator_agent=navigator,
            max_iterations=3,
            require_approval=True  # Requirements must be approved
        )
    
    async def execute_requirements_analysis(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute requirements analysis with review cycle.
        
        Returns comprehensive requirements that are Navigator-approved.
        """
        logger.info(f"Starting requirements analysis for task {task['id']}")
        
        # Execute with pair programming pattern
        result = await self.execute_task(task, context)
        
        if result.success:
            logger.info(f"Requirements analysis completed in {len(result.iterations)} iterations")
            
            # Add analysis summary
            final_output = result.final_output
            final_output["analysis_summary"] = self._create_analysis_summary(result)
            
            return final_output
        else:
            logger.error(f"Requirements analysis failed: {result.failure_reason}")
            return {
                "success": False,
                "error": result.failure_reason,
                "artifacts": []
            }
    
    def _create_analysis_summary(self, pair_result) -> str:
        """Create summary of analysis process."""
        iterations = len(pair_result.iterations)
        final_scores = pair_result.iterations[-1].navigator_feedback
        
        return f"""
## Analysis Process Summary

- **Iterations**: {iterations}
- **Final Scores**: 
  - Completeness: {final_scores.completeness_score}/10
  - Clarity: {final_scores.clarity_score}/10  
  - Testability: {final_scores.testability_score}/10
- **Issues Found**: {len(final_scores.requirements_issues)}
- **Navigator Decision**: {final_scores.decision}

The requirements have been thoroughly analyzed and approved for implementation.
"""
```

### Enhanced Analyst with Feedback Integration
```python
# agents/analyst/agent.py (update for feedback handling)
class AnalystAgent:
    # ... existing code ...
    
    async def _incorporate_requirements_feedback(
        self,
        original_specification: TechnicalSpecification,
        feedback: RequirementsReviewFeedback
    ) -> TechnicalSpecification:
        """Incorporate Navigator feedback into requirements."""
        
        prompt = f"""
        Improve the requirements specification based on Navigator feedback.
        
        Original Specification:
        {original_specification.model_dump_json(indent=2)}
        
        Navigator Feedback:
        - Overall Assessment: {feedback.overall_assessment}
        - Issues Found: {[issue.model_dump() for issue in feedback.requirements_issues]}
        - Missing Elements: {feedback.missing_elements}
        - Required Changes: {feedback.required_changes}
        - Suggestions: {feedback.suggestions}
        
        Address all the feedback points while preserving what was done well.
        Make requirements more specific, complete, and testable.
        """
        
        response = await self.llm.ainvoke([("human", prompt)])
        improved_spec = self.parser.parse(response.content)
        
        return improved_spec
```

## Example Requirements Review Process

### Iteration 1: Initial Analysis
```
Analyst creates: "Remove phrase from README"

Navigator Review:
- Clarity: 4/10 - Too vague! Which phrase? Which README?
- Completeness: 3/10 - Missing specific location, preservation requirements
- Testability: 2/10 - How do we verify success?

Decision: NEEDS_CHANGES
Issues:
- Critical: Phrase not specifically identified
- Major: No preservation requirements for other content
- Major: Missing verification criteria
```

### Iteration 2: Improved Analysis
```
Analyst creates: "Remove ONLY the phrase '解释文化细节' from README.md, preserving all other content"

Navigator Review:
- Clarity: 8/10 - Much better! Specific phrase identified
- Completeness: 7/10 - Good, but missing edge case handling
- Testability: 9/10 - Clear success criteria

Decision: NEEDS_CHANGES  
Suggestions:
- Minor: Add check for phrase occurring multiple times
- Minor: Specify handling if phrase not found
```

### Iteration 3: Final Analysis
```
Analyst creates: Complete specification with all edge cases

Navigator Review:
- Clarity: 9/10 - Crystal clear requirements
- Completeness: 9/10 - All scenarios covered
- Testability: 10/10 - Comprehensive success criteria

Decision: APPROVED ✅
```

## Testing Requirements

### Unit Tests
```python
# tests/test_analyst_navigator_pair.py
import pytest
from agents.pairs.analyst_navigator_pair import AnalystNavigatorPair

@pytest.mark.asyncio
async def test_requirements_review_cycle():
    """Test complete requirements analysis with review."""
    pair = AnalystNavigatorPair()
    
    task = {
        "id": "analysis-1",
        "description": "Analyze requirements for README change",
        "type": "analysis"
    }
    
    context = {
        "issue": {
            "number": 21,
            "title": "remove phrase from readme",
            "body": "Remove '解释文化细节' from README.md"
        },
        "repository": "test/repo"
    }
    
    result = await pair.execute_requirements_analysis(task, context)
    
    assert result["success"]
    assert len(result["artifacts"]) > 0
    
    # Should have detailed requirements
    spec = result["artifacts"][0]["specification"]
    assert len(spec["requirements"]) > 0
    assert all(len(req["acceptance_criteria"]) > 0 for req in spec["requirements"])

@pytest.mark.asyncio
async def test_prevents_vague_requirements():
    """Test that Navigator catches vague requirements."""
    navigator = RequirementsNavigator()
    
    vague_requirements = {
        "artifacts": [{
            "type": "requirements",
            "content": "Fix the thing",  # Too vague!
            "specification": {"requirements": []}
        }]
    }
    
    feedback = await navigator.review_requirements(
        task={}, 
        requirements_output=vague_requirements,
        context={},
        iteration_number=1
    )
    
    assert feedback.decision == ReviewDecision.NEEDS_CHANGES
    assert feedback.clarity_score < 5
    assert any("vague" in issue.description.lower() 
              for issue in feedback.requirements_issues)
```

## Dependencies & Risks

### Prerequisites
- Analyst Agent implemented (Story 5.1)
- Navigator Agent with requirements review capability
- Task Pair system functioning

### Risks
- **Over-detailed requirements**: Analysis paralysis
- **Review loops**: Navigator too strict, never approves
- **Inconsistent feedback**: Navigator feedback contradicts itself
- **Performance impact**: Multiple iterations slow down process

### Mitigations
- Progressive leniency in Navigator reviews
- Clear feedback format and templates
- Maximum iteration limits
- Quality thresholds for approval

## Definition of Done

1. ✅ Navigator configured for requirements review
2. ✅ Analyst-Navigator pair working with iteration
3. ✅ Requirements quality improved through feedback
4. ✅ Clear approval criteria for requirements
5. ✅ Integration with overall Task Pair system
6. ✅ Prevents vague requirements that cause disasters
7. ✅ Unit tests passing
8. ✅ Requirements ready for development team
9. ✅ Documentation of review process

## Implementation Notes for AI Agents

### DO
- Be specific about what's unclear in requirements
- Provide actionable suggestions for improvement
- Recognize and praise good requirements
- Focus on preventing implementation disasters
- Be progressively more lenient with iterations

### DON'T
- Don't reject without specific reasons
- Don't require perfection on first iteration  
- Don't provide vague feedback ("make it better")
- Don't ignore critical clarity issues
- Don't approve requirements that will confuse developers

### Common Pitfalls to Avoid
1. Navigator feedback too vague to act on
2. Requirements becoming over-engineered
3. Not focusing on implementation clarity
4. Ignoring testability requirements
5. Approval without thorough review

## Success Example

Preventing PR #23 through requirements review:
```
Original Issue: "remove phrase from readme"

Iteration 1:
Analyst: "Remove phrase from README"
Navigator: "REJECTED - Which phrase? Which README? Too vague!"

Iteration 2:  
Analyst: "Remove '解释文化细节' from README.md, preserve other content"
Navigator: "APPROVED - Clear, specific, testable requirements ✅"

Result: Developer gets crystal-clear requirements, makes targeted change
```

## Next Story
Once this story is complete, proceed to [Milestone 6: Tester Agent stories](../milestone-6-tester/story-6.1-tester-agent.md)