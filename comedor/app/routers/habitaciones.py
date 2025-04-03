from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas
from app.models import Habitacion
from app.database import get_db
from app.utils.auth import create_access_token
from typing import List

router = APIRouter()

@router.post("/verificar/")
async def verificar_habitacion(
    request: Request,
    numero: str,
    apellido: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Habitacion).where(
        Habitacion.numero == numero,
        Habitacion.apellido == apellido
    )
    result = await db.execute(stmt)
    habitacion = result.scalars().first()

    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    token = create_access_token({
        "habitacion_id": habitacion.id,
        "numero": habitacion.numero,
        "apellido": habitacion.apellido
    })
    
    response = Response(content="Verificación exitosa")
    response.set_cookie(
        key="habitacion_token",
        value=token,
        httponly=True,
        max_age=3600
    )
    
    return response

@router.get("/", response_model=List[schemas.HabitacionResponse])
async def listar_habitaciones(db: AsyncSession = Depends(get_db)):
    stmt = select(Habitacion)
    result = await db.execute(stmt)
    return result.scalars().all()