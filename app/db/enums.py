from enum import Enum


class WorkspaceRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    KILLED = "killed"
    MAINTENANCE = "maintenance"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    KILLED = "killed"
    CACHE_HIT = "cache_hit"


class UsageType(str, Enum):
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    CACHE_HIT = "cache_hit"
    RETRY = "retry"
    PAUSED = "paused"
    RESUMED = "resumed"
    KILLED = "killed"
    BUDGET_EXCEEDED = "budget_exceeded"