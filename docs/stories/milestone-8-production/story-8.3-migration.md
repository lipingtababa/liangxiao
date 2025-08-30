# Story 8.3: Migration Strategy

## Story Details
- **ID**: 8.3
- **Title**: Implement Safe Migration from TypeScript
- **Milestone**: Milestone 8 - Production Deployment
- **Points**: 8
- **Priority**: P1 (Essential)
- **Dependencies**: Stories 7.1 (End-to-End), 8.1 (Containerization), 8.2 (Monitoring)

## Description

### Overview
Implement a safe, reversible migration strategy from the current broken TypeScript single-agent system to the new Python multi-agent system. This includes feature flags, parallel processing, rollback mechanisms, and performance validation to ensure zero disruption.

### Why This Is Important
- Enables confident production deployment
- Provides safety net if issues arise
- Allows performance comparison between systems
- Ensures business continuity during transition
- Validates new system works in production

### Context
The current TypeScript system produces disasters like PR #23, but it's what's currently deployed. We need to migrate to the new Python system without breaking anything, with the ability to quickly rollback if needed.

## Acceptance Criteria

### Required
- [ ] Feature flag system to switch between TypeScript and Python agents
- [ ] Parallel processing mode to run both systems simultaneously
- [ ] Performance comparison metrics between old and new systems
- [ ] Rollback mechanism to instantly switch back to TypeScript
- [ ] Quality metrics tracking (PR acceptance rate, build success rate)
- [ ] Gradual rollout capability (percentage-based traffic splitting)
- [ ] Safety checks to prevent both systems processing the same issue
- [ ] Migration status dashboard for monitoring
- [ ] Automated rollback triggers for quality degradation
- [ ] Complete system health monitoring during migration

## Technical Details

### Migration Architecture
```python
# migration/migration_controller.py
from enum import Enum
from typing import Optional, Dict, Any
import redis
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemMode(str, Enum):
    TYPESCRIPT_ONLY = "typescript_only"      # Legacy system only
    PYTHON_ONLY = "python_only"             # New system only
    PARALLEL_COMPARISON = "parallel"        # Both systems, compare results
    GRADUAL_ROLLOUT = "gradual"             # Percentage-based split
    EMERGENCY_ROLLBACK = "emergency_rollback" # Emergency fallback

class MigrationController:
    """
    Controls migration from TypeScript to Python system.
    
    Provides safe switching, rollback, and parallel execution.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.system_mode = self._get_current_mode()
        
    def _get_current_mode(self) -> SystemMode:
        """Get current system mode from Redis."""
        mode = self.redis.get("system_mode")
        if mode:
            return SystemMode(mode.decode())
        return SystemMode.TYPESCRIPT_ONLY  # Safe default
    
    def set_system_mode(self, mode: SystemMode, reason: str = "") -> bool:
        """
        Change system mode with logging and validation.
        
        Args:
            mode: New system mode
            reason: Reason for change (for audit trail)
            
        Returns:
            True if change successful
        """
        try:
            old_mode = self.system_mode
            
            # Validate transition is allowed
            if not self._is_valid_transition(old_mode, mode):
                logger.error(f"Invalid transition: {old_mode} -> {mode}")
                return False
            
            # Set new mode
            self.redis.set("system_mode", mode.value)
            self.system_mode = mode
            
            # Log change
            self._log_mode_change(old_mode, mode, reason)
            
            # Update metrics
            self._update_migration_metrics(mode)
            
            logger.info(f"System mode changed: {old_mode} -> {mode} ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change system mode: {e}")
            return False
    
    def should_use_python_system(self, issue_number: int) -> bool:
        """
        Determine if issue should be processed by Python system.
        
        Based on current mode and routing logic.
        """
        mode = self._get_current_mode()
        
        if mode == SystemMode.TYPESCRIPT_ONLY:
            return False
        elif mode == SystemMode.PYTHON_ONLY:
            return True
        elif mode == SystemMode.PARALLEL_COMPARISON:
            # Use both systems
            return True
        elif mode == SystemMode.GRADUAL_ROLLOUT:
            # Route based on percentage
            rollout_percentage = self._get_rollout_percentage()
            return self._should_route_to_python(issue_number, rollout_percentage)
        else:  # EMERGENCY_ROLLBACK
            return False
    
    def should_use_typescript_system(self, issue_number: int) -> bool:
        """Determine if issue should be processed by TypeScript system."""
        mode = self._get_current_mode()
        
        if mode == SystemMode.TYPESCRIPT_ONLY:
            return True
        elif mode == SystemMode.PYTHON_ONLY:
            return False
        elif mode == SystemMode.PARALLEL_COMPARISON:
            return True  # Use both
        elif mode == SystemMode.GRADUAL_ROLLOUT:
            return not self._should_route_to_python(
                issue_number, 
                self._get_rollout_percentage()
            )
        else:  # EMERGENCY_ROLLBACK
            return True
    
    def _should_route_to_python(self, issue_number: int, percentage: int) -> bool:
        """Consistent routing based on issue number hash."""
        return (issue_number % 100) < percentage
    
    def _get_rollout_percentage(self) -> int:
        """Get current rollout percentage (0-100)."""
        percentage = self.redis.get("rollout_percentage")
        return int(percentage.decode()) if percentage else 0
    
    def set_rollout_percentage(self, percentage: int) -> bool:
        """Set rollout percentage for gradual migration."""
        if not 0 <= percentage <= 100:
            return False
            
        self.redis.set("rollout_percentage", str(percentage))
        logger.info(f"Rollout percentage set to {percentage}%")
        return True
    
    def emergency_rollback(self, reason: str) -> bool:
        """Immediately rollback to TypeScript system."""
        return self.set_system_mode(
            SystemMode.EMERGENCY_ROLLBACK, 
            f"EMERGENCY: {reason}"
        )
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        return {
            "current_mode": self.system_mode.value,
            "rollout_percentage": self._get_rollout_percentage(),
            "python_system_health": self._check_python_health(),
            "typescript_system_health": self._check_typescript_health(),
            "recent_transitions": self._get_recent_transitions(),
            "performance_comparison": self._get_performance_comparison()
        }
```

### Webhook Router Enhancement
```python
# api/webhooks.py (enhanced for migration)
from migration.migration_controller import MigrationController
from legacy.typescript_client import TypeScriptAgentClient

migration_controller = MigrationController(redis_client)
typescript_client = TypeScriptAgentClient()

async def handle_issue_event(payload: dict):
    """Handle issue events with migration routing."""
    try:
        event = IssueEvent.model_validate(payload)
        
        if event.action not in ["opened", "edited", "labeled", "assigned"]:
            return {"status": "ignored", "action": event.action}
        
        issue_number = event.issue.number
        
        # Check migration routing
        use_python = migration_controller.should_use_python_system(issue_number)
        use_typescript = migration_controller.should_use_typescript_system(issue_number)
        
        results = []
        
        # Route to Python system
        if use_python:
            try:
                workflow_id = await orchestrator.start_workflow(event)
                results.append({
                    "system": "python",
                    "status": "workflow_started",
                    "workflow_id": workflow_id
                })
                logger.info(f"Issue #{issue_number} routed to Python system")
            except Exception as e:
                logger.error(f"Python system failed for issue #{issue_number}: {e}")
                
                # Auto-fallback in some cases
                if migration_controller.system_mode == SystemMode.PYTHON_ONLY:
                    migration_controller.emergency_rollback(f"Python system failure: {e}")
                    use_typescript = True
        
        # Route to TypeScript system  
        if use_typescript:
            try:
                response = await typescript_client.process_issue(event)
                results.append({
                    "system": "typescript",
                    "status": "processing_started",
                    "response": response
                })
                logger.info(f"Issue #{issue_number} routed to TypeScript system")
            except Exception as e:
                logger.error(f"TypeScript system failed for issue #{issue_number}: {e}")
        
        # Prevent duplicate processing
        if len(results) > 1:
            # Mark issue as being processed by both systems
            await mark_parallel_processing(issue_number, results)
        
        return {
            "status": "routed",
            "systems": results,
            "mode": migration_controller.system_mode
        }
        
    except Exception as e:
        logger.error(f"Failed to handle issue event: {e}")
        raise HTTPException(status_code=500, detail="Routing failed")
```

