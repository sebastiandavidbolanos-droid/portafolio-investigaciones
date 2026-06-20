from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
import database, models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

# --- CONFIGURA TUS DATOS DE CLOUDINARY AQUÍ ---
cloudinary.config(
    cloud_name = "dyztae4s3",
    api_key = "426115579511919",
    api_secret = "iF_wRp4nN9Y90CbJ2zzWvSOt1zk" 
)


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/investigaciones/")
async def create_investigacion(
    titulo: str = Form(...),
    autor: str = Form(...),
    resumen: str = Form(...),
    linea_investigacion: str = Form(...),
    file: UploadFile = File(None), # El archivo es opcional
    db: Session = Depends(get_db)
):
    file_url = None
    if file:
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(file.file, resource_type="auto")
        file_url = result.get("secure_url")

    new_inv = models.Investigacion(
        titulo=titulo, autor=autor, resumen=resumen, 
        linea_investigacion=linea_investigacion, archivo_url=file_url
    )
    db.add(new_inv)
    db.commit()
    return {"message": "Guardado"}

@app.get("/investigaciones/")
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Investigacion).all()