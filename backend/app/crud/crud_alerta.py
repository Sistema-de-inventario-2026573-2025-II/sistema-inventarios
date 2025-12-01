# sistema-inventarios/backend/app/crud/crud_alerta.py
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any

from app.models.alerta import Alerta
from app.schemas.alerta import AlertaCreate, AlertaUpdate

logger = logging.getLogger(__name__)

def get_alerta(db: Session, alerta_id: int) -> Optional[Alerta]:
    """Obtiene una alerta por su ID."""
    return db.get(Alerta, alerta_id)

def get_alertas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[Alerta]:
    """Obtiene una lista de alertas."""
    return db.scalars(select(Alerta).offset(skip).limit(limit)).all()

def get_alertas_activas_by_tipo_entidad(
    db: Session, 
    tipo_alerta: str, 
    entidad_id: int, 
    entidad_tipo: str
) -> List[Alerta]:
    """
    Obtiene alertas activas para un tipo y entidad especificos.
    """
    stmt = select(Alerta).where(
        Alerta.tipo_alerta == tipo_alerta,
        Alerta.entidad_id == entidad_id,
        Alerta.entidad_tipo == entidad_tipo,
        Alerta.esta_activa == True
    )
    return db.scalars(stmt).all()


def create_alerta(db: Session, alerta: AlertaCreate) -> Alerta:
    """Crea una nueva alerta en la base de datos."""
    db_alerta = Alerta(**alerta.model_dump())
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)
    logger.info(f"Alerta creada: {db_alerta.tipo_alerta} para {db_alerta.entidad_tipo} ID {db_alerta.entidad_id}")
    return db_alerta

def deactivate_alerta(db: Session, alerta_id: int) -> Optional[Alerta]:
    """
    Desactiva una alerta existente por su ID.
    """
    db_alerta = db.get(Alerta, alerta_id)
    if db_alerta:
        db_alerta.esta_activa = False
        db.add(db_alerta)
        db.commit()
        db.refresh(db_alerta)
        logger.info(f"Alerta ID {alerta_id} desactivada.")
    return db_alerta

def deactivate_alertas_by_tipo_entidad(
    db: Session, 
    tipo_alerta: str, 
    entidad_id: int, 
    entidad_tipo: str
) -> None:
    """
    Desactiva todas las alertas activas para un tipo y entidad especificos.
    """
    stmt = update(Alerta).where(
        Alerta.tipo_alerta == tipo_alerta,
        Alerta.entidad_id == entidad_id,
        Alerta.entidad_tipo == entidad_tipo,
        Alerta.esta_activa == True
    ).values(esta_activa=False)
    db.execute(stmt)
    db.commit()
    logger.info(
        f"Alertas de tipo '{tipo_alerta}' para {entidad_tipo} "
        f"ID {entidad_id} desactivadas."
    )

def get_active_alertas(
    db: Session, 
    tipo_alerta: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Alerta]:
    """
    Obtiene todas las alertas activas, opcionalmente filtradas por tipo_alerta.
    """
    stmt = select(Alerta).where(Alerta.esta_activa == True)
    if tipo_alerta:
        stmt = stmt.where(Alerta.tipo_alerta == tipo_alerta)
    return db.scalars(stmt.offset(skip).limit(limit)).all()

