"""Pair programming agents module.

This module implements the revolutionary Task Pair execution system where 
Tasker agents (Developer, Analyst, Tester) work with Navigator agents in
pair programming patterns to produce high-quality work through iteration
and review.

This is the key innovation that prevents disasters like PR #23 by implementing
proper review cycles before accepting work.
"""

from .task_pair import (
    TaskPair,
    TaskPairResult, 
    IterationResult,
    ReviewDecision,
    ReviewFeedback,
    create_task_pair
)

__all__ = [
    'TaskPair',
    'TaskPairResult',
    'IterationResult', 
    'ReviewDecision',
    'ReviewFeedback',
    'create_task_pair'
]