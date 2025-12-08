from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry


Base = declarative_base()


class GPSData(Base):
    __tablename__ = "gps_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, nullable=False)  # Assuming vehicle ID is an integer
    timestamp = Column(DateTime, nullable=False)
    speed = Column(Integer, nullable=True)
    route_id = Column(Integer, nullable=True)
    azimuth = Column(Integer, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
