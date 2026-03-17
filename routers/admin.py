from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database.db_connection import get_db
from core.database.tables import UserRole, User
from core.security import require_roles

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.patch("users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.admin])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi.")

    user.role = new_role
    db.commit()
    db.refresh(user)

    return {"message": f"Kullanici rolu guncellendi. Yeni rol: '{new_role.value}'"}
