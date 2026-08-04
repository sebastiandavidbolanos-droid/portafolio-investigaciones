import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import cloudinary
import cloudinary.uploader
import jwt
from passlib.context import CryptContext

# ----------------------------------------------------
# 1. CONFIGURACIÓN DE SEGURIDAD JWT Y HASHER
# ----------------------------------------------------
SECRET_KEY = "CAMBIA_ESTA_CLAVE_SUPER_SECRETA_Y_LARGA_PARA_PRODUCCION" # Cambiar por una cadena segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # El token durará 8 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Credenciales del Administrador (En producción pueden guardarse en variables de entorno)
ADMIN_USERNAME = "admin_eugenia"
# Hash cifrado de la contraseña inicial (por ejemplo, para la clave 'Eugenia2026*')
# Puedes cambiar la contraseña usando pwd_context.hash("tu_clave")
ADMIN_PASSWORD_HASH = pwd_context.hash("Eugenia2026*")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación no válidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


# ----------------------------------------------------
# 2. CONFIGURACIÓN DE CLOUDINARY
# ----------------------------------------------------
cloudinary.config(
    cloud_name="dyztae4s3",
    api_key="426115579511919",
    api_secret="AQUI_PONES_TU_API_SECRET" # <-- Tu API Secret real de Cloudinary
)


# ----------------------------------------------------
# 3. BASE DE DATOS (SQLAlchemy)
# ----------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./investigaciones.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Investigacion(Base):
    __tablename__ = "investigaciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), index=True)
    autor = Column(String(100))
    resumen = Column(Text)
    linea_investigacion = Column(String(100))
    archivo_url = Column(String(500), nullable=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------
# 4. INICIALIZACIÓN DE FASTAPI Y CORS
# ----------------------------------------------------
app = FastAPI(title="API Portafolio de Investigación")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cuando tengamos el dominio definitivo, lo restringiremos aquí
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------
# 5. RUTAS DE LA API
# ----------------------------------------------------

# Ruta de Login para obtener el Token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or not verify_password(form_data.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# RUTA PÚBLICA: Obtener lista de investigaciones (No requiere token)
@app.get("/investigaciones/")
def obtener_investigaciones(db: Session = Depends(get_db)):
    return db.query(Investigacion).all()


# RUTA PROTEGIDA: Crear una nueva investigación (REQUIERE TOKEN JWT)
@app.post("/investigaciones/", status_code=201)
async def crear_investigacion(
    titulo: str = Form(...),
    autor: str = Form(...),
    resumen: str = Form(...),
    linea_investigacion: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin) # <-- Protección activada
):
    archivo_url = None
    if file:
        resultado_subida = cloudinary.uploader.upload(file.file, resource_type="auto")
        archivo_url = resultado_subida.get("secure_url")

    nueva_investigacion = Investigacion(
        titulo=titulo,
        autor=autor,
        resumen=resumen,
        linea_investigacion=linea_investigacion,
        archivo_url=archivo_url
    )
    db.add(nueva_investigacion)
    db.commit()
    db.refresh(nueva_investigacion)
    return nueva_investigacion


# RUTA PROTEGIDA: Eliminar investigación (REQUIERE TOKEN JWT)
@app.delete("/investigaciones/{investigacion_id}")
def eliminar_investigacion(
    investigacion_id: int, 
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin) # <-- Protección activada
):
    investigacion = db.query(Investigacion).filter(Investigacion.id == investigacion_id).first()
    if not investigacion:
        raise HTTPException(status_code=404, detail="Investigación no encontrada")
    
    db.delete(investigacion)
    db.commit()
    return {"mensaje": "Investigación eliminada exitosamente"}