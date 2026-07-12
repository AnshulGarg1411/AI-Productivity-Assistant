from typing import List

from pydantic import BaseModel


class MorningBriefResponse(BaseModel):

    greeting: str

    summary: List[str]

    top_priority: str | None = None

    focus_window: str | None = None

    productivity_score: int

    recommendations: List[str]