"""
Status constants for compute operations.

These constants represent the possible states of a compute job or operation.
"""

from enum import Enum


class StatusCheckCompute(Enum):
    """
    Enum representing the possible states of a compute job or operation.
    """

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    STARTING_UP = "STARTING_UP"
    SCHEDULED = "SCHEDULED"
    UNSCHEDULED = "UNSCHEDULED"
