"""
Performance monitoring and comparison system for migration validation.

Tracks metrics between TypeScript and Python systems to validate
migration success and detect performance regressions.
"""

import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
import redis
import statistics
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics we track for performance comparison."""
    SUCCESS_RATE = "success_rate"
    DURATION = "duration"
    QUALITY_SCORE = "quality_score" 
    ERROR_RATE = "error_rate"
    BUILD_SUCCESS = "build_success_rate"
    PR_ACCEPTANCE = "pr_acceptance_rate"


@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow execution."""
    system: str
    issue_number: int
    workflow_id: str
    timestamp: datetime
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    
    # Quality metrics
    code_quality_score: Optional[float] = None
    test_coverage: Optional[float] = None
    build_successful: Optional[bool] = None
    pr_created: Optional[bool] = None
    pr_accepted: Optional[bool] = None
    
    # Performance metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """
    Monitor and compare performance between TypeScript and Python systems.
    
    Features:
    - Real-time performance tracking
    - Statistical comparison between systems
    - Performance regression detection
    - Threshold-based alerting
    - Historical trend analysis
    - Quality metrics correlation
    """
    
    REDIS_METRICS_KEY = "performance:metrics"
    REDIS_AGGREGATES_KEY = "performance:aggregates"
    REDIS_THRESHOLDS_KEY = "performance:thresholds"
    REDIS_ALERTS_KEY = "performance:alerts"
    
    # Default performance thresholds
    DEFAULT_THRESHOLDS = {
        "min_success_rate": 0.7,           # 70% minimum success rate
        "max_avg_duration": 600,           # 10 minutes max average
        "min_quality_score": 0.6,          # 60% minimum quality
        "max_error_rate": 0.3,             # 30% maximum error rate
        "alert_window_minutes": 60,        # Alert if issues persist for 1 hour
        "min_samples": 5                   # Minimum samples before alerting
    }
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize performance monitor.
        
        Args:
            redis_client: Redis client for metrics storage
        """
        self.redis = redis_client
        self._initialize_thresholds()
    
    def _initialize_thresholds(self) -> None:
        """Initialize default thresholds if not set."""
        if not self.redis.exists(self.REDIS_THRESHOLDS_KEY):
            self.redis.set(
                self.REDIS_THRESHOLDS_KEY, 
                json.dumps(self.DEFAULT_THRESHOLDS)
            )
    
    def track_workflow_completion(
        self,
        system: str,
        issue_number: int,
        workflow_id: str,
        success: bool,
        duration_seconds: float,
        quality_metrics: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Track completion of a workflow for performance analysis.
        
        Args:
            system: System that processed the workflow ('python' or 'typescript')
            issue_number: GitHub issue number
            workflow_id: Unique workflow identifier
            success: Whether the workflow completed successfully
            duration_seconds: Time taken to complete workflow
            quality_metrics: Optional quality metrics (test coverage, etc.)
            performance_metrics: Optional performance metrics (memory, CPU)
            error_message: Error message if workflow failed
        """
        try:
            # Create metrics object
            metrics = WorkflowMetrics(
                system=system,
                issue_number=issue_number,
                workflow_id=workflow_id,
                timestamp=datetime.now(),
                success=success,
                duration_seconds=duration_seconds,
                error_message=error_message
            )
            
            # Add quality metrics if provided
            if quality_metrics:
                metrics.code_quality_score = quality_metrics.get("code_quality_score")
                metrics.test_coverage = quality_metrics.get("test_coverage")
                metrics.build_successful = quality_metrics.get("build_successful")
                metrics.pr_created = quality_metrics.get("pr_created")
                metrics.pr_accepted = quality_metrics.get("pr_accepted")
                metrics.custom_metrics = quality_metrics.get("custom_metrics", {})
            
            # Add performance metrics if provided
            if performance_metrics:
                metrics.memory_usage_mb = performance_metrics.get("memory_usage_mb")
                metrics.cpu_usage_percent = performance_metrics.get("cpu_usage_percent")
            
            # Store metrics
            self._store_metrics(metrics)
            
            # Update aggregated statistics
            self._update_aggregates(system, metrics)
            
            # Check for performance issues
            self._check_performance_thresholds(system, metrics)
            
            logger.info(
                f"Tracked workflow completion: {system} system, "
                f"issue #{issue_number}, success={success}, "
                f"duration={duration_seconds:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Failed to track workflow completion: {e}")
    
    def _store_metrics(self, metrics: WorkflowMetrics) -> None:
        """Store individual metrics in Redis with TTL."""
        try:
            # Create storage key with timestamp
            timestamp_str = metrics.timestamp.isoformat()
            key = f"{self.REDIS_METRICS_KEY}:{metrics.system}:{timestamp_str}"
            
            # Convert to dict and handle datetime serialization
            metrics_dict = asdict(metrics)
            metrics_dict['timestamp'] = timestamp_str
            
            # Store with 30-day TTL
            self.redis.setex(
                key,
                timedelta(days=30),
                json.dumps(metrics_dict)
            )
            
            # Add to system-specific sorted set for time-based queries
            score = metrics.timestamp.timestamp()
            self.redis.zadd(
                f"{self.REDIS_METRICS_KEY}:{metrics.system}:timeline",
                {key: score}
            )
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _update_aggregates(self, system: str, metrics: WorkflowMetrics) -> None:
        """Update aggregated statistics for quick access."""
        try:
            # Update counters
            date_key = metrics.timestamp.strftime("%Y-%m-%d")
            hour_key = metrics.timestamp.strftime("%Y-%m-%d-%H")
            
            # Daily aggregates
            daily_key = f"{self.REDIS_AGGREGATES_KEY}:{system}:daily:{date_key}"
            self._increment_counters(daily_key, metrics)
            self.redis.expire(daily_key, timedelta(days=7))  # Keep 7 days
            
            # Hourly aggregates  
            hourly_key = f"{self.REDIS_AGGREGATES_KEY}:{system}:hourly:{hour_key}"
            self._increment_counters(hourly_key, metrics)
            self.redis.expire(hourly_key, timedelta(hours=48))  # Keep 48 hours
            
        except Exception as e:
            logger.error(f"Failed to update aggregates: {e}")
    
    def _increment_counters(self, key: str, metrics: WorkflowMetrics) -> None:
        """Increment various counters for a metrics key."""
        # Total workflows
        self.redis.hincrby(key, "total_workflows", 1)
        
        # Success/failure counts
        if metrics.success:
            self.redis.hincrby(key, "successful_workflows", 1)
        else:
            self.redis.hincrby(key, "failed_workflows", 1)
        
        # Duration tracking
        self.redis.hincrbyfloat(key, "total_duration", metrics.duration_seconds)
        
        # Quality metrics
        if metrics.code_quality_score:
            self.redis.hincrbyfloat(key, "total_quality_score", metrics.code_quality_score)
            self.redis.hincrby(key, "quality_sample_count", 1)
        
        if metrics.build_successful:
            self.redis.hincrby(key, "successful_builds", 1)
        
        if metrics.pr_accepted:
            self.redis.hincrby(key, "accepted_prs", 1)
        
        if metrics.pr_created:
            self.redis.hincrby(key, "created_prs", 1)
    
    def _check_performance_thresholds(
        self, 
        system: str, 
        metrics: WorkflowMetrics
    ) -> None:
        """Check if performance has degraded significantly."""
        try:
            recent_stats = self._get_recent_stats(system, minutes=60)
            
            if not recent_stats or recent_stats["sample_count"] < 5:
                return  # Not enough data for meaningful analysis
            
            thresholds = self._get_thresholds()
            alerts_triggered = []
            
            # Check success rate
            if recent_stats["success_rate"] < thresholds["min_success_rate"]:
                alerts_triggered.append({
                    "type": "low_success_rate",
                    "value": recent_stats["success_rate"],
                    "threshold": thresholds["min_success_rate"],
                    "severity": "high"
                })
            
            # Check average duration
            if recent_stats["avg_duration"] > thresholds["max_avg_duration"]:
                alerts_triggered.append({
                    "type": "high_duration",
                    "value": recent_stats["avg_duration"],
                    "threshold": thresholds["max_avg_duration"],
                    "severity": "medium"
                })
            
            # Check quality score
            if (recent_stats["avg_quality_score"] and 
                recent_stats["avg_quality_score"] < thresholds["min_quality_score"]):
                alerts_triggered.append({
                    "type": "low_quality",
                    "value": recent_stats["avg_quality_score"],
                    "threshold": thresholds["min_quality_score"],
                    "severity": "high"
                })
            
            # Trigger alerts if any thresholds exceeded
            if alerts_triggered:
                self._trigger_performance_alerts(system, alerts_triggered, recent_stats)
                
        except Exception as e:
            logger.error(f"Failed to check performance thresholds: {e}")
    
    def _get_recent_stats(self, system: str, minutes: int = 60) -> Dict[str, Any]:
        """Get recent performance statistics for a system."""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            cutoff_score = cutoff_time.timestamp()
            
            # Get recent metrics from sorted set
            timeline_key = f"{self.REDIS_METRICS_KEY}:{system}:timeline"
            recent_keys = self.redis.zrangebyscore(
                timeline_key,
                cutoff_score,
                "+inf"
            )
            
            if not recent_keys:
                return {}
            
            # Collect metrics
            metrics_list = []
            for key in recent_keys:
                try:
                    data = self.redis.get(key)
                    if data:
                        metric = json.loads(data.decode())
                        metrics_list.append(metric)
                except Exception as e:
                    logger.warning(f"Failed to load metric {key}: {e}")
            
            if not metrics_list:
                return {}
            
            # Calculate statistics
            successes = [m for m in metrics_list if m["success"]]
            durations = [m["duration_seconds"] for m in metrics_list]
            quality_scores = [
                m["code_quality_score"] for m in metrics_list 
                if m.get("code_quality_score") is not None
            ]
            
            return {
                "sample_count": len(metrics_list),
                "success_rate": len(successes) / len(metrics_list),
                "avg_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations),
                "avg_quality_score": (
                    statistics.mean(quality_scores) 
                    if quality_scores else None
                ),
                "total_successes": len(successes),
                "total_failures": len(metrics_list) - len(successes)
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent stats for {system}: {e}")
            return {}
    
    def _get_thresholds(self) -> Dict[str, Any]:
        """Get current performance thresholds."""
        try:
            thresholds = self.redis.get(self.REDIS_THRESHOLDS_KEY)
            if thresholds:
                return json.loads(thresholds.decode())
            return self.DEFAULT_THRESHOLDS
        except Exception as e:
            logger.error(f"Failed to get thresholds: {e}")
            return self.DEFAULT_THRESHOLDS
    
    def _trigger_performance_alerts(
        self,
        system: str,
        alerts: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> None:
        """Trigger performance degradation alerts."""
        try:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "system": system,
                "alerts": alerts,
                "recent_stats": stats,
                "sample_size": stats.get("sample_count", 0)
            }
            
            # Store alert
            alert_key = f"{self.REDIS_ALERTS_KEY}:{system}:{datetime.now().timestamp()}"
            self.redis.setex(
                alert_key,
                timedelta(days=7),
                json.dumps(alert_data)
            )
            
            # Log alerts
            for alert in alerts:
                severity = alert["severity"]
                logger.warning(
                    f"PERFORMANCE ALERT [{severity.upper()}]: {system} system - "
                    f"{alert['type']} = {alert['value']:.3f}, "
                    f"threshold = {alert['threshold']:.3f}"
                )
            
            # TODO: Send notifications (Slack, email, etc.)
            
        except Exception as e:
            logger.error(f"Failed to trigger performance alerts: {e}")
    
    def get_performance_comparison(
        self, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Compare performance between Python and TypeScript systems.
        
        Args:
            hours: Time window for comparison (default 24 hours)
            
        Returns:
            Comprehensive comparison of system performance
        """
        try:
            python_stats = self._get_recent_stats("python", hours * 60)
            typescript_stats = self._get_recent_stats("typescript", hours * 60)
            
            if not python_stats and not typescript_stats:
                return {"error": "No performance data available"}
            
            comparison = {}
            
            # Individual system stats
            comparison["python"] = python_stats or {"sample_count": 0}
            comparison["typescript"] = typescript_stats or {"sample_count": 0}
            
            # Relative comparisons
            if python_stats and typescript_stats:
                comparison["relative"] = {
                    "success_rate_improvement": (
                        python_stats["success_rate"] - 
                        typescript_stats["success_rate"]
                    ),
                    "duration_improvement_percent": (
                        (typescript_stats["avg_duration"] - python_stats["avg_duration"]) /
                        typescript_stats["avg_duration"] * 100
                        if typescript_stats["avg_duration"] > 0 else 0
                    ),
                    "quality_improvement": (
                        (python_stats.get("avg_quality_score", 0) or 0) -
                        (typescript_stats.get("avg_quality_score", 0) or 0)
                    )
                }
                
                # Determine which system is performing better
                comparison["recommendation"] = self._generate_recommendation(
                    python_stats, typescript_stats
                )
            
            # Recent alerts
            comparison["recent_alerts"] = self._get_recent_alerts(hours)
            
            # Analysis timestamp
            comparison["analysis_timestamp"] = datetime.now().isoformat()
            comparison["time_window_hours"] = hours
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to get performance comparison: {e}")
            return {"error": str(e)}
    
    def _generate_recommendation(
        self,
        python_stats: Dict[str, Any],
        typescript_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendation based on performance comparison."""
        try:
            python_score = self._calculate_performance_score(python_stats)
            typescript_score = self._calculate_performance_score(typescript_stats)
            
            if python_score > typescript_score:
                return {
                    "preferred_system": "python",
                    "confidence": min((python_score - typescript_score) / python_score, 1.0),
                    "python_score": python_score,
                    "typescript_score": typescript_score,
                    "reasoning": "Python system shows better overall performance"
                }
            else:
                return {
                    "preferred_system": "typescript", 
                    "confidence": min((typescript_score - python_score) / typescript_score, 1.0),
                    "python_score": python_score,
                    "typescript_score": typescript_score,
                    "reasoning": "TypeScript system shows better overall performance"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_score(self, stats: Dict[str, Any]) -> float:
        """Calculate overall performance score from statistics."""
        if not stats or stats.get("sample_count", 0) == 0:
            return 0.0
        
        # Weighted scoring
        score = 0.0
        
        # Success rate (40% weight)
        score += stats.get("success_rate", 0) * 0.4
        
        # Duration (30% weight, inverted - faster is better)
        max_duration = 600  # 10 minutes
        duration_score = max(0, 1 - (stats.get("avg_duration", max_duration) / max_duration))
        score += duration_score * 0.3
        
        # Quality (30% weight)
        quality_score = stats.get("avg_quality_score", 0) or 0
        score += quality_score * 0.3
        
        return score
    
    def _get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent performance alerts."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_score = cutoff_time.timestamp()
            
            # Get alert keys for both systems
            python_pattern = f"{self.REDIS_ALERTS_KEY}:python:*"
            typescript_pattern = f"{self.REDIS_ALERTS_KEY}:typescript:*"
            
            all_alerts = []
            
            for pattern in [python_pattern, typescript_pattern]:
                alert_keys = self.redis.keys(pattern)
                for key in alert_keys:
                    try:
                        # Extract timestamp from key
                        timestamp = float(key.decode().split(":")[-1])
                        if timestamp >= cutoff_score:
                            alert_data = self.redis.get(key)
                            if alert_data:
                                all_alerts.append(json.loads(alert_data.decode()))
                    except Exception as e:
                        logger.warning(f"Failed to process alert {key}: {e}")
            
            # Sort by timestamp
            all_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            return all_alerts[:20]  # Return most recent 20 alerts
            
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []
    
    def update_thresholds(self, new_thresholds: Dict[str, Any]) -> bool:
        """
        Update performance thresholds.
        
        Args:
            new_thresholds: Dictionary of new threshold values
            
        Returns:
            True if thresholds were updated successfully
        """
        try:
            # Validate threshold values
            for key, value in new_thresholds.items():
                if key not in self.DEFAULT_THRESHOLDS:
                    logger.warning(f"Unknown threshold key: {key}")
                    continue
                
                # Validate ranges
                if key == "min_success_rate" and not 0 <= value <= 1:
                    return False
                elif key == "max_avg_duration" and value <= 0:
                    return False
                elif key == "min_quality_score" and not 0 <= value <= 1:
                    return False
            
            # Get current thresholds and update
            current = self._get_thresholds()
            current.update(new_thresholds)
            
            # Store updated thresholds
            self.redis.set(self.REDIS_THRESHOLDS_KEY, json.dumps(current))
            
            logger.info(f"Updated performance thresholds: {new_thresholds}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update thresholds: {e}")
            return False
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health for both systems."""
        try:
            python_stats = self._get_recent_stats("python", 60)  # Last hour
            typescript_stats = self._get_recent_stats("typescript", 60)
            
            thresholds = self._get_thresholds()
            
            def assess_health(stats: Dict[str, Any]) -> Dict[str, Any]:
                if not stats or stats.get("sample_count", 0) < 3:
                    return {"status": "unknown", "reason": "insufficient_data"}
                
                issues = []
                
                if stats["success_rate"] < thresholds["min_success_rate"]:
                    issues.append("low_success_rate")
                
                if stats["avg_duration"] > thresholds["max_avg_duration"]:
                    issues.append("high_duration")
                
                if (stats.get("avg_quality_score") and 
                    stats["avg_quality_score"] < thresholds["min_quality_score"]):
                    issues.append("low_quality")
                
                if not issues:
                    return {"status": "healthy", "issues": []}
                elif len(issues) == 1:
                    return {"status": "degraded", "issues": issues}
                else:
                    return {"status": "unhealthy", "issues": issues}
            
            return {
                "python_system": assess_health(python_stats),
                "typescript_system": assess_health(typescript_stats),
                "thresholds": thresholds,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health summary: {e}")
            return {"error": str(e)}