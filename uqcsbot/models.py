from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer


Base = declarative_base()


class Link(Base):  # type: ignore
    __tablename__ = 'links'

    id = Column("id", Integer, primary_key=True, nullable=False, autoincrement=True)
    key = Column("key", String, nullable=False)
    channel = Column("channel", String, nullable=True)
    value = Column("value", String, nullable=False)

    def __repr__(self):
        return f"Link({self.key}, {self.channel}, {self.value})"
