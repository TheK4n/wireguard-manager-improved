from typing import Optional
import sqlalchemy as sa
from sqlalchemy import ForeignKey, orm
from sqlalchemy.dialects import postgresql
import datetime
from wireguard.config import CLIENT_USERNAME_MAX_LENGTH


class Base(orm.DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    __table_args__ = (
        sa.CheckConstraint("addr4 >= INET '10.0.0.2'"),
        sa.CheckConstraint("addr4 <= INET '10.0.0.254'"),
        sa.CheckConstraint("length(privatekey) = 44"),
        sa.CheckConstraint("length(publickey) = 44"),
        sa.CheckConstraint("length(presharedkey) = 44"),
    )

    pid: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(CLIENT_USERNAME_MAX_LENGTH), unique=True)
    contact: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(350))
    addr4 = sa.Column(postgresql.INET(), unique=True, nullable=False)
    addr6 = sa.Column(postgresql.INET(), unique=True)
    privatekey: orm.Mapped[str] = orm.mapped_column(sa.String(44))
    publickey: orm.Mapped[str] = orm.mapped_column(sa.String(44))
    presharedkey: orm.Mapped[str] = orm.mapped_column(sa.String(44), nullable=True)
    is_active: orm.Mapped[bool] = orm.mapped_column(default=True)
    reg: orm.Mapped[datetime.date] = orm.mapped_column(default=datetime.date.today)
    last_update: orm.Mapped[datetime.date] = orm.mapped_column()
    plan_pid: orm.Mapped[int] = orm.mapped_column(ForeignKey("plans.pid"))


class Plan(Base):
    __tablename__ = "plans"

    __table_args__ = (
        sa.CheckConstraint("length(name) <= 70"),
        sa.CheckConstraint("price > MONEY(0)"),
        sa.CheckConstraint("period >= INTERVAL '1 day'"),
    )

    pid: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)
    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    price = sa.Column(postgresql.MONEY(), nullable=False)
    period = sa.Column(postgresql.INTERVAL(), nullable=False)

