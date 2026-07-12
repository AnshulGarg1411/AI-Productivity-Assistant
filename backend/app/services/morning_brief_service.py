from sqlalchemy.orm import Session

from app.models.user import User

from app.services.dashboard_service import get_dashboard_data


def get_morning_brief(
    db: Session,
    user: User
):
    # The dashboard already computes the morning brief (via
    # app/services/brief_builder.py) as part of building its response, so
    # this endpoint just reuses that instead of recomputing everything.
    dashboard = get_dashboard_data(
        db,
        user
    )

    return dashboard.morning_brief
