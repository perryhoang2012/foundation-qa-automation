"""
Status constants for compute operations.

These constants represent the possible states of a compute job or operation.
"""

# The operation finished successfully.
COMPLETED = "COMPLETED"

# The operation encountered an error.
FAILED = "FAILED"

# The operation is currently executing.
RUNNING = "RUNNING"

# The operation is starting to be executed.
STARTING_UP = "STARTING_UP"

# The operation is scheduled for future execution.
SCHEDULED = "SCHEDULED"

# The job was not able to be scheduled or executed.
UNSCHEDULED = "UNSCHEDULED"
