from sqlalchemy import Column, String, Integer

from base import Base


class Cinema(Base):
    __tablename__ = 'Cinemas'

    id = Column(Integer, primary_key=True)
    c_name = Column(String(20))
    address = Column(String(40))

    def __repr__(self):
        return "<Cinemas('%s', '%s')>" % (self.c_name, self.address)
