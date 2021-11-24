from .database import SessionLocal, engine
from .database import Base,engine,SessionLocal


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

