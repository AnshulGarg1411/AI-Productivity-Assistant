import logging
import base64

from datetime import datetime
from email.utils import parsedate_to_datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.email import Email

from app.services.google_client import (
    build_google_service
)

from app.ai.task_extraction_agent import (
    extract_tasks_from_new_emails
)
from app.ai.email_intelligence_agent import (
    analyze_new_emails
)

logger = logging.getLogger(__name__)

GMAIL_SCOPE = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


# =====================================================
# GET MESSAGE IDS
# =====================================================

def get_message_ids(
    service,
    max_results: int = 20
):

    try:

        response = (

            service.users()

            .messages()

            .list(
                userId="me",
                maxResults=max_results
            )

            .execute()

        )

        return response.get(
            "messages",
            []
        )

    except Exception as e:

        logger.exception(e)

        raise HTTPException(

            status_code=500,

            detail="Failed to fetch Gmail messages."

        )


# =====================================================
# GET MESSAGE DETAILS
# =====================================================

def get_message_details(
    service,
    message_id: str
):

    return (

        service.users()

        .messages()

        .get(

            userId="me",

            id=message_id,

            format="full"

        )

        .execute()

    )


# =====================================================
# DECODE GMAIL BODY
# =====================================================

def decode_body(data):

    if not data:

        return ""

    try:

        return (

            base64.urlsafe_b64decode(

                data

            )

            .decode(
                "utf-8",
                errors="ignore"
            )

        )

    except Exception:

        return ""


# =====================================================
# EXTRACT BODY
# =====================================================

def extract_body(payload):

    body = ""

    if payload.get("body", {}).get("data"):

        body = decode_body(

            payload["body"]["data"]

        )

    for part in payload.get(

        "parts",

        []

    ):

        mime = part.get(

            "mimeType",

            ""

        )

        if mime == "text/plain":

            return decode_body(

                part["body"].get(

                    "data",

                    ""

                )

            )

    return body


# =====================================================
# EXTRACT EMAIL DATA
# =====================================================

def extract_email_data(message):

    payload = message["payload"]

    headers = payload["headers"]

    sender = ""

    subject = ""

    received = None

    for header in headers:

        if header["name"] == "From":

            sender = header["value"]

        elif header["name"] == "Subject":

            subject = header["value"]

        elif header["name"] == "Date":

            try:

                received = parsedate_to_datetime(

                    header["value"]

                )

            except Exception:

                received = datetime.utcnow()

    labels = message.get(

        "labelIds",

        []

    )

    unread = "UNREAD" in labels

    importance = "IMPORTANT" in labels

    starred = "STARRED" in labels

    archived = False

    category = None

    for label in labels:

        if label.startswith(

            "CATEGORY_"

        ):

            category = label.replace(

                "CATEGORY_",

                ""

            )

            break

    has_attachment = False

    for part in payload.get(

        "parts",

        []

    ):

        if part.get("filename"):

            has_attachment = True

            break

    body = extract_body(

        payload

    )

    return {

        "gmail_message_id": message["id"],

        "thread_id": message["threadId"],

        "sender": sender,

        "subject": subject,

        "snippet": message.get(

            "snippet",

            ""

        ),

        "body": body,

        "labels": ",".join(labels),

        "category": category,

        "importance": importance,

        "starred": starred,

        "archived": archived,

        "has_attachment": has_attachment,

        "unread": unread,

        "received_at": received

        or datetime.utcnow()

    }
# =====================================================
# CREATE EMAIL OBJECT
# =====================================================

def create_email_object(
    user_id: int,
    email_data: dict
):

    return Email(

        user_id=user_id,

        gmail_message_id=email_data["gmail_message_id"],

        thread_id=email_data["thread_id"],

        sender=email_data["sender"],

        subject=email_data["subject"],

        snippet=email_data["snippet"],

        body=email_data["body"],

        labels=email_data["labels"],

        category=email_data["category"],

        importance=email_data["importance"],

        starred=email_data["starred"],

        archived=email_data["archived"],

        has_attachment=email_data["has_attachment"],

        unread=email_data["unread"],

        received_at=email_data["received_at"]

    )


# =====================================================
# SYNC GMAIL
# =====================================================

def sync_gmail(
    db: Session,
    user_id: int
):

    logger.info(
        "Starting Gmail sync for user %s",
        user_id
    )

    service = build_google_service(

        db=db,

        user_id=user_id,

        api_name="gmail",

        version="v1",

        scopes=GMAIL_SCOPE

    )

    message_ids = get_message_ids(
        service
    )

    emails_to_insert = []

    synced = 0

    skipped = 0

    failed = 0

    for message in message_ids:

        try:

            details = get_message_details(

                service,

                message["id"]

            )

            email_data = extract_email_data(
                details
            )

            existing = (

                db.query(Email)

                .filter(
                    Email.user_id == user_id
                )

                .filter(
                    Email.gmail_message_id ==
                    email_data["gmail_message_id"]
                )

                .first()

            )

            if existing:

                skipped += 1

                continue

            email = create_email_object(

                user_id,

                email_data

            )

            emails_to_insert.append(
                email
            )

            synced += 1

        except Exception as e:

            failed += 1

            logger.exception(
                "Failed to sync Gmail message %s",
                message.get("id")
            )

    try:

        if emails_to_insert:

            db.add_all(
                emails_to_insert
            )

            db.commit()

            logger.info(
                "%d emails inserted.",
                len(emails_to_insert)
            )

            # AI task extraction runs after commit so each email already
            # has a real id (needed for source_email_id). A failure here
            # can never take down the sync itself -- see
            # extract_tasks_from_new_emails for the error handling.
            extract_tasks_from_new_emails(
                db,
                emails_to_insert
            )

            # Same pattern for email intelligence (summary/category/priority).
            analyze_new_emails(
                db,
                emails_to_insert
            )

    except Exception as e:

        db.rollback()

        logger.exception(e)

        raise HTTPException(

            status_code=500,

            detail="Failed to save Gmail emails."

        )

    logger.info(
        "Gmail Sync Finished"
    )

    logger.info(

        "Synced=%d Skipped=%d Failed=%d",

        synced,

        skipped,

        failed

    )

    return {

        "success": True,

        "synced": synced,

        "skipped": skipped,

        "failed": failed,

        "total": len(message_ids)

    }