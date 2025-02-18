import asyncio

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

from .models import Bank, Base, Journal, Proxy, User


class BaseManager:
    """
    Базовый менеджер для работы с асинхронной ORM.
    """

    def __init__(self, session_maker):
        self.session_maker = session_maker


class UserManager(BaseManager):
    """
    Менеджер для управления пользователями.
    """

    async def add_user(self, tg_id: int, tg_name: str) -> None:
        """Добавляет нового пользователя в таблицу users."""
        async with self.session_maker() as session:
            try:
                user = User(id=tg_id, name=tg_name)
                session.add(user)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при добавлении пользователя: {e}")

    async def change_balance(self, tg_id: int, amount: float) -> None:
        """Изменяет баланс пользователя на указанную сумму."""
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == tg_id)
                )
                user: User = result.scalar_one_or_none()
                if user:
                    user.money += amount
                    await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при изменении баланса: {e}")

    async def change_proxy_count(self, tg_id: int, count: int) -> None:
        """Изменяет количество прокси у пользователя."""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == tg_id)
                )
                user: User = result.scalar_one_or_none()
                if user:
                    user.proxy_count += count
                    await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при изменении количества прокси: {e}")


class ProxyManager(BaseManager):
    """
    Менеджер для управления прокси.
    """

    async def add_proxy(
        self, uuid: str, short_id: str, user_id: int, server_ip: str, link: str
    ) -> None:
        """Добавляет новый прокси в таблицу proxies."""
        async with self.session_maker() as session:
            try:
                proxy = Proxy(
                    uuid=uuid,
                    short_id=short_id,
                    user_id=user_id,
                    server_ip=server_ip,
                    link=link,
                )
                session.add(proxy)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при добавлении прокси: {e}")

    async def remove_proxy(self, short_id: str) -> None:
        """Удаляет прокси из таблицы proxies."""
        async with self.session_maker() as session:
            try:
                query = delete(Proxy).where(Proxy.short_id == short_id)
                await session.execute(query)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при удалении прокси: {e}")

    async def freeze_proxy(self, short_id: str) -> None:
        """Замораживает прокси, устанавливая флаг is_freeze в True."""
        await self._update_proxy_status(short_id, True)

    async def unfreeze_proxy(self, short_id: str) -> None:
        """Размораживает прокси, устанавливая флаг is_freeze в False."""
        await self._update_proxy_status(short_id, False)

    async def _update_proxy_status(self, short_id: str, status: bool) -> None:
        """Вспомогательный метод для обновления статуса `is_freeze`."""
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Proxy).where(Proxy.short_id == short_id)
                )
                proxy: Proxy = result.scalar_one_or_none()
                if proxy:
                    proxy.is_freeze = status
                    await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при изменении статуса прокси: {e}")


class JournalManager(BaseManager):
    """
    Менеджер для управления журналом событий.
    """

    async def add_journal_record(self, action: str, description: str) -> None:
        """Добавляет запись в журнал (таблица journal)."""
        async with self.session_maker() as session:
            try:
                record = Journal(action=action, description=description)
                session.add(record)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при добавлении записи в журнал: {e}")


class BankManager(BaseManager):
    """
    Менеджер для управления банковскими операциями.
    """

    async def add_bank_record(self, tg_id: int, amount: float) -> None:
        """Добавляет запись о финансовой операции в таблицу bank."""
        async with self.session_maker() as session:
            try:
                record = Bank(user_id=tg_id, amount=amount)
                session.add(record)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(f"Ошибка при добавлении записи в банк: {e}")


class AsyncORM:
    """
    Главный класс ORM, объединяющий управление пользователями,
    прокси, журналом и банком.
    """

    _instance: "AsyncORM | None" = None
    _lock: asyncio.Lock

    _async_session: async_sessionmaker
    _async_engine: AsyncEngine

    user: UserManager
    proxy: ProxyManager
    journal: JournalManager
    bank: BankManager

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._async_engine = create_async_engine(
                url=settings.db.DB_URL, echo=False
            )
            cls._instance._async_session = async_sessionmaker(
                bind=cls._instance._async_engine, expire_on_commit=False
            )

            # Создаем менеджеры
            cls._instance.user = UserManager(cls._instance._async_session)
            cls._instance.proxy = ProxyManager(cls._instance._async_session)
            cls._instance.journal = JournalManager(
                cls._instance._async_session
            )
            cls._instance.bank = BankManager(cls._instance._async_session)
        return cls._instance

    async def create_tables(self) -> None:
        """Создает все таблицы в базе данных."""
        async with self._async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Удаляет все таблицы из базы данных."""
        async with self._async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
