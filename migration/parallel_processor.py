"""
Parallel processing manager for safe comparison between TypeScript and Python systems.

Prevents conflicts when both systems process the same issue during migration,
provides result comparison, and ensures data consistency.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
import redis
from enum import Enum

from models.github import IssueEvent
from .typescript_client import TypeScriptResponse

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Status of parallel processing for an issue."""
    PENDING = "pending"
    PYTHON_PROCESSING = "python_processing"
    TYPESCRIPT_PROCESSING = "typescript_processing"
    BOTH_PROCESSING = "both_processing"
    PYTHON_COMPLETED = "python_completed"
    TYPESCRIPT_COMPLETED = "typescript_completed"
    BOTH_COMPLETED = "both_completed"
    COMPARISON_COMPLETE = "comparison_complete"
    ERROR = "error"


@dataclass
class ProcessingResult:
    """Result from a single system processing an issue."""
    system: str
    issue_number: int
    workflow_id: Optional[str]
    success: bool
    duration_seconds: float
    timestamp: datetime
    message: str
    error_details: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[str]] = None  # File paths, URLs, etc.


@dataclass
class ComparisonResult:
    """Result of comparing outputs from both systems."""
    issue_number: int
    comparison_timestamp: datetime
    python_result: ProcessingResult
    typescript_result: ProcessingResult
    
    # Comparison metrics
    both_successful: bool
    duration_difference_seconds: float
    quality_comparison: Optional[Dict[str, Any]] = None
    output_similarity: Optional[float] = None  # 0.0-1.0 similarity score
    
    # Analysis
    recommended_system: Optional[str] = None
    confidence_score: Optional[float] = None
    issues_found: Optional[List[str]] = None


