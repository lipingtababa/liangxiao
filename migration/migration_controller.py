"""
Migration controller for managing transition between TypeScript and Python systems.

Provides safe switching, rollback capabilities, and gradual migration support.
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional
import redis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class SystemMode(str, Enum):
    """Migration system modes for different phases of transition."""
    TYPESCRIPT_ONLY = "typescript_only"          # Legacy system only
    PYTHON_ONLY = "python_only"                 # New system only  
    PARALLEL_COMPARISON = "parallel_comparison"  # Both systems, compare results
    GRADUAL_ROLLOUT = "gradual_rollout"         # Percentage-based split
    EMERGENCY_ROLLBACK = "emergency_rollback"    # Emergency fallback


@dataclass
class MigrationTransition:
    """Represents a mode transition for audit trail."""
    timestamp: datetime
    from_mode: SystemMode
    to_mode: SystemMode
    reason: str
    initiated_by: str


class MigrationController:
    """
    Controls migration from TypeScript to Python system.
    
    Provides safe switching, rollback, and parallel execution with comprehensive
    logging and safety mechanisms.
    
    Features:
    - Feature flag system for gradual rollout
    - Consistent routing based on issue number hashing
    - Emergency rollback capability
    - Audit trail of all transitions
    - Health monitoring integration
    - Configurable rollout percentages
    """
    
    REDIS_MODE_KEY = "migration:system_mode"
    REDIS_PERCENTAGE_KEY = "migration:rollout_percentage"
    REDIS_TRANSITIONS_KEY = "migration:transitions"
    REDIS_HEALTH_KEY = "migration:system_health"
    REDIS_STATS_KEY = "migration:statistics"
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize migration controller.
        
        Args:
            redis_client: Redis client for state persistence
        """
        self.redis = redis_client
        self.system_mode = self._get_current_mode()
        
        # Initialize default values if not set
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default values in Redis if not already set."""
        if not self.redis.exists(self.REDIS_MODE_KEY):
            self.redis.set(self.REDIS_MODE_KEY, SystemMode.TYPESCRIPT_ONLY.value)
            
        if not self.redis.exists(self.REDIS_PERCENTAGE_KEY):
            self.redis.set(self.REDIS_PERCENTAGE_KEY, "0")
            
        if not self.redis.exists(self.REDIS_HEALTH_KEY):
            default_health = {
                "python_system": True,
                "typescript_system": True,
                "last_check": datetime.now().isoformat()
            }
            self.redis.set(self.REDIS_HEALTH_KEY, json.dumps(default_health))
    
    def _get_current_mode(self) -> SystemMode:
        """Get current system mode from Redis with fallback."""
        try:
            mode = self.redis.get(self.REDIS_MODE_KEY)
            if mode:
                return SystemMode(mode.decode())
            return SystemMode.TYPESCRIPT_ONLY  # Safe default
        except Exception as e:
            logger.error(f"Failed to get current mode from Redis: {e}")
            return SystemMode.TYPESCRIPT_ONLY
    
    def set_system_mode(
        self, 
        mode: SystemMode, 
        reason: str = "Manual change",
        initiated_by: str = "system"
    ) -> bool:
        """
        Change system mode with validation and audit trail.
        
        Args:
            mode: New system mode to set
            reason: Reason for the change (for audit trail)
            initiated_by: Who/what initiated the change
            
        Returns:
            True if mode change was successful, False otherwise
        """
        try:
            old_mode = self.system_mode
            
            # Validate transition is allowed
            if not self._is_valid_transition(old_mode, mode):
                logger.error(f"Invalid transition attempted: {old_mode} -> {mode}")
                return False
            
            # Set new mode in Redis
            self.redis.set(self.REDIS_MODE_KEY, mode.value)
            self.system_mode = mode
            
            # Record transition in audit trail
            transition = MigrationTransition(
                timestamp=datetime.now(),
                from_mode=old_mode,
                to_mode=mode,
                reason=reason,
                initiated_by=initiated_by
            )
            self._record_transition(transition)
            
            # Update metrics
            self._update_migration_metrics(mode)
            
            logger.info(f"System mode changed: {old_mode} -> {mode} ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change system mode to {mode}: {e}")
            return False
    
    def _is_valid_transition(self, from_mode: SystemMode, to_mode: SystemMode) -> bool:
        """
        Validate if a mode transition is allowed.
        
        Args:
            from_mode: Current system mode
            to_mode: Desired system mode
            
        Returns:
            True if transition is valid
        """
        # Emergency rollback is always allowed
        if to_mode == SystemMode.EMERGENCY_ROLLBACK:
            return True
            
        # From emergency rollback, only allow typescript_only
        if from_mode == SystemMode.EMERGENCY_ROLLBACK:
            return to_mode == SystemMode.TYPESCRIPT_ONLY
            
        # Other transitions are generally allowed
        # Could add more specific business rules here
        return True
    
    def _record_transition(self, transition: MigrationTransition) -> None:
        """Record transition in Redis for audit trail."""
        try:
            transition_data = asdict(transition)
            # Convert datetime to ISO string for JSON serialization
            transition_data['timestamp'] = transition.timestamp.isoformat()
            
            # Add to list of recent transitions (keep last 100)
            self.redis.lpush(
                self.REDIS_TRANSITIONS_KEY, 
                json.dumps(transition_data)
            )
            self.redis.ltrim(self.REDIS_TRANSITIONS_KEY, 0, 99)
            
        except Exception as e:
            logger.error(f"Failed to record transition: {e}")
    
    def should_use_python_system(self, issue_number: int) -> bool:
        """
        Determine if issue should be processed by Python system.
        
        Uses consistent hashing based on issue number to ensure
        the same issue always routes to the same system during
        gradual rollout.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            True if issue should use Python system
        """
        mode = self._get_current_mode()
        
        if mode == SystemMode.TYPESCRIPT_ONLY:
            return False
        elif mode == SystemMode.PYTHON_ONLY:
            return True
        elif mode == SystemMode.PARALLEL_COMPARISON:
            return True  # Both systems process
        elif mode == SystemMode.GRADUAL_ROLLOUT:
            rollout_percentage = self._get_rollout_percentage()
            return self._should_route_to_python(issue_number, rollout_percentage)
        else:  # EMERGENCY_ROLLBACK
            return False
    
    def should_use_typescript_system(self, issue_number: int) -> bool:
        """
        Determine if issue should be processed by TypeScript system.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            True if issue should use TypeScript system
        """
        mode = self._get_current_mode()
        
        if mode == SystemMode.TYPESCRIPT_ONLY:
            return True
        elif mode == SystemMode.PYTHON_ONLY:
            return False
        elif mode == SystemMode.PARALLEL_COMPARISON:
            return True  # Both systems process
        elif mode == SystemMode.GRADUAL_ROLLOUT:
            rollout_percentage = self._get_rollout_percentage()
            return not self._should_route_to_python(issue_number, rollout_percentage)
        else:  # EMERGENCY_ROLLBACK
            return True
    
    def _should_route_to_python(self, issue_number: int, percentage: int) -> bool:
        """
        Consistent routing decision based on issue number hash.
        
        Uses modulo operation to ensure same issue always routes
        to same system during gradual rollout.
        
        Args:
            issue_number: GitHub issue number
            percentage: Rollout percentage (0-100)
            
        Returns:
            True if issue should route to Python system
        """
        return (issue_number % 100) < percentage
    
    def _get_rollout_percentage(self) -> int:
        """Get current rollout percentage from Redis."""
        try:
            percentage = self.redis.get(self.REDIS_PERCENTAGE_KEY)
            return int(percentage.decode()) if percentage else 0
        except Exception as e:
            logger.error(f"Failed to get rollout percentage: {e}")
            return 0
    
    def set_rollout_percentage(self, percentage: int) -> bool:
        """
        Set rollout percentage for gradual migration.
        
        Args:
            percentage: Percentage of traffic to route to Python (0-100)
            
        Returns:
            True if percentage was set successfully
        """
        if not 0 <= percentage <= 100:
            logger.error(f"Invalid rollout percentage: {percentage} (must be 0-100)")
            return False
            
        try:
            self.redis.set(self.REDIS_PERCENTAGE_KEY, str(percentage))
            logger.info(f"Rollout percentage set to {percentage}%")
            return True
        except Exception as e:
            logger.error(f"Failed to set rollout percentage: {e}")
            return False
    
    def emergency_rollback(self, reason: str, initiated_by: str = "system") -> bool:
        """
        Immediately rollback to TypeScript system.
        
        Args:
            reason: Reason for emergency rollback
            initiated_by: Who/what initiated the rollback
            
        Returns:
            True if rollback was successful
        """
        logger.critical(f"EMERGENCY ROLLBACK triggered: {reason}")
        
        success = self.set_system_mode(
            SystemMode.EMERGENCY_ROLLBACK,
            f"EMERGENCY: {reason}",
            initiated_by
        )
        
        if success:
            # Send alert notifications (if configured)
            self._send_emergency_alert(reason)
            
        return success
    
    def _send_emergency_alert(self, reason: str) -> None:
        """Send emergency alert notifications."""
        # TODO: Implement alerting system (Slack, email, PagerDuty, etc.)
        logger.critical(f"EMERGENCY ALERT: Migration rollback triggered - {reason}")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive migration status.
        
        Returns:
            Dictionary containing current migration state and metrics
        """
        try:
            return {
                "current_mode": self.system_mode.value,
                "rollout_percentage": self._get_rollout_percentage(),
                "system_health": self._get_system_health(),
                "recent_transitions": self._get_recent_transitions(),
                "statistics": self._get_migration_statistics(),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                "current_mode": "unknown",
                "error": str(e)
            }
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            health_data = self.redis.get(self.REDIS_HEALTH_KEY)
            if health_data:
                return json.loads(health_data.decode())
            return {
                "python_system": False,
                "typescript_system": False,
                "last_check": "never"
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}
    
    def update_system_health(
        self, 
        python_healthy: bool, 
        typescript_healthy: bool
    ) -> None:
        """
        Update system health status.
        
        Args:
            python_healthy: Whether Python system is healthy
            typescript_healthy: Whether TypeScript system is healthy
        """
        try:
            health_data = {
                "python_system": python_healthy,
                "typescript_system": typescript_healthy,
                "last_check": datetime.now().isoformat()
            }
            self.redis.set(self.REDIS_HEALTH_KEY, json.dumps(health_data))
            
            # Check if emergency rollback is needed
            if (self.system_mode == SystemMode.PYTHON_ONLY and 
                not python_healthy and typescript_healthy):
                self.emergency_rollback(
                    "Python system unhealthy, TypeScript available",
                    "health_monitor"
                )
                
        except Exception as e:
            logger.error(f"Failed to update system health: {e}")
    
    def _get_recent_transitions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent mode transitions from audit trail."""
        try:
            transitions = self.redis.lrange(self.REDIS_TRANSITIONS_KEY, 0, limit - 1)
            return [json.loads(t.decode()) for t in transitions]
        except Exception as e:
            logger.error(f"Failed to get recent transitions: {e}")
            return []
    
    def _update_migration_metrics(self, mode: SystemMode) -> None:
        """Update migration statistics."""
        try:
            stats_key = f"{self.REDIS_STATS_KEY}:{mode.value}"
            self.redis.incr(stats_key)
            self.redis.incr(f"{self.REDIS_STATS_KEY}:total_transitions")
        except Exception as e:
            logger.error(f"Failed to update migration metrics: {e}")
    
    def _get_migration_statistics(self) -> Dict[str, Any]:
        """Get migration statistics."""
        try:
            stats = {}
            for mode in SystemMode:
                key = f"{self.REDIS_STATS_KEY}:{mode.value}"
                count = self.redis.get(key)
                stats[mode.value] = int(count.decode()) if count else 0
            
            total_key = f"{self.REDIS_STATS_KEY}:total_transitions"
            total = self.redis.get(total_key)
            stats["total_transitions"] = int(total.decode()) if total else 0
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get migration statistics: {e}")
            return {}
    
    def get_routing_preview(self, issue_numbers: List[int]) -> Dict[str, List[int]]:
        """
        Preview how issues would be routed in current mode.
        
        Useful for testing and validation before changing modes.
        
        Args:
            issue_numbers: List of issue numbers to test
            
        Returns:
            Dictionary showing which system each issue would use
        """
        python_issues = []
        typescript_issues = []
        both_systems = []
        
        for issue_num in issue_numbers:
            use_python = self.should_use_python_system(issue_num)
            use_typescript = self.should_use_typescript_system(issue_num)
            
            if use_python and use_typescript:
                both_systems.append(issue_num)
            elif use_python:
                python_issues.append(issue_num)
            elif use_typescript:
                typescript_issues.append(issue_num)
        
        return {
            "python_only": python_issues,
            "typescript_only": typescript_issues,
            "both_systems": both_systems,
            "current_mode": self.system_mode.value,
            "rollout_percentage": self._get_rollout_percentage()
        }