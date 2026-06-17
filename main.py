from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import get_db, engine

# Nos aseguramos de que las tablas existan
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Investigación",
    description="Sistema de gestión para portafolio de investigaciones personales",
    version="1.0.0"
)

# Configuración de CORS para permitir la conexión desde el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta base de prueba
@app.get("/")
def ruta_principal():
    return {"mensaje": "El servidor está funcionando correctamente"}

# 1. Ruta para CREAR una investigación (POST)
@app.post("/investigaciones/", response_model=schemas.InvestigacionResponse)
def crear_investigacion(investigacion: schemas.InvestigacionCreate, db: Session = Depends(get_db)):
    nueva_investigacion = models.Investigacion(**investigacion.model_dump())
    db.add(nueva_investigacion)
    db.commit()
    db.refresh(nueva_investigacion)
    return nueva_investigacion

# 2. Ruta para OBTENER todas las investigaciones (GET)
@app.get("/investigaciones/", response_model=list[schemas.InvestigacionResponse])
def listar_investigaciones(db: Session = Depends(get_db)):
    investigaciones = db.query(models.Investigacion).all()
    return investigaciones

# 3. Ruta para ELIMINAR una investigación por ID (DELETE)
@app.delete("/investigaciones/{investigacion_id}")
def eliminar_investigacion(investigacion_id: int, db: Session = Depends(get_db)):
    investigacion = db.query(models.Investigacion).filter(models.Investigacion.id == investigacion_id).first()
    
    if not investigacion:
        raise HTTPException(status_code=404, detail="La investigación no existe")
        
    db.delete(investigacion)
    db.commit()
    return {"mensaje": f"Investigación con ID {investigacion_id} eliminada correctamente"}