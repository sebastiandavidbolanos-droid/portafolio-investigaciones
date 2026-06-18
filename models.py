from sqlalchemy import Column, Integer, String
from database import Base

class Investigacion(Base):
    __tablename__ = "investigaciones"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    autor = Column(String)
    resumen = Column(String)
    linea_investigacion = Column(String)
    archivo_url = Column(String, nullable=True) # <-- NUEVO CAMPO