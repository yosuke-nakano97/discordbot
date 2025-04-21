from datetime import datetime
from logging import getLogger

import pytz
import sqlalchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(length=255))
    platform = Column(String(length=255), default="")
    time = Column(DateTime, index=True)
    user_id = Column(String(length=255), ForeignKey("user.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channel_d.id"), nullable=False)
    status = Column(String(length=255), default="unprocessed")
    user = relationship("User")
    channel = relationship("Channel_D")


class User(Base):
    __tablename__ = "user"

    id = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    count = Column(Integer, default=0)

    def increment(self):
        self.count += 1


class Channel_D(Base):
    __tablename__ = "channel_d"

    id = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    name = Column(String(length=255), nullable=False)
    count = Column(Integer, default=0)
    category_name = Column(Integer, ForeignKey("category.name"), nullable=True)
    category = relationship("Category")

    def increment(self):
        self.count += 1


class Channel_Y(Base):
    __tablename__ = "channel_y"

    id = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    name = Column(String(length=255), nullable=False)
    count = Column(Integer, default=0)
    icon = Column(String(length=255), default="")
    groupname = Column(Integer, ForeignKey("group.name"), nullable=True)
    group = relationship("Group")

    def increment(self):
        self.count += 1


class Twitter(Base):
    __tablename__ = "twitter"

    id = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    count = Column(Integer, default=0)
    groupname = Column(Integer, ForeignKey("group.name"), nullable=True)
    group = relationship("Group")

    def increment(self):
        self.count += 1


class Group(Base):
    __tablename__ = "group"

    name = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    count = Column(Integer, default=0)

    def increment(self):
        self.count += 1


class Domain(Base):
    __tablename__ = "domain"

    domain = Column(
        String(length=255),
        primary_key=True,
        index=True,
    )
    count = Column(Integer, default=0)

    def increment(self):
        self.count += 1


class VoiceStatus(Base):
    __tablename__ = "voice_status"
    unique_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(length=255), ForeignKey("user.id"))
    start_at = Column(DateTime, default=datetime.now(pytz.timezone("Asia/Tokyo")))
    end_at = Column(DateTime, nullable=True)
    channel_id = Column(String(length=255), ForeignKey("channel_d.id"))
    user = relationship("User")
    channel = relationship("Channel_D")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)


class Booking(Base):
    __tablename__ = "booking"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer())
    message = Column(String(length=400))
    datetime = Column(DateTime())
    channel_id = Column(Integer())
    target = Column(Integer())
    role = Column(Boolean())
    job_id = Column(String())


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)


engine = sqlalchemy.create_engine("sqlite:///vken.sqlite3", echo=False)

Base.metadata.create_all(bind=engine)
