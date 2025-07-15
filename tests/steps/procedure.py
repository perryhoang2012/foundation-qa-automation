from typing import Any, Dict


class ProcedureStep:
    """Base class for all procedure steps."""

    def __init__(
        self,
        request: Any,
        step: Dict[str, Any],
        api_context: tuple[Any, str],
        id_map: Dict[str, Any],
    ):
        """
        Initialize a procedure step.

        Args:
            request: The test request object
            step: The step configuration
            api_context: Tuple of (context, access_token)
            id_map: The entity ID mapping dictionary
        """
        self.request = request
        self.step = step
        self.api_context = api_context
        self.id_map = id_map

    def execute(self) -> None:
        """Execute the procedure step. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must override this method")
