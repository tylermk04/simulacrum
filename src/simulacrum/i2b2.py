from sqlalchemy.ext.automap import automap_base

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine("postgresql+psycopg2://i2b2:i2b2@localhost/i2b2")

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.
# i.e. Observation = Base.classes.observation_fact

i2b2 = Base.classes

session = Session(engine)


def query(entity):
    return session.query(entity).all()
