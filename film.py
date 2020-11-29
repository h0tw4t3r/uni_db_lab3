from sqlalchemy import Column, String, Integer, Date

from base import Base


class Film(Base):
    __tablename__ = 'Films'

    id = Column(Integer, primary_key=True)
    f_duration = Column(Integer)
    f_name = Column(String(20))
    release_year = Column(Integer)
    f_genre = Column(String(10))
    def __repr__(self):
        return "<Films('%s', '%s', '%s', '%s')>" % (self.f_name, self.release_year, self.f_genre, self.f_duration)

