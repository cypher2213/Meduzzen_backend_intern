import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)


class AsyncBaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def create(
        self, session: AsyncSession, data: Dict[str, Any], commit=True
    ) -> T:
        obj = self.model(**data)
        session.add(obj)
        if commit:
            await session.commit()
            await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, id: uuid.UUID) -> Optional[T]:
        return await session.get(self.model, id)

    async def get_all(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ) -> List[T]:
        statement = select(self.model).limit(limit).offset(offset)
        result = await session.execute(statement)
        return result.scalars().all()

    async def update(self, session: AsyncSession, obj: T, commit=True) -> T:
        session.add(obj)
        if commit:
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj: T, commit=True) -> bool:
        await session.delete(obj)
        if commit:
            await session.commit()
        return True