### Performance Monitoring
```python
# migration/performance_monitor.py
class PerformanceMonitor:
    """Monitor and compare system performance."""
    
    def track_workflow_completion(
        self,
        system: str,
        issue_number: int,
        success: bool,
        duration_seconds: float,
        quality_metrics: Dict[str, Any]
    ):
        """Track completion of issue processing."""
        
        # Store in time series database
        metrics = {
            "system": system,
            "issue_number": issue_number,
            "success": success,
            "duration": duration_seconds,
            "timestamp": datetime.now(),
            **quality_metrics
        }
        
        # Add to performance tracking
        self._store_performance_data(metrics)
        
        # Check for performance degradation
        self._check_performance_thresholds(system, metrics)
    
    def _check_performance_thresholds(self, system: str, metrics: Dict[str, Any]):
        """Check if performance has degraded significantly."""
        
        recent_success_rate = self._get_recent_success_rate(system)
        recent_avg_duration = self._get_recent_avg_duration(system)
        
        # Define thresholds
        if recent_success_rate < 0.7:  # Less than 70% success
            logger.warning(f"{system} success rate dropped to {recent_success_rate:.1%}")
            
            if system == "python":
                # Consider rollback
                self._trigger_rollback_evaluation("Low success rate")
        
        if recent_avg_duration > 600:  # More than 10 minutes average
            logger.warning(f"{system} average duration: {recent_avg_duration}s")
    
    def get_performance_comparison(self) -> Dict[str, Any]:
        """Compare performance between systems."""
        
        python_metrics = self._get_system_metrics("python")
        typescript_metrics = self._get_system_metrics("typescript")
        
        return {
            "python": python_metrics,
            "typescript": typescript_metrics,
            "comparison": {
                "success_rate_improvement": (
                    python_metrics["success_rate"] - 
                    typescript_metrics["success_rate"]
                ),
                "duration_improvement": (
                    typescript_metrics["avg_duration"] - 
                    python_metrics["avg_duration"]
                ),
                "quality_improvement": (
                    python_metrics["quality_score"] - 
                    typescript_metrics["quality_score"]
                )
            }
        }
```

### Migration Dashboard
```python
# api/migration_dashboard.py
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/migration/dashboard", response_class=HTMLResponse)
async def migration_dashboard():
    """Serve migration status dashboard."""
    
    status = migration_controller.get_migration_status()
    
    return f"""
    <html>
    <head><title>Migration Dashboard</title></head>
    <body>
        <h1>System Migration Status</h1>
        
        <div>
            <h2>Current Mode: {status['current_mode']}</h2>
            <p>Rollout: {status['rollout_percentage']}%</p>
        </div>
        
        <div>
            <h2>System Health</h2>
            <p>Python: {'✅' if status['python_system_health'] else '❌'}</p>
            <p>TypeScript: {'✅' if status['typescript_system_health'] else '❌'}</p>
        </div>
        
        <div>
            <h2>Performance Comparison</h2>
            <pre>{json.dumps(status['performance_comparison'], indent=2)}</pre>
        </div>
        
        <div>
            <h2>Quick Actions</h2>
            <button onclick="setMode('python_only')">Switch to Python Only</button>
            <button onclick="setMode('typescript_only')">Switch to TypeScript Only</button>
            <button onclick="emergencyRollback()">Emergency Rollback</button>
        </div>
    </body>
    </html>
    """

@router.post("/migration/mode/{mode}")
async def set_migration_mode(mode: str, reason: str = "Manual change"):
    """Change migration mode."""
    
    success = migration_controller.set_system_mode(
        SystemMode(mode), 
        reason
    )
    
    return {"success": success, "new_mode": mode}

@router.post("/migration/rollback")
async def emergency_rollback(reason: str = "Manual rollback"):
    """Trigger emergency rollback."""
    
    success = migration_controller.emergency_rollback(reason)
    return {"success": success, "mode": "emergency_rollback"}
```

