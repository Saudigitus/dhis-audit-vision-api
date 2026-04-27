from sqlalchemy import desc
from sqlalchemy.orm import Session
from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit


class AuditCRUD(CRUDBase[Audit, AuditCreate, AuditRead]):

    def get_latest_per_uid(self, db: Session, page: int = 1, pageSize: int = 50, filters: dict = None):
        query = db.query(Audit)

        # filtros dinâmicos
        if filters:
            for field, value in filters.items():
                if hasattr(Audit, field):
                    query = query.filter(getattr(Audit, field) == value)

        query = query.filter(Audit.uid.isnot(None))

        #  lógica principal de ordenação e distinct
        query = query.order_by(Audit.uid, desc(Audit.created_at))
        query = query.distinct(Audit.uid)

        total = query.count()
        data = query.offset((page - 1) * pageSize).limit(pageSize).all()

        return {
            "pager": {
                "page": page,
                "pageSize": pageSize,
                "total": total
            },
            "audits": data
        }
