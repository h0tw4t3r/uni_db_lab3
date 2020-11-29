from datetime import date

import base
from film import Film
from cinema import Cinema
from session import Session

# 1 - drop all data
base.Base.metadata.drop_all(base.engine)
# 2 - generate database schema
base.Base.metadata.create_all(base.engine)

# 3 - create a new session
session = base.Session()


# 4 - create films
#bourne_identity = Film("The Bourne Identity", 2002, "Action", 119)
#furious_7 = Film("Furious 7", 2015, "Action", 137)
#pain_and_gain = Film("Pain & Gain", 2013, "Comedy", 129)
#session.add(bourne_identity)
#session.add(furious_7)
#session.add(pain_and_gain)
#c1 = Cinema("123", "123")
#session.add(c1)

#Cinema
cinema1 = Cinema("Kiev", "Velyka Vasylkivska Street, 19")
cinema2 = Cinema("October", "Konstantinovskaya Street, 26")
cinema3 = Cinema("Torch", "Mykola Bazhana Avenue, 3")

#Film
film1 = Film("InterStellar", 2014, "Fantastic", 168)
film2 = Film("Joker", 2019, "Drama", 116)
film3 = Film("Gentlemen", 2019, "Criminal", 113)

#Session
session1 = Session("2020-09-17", "Almandine", film1)
session1.cinemas = [cinema1]
session2 = Session("2020-09-17", "Ultramarine", film2)
session2.cinemas = [cinema2]
session3 = Session("2020-09-18", "Terracotta", film3)
session3.cinemas = [cinema3]

# 9 - persists data

session.add(cinema1)
session.add(cinema2)
session.add(cinema3)

session.add(film1)
session.add(film2)
session.add(film3)


session.add(session1)
session.add(session2)
session.add(session3)

# 10 - commit and close session
session.commit()

films = session.query(Film).all()

print('\n### All movies:')
for film in films:
    print(film)
print('')

session.close()

fruits = ['lemon', 'pear', 'watermelon', 'tomato']
print(*fruits)
print(Cinema.__table__.columns.keys())
for c in Cinema.__table__.columns:
    print(c.name, c.type)
print(Cinema.__table__.columns)

