"""Tester Agent package.

This package contains the Tester Agent implementation that generates comprehensive
test suites based on requirements and validates implementations.
"""

from .agent import TesterAgent
from .models import TestCase, TestSuite

__all__ = ['TesterAgent', 'TestCase', 'TestSuite']