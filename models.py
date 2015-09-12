from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float


class States(Base):

    __tablename__ = 'states'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)

    # These two flags to identify the latlngs processd or not.
    latlongs = Column(Boolean)
    pincodes = Column(Boolean)


    def __repr__(self):
        return '<States %r>' % (self.name)


class Pincodes(Base):

    __tablename__ = 'pincodes'

    pincode = Column(Integer, primary_key=True, autoincrement=False)
    state_id = Column(Integer, ForeignKey('states.id'))
    latitude = Column(Float)
    longitude = Column(Float)

    def __repr__(self):
        return '<Pincodes %r>' % (self.pincode)

