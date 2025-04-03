# hotel_pedidos/app/routers/pedidos.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete, update
from app import schemas
from app.database import get_db
from app.models import Pedido
from app.utils.security import get_current_habitacion
from typing import List

router = APIRouter(tags=["Pedidos"])

@router.post("/", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED)
async def create_pedido(
    pedido: schemas.PedidoCreateFrontend,
    request: Request,
    habitacion: dict = Depends(get_current_habitacion),
    db: AsyncSession = Depends(get_db)
):
    db_pedido = Pedido(
        habitacion_id=habitacion["id"],
        producto_id=pedido.producto_id,
        cantidad=pedido.cantidad,
        notas=pedido.notas,
        estado="pendiente"
    )
    db.add(db_pedido)
    await db.commit()
    await db.refresh(db_pedido)
    
    stmt = (
        select(Pedido)
        .where(Pedido.id == db_pedido.id)
        .options(
            selectinload(Pedido.habitacion),
            selectinload(Pedido.producto)
        )
    )
    result = await db.execute(stmt)
    pedido_completo = result.scalars().first()
    
    # Serialización manual
    return schemas.PedidoResponse(
        id=pedido_completo.id,
        habitacion_id=pedido_completo.habitacion_id,
        producto_id=pedido_completo.producto_id,
        cantidad=pedido_completo.cantidad,
        notas=pedido_completo.notas,
        estado=pedido_completo.estado,
        fecha=pedido_completo.fecha,
        hora_entrega=pedido_completo.hora_entrega,
        producto=schemas.ProductoSimpleResponse(
            id=pedido_completo.producto.id,
            nombre=pedido_completo.producto.nombre,
            precio=pedido_completo.producto.precio,
            imagen=pedido_completo.producto.imagen,
            disponible=pedido_completo.producto.disponible
        ),
        habitacion=schemas.HabitacionResponse(
            id=pedido_completo.habitacion.id,
            numero=pedido_completo.habitacion.numero,
            apellido=pedido_completo.habitacion.apellido,
            telefono=pedido_completo.habitacion.telefono,
            check_in=pedido_completo.habitacion.check_in,
            check_out=pedido_completo.habitacion.check_out,
            activa=pedido_completo.habitacion.activa
        )
    )

@router.get("/pendientes", response_model=List[schemas.PedidoResponse])
async def get_pedidos_pendientes(
    request: Request,
    habitacion: dict = Depends(get_current_habitacion),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Pedido)
        .where(Pedido.estado == "pendiente")
        .where(Pedido.habitacion_id == habitacion["id"])
        .options(
            selectinload(Pedido.habitacion),
            selectinload(Pedido.producto)
        )
    )
    result = await db.execute(stmt)
    pedidos = result.scalars().all()
    
    # Serialización manual para la lista
    return [
        schemas.PedidoResponse(
            id=pedido.id,
            habitacion_id=pedido.habitacion_id,
            producto_id=pedido.producto_id,
            cantidad=pedido.cantidad,
            notas=pedido.notas,
            estado=pedido.estado,
            fecha=pedido.fecha,
            hora_entrega=pedido.hora_entrega,
            producto=schemas.ProductoSimpleResponse(
                id=pedido.producto.id,
                nombre=pedido.producto.nombre,
                precio=pedido.producto.precio,
                imagen=pedido.producto.imagen,
                disponible=pedido.producto.disponible
            ),
            habitacion=schemas.HabitacionResponse(
                id=pedido.habitacion.id,
                numero=pedido.habitacion.numero,
                apellido=pedido.habitacion.apellido,
                telefono=pedido.habitacion.telefono,
                check_in=pedido.habitacion.check_in,
                check_out=pedido.habitacion.check_out,
                activa=pedido.habitacion.activa
            )
        )
        for pedido in pedidos
    ]

@router.put("/{pedido_id}", response_model=schemas.PedidoResponse)
async def update_pedido(
    pedido_id: int,
    pedido_update: schemas.PedidoUpdate,
    request: Request,
    habitacion: dict = Depends(get_current_habitacion),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Pedido)
        .where(Pedido.id == pedido_id)
        .where(Pedido.habitacion_id == habitacion["id"])
        .options(
            selectinload(Pedido.habitacion),
            selectinload(Pedido.producto)
        )
    )
    result = await db.execute(stmt)
    pedido = result.scalars().first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    update_data = pedido_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pedido, key, value)
    
    await db.commit()
    await db.refresh(pedido)
    
    # Serialización manual
    return schemas.PedidoResponse(
        id=pedido.id,
        habitacion_id=pedido.habitacion_id,
        producto_id=pedido.producto_id,
        cantidad=pedido.cantidad,
        notas=pedido.notas,
        estado=pedido.estado,
        fecha=pedido.fecha,
        hora_entrega=pedido.hora_entrega,
        producto=schemas.ProductoSimpleResponse(
            id=pedido.producto.id,
            nombre=pedido.producto.nombre,
            precio=pedido.producto.precio,
            imagen=pedido.producto.imagen,
            disponible=pedido.producto.disponible
        ),
        habitacion=schemas.HabitacionResponse(
            id=pedido.habitacion.id,
            numero=pedido.habitacion.numero,
            apellido=pedido.habitacion.apellido,
            telefono=pedido.habitacion.telefono,
            check_in=pedido.habitacion.check_in,
            check_out=pedido.habitacion.check_out,
            activa=pedido.habitacion.activa
        )
    )

@router.delete("/{pedido_id}")
async def delete_pedido(
    pedido_id: int,
    request: Request,
    habitacion: dict = Depends(get_current_habitacion),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Pedido)
        .where(Pedido.id == pedido_id)
        .where(Pedido.habitacion_id == habitacion["id"])
    )
    result = await db.execute(stmt)
    pedido = result.scalars().first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    await db.execute(delete(Pedido).where(Pedido.id == pedido_id))
    await db.commit()
    return {"message": "Pedido eliminado"}

@router.post("/confirmar")
async def confirmar_pedidos(
    request: Request,
    habitacion: dict = Depends(get_current_habitacion),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        update(Pedido)
        .where(Pedido.habitacion_id == habitacion["id"])
        .where(Pedido.estado == "pendiente")
        .values(estado="en_proceso")
    )
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No hay pedidos pendientes para confirmar")
    return {"message": "Pedidos confirmados exitosamente"}