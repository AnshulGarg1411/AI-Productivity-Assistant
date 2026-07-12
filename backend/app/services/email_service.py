from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.email import Email


# =====================================================
# CREATE EMAIL
# =====================================================

def create_email(
    db: Session,
    email_data: dict
):

    email = Email(
        **email_data
    )

    db.add(email)

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# GET EMAIL BY ID
# =====================================================

def get_email_by_id(
    db: Session,
    user_id: int,
    email_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.id == email_id
        )

        .first()

    )


# =====================================================
# GET BY GMAIL MESSAGE ID
# =====================================================

def get_email_by_gmail_id(
    db: Session,
    user_id: int,
    gmail_message_id: str
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.gmail_message_id == gmail_message_id
        )

        .first()

    )


# =====================================================
# GET ALL EMAILS
# =====================================================

def get_all_emails(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.archived == False
        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )


# =====================================================
# GET UNREAD EMAILS
# =====================================================

def get_unread_emails(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.unread == True
        )

        .filter(
            Email.archived == False
        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )


# =====================================================
# GET IMPORTANT EMAILS
# =====================================================

def get_important_emails(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.importance == True
        )

        .filter(
            Email.archived == False
        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )


# =====================================================
# GET STARRED EMAILS
# =====================================================

def get_starred_emails(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.starred == True
        )

        .filter(
            Email.archived == False
        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )


# =====================================================
# GET ARCHIVED EMAILS
# =====================================================

def get_archived_emails(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.archived == True
        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )


# =====================================================
# SEARCH EMAILS
# =====================================================

def search_emails(
    db: Session,
    user_id: int,
    query: str
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(

            or_(

                Email.subject.ilike(f"%{query}%"),

                Email.sender.ilike(f"%{query}%"),

                Email.snippet.ilike(f"%{query}%"),

                Email.body.ilike(f"%{query}%")

            )

        )

        .order_by(
            Email.received_at.desc()
        )

        .all()

    )
# =====================================================
# GET EMAIL COUNT
# =====================================================

def get_email_count(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.archived == False
        )

        .count()

    )


# =====================================================
# GET UNREAD COUNT
# =====================================================

def get_unread_email_count(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.unread == True
        )

        .filter(
            Email.archived == False
        )

        .count()

    )


# =====================================================
# GET IMPORTANT COUNT
# =====================================================

def get_important_email_count(
    db: Session,
    user_id: int
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.importance == True
        )

        .filter(
            Email.archived == False
        )

        .count()

    )


# =====================================================
# URGENT EMAILS
# =====================================================

def get_urgent_emails(
    db: Session,
    user_id: int,
    limit: int = 5
):

    return (

        db.query(Email)

        .filter(
            Email.user_id == user_id
        )

        .filter(
            Email.unread == True
        )

        .filter(
            # Prefer the AI's HIGH classification (reads actual content)
            # when available; fall back to Gmail's own IMPORTANT label for
            # emails that haven't been analyzed yet (no Gemini key, or not
            # synced through the AI pipeline).
            or_(
                Email.ai_priority == "HIGH",
                Email.importance == True
            )
        )

        .filter(
            Email.archived == False
        )

        .order_by(
            Email.received_at.desc()
        )

        .limit(limit)

        .all()

    )


# =====================================================
# MARK EMAIL AS READ
# =====================================================

def mark_as_read(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return None

    email.unread = False

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# ARCHIVE EMAIL
# =====================================================

def archive_email(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return None

    email.archived = True

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# UNARCHIVE EMAIL
# =====================================================

def unarchive_email(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return None

    email.archived = False

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# STAR EMAIL
# =====================================================

def star_email(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return None

    email.starred = True

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# UNSTAR EMAIL
# =====================================================

def unstar_email(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return None

    email.starred = False

    db.commit()

    db.refresh(email)

    return email


# =====================================================
# DELETE EMAIL
# =====================================================

def delete_email(
    db: Session,
    user_id: int,
    email_id: int
):

    email = get_email_by_id(
        db,
        user_id,
        email_id
    )

    if email is None:

        return False

    db.delete(email)

    db.commit()

    return True