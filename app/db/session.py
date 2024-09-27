from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from app.shared.config import cfg


# Synchronous engine
engine_url = URL.create(
    cfg.DB_SCHEME,
    username=cfg.DB_USER,
    password=cfg.DB_PASSWORD,
    host=cfg.DB_HOST,
    port=cfg.DB_PORT,
    database=cfg.DB_NAME,
    query={'sslmode': f"{'disable' if cfg.BUILD_ENV == 'dev' else 'verify-full'}"},
)
engine = create_engine(engine_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous engine
engine_async_url = URL.create(
    cfg.DB_ASYNC_SCHEME,
    username=cfg.DB_USER,
    password=cfg.DB_PASSWORD,
    host=cfg.DB_HOST,
    port=cfg.DB_PORT,
    database=cfg.DB_NAME,
    query={'sslmode': 'verify-full'},
)
async_engine = create_async_engine(engine_async_url)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
