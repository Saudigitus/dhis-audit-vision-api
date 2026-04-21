from typing import TypeVar, Generic, List, Optional, Any
from core.db.base import BoundBaseClass
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, or_
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import math
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

T = TypeVar("T", bound=BoundBaseClass)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
ReadSchema = TypeVar("ReadSchema", bound=BaseModel)


class Pager(BaseModel):
    page: int
    total: int
    pageSize: int
    pageCount: int


class PaginatedResponse(BaseModel, Generic[ReadSchema]):
    pager: Pager
    data: List[ReadSchema]

    model_config = ConfigDict(from_attributes=True)

    def model_dump(self, **kwargs):
        # Not used directly — routers rely on response_model serialization
        return super().model_dump(**kwargs)


class CRUDBase(Generic[T, CreateSchema, ReadSchema]):

    def __init__(self, model: type[T]):
        self.model = model

    def _build_query(
        self,
        filters: Optional[dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ):
        query = select(self.model)

        if filters:
            # Get filterable columns — skip JSON/JSONB and None values
            filterable = {
                col.key
                for col in self.model.__table__.columns
                if not isinstance(col.type, (JSON, JSONB))
            }
            for field, value in filters.items():
                if field in filterable and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        if search and search_fields:
            conditions = [
                getattr(self.model, f).ilike(f"%{search}%")
                for f in search_fields
                if hasattr(self.model, f)
            ]
            if conditions:
                query = query.where(or_(*conditions))

        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            query = query.order_by(col.desc() if order_desc else col.asc())

        return query

    def get_total(self, db: Session, base_query=None) -> int:
        if base_query is None:
            count_query = select(func.count()).select_from(self.model)
        else:
            count_query = select(func.count()).select_from(base_query.subquery())
        return db.execute(count_query).scalar()

    def get(self, db: Session, id: str) -> ReadSchema:
        if id is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} id needed")

        obj = db.execute(select(self.model).where(self.model.id == id)).scalar_one_or_none()

        if obj is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return obj

    def get_all(
        self,
        db: Session,
        *,
        page: int = 1,
        pageSize: int = 100,
        filters: Optional[dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[list[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> dict:

        query = self._build_query(filters, search, search_fields, order_by, order_desc)
        total = self.get_total(db, query)

        skip = (page - 1) * pageSize
        data = db.execute(query.offset(skip).limit(pageSize)).scalars().all()

        return {
            "pager": {
                "page": page,
                "total": total,
                "pageSize": pageSize,
                "pageCount": math.ceil(total / pageSize) if total else 0,
            },
            "data": data,
        }

    def create(self, db: Session, *, payload_in: CreateSchema) -> ReadSchema:
        payload = payload_in.model_dump(exclude_unset=True)
        provided_id = payload.get("id")

        try:
            if provided_id:
                existing_obj = db.execute(
                    select(self.model).where(self.model.id == provided_id)
                ).scalar_one_or_none()

                if existing_obj:
                    update_data = {k: v for k, v in payload.items() if k != "id"}
                    result = db.execute(
                        update(self.model)
                        .where(self.model.id == provided_id)
                        .values(**update_data)
                        .returning(self.model)
                    )
                    db.commit()
                    updated_obj = result.scalar_one()
                    db.refresh(updated_obj)
                    return updated_obj

            db_obj = self.model(**payload)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete(self, db: Session, *, id: str) -> None:
        result = db.execute(delete(self.model).where(self.model.id == id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        db.commit()
