from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import AdminAccount, User


def is_active_admin(db: Session, user_id: int) -> bool:
    return db.scalar(
        select(AdminAccount.id).where(
            AdminAccount.user_id == user_id,
            AdminAccount.enabled.is_(True),
        )
    ) is not None


def create_or_enable_admin(db: Session, user: User) -> AdminAccount:
    admin = db.scalar(select(AdminAccount).where(AdminAccount.user_id == user.id))
    if admin:
        admin.enabled = True
    else:
        admin = AdminAccount(user_id=user.id, enabled=True)
        db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