## Testing Requirements

### Migration Tests
```python
# tests/test_migration.py
import pytest
from migration.migration_controller import MigrationController

def test_routing_logic():
    """Test issue routing between systems."""
    controller = MigrationController(redis_client)
    
    # Test gradual rollout at 25%
    controller.set_rollout_percentage(25)
    controller.set_system_mode(SystemMode.GRADUAL_ROLLOUT)
    
    # Issues 1-24 should go to Python, 25-100 to TypeScript
    assert controller.should_use_python_system(1)
    assert controller.should_use_python_system(24)
    assert not controller.should_use_python_system(25)
    assert not controller.should_use_python_system(99)

def test_emergency_rollback():
    """Test emergency rollback functionality."""
    controller = MigrationController(redis_client)
    
    controller.set_system_mode(SystemMode.PYTHON_ONLY)
    
    success = controller.emergency_rollback("Test failure")
    assert success
    assert controller.system_mode == SystemMode.EMERGENCY_ROLLBACK

@pytest.mark.integration
async def test_parallel_processing():
    """Test both systems processing same issue."""
    # Both systems should handle issue without conflict
    # Compare results for quality validation
    pass
```

## Dependencies & Risks

### Prerequisites
- Both TypeScript and Python systems operational
- Redis for state management
- Monitoring infrastructure
- Dashboard access

### Risks
- **Double processing**: Both systems process same issue
- **State inconsistency**: Systems disagree on issue status
- **Performance impact**: Parallel processing uses more resources
- **Complexity**: Migration logic adds system complexity

### Mitigations
- Issue locking to prevent double processing
- State reconciliation checks
- Resource monitoring and limits
- Simple fallback to TypeScript if needed

## Definition of Done

1. ✅ Migration controller implemented
2. ✅ Feature flag system working
3. ✅ Parallel processing capability
4. ✅ Rollback mechanism tested
5. ✅ Performance monitoring active
6. ✅ Migration dashboard operational
7. ✅ Safety checks preventing conflicts
8. ✅ Emergency procedures documented
9. ✅ Production deployment ready

## Implementation Notes for AI Agents

### DO
- Test rollback thoroughly before production
- Monitor performance metrics constantly
- Use gradual rollout percentages
- Keep fallback simple and reliable
- Log all migration decisions

### DON'T
- Don't switch systems without monitoring
- Don't skip rollback testing
- Don't rush migration percentages
- Don't ignore performance degradation
- Don't make migration logic complex

### Common Pitfalls to Avoid
1. Not testing rollback until emergency
2. Complex migration logic that fails
3. Missing performance monitoring
4. Not handling system failures gracefully
5. Switching too quickly without validation

## Success Example

Safe migration preventing disasters:
```
Week 1: 10% Python, 90% TypeScript - Monitor quality
Week 2: 25% Python, 75% TypeScript - Python showing better results
Week 3: 50% Python, 50% TypeScript - Both systems stable
Week 4: 75% Python, 25% TypeScript - Python preventing PR #23 disasters
Week 5: 100% Python - Migration complete, quality improved ✅
```

## Next Story
Migration complete! System ready for production with confidence.

🎉 **The transformation from disaster-prone single agent to quality multi-agent system is complete!** 🎉