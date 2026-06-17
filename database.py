from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuramos la conexión a SQLite (se creará el archivo localmente)
SQLALCHEMY_DATABASE_URL = "sqlite:///./investigaciones.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para obtener la base de datos cuando la necesitemos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()