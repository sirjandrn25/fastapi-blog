from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:meronaam54@localhost/blog_fastapi"
SQLALCHEMY_DATABASE_URL="postgresql://wimurfeprqdbde:6408e1bd2aca6118bc2e3fc987e8291cd03f3645986e00b4f185bef3dfaa9d38@ec2-75-101-141-195.compute-1.amazonaws.com:5432/d4gsjofmrjcl5h"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()