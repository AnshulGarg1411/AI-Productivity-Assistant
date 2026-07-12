from enum import Enum


class MeetingType(str, Enum):

    ONLINE = "ONLINE"

    OFFLINE = "OFFLINE"


class MeetingStatus(str, Enum):

    CONFIRMED = "CONFIRMED"

    CANCELLED = "CANCELLED"

    TENTATIVE = "TENTATIVE"