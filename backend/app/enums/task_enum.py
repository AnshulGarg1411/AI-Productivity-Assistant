from enum import Enum


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskCategory(str, Enum):
    WORK = "WORK"
    STUDY = "STUDY"
    PERSONAL = "PERSONAL"
    HEALTH = "HEALTH"

class TaskSource(str, Enum):

    MANUAL = "MANUAL"

    EMAIL = "EMAIL"

    CALENDAR = "CALENDAR"

    AI = "AI"