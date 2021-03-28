from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String


Base = declarative_base()


class Link(Base):
    __tablename__ = 'links'

    key = Column("key", String, primary_key=True, nullable=False)
    channel = Column("channel", String, primary_key=True, nullable=True)
    value = Column("value", String, nullable=False)

    def __repr__(self):
        return f"<Link: ({self.key}, {self.channel} = {self.value})>"
