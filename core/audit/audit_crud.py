from sqlalchemy import desc
from sqlalchemy.orm import Session
from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit
import math


class AuditCRUD(CRUDBase[Audit, AuditCreate, AuditRead]):

   def get_latest_per_uid(self, db: Session, page: int = 1, pageSize: int = 50, filters: dict = None):
        base_query = db.query(Audit)

        if filters:
            for field, value in filters.items():
                if hasattr(Audit, field):
                    base_query = base_query.filter(getattr(Audit, field) == value)

        base_query = base_query.filter(Audit.uid.isnot(None))

        base_query = base_query.order_by(Audit.uid, desc(Audit.updated_at))
        base_query = base_query.distinct(Audit.uid)
        subquery = base_query.subquery()
        query = db.query(subquery).order_by(desc(subquery.c.updated_at))

        total = query.count()
        data = query.offset((page - 1) * pageSize).limit(pageSize).all()

        audits =  [dict(row._mapping) for row in data]
        return {
            "pager": {
                "page": page,
                "pageSize": pageSize,
                "total": total,
                "pageCount": math.ceil(total / pageSize) if total else 0
            },
            "audits": audits
        }
