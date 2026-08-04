from pydantic import BaseModel

# Esquema para crear una nueva investigación (lo que pedimos al usuario)
class InvestigacionCreate(BaseModel):
    titulo: str
    autor: str
    resumen: str
    linea_investigacion: str

# Esquema para responder (incluye el ID que genera la base de datos)
class InvestigacionResponse(InvestigacionCreate):
    id: int

    class Config:
        from_attributes = True