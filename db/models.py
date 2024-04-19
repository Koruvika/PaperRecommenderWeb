"""Models"""

import uuid

from sqlalchemy import (
    UUID,
    ARRAY,
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    create_engine,
    func,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from .constant import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)
from logger.logger import custom_logger

custom_logger.info("Connecting PostgreSQL Database.")

POSTGRES_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    POSTGRES_DATABASE_URL,
    pool_size=10,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)

custom_logger.info("Connect to PostgreSQL Database Success.")


def get_db():
    """Get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BaseModel(Base):
    """Base model."""
    __abstract__ = True

    updated_at = Column(name="updated_at", type_=DateTime(timezone=True), server_default=func.now())


class PaperInformation(BaseModel):
    """Paper information model."""
    __tablename__ = "paper_information"

    id = Column(name="id", type_=String, primary_key=True)
    title = Column(name="title", type_=String)
    link = Column(name="link", type_=String)
    publish_year = Column(name="publish_year", type_=Integer)
    abstract = Column(name="abstract", type_=String)
    n_citations = Column(name="n_citatons", type_=Integer)
    author = Column(name="author", type_=ARRAY(String))
    conference = Column(name="conference", type_=String)
    tag = Column(name="tags", type_=ARRAY(String))


class User(BaseModel):
    """User model."""
    __tablename__ = "user"

    id = Column(name="id", type_=UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(name="username", type_=String, nullable=False)
    email = Column(name="email", type_=String, nullable=False)
    hashed_password  = Column(name="password", type_=String)
    name = Column(name="name", type_=String)


class PaperGroup(BaseModel):
    """Paper group model."""
    __tablename__ = "paper_group"

    id = Column(name="id", type_=UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    group_name = Column(name="group_name", type_=String)
    user_id = Column(UUID, ForeignKey("user.id"))


class PaperGroupInformation(BaseModel):
    """Paper group model."""
    __tablename__ = "paper_group_information"

    id = Column(name="id", type_=UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    group_id = Column(ForeignKey("paper_group.id"), type_=UUID(as_uuid=True))
    paper_id = Column(name="paper_id", type_=String)
    date = Column(name="date", type_=DateTime(timezone=True), server_default=func.now())
    appropriate = Column(name="appropriate", type_=Boolean)
    