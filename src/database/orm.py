from typing import List, Optional, Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql.expression import and_

from config import db_settings
from database.tables import Base, Journal, Proxy, User


class AsyncORM:
    _instance = None
    _async_engine = None
    _async_session = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._async_engine = create_async_engine(
                url=db_settings.db_url,
                echo=False,
            )

            cls._async_session = async_sessionmaker(bind=cls._async_engine)
        return cls._instance

    def __init__(self):
        self.async_engine = self._async_engine
        self.async_session = self._async_session

    # Table
    async def create_tables(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

    # User
    async def add_user(self, telegram_id: int, telegram_name: str) -> None:
        async with self.async_session() as session:
            query = insert(User).values(id=telegram_id, name=telegram_name)
            await session.execute(query)
            await session.commit()

    async def get_user(
        self,
        telegram_id: Optional[int] = None,
    ) -> Optional[Union[User, List[User]]]:
        if telegram_id:
            async with self.async_session() as session:
                query = select(User).where(User.id == telegram_id)
                result = await session.execute(query)
                user: Optional[User] = result.scalar_one_or_none()
            return user
        else:
            async with self.async_session() as session:
                query = select(User)
                result = await session.execute(query)
                users: Optional[List[User]] = result.scalars().all()
            return users

    async def change_money(self, id: int, amount: float) -> None:
        async with self.async_session() as session:
            query = (
                update(User)
                .where(User.id == id)
                .values(money=User.money + amount)
            )
            await session.execute(query)
            await session.commit()

    async def change_count_proxy(self, id: int, number: int) -> None:
        async with self.async_session() as session:
            query = (
                update(User)
                .where(User.id == id)
                .values(count_proxies=User.count_proxies + number)
            )
            await session.execute(query)
            await session.commit()

    # Proxy
    async def add_proxy(self, proxy: Proxy) -> None:
        async with self.async_session() as session:
            query = insert(Proxy).values(
                user_id=proxy.user_id,
                ip=proxy.ip,
                port=proxy.port,
                vless_id=proxy.vless_id,
                private_key=proxy.private_key,
                public_key=proxy.public_key,
                short_id=proxy.short_id,
                link=proxy.link,
                is_freezed=proxy.is_freezed,
            )
            await session.execute(query)
            await session.commit()

    async def remove_proxy(self, short_id: str) -> None:
        async with self.async_session() as session:
            query = delete(Proxy).where(Proxy.short_id == short_id)
            await session.execute(query)
            await session.commit()

    async def get_proxy(
        self, short_id: Optional[str] = None, user_id: Optional[int] = None
    ) -> Optional[Union[Proxy, List[Proxy]]]:
        if short_id:
            async with self.async_session() as session:
                query = select(Proxy).where(Proxy.short_id == short_id)
                result = await session.execute(query)
                proxy: Proxy = result.scalar_one_or_none()
            return proxy
        elif user_id:
            async with self.async_session() as session:
                query = select(Proxy).where(Proxy.user_id == user_id)
                result = await session.execute(query)
                proxies: Optional[List[Proxy]] = result.scalars().all()
            return proxies
        else:
            async with self.async_session() as session:
                query = select(Proxy)
                result = await session.execute(query)
                proxies: Optional[List[Proxy]] = result.scalars().all()
            return proxies

    async def freeze_proxy(self, short_id: str) -> None:
        async with self.async_session() as session:
            query = (
                update(Proxy)
                .where(Proxy.short_id == short_id)
                .values(is_freezed=True)
            )
            await session.execute(query)
            await session.commit()

    async def unfreeze_proxy(self, short_id: str) -> None:
        async with self.async_session() as session:
            query = (
                update(Proxy)
                .where(Proxy.short_id == short_id)
                .values(is_freezed=False)
            )
            await session.execute(query)
            await session.commit()

    # Journal
    async def add_journal_value(self, journal: Journal) -> None:
        async with self.async_session() as session:
            query = insert(Journal).values(
                user_id=journal.user_id,
                action=journal.action,
                proxy_id=journal.proxy_id,
            )
            await session.execute(query)
            await session.commit()

    async def get_journal_values(
        self,
        short_id: Optional[str] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
    ):
        if short_id:
            async with self.async_session() as session:
                query = select(Journal).where(Journal.proxy_id == short_id)
                result = await session.execute(query)
                journal_value: Journal = result.scalar_one_or_none()
            return journal_value
        elif user_id and action:
            async with self.async_session() as session:
                query = select(Journal).where(
                    and_(Journal.user_id == user_id, Journal.action == action)
                )
                result = await session.execute(query)
                journal_values: Optional[List[Journal]] = (
                    result.scalars().all()
                )
            return journal_values
        elif user_id:
            async with self.async_session() as session:
                query = select(Journal).where(Journal.user_id == user_id)
                result = await session.execute(query)
                journal_values: Optional[List[Journal]] = (
                    result.scalars().all()
                )
            return journal_values
        else:
            async with self.async_session() as session:
                query = select(Journal)
                result = await session.execute(query)
                journal_values: Optional[List[Journal]] = (
                    result.scalars().all()
                )
            return journal_values
