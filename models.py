from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base

class Parcela(Base):
    __tablename__ = "parcelas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    cultivo = Column(String, nullable=False)
    textura_suelo = Column(String, nullable=False)
    
    # Campo geométrico de PostGIS. Utiliza SRID 4326 (WGS 84, Lat/Lon)
    geometria = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=True)
    
    # Datos generales
    area_util_ha = Column(Float, nullable=False)
    
    # Parámetros agronómicos extraídos de la FASE 0-1
    cad = Column(Float, nullable=True)  # Capacidad de Almacenamiento de Agua
    profundidad_radicular = Column(Float, nullable=True) # metros
    fraccion_agotamiento = Column(Float, nullable=True) # factor f (0-1)
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