class ParallelProcessingManager:
    """
    Manages parallel processing to prevent conflicts and enable comparison.
    
    Features:
    - Issue locking to prevent race conditions
    - Status tracking for both systems
    - Result comparison and analysis
    - Conflict detection and resolution
    - Performance metrics collection
    - Data consistency validation
    """
    
    REDIS_LOCK_KEY = "parallel:locks"
    REDIS_STATUS_KEY = "parallel:status"
    REDIS_RESULTS_KEY = "parallel:results"
    REDIS_COMPARISON_KEY = "parallel:comparisons"
    REDIS_CONFLICTS_KEY = "parallel:conflicts"
    
    LOCK_TTL_SECONDS = 1800  # 30 minutes
    RESULT_TTL_DAYS = 7      # Keep results for 7 days
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize parallel processing manager.
        
        Args:
            redis_client: Redis client for coordination and storage
        """
        self.redis = redis_client
    
    async def acquire_processing_lock(
        self,
        issue_number: int,
        system: str,
        workflow_id: str
    ) -> bool:
        """
        Acquire processing lock for an issue to prevent conflicts.
        
        Args:
            issue_number: GitHub issue number
            system: Processing system ('python' or 'typescript')
            workflow_id: Workflow identifier
            
        Returns:
            True if lock was acquired successfully
        """
        try:
            lock_key = f"{self.REDIS_LOCK_KEY}:{issue_number}:{system}"
            status_key = f"{self.REDIS_STATUS_KEY}:{issue_number}"
            
            # Create lock entry with TTL
            lock_data = {
                "system": system,
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "status": "processing"
            }
            
            # Use SET with NX (only set if key doesn't exist) and EX (expiry)
            success = self.redis.set(
                lock_key,
                json.dumps(lock_data),
                nx=True,
                ex=self.LOCK_TTL_SECONDS
            )
            
            if success:
                # Update processing status
                await self._update_processing_status(issue_number, system, "processing")
                
                logger.info(
                    f"Acquired processing lock: issue #{issue_number}, "
                    f"system={system}, workflow={workflow_id}"
                )
                return True
            else:
                logger.warning(
                    f"Failed to acquire processing lock: issue #{issue_number}, "
                    f"system={system} (already locked)"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error acquiring processing lock: {e}")
            return False
    
    async def release_processing_lock(
        self,
        issue_number: int,
        system: str,
        workflow_id: str
    ) -> None:
        """
        Release processing lock for an issue.
        
        Args:
            issue_number: GitHub issue number
            system: Processing system
            workflow_id: Workflow identifier (for verification)
        """
        try:
            lock_key = f"{self.REDIS_LOCK_KEY}:{issue_number}:{system}"
            
            # Verify this workflow owns the lock before releasing
            lock_data = self.redis.get(lock_key)
            if lock_data:
                current_lock = json.loads(lock_data.decode())
                if current_lock.get("workflow_id") == workflow_id:
                    self.redis.delete(lock_key)
                    logger.info(
                        f"Released processing lock: issue #{issue_number}, "
                        f"system={system}, workflow={workflow_id}"
                    )
                else:
                    logger.warning(
                        f"Cannot release lock - workflow ID mismatch: "
                        f"issue #{issue_number}, system={system}"
                    )
            
        except Exception as e:
            logger.error(f"Error releasing processing lock: {e}")
    
    async def _update_processing_status(
        self,
        issue_number: int,
        system: str,
        status: str
    ) -> None:
        """Update the processing status for an issue."""
        try:
            status_key = f"{self.REDIS_STATUS_KEY}:{issue_number}"
            
            # Get current status
            current_data = self.redis.get(status_key)
            if current_data:
                status_info = json.loads(current_data.decode())
            else:
                status_info = {
                    "issue_number": issue_number,
                    "python_status": "pending",
                    "typescript_status": "pending",
                    "overall_status": ProcessingStatus.PENDING.value,
                    "created_at": datetime.now().isoformat()
                }
            
            # Update system-specific status
            status_info[f"{system}_status"] = status
            status_info["last_updated"] = datetime.now().isoformat()
            
            # Determine overall status
            python_status = status_info.get("python_status", "pending")
            typescript_status = status_info.get("typescript_status", "pending")
            
            if python_status == "processing" and typescript_status == "processing":
                overall_status = ProcessingStatus.BOTH_PROCESSING
            elif python_status == "processing":
                overall_status = ProcessingStatus.PYTHON_PROCESSING
            elif typescript_status == "processing":
                overall_status = ProcessingStatus.TYPESCRIPT_PROCESSING
            elif python_status == "completed" and typescript_status == "completed":
                overall_status = ProcessingStatus.BOTH_COMPLETED
            elif python_status == "completed":
                overall_status = ProcessingStatus.PYTHON_COMPLETED
            elif typescript_status == "completed":
                overall_status = ProcessingStatus.TYPESCRIPT_COMPLETED
            else:
                overall_status = ProcessingStatus.PENDING
            
            status_info["overall_status"] = overall_status.value
            
            # Store with TTL
            self.redis.setex(
                status_key,
                timedelta(days=self.RESULT_TTL_DAYS),
                json.dumps(status_info)
            )
            
        except Exception as e:
            logger.error(f"Error updating processing status: {e}")
    
    async def record_processing_result(
        self,
        result: ProcessingResult
    ) -> None:
        """
        Record the result of processing from one system.
        
        Args:
            result: Processing result to record
        """
        try:
            result_key = f"{self.REDIS_RESULTS_KEY}:{result.issue_number}:{result.system}"
            
            # Convert result to dict for JSON serialization
            result_dict = asdict(result)
            result_dict['timestamp'] = result.timestamp.isoformat()
            
            # Store result with TTL
            self.redis.setex(
                result_key,
                timedelta(days=self.RESULT_TTL_DAYS),
                json.dumps(result_dict)
            )
            
            # Update processing status
            await self._update_processing_status(
                result.issue_number,
                result.system,
                "completed"
            )
            
            logger.info(
                f"Recorded processing result: issue #{result.issue_number}, "
                f"system={result.system}, success={result.success}"
            )
            
            # Check if both systems have completed for comparison
            await self._check_for_comparison_opportunity(result.issue_number)
            
        except Exception as e:
            logger.error(f"Error recording processing result: {e}")
    
    async def _check_for_comparison_opportunity(self, issue_number: int) -> None:
        """Check if both systems have completed and trigger comparison."""
        try:
            python_key = f"{self.REDIS_RESULTS_KEY}:{issue_number}:python"
            typescript_key = f"{self.REDIS_RESULTS_KEY}:{issue_number}:typescript"
            
            python_data = self.redis.get(python_key)
            typescript_data = self.redis.get(typescript_key)
            
            if python_data and typescript_data:
                # Both systems completed - perform comparison
                python_result = self._deserialize_result(python_data.decode())
                typescript_result = self._deserialize_result(typescript_data.decode())
                
                comparison = await self._compare_results(python_result, typescript_result)
                await self._store_comparison(comparison)
                
                # Update overall status
                await self._update_processing_status(
                    issue_number,
                    "comparison",
                    "complete"
                )
                
                logger.info(f"Completed comparison for issue #{issue_number}")
                
        except Exception as e:
            logger.error(f"Error checking for comparison opportunity: {e}")
    
    def _deserialize_result(self, data: str) -> ProcessingResult:
        """Deserialize processing result from JSON."""
        result_dict = json.loads(data)
        result_dict['timestamp'] = datetime.fromisoformat(result_dict['timestamp'])
        return ProcessingResult(**result_dict)
    
    async def _compare_results(
        self,
        python_result: ProcessingResult,
        typescript_result: ProcessingResult
    ) -> ComparisonResult:
        """
        Compare results from both systems.
        
        Args:
            python_result: Result from Python system
            typescript_result: Result from TypeScript system
            
        Returns:
            Detailed comparison analysis
        """
        try:
            # Basic comparison metrics
            both_successful = python_result.success and typescript_result.success
            duration_diff = python_result.duration_seconds - typescript_result.duration_seconds
            
            # Quality comparison (if both have quality metrics)
            quality_comparison = None
            if (python_result.quality_metrics and typescript_result.quality_metrics):
                quality_comparison = self._compare_quality_metrics(
                    python_result.quality_metrics,
                    typescript_result.quality_metrics
                )
            
            # Determine recommended system based on performance
            recommended_system, confidence = self._determine_recommendation(
                python_result, typescript_result
            )
            
            # Identify any issues or concerns
            issues_found = self._identify_issues(python_result, typescript_result)
            
            comparison = ComparisonResult(
                issue_number=python_result.issue_number,
                comparison_timestamp=datetime.now(),
                python_result=python_result,
                typescript_result=typescript_result,
                both_successful=both_successful,
                duration_difference_seconds=duration_diff,
                quality_comparison=quality_comparison,
                recommended_system=recommended_system,
                confidence_score=confidence,
                issues_found=issues_found
            )
            
            logger.info(
                f"Compared results for issue #{python_result.issue_number}: "
                f"both_successful={both_successful}, "
                f"duration_diff={duration_diff:.2f}s, "
                f"recommended={recommended_system}"
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing results: {e}")
            # Return basic comparison on error
            return ComparisonResult(
                issue_number=python_result.issue_number,
                comparison_timestamp=datetime.now(),
                python_result=python_result,
                typescript_result=typescript_result,
                both_successful=False,
                duration_difference_seconds=0.0,
                issues_found=[f"Comparison error: {str(e)}"]
            )
    
    def _compare_quality_metrics(
        self,
        python_metrics: Dict[str, Any],
        typescript_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare quality metrics between systems."""
        comparison = {}
        
        # Compare common metrics
        common_metrics = set(python_metrics.keys()) & set(typescript_metrics.keys())
        
        for metric in common_metrics:
            python_value = python_metrics[metric]
            typescript_value = typescript_metrics[metric]
            
            if isinstance(python_value, (int, float)) and isinstance(typescript_value, (int, float)):
                comparison[metric] = {
                    "python": python_value,
                    "typescript": typescript_value,
                    "difference": python_value - typescript_value,
                    "improvement_percent": (
                        (python_value - typescript_value) / typescript_value * 100
                        if typescript_value != 0 else 0
                    )
                }
            else:
                comparison[metric] = {
                    "python": python_value,
                    "typescript": typescript_value,
                    "match": python_value == typescript_value
                }
        
        # Note metrics that are only in one system
        python_only = set(python_metrics.keys()) - set(typescript_metrics.keys())
        typescript_only = set(typescript_metrics.keys()) - set(python_metrics.keys())
        
        if python_only:
            comparison["python_exclusive_metrics"] = {
                metric: python_metrics[metric] for metric in python_only
            }
        
        if typescript_only:
            comparison["typescript_exclusive_metrics"] = {
                metric: typescript_metrics[metric] for metric in typescript_only
            }
        
        return comparison
    
    def _determine_recommendation(
        self,
        python_result: ProcessingResult,
        typescript_result: ProcessingResult
    ) -> Tuple[Optional[str], Optional[float]]:
        """Determine which system performed better and confidence level."""
        try:
            # Score each system (0.0 - 1.0)
            python_score = self._calculate_result_score(python_result)
            typescript_score = self._calculate_result_score(typescript_result)
            
            # Determine recommendation
            if python_score > typescript_score:
                confidence = min((python_score - typescript_score) / python_score, 1.0)
                return "python", confidence
            elif typescript_score > python_score:
                confidence = min((typescript_score - python_score) / typescript_score, 1.0)
                return "typescript", confidence
            else:
                return None, 0.5  # Tie
                
        except Exception as e:
            logger.error(f"Error determining recommendation: {e}")
            return None, 0.0
    
    def _calculate_result_score(self, result: ProcessingResult) -> float:
        """Calculate overall score for a processing result."""
        score = 0.0
        
        # Success/failure (50% weight)
        if result.success:
            score += 0.5
        
        # Duration (25% weight, faster is better)
        max_duration = 600  # 10 minutes baseline
        if result.duration_seconds <= max_duration:
            duration_score = 1.0 - (result.duration_seconds / max_duration)
            score += duration_score * 0.25
        
        # Quality metrics (25% weight)
        if result.quality_metrics:
            quality_score = self._extract_quality_score(result.quality_metrics)
            score += quality_score * 0.25
        
        return min(score, 1.0)
    
    def _extract_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Extract overall quality score from metrics."""
        # This is a simple implementation - can be enhanced based on actual metrics
        scores = []
        
        # Extract numeric quality metrics
        for key, value in quality_metrics.items():
            if isinstance(value, (int, float)) and 0 <= value <= 1:
                scores.append(value)
            elif key == "test_coverage" and isinstance(value, (int, float)):
                scores.append(min(value / 100.0, 1.0))  # Convert percentage
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _identify_issues(
        self,
        python_result: ProcessingResult,
        typescript_result: ProcessingResult
    ) -> List[str]:
        """Identify potential issues or concerns from the comparison."""
        issues = []
        
        # Check if both systems failed
        if not python_result.success and not typescript_result.success:
            issues.append("Both systems failed to process the issue")
        
        # Check for significant duration differences
        duration_diff = abs(python_result.duration_seconds - typescript_result.duration_seconds)
        if duration_diff > 300:  # 5 minutes
            slower_system = "python" if python_result.duration_seconds > typescript_result.duration_seconds else "typescript"
            issues.append(f"{slower_system} system was significantly slower ({duration_diff:.1f}s difference)")
        
        # Check for timeout issues
        if python_result.duration_seconds > 600:
            issues.append("Python system took longer than 10 minutes")
        if typescript_result.duration_seconds > 600:
            issues.append("TypeScript system took longer than 10 minutes")
        
        # Check for error patterns
        if python_result.error_details:
            issues.append(f"Python system error: {python_result.error_details.get('exception', 'Unknown error')}")
        if typescript_result.error_details:
            issues.append(f"TypeScript system error: {typescript_result.error_details.get('exception', 'Unknown error')}")
        
        return issues
    
    async def _store_comparison(self, comparison: ComparisonResult) -> None:
        """Store comparison result for analysis."""
        try:
            comparison_key = f"{self.REDIS_COMPARISON_KEY}:{comparison.issue_number}"
            
            # Convert to dict for JSON serialization
            comparison_dict = asdict(comparison)
            comparison_dict['comparison_timestamp'] = comparison.comparison_timestamp.isoformat()
            
            # Handle nested ProcessingResult objects
            comparison_dict['python_result']['timestamp'] = comparison.python_result.timestamp.isoformat()
            comparison_dict['typescript_result']['timestamp'] = comparison.typescript_result.timestamp.isoformat()
            
            # Store with TTL
            self.redis.setex(
                comparison_key,
                timedelta(days=self.RESULT_TTL_DAYS),
                json.dumps(comparison_dict)
            )
            
            # Add to timeline for analysis
            score = comparison.comparison_timestamp.timestamp()
            self.redis.zadd(
                f"{self.REDIS_COMPARISON_KEY}:timeline",
                {comparison_key: score}
            )
            
        except Exception as e:
            logger.error(f"Error storing comparison: {e}")
    
    async def get_processing_status(self, issue_number: int) -> Dict[str, Any]:
        """
        Get current processing status for an issue.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Processing status information
        """
        try:
            status_key = f"{self.REDIS_STATUS_KEY}:{issue_number}"
            status_data = self.redis.get(status_key)
            
            if status_data:
                return json.loads(status_data.decode())
            else:
                return {
                    "issue_number": issue_number,
                    "python_status": "not_started",
                    "typescript_status": "not_started",
                    "overall_status": ProcessingStatus.PENDING.value
                }
                
        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return {"error": str(e)}
    
    async def get_comparison_result(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """
        Get comparison result for an issue.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Comparison result if available
        """
        try:
            comparison_key = f"{self.REDIS_COMPARISON_KEY}:{issue_number}"
            comparison_data = self.redis.get(comparison_key)
            
            if comparison_data:
                return json.loads(comparison_data.decode())
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting comparison result: {e}")
            return None
    
    async def get_recent_comparisons(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent comparison results for analysis."""
        try:
            timeline_key = f"{self.REDIS_COMPARISON_KEY}:timeline"
            recent_keys = self.redis.zrevrange(timeline_key, 0, limit - 1)
            
            comparisons = []
            for key in recent_keys:
                try:
                    comparison_data = self.redis.get(key)
                    if comparison_data:
                        comparisons.append(json.loads(comparison_data.decode()))
                except Exception as e:
                    logger.warning(f"Failed to load comparison {key}: {e}")
            
            return comparisons
            
        except Exception as e:
            logger.error(f"Error getting recent comparisons: {e}")
            return []
    
    async def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect potential processing conflicts."""
        try:
            conflicts = []
            
            # Find issues with locks from both systems
            lock_pattern = f"{self.REDIS_LOCK_KEY}:*"
            lock_keys = self.redis.keys(lock_pattern)
            
            # Group by issue number
            issue_locks = {}
            for key in lock_keys:
                key_str = key.decode()
                parts = key_str.split(":")
                if len(parts) >= 3:
                    issue_number = int(parts[2])
                    system = parts[3] if len(parts) > 3 else "unknown"
                    
                    if issue_number not in issue_locks:
                        issue_locks[issue_number] = []
                    
                    lock_data = self.redis.get(key)
                    if lock_data:
                        lock_info = json.loads(lock_data.decode())
                        lock_info['system'] = system
                        issue_locks[issue_number].append(lock_info)
            
            # Identify conflicts (multiple locks for same issue)
            for issue_number, locks in issue_locks.items():
                if len(locks) > 1:
                    conflicts.append({
                        "issue_number": issue_number,
                        "conflict_type": "multiple_locks",
                        "locks": locks,
                        "detected_at": datetime.now().isoformat()
                    })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []
    
    async def resolve_conflict(self, issue_number: int, preferred_system: str) -> bool:
        """
        Resolve processing conflict by preferring one system.
        
        Args:
            issue_number: Issue with conflict
            preferred_system: System to prefer ('python' or 'typescript')
            
        Returns:
            True if conflict was resolved
        """
        try:
            # Remove locks from non-preferred system
            other_system = "typescript" if preferred_system == "python" else "python"
            other_lock_key = f"{self.REDIS_LOCK_KEY}:{issue_number}:{other_system}"
            
            deleted = self.redis.delete(other_lock_key)
            
            if deleted:
                logger.info(
                    f"Resolved conflict for issue #{issue_number}: "
                    f"preferred {preferred_system}, removed {other_system} lock"
                )
                
                # Record conflict resolution
                conflict_key = f"{self.REDIS_CONFLICTS_KEY}:{issue_number}:{datetime.now().timestamp()}"
                conflict_data = {
                    "issue_number": issue_number,
                    "preferred_system": preferred_system,
                    "removed_system": other_system,
                    "resolved_at": datetime.now().isoformat(),
                    "resolution_method": "manual"
                }
                
                self.redis.setex(
                    conflict_key,
                    timedelta(days=7),
                    json.dumps(conflict_data)
                )
                
                return True
            else:
                logger.warning(f"No conflict found for issue #{issue_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error resolving conflict for issue #{issue_number}: {e}")
            return False