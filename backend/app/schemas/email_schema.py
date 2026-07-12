from datetime import datetime

from pydantic import BaseModel


# ======================================================
# CREATE
# ======================================================

class EmailCreate(BaseModel):

    user_id: int

    gmail_message_id: str

    thread_id: str

    sender: str

    subject: str

    snippet: str | None = None

    labels: str | None = None

    category: str | None = None

    importance: bool = False

    has_attachment: bool = False

    unread: bool = True

    received_at: datetime


# ======================================================
# RESPONSE
# ======================================================

class EmailResponse(EmailCreate):

    id: int

    ai_summary: str | None = None

    ai_priority: str | None = None

    class Config:

        from_attributes = True


# ======================================================
# EMAIL CARD
# ======================================================

class EmailCardResponse(BaseModel):

    id: int

    sender: str

    subject: str

    snippet: str

    received_at: datetime

    unread: bool

    importance: bool

    has_attachment: bool

    class Config:
        from_attributes = True

# ======================================================
# EMAIL DETAIL
# ======================================================

class EmailDetailResponse(BaseModel):

    id: int

    sender: str

    subject: str

    snippet: str

    labels: str | None = None

    category: str | None = None

    ai_summary: str | None = None

    ai_priority: str | None = None

    unread: bool

    importance: bool

    has_attachment: bool

    received_at: datetime

    class Config:

        from_attributes = True


# ======================================================
# URGENT EMAILS
# ======================================================

class UrgentEmailsResponse(BaseModel):

    emails: list[EmailCardResponse]


# ======================================================
# AI SUMMARY
# ======================================================

class EmailSummaryResponse(BaseModel):

    summary: str


# ======================================================
# AI REPLY
# ======================================================

class EmailReplyResponse(BaseModel):

    reply: str


# ======================================================
# ACTION ITEMS
# ======================================================

class EmailActionItem(BaseModel):

    title: str

    deadline: str | None = None


class EmailActionResponse(BaseModel):

    action_items: list[EmailActionItem]