"""Trace Logger for Multi-Agent Workflow.

This module provides a singleton logger that captures all agent steps
for visualization in HTML reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ActionType(Enum):
    """Types of actions that can be logged."""

    PLANNING = "Planificación"
    TOOL_USE = "Uso de Herramienta"
    GENERATION = "Generación de Texto"
    CRITIQUE = "Crítica"
    ERROR = "Error"
    INFO = "Información"
    REWRITE = "Reescritura"


class StepStatus(Enum):
    """Status of a logged step."""

    SUCCESS = "success"  # Verde
    FAILURE = "failure"  # Rojo
    THINKING = "thinking"  # Azul
    TOOL = "tool"  # Amarillo
    WARNING = "warning"  # Naranja


@dataclass
class LogStep:
    """A single step in the workflow.

    Attributes:
        agent_name: Name of the agent (Planner, Writer, Critique, etc.)
        action_type: Type of action being performed
        content: Content/description of the step
        status: Status of the step
        duration: Duration in seconds
        timestamp: When the step occurred
        metadata: Additional metadata
    """

    agent_name: str
    action_type: ActionType
    content: str
    status: StepStatus
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the step.
        """
        return {
            "agent_name": self.agent_name,
            "action_type": self.action_type.value,
            "content": self.content,
            "status": self.status.value,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class TraceLogger:
    """Singleton logger for capturing agent workflow steps.

    This logger captures all steps from the multi-agent workflow
    for later visualization in HTML reports.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the trace logger."""
        if not TraceLogger._initialized:
            self.steps: list[LogStep] = []
            self.start_time: datetime | None = None
            self.end_time: datetime | None = None
            self.workflow_metadata: dict[str, Any] = {}
            TraceLogger._initialized = True

    def reset(self):
        """Reset the logger for a new execution."""
        self.steps = []
        self.start_time = None
        self.end_time = None
        self.workflow_metadata = {}

    def start_workflow(self, **metadata):
        """Mark the start of a workflow execution.

        Args:
            **metadata: Additional metadata about the workflow
        """
        self.start_time = datetime.now()
        self.workflow_metadata = metadata

    def end_workflow(self, **metadata):
        """Mark the end of a workflow execution.

        Args:
            **metadata: Additional metadata about the workflow completion
        """
        self.end_time = datetime.now()
        self.workflow_metadata.update(metadata)

    def log_step(
        self,
        agent_name: str,
        action_type: ActionType | str,
        content: str,
        status: StepStatus | str,
        duration: float = 0.0,
        **metadata,
    ):
        """Log a step in the workflow.

        Args:
            agent_name: Name of the agent performing the action
            action_type: Type of action (can be ActionType enum or string)
            content: Description/content of the step
            status: Status of the step (can be StepStatus enum or string)
            duration: Duration of the step in seconds
            **metadata: Additional metadata to store
        """
        # Convert string to enum if needed
        if isinstance(action_type, str):
            try:
                action_type = ActionType[action_type.upper().replace(" ", "_")]
            except KeyError:
                action_type = ActionType.INFO

        if isinstance(status, str):
            try:
                status = StepStatus[status.upper()]
            except KeyError:
                status = StepStatus.THINKING

        step = LogStep(
            agent_name=agent_name,
            action_type=action_type,
            content=content,
            status=status,
            duration=duration,
            metadata=metadata,
        )

        self.steps.append(step)

    def get_total_duration(self) -> float:
        """Get total duration of the workflow.

        Returns:
            Total duration in seconds
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def get_step_count(self) -> dict[str, int]:
        """Get count of steps by agent.

        Returns:
            Dictionary mapping agent name to step count
        """
        counts = {}
        for step in self.steps:
            counts[step.agent_name] = counts.get(step.agent_name, 0) + 1
        return counts

    def get_success_rate(self) -> float:
        """Get success rate of steps.

        Returns:
            Success rate as a percentage (0-100)
        """
        if not self.steps:
            return 0.0

        success_count = sum(1 for step in self.steps if step.status == StepStatus.SUCCESS)
        return (success_count / len(self.steps)) * 100

    def estimate_cost(self, tokens_per_step: int = 500, cost_per_1k: float = 0.002) -> float:
        """Estimate cost of the workflow.

        Args:
            tokens_per_step: Average tokens per step
            cost_per_1k: Cost per 1000 tokens

        Returns:
            Estimated cost in dollars
        """
        total_tokens = len(self.steps) * tokens_per_step
        return (total_tokens / 1000) * cost_per_1k

    def to_dict(self) -> dict:
        """Convert the entire trace to a dictionary.

        Returns:
            Dictionary representation of the trace
        """
        return {
            "steps": [step.to_dict() for step in self.steps],
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": self.get_total_duration(),
            "metadata": self.workflow_metadata,
            "stats": {
                "total_steps": len(self.steps),
                "step_counts": self.get_step_count(),
                "success_rate": self.get_success_rate(),
                "estimated_cost": self.estimate_cost(),
            },
        }


# Global instance
_trace_logger = TraceLogger()


def get_trace_logger() -> TraceLogger:
    """Get the global trace logger instance.

    Returns:
        The singleton TraceLogger instance
    """
    return _trace_logger
