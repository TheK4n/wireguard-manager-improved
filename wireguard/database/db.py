from typing import Sequence
import asyncio
from datetime import timedelta, date
from sqlalchemy import CursorResult, delete, insert, select, func, update
from sqlalchemy.ext.asyncio import create_async_engine

from wireguard.database.models import Client, Plan, Base
from wireguard.wireguard_config.models import Client as ClientModel


class DB:
    _blank_client_name = "blank"

    def __init__(self, user, password, host, port, dbname):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}",
            echo=True)


class DBMain(DB):
    async def select_all_active_clients(self) -> Sequence[Client]:
        async with self.engine.connect() as conn:
            active_clients = await conn.execute(
                select(Client).
                where(Client.is_active).
                filter(Client.name != self._blank_client_name)
            )
            return active_clients.fetchall()

    async def create_and_populate_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            plans = await self.__generate_plans()

            await conn.execute(insert(Plan), plans)

            await conn.execute(insert(Client),
                 {"name": self._blank_client_name,
                  "addr4": "10.0.0.2",
                  "privatekey": "0"*44,
                  "publickey": "0"*44,
                  "presharedkey": "0"*44,
                  "last_update": date.today(),
                  "plan_pid": 1,
                 })
        
            await conn.commit()
        await self.engine.dispose()

    async def __generate_plans(self) -> list[dict[str, str | timedelta]]:
        res = []
        res.append(await self.__generate_plan("1 month", 199, timedelta(days=30)))
        res.append(await self.__generate_plan("3 month", 399, timedelta(days=90)))
        res.append(await self.__generate_plan("1 year", 1599, timedelta(days=365)))
        return res

    async def __generate_plan(self, name: str, price: int, period: timedelta) -> dict[str, str | timedelta]:
        return {
                "name": name,
                "price": str(price),
                "period": period
               }


class DBApi(DB):
    async def select_all_active_clients_names(self):
        async with self.engine.connect() as conn:
            active_clients = await conn.execute(
                select(Client.name).
                where(Client.is_active).
                filter(Client.name != self._blank_client_name)
            )
            return [row[0] for row in active_clients.fetchall()]

    async def select_unactive_clients_names(self):
        async with self.engine.connect() as conn:
            active_clients = await conn.execute(
                select(Client.name).
                where(not Client.is_active).
                filter(Client.name != self._blank_client_name)
            )
            return [row[0] for row in active_clients.fetchall()]


    async def select_client(self, username: str) -> Client:
        async with self.engine.connect() as conn:
            client = await conn.execute(
                select(Client).
                where(Client.name == username)
            )
            return client.fetchone()

    async def deactivate_client(self, username: str):
        await self.__commit_query(
                   update(Client).
                   values(is_active=False).
                   where(Client.name==username))

    async def activate_client(self, username: str):
        await self.__commit_query(
                   update(Client).
                   values(is_active=True).
                   where(Client.name==username))

    async def delete_client(self, username: str) -> Client:
        res = await self.__commit_query(
                   delete(Client).
                   returning(Client).
                   where(Client.name==username))
        return res.fetchone()

    async def __commit_query(self, query) -> CursorResult:
        async with self.engine.connect() as conn:
            res = await conn.execute(query)
            await conn.commit()
            return res
    
    async def insert_new_client(self, client: ClientModel) -> Client:
        async with self.engine.connect() as conn:
            free_addr = await self.__get_free_ipv4_addr(conn)
            res = await conn.execute(
                insert(Client).returning(Client), {
                    "name": client.name,
                    "addr4": free_addr,
                    "privatekey": client.privatekey,
                    "publickey": client.publickey,
                    "presharedkey": client.presharedkey,
                    "last_update": date.today(),
                    "plan_pid": 1,
                    }
            )
            await conn.commit()
            return res.fetchone()

    async def __get_free_ipv4_addr(self, conn) -> str:
        addresses = (await conn.execute(select(Client.addr4))).fetchall()
        missing_adress_numbers = self.__find_missing_address_numbers(addresses)

        if missing_adress_numbers:
            return f"10.0.0.{missing_adress_numbers[0]}"

        return (
                await conn.execute(
                    func.max(Client.addr4 + 1)
                )
               ).fetchone()[0]

    @staticmethod
    def __find_missing_address_numbers(addresses: list[str]) -> list[int]:

        address_numbers = tuple(map(lambda addr: int(str(addr[0]).split(".")[-1]), addresses))

        start = address_numbers[0]
        end = address_numbers[-1]
        free_address_numbers = sorted(set(range(start, end + 1)). difference(address_numbers))

        return free_address_numbers


if __name__ == '__main__':
    from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
    db = DBMain(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    asyncio.run(db.create_and_populate_tables())

