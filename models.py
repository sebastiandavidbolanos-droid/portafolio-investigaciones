from sqlalchemy import Column, Integer, String, Text
from database import Base

class Investigacion(Base):
    __tablename__ = "investigaciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    resumen = Column(Text)
    linea_investigacion = Column(String)