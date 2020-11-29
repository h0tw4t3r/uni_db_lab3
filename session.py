from sqlalchemy import Column, String, Integer, Date, ForeignKey, Table
from sqlalchemy.orm import relationship

from base import Base

cinema_session_association = Table(
    'Cinema_Session', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('session_id', Integer, ForeignKey('Sessions.id')),
    Column('cinema_id', Integer, ForeignKey('Cinemas.id'))
)


class Session(Base):
    __tablename__ = 'Sessions'

    id = Column(Integer, primary_key=True)
    start_date = Column(Date)
    hall_name = Column(String(20))
    film_id = Column(Integer, ForeignKey('Films.id'))
    film = relationship("Film", uselist=False)
    cinemas = relationship("Cinema", secondary=cinema_session_association)

    def __repr__(self):
        return "<Sessions('%s', '%s', '%s')>" % (self.start_date, self.hall_name, self.film.s_name)
