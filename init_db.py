from database import engine, Base
import models

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Base de datos creada exitosamente!")