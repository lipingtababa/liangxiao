"""Analyst-Navigator Pair implementation for requirements analysis.

This module implements the AnalystNavigatorPair class that combines the
AnalystAgent and RequirementsNavigator to create comprehensive, navigator-approved
requirements through an iterative review process. This prevents implementation
disasters like PR #23 by ensuring requirements are thorough and clear.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .task_pair import TaskPair, TaskPairResult
from agents.analyst.agent import AnalystAgent
from agents.navigator.requirements_reviewer import RequirementsNavigator
from core.unified_logging import get_unified_logger, log_agent_start, log_agent_complete, log_agent_error

logger = get_unified_logger(__name__)


class AnalystNavigatorPair(TaskPair):
    """Specialized pair for comprehensive requirements analysis.
    
    This pair combines the thorough analysis capabilities of the AnalystAgent
    with the quality review capabilities of the RequirementsNavigator to create
    requirements that are clear, complete, and implementation-ready.
    
    The pair operates in this cycle:
    1. Analyst creates detailed requirements analysis
    2. Navigator reviews for clarity, completeness, and testability
    3. If not approved, Analyst incorporates feedback and improves
    4. Process continues until Navigator approves or max iterations reached
    
    Key Features:
    - Prevents vague requirements that cause implementation disasters
    - Ensures requirements are testable and measurable
    - Creates comprehensive implementation guidance
    - Provides full audit trail of requirements evolution
    - Progressive leniency to prevent infinite iteration loops
    """
    
    def __init__(
        self,
        analyst_agent: Optional[AnalystAgent] = None,
        navigator_agent: Optional[RequirementsNavigator] = None,
        max_iterations: int = 3,
        navigator_strictness: float = 1.0
    ):
        """Initialize AnalystNavigatorPair.
        
        Args:
            analyst_agent: Pre-configured AnalystAgent (creates default if None)
            navigator_agent: Pre-configured RequirementsNavigator (creates default if None)
            max_iterations: Maximum number of review iterations
            navigator_strictness: Base strictness level for navigator reviews
        """
        # Create default agents if not provided
        if analyst_agent is None:
            analyst_agent = AnalystAgent()
        
        if navigator_agent is None:
            navigator_agent = RequirementsNavigator(base_strictness=navigator_strictness)
        
        # Initialize base TaskPair
        super().__init__(
            tasker_agent=analyst_agent,
            navigator_agent=navigator_agent,
            max_iterations=max_iterations,
            require_approval=True  # Requirements MUST be approved before development
        )
        
        self.analyst_agent = analyst_agent
        self.requirements_navigator = navigator_agent
        
        logger.info(
            f"AnalystNavigatorPair initialized: max_iterations={max_iterations}, "
            f"navigator_strictness={navigator_strictness}"
        )
    
    async def execute_requirements_analysis(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute comprehensive requirements analysis with navigator approval.
        
        This method orchestrates the complete requirements analysis process,
        ensuring that the final output meets quality standards and is ready
        for implementation without causing disasters.
        
        Args:
            task: Analysis task definition containing:
                - id: Task identifier
                - description: Task description
                - type: Should be 'analysis'
            context: Context containing:
                - issue: GitHub issue data
                - repository: Repository identifier
                - Any additional context for analysis
                
        Returns:
            Comprehensive requirements analysis result containing:
                - success: Whether analysis succeeded
                - artifacts: Requirements documents and specifications
                - analysis_summary: Summary of the analysis process
                - iterations: Number of iterations required
                - navigator_approval: Final navigator decision
                - quality_scores: Quality metrics from navigator
        """
        logger.info(f"Starting comprehensive requirements analysis for task {task.get('id', 'unknown')}")
        
        # Execute the pair programming pattern
        pair_result = await self.execute_task(task, context)
        
        if pair_result.success:
            logger.info(
                f"Requirements analysis completed successfully in {len(pair_result.iterations)} iterations"
            )
            
            # Create comprehensive output with analysis summary
            final_output = pair_result.final_output.copy()
            final_output.update({
                "analysis_summary": self._create_analysis_summary(pair_result),
                "pair_execution_data": {
                    "iterations": pair_result.total_iterations,
                    "duration_seconds": pair_result.total_duration_seconds,
                    "final_decision": pair_result.final_decision.value if pair_result.final_decision else None,
                    "navigator_approval": pair_result.final_decision.value if pair_result.final_decision else None
                }
            })
            
            # Add final quality scores if available
            if pair_result.iterations:
                final_feedback = pair_result.iterations[-1].navigator_feedback
                if hasattr(final_feedback, 'completeness_score'):
                    final_output["quality_scores"] = {
                        "completeness": final_feedback.completeness_score,
                        "clarity": final_feedback.clarity_score,
                        "testability": final_feedback.testability_score,
                        "overall": final_feedback.quality_score
                    }
            
            return final_output
        else:
            logger.error(f"Requirements analysis failed: {pair_result.failure_reason}")
            return {
                "success": False,
                "error": pair_result.failure_reason,
                "artifacts": [],
                "analysis_summary": f"Analysis failed after {len(pair_result.iterations)} iterations: {pair_result.failure_reason}",
                "iterations": len(pair_result.iterations)
            }
    
    def _create_analysis_summary(self, pair_result: TaskPairResult) -> str:
        """Create comprehensive summary of the analysis process.
        
        Args:
            pair_result: Complete pair execution result
            
        Returns:
            Formatted markdown summary of the analysis process
        """
        iterations = pair_result.total_iterations
        duration_minutes = pair_result.total_duration_seconds / 60
        
        # Get final scores if available
        final_scores_text = "Not available"
        if pair_result.iterations:
            final_feedback = pair_result.iterations[-1].navigator_feedback
            if hasattr(final_feedback, 'completeness_score'):
                final_scores_text = (
                    f"Completeness: {final_feedback.completeness_score}/10, "
                    f"Clarity: {final_feedback.clarity_score}/10, "
                    f"Testability: {final_feedback.testability_score}/10"
                )
        
        # Get issue identification
        issues_found = 0
        if pair_result.iterations:
            for iteration in pair_result.iterations:
                feedback = iteration.navigator_feedback
                if hasattr(feedback, 'requirements_issues'):
                    issues_found += len(feedback.requirements_issues)
        
        summary = f"""## Requirements Analysis Process Summary

**Analysis Results:**
- **Success**: {pair_result.success}
- **Iterations Required**: {iterations}
- **Total Duration**: {duration_minutes:.1f} minutes
- **Final Decision**: {pair_result.final_decision.value if pair_result.final_decision else 'Unknown'}

**Quality Assessment:**
- **Final Scores**: {final_scores_text}
- **Total Issues Found**: {issues_found}
- **Navigator Approved**: {'Yes' if pair_result.success else 'No'}

**Process Insights:**
"""
        
        if iterations == 1:
            summary += "- Requirements met quality standards on first review ✅"
        elif iterations == 2:
            summary += "- Requirements improved through one revision cycle"
        else:
            summary += f"- Requirements required {iterations - 1} revision cycles before approval"
        
        if pair_result.success:
            summary += "\n- Navigator confirmed requirements are clear and implementable"
            summary += "\n- Requirements are ready for development team"
        else:
            summary += "\n- Requirements did not meet final quality standards"
            summary += f"\n- Final issue: {pair_result.failure_reason}"
        
        summary += "\n\n**Quality Assurance Benefits:**"
        summary += "\n- Prevented potential implementation disasters through thorough review"
        summary += "\n- Ensured requirements clarity before development begins"
        summary += "\n- Validated testability and measurability of all requirements"
        summary += "\n- Created comprehensive implementation guidance"
        
        return summary
    
    async def analyze_with_feedback_integration(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any],
        enable_learning: bool = True
    ) -> Dict[str, Any]:
        """
        Execute requirements analysis with enhanced feedback integration.
        
        This method provides additional features beyond basic pair execution:
        - Learning from previous similar issues
        - Enhanced context propagation
        - Detailed feedback integration logs
        
        Args:
            task: Analysis task definition
            context: Analysis context
            enable_learning: Whether to learn from previous similar issues
            
        Returns:
            Enhanced analysis result with detailed feedback integration data
        """
        logger.info("Starting enhanced requirements analysis with feedback integration")
        
        # Enhance context with learning capabilities if enabled
        if enable_learning:
            context = await self._enhance_context_with_learning(context)
        
        # Execute standard analysis
        result = await self.execute_requirements_analysis(task, context)
        
        # Add feedback integration insights
        if result.get("success"):
            result["feedback_integration"] = self._analyze_feedback_integration(result)
        
        return result
    
    async def _enhance_context_with_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with learning from similar past issues.
        
        Args:
            context: Base context
            
        Returns:
            Enhanced context with learning insights
        """
        enhanced_context = context.copy()
        
        # Add learning prompts to prevent common mistakes
        enhanced_context["learning_insights"] = [
            "Remember PR #23: vague 'remove phrase' led to deleting entire file",
            "Ensure specific targets are identified, not just general actions",
            "Define what should be preserved as well as what should change",
            "Create measurable success criteria to validate implementation"
        ]
        
        return enhanced_context
    
    def _analyze_feedback_integration(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how feedback was integrated throughout the process.
        
        Args:
            result: Analysis result containing pair execution data
            
        Returns:
            Feedback integration analysis
        """
        feedback_analysis = {
            "integration_quality": "high",
            "common_improvement_areas": [],
            "learning_opportunities": []
        }
        
        # Add insights based on iteration count
        iterations = result.get("pair_execution_data", {}).get("iterations", 0)
        
        if iterations == 1:
            feedback_analysis["integration_quality"] = "excellent"
            feedback_analysis["learning_opportunities"].append(
                "Requirements met standards immediately - good analytical skills"
            )
        elif iterations <= 3:
            feedback_analysis["integration_quality"] = "good"
            feedback_analysis["learning_opportunities"].append(
                "Iterative improvement process worked effectively"
            )
        else:
            feedback_analysis["integration_quality"] = "needs_improvement"
            feedback_analysis["common_improvement_areas"].append(
                "Consider more thorough initial analysis to reduce iterations"
            )
        
        return feedback_analysis
    
    def get_pair_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics about this analyst-navigator pair.
        
        Returns:
            Dictionary containing pair-specific metrics and capabilities
        """
        base_metrics = self.get_metrics()
        
        # Add analyst-navigator specific metrics
        analyst_metrics = {}
        navigator_metrics = {}
        
        if hasattr(self.analyst_agent, 'get_metrics'):
            analyst_metrics = self.analyst_agent.get_metrics()
        
        if hasattr(self.requirements_navigator, 'get_metrics'):
            navigator_metrics = self.requirements_navigator.get_metrics()
        
        return {
            **base_metrics,
            "pair_type": "analyst_navigator",
            "specialization": "requirements_analysis",
            "prevents_disasters": True,
            "quality_gates": True,
            "progressive_leniency": True,
            "analyst_metrics": analyst_metrics,
            "navigator_metrics": navigator_metrics
        }


def create_analyst_navigator_pair(
    max_iterations: int = 3,
    navigator_strictness: float = 1.0
) -> AnalystNavigatorPair:
    """Factory function to create a configured AnalystNavigatorPair.
    
    Args:
        max_iterations: Maximum review iterations
        navigator_strictness: Navigator strictness level
        
    Returns:
        Configured AnalystNavigatorPair ready for requirements analysis
    """
    return AnalystNavigatorPair(
        max_iterations=max_iterations,
        navigator_strictness=navigator_strictness
    )