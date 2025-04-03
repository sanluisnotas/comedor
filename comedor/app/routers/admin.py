# hotel_pedidos/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app import schemas
from app.models import Habitacion, Pedido, Producto, Categoria
from app.database import get_db
from app.utils.security import get_current_admin  # Cambiado de auth a security

router = APIRouter(
    prefix="/api/admin",
    tags=["Administración"],
    dependencies=[Depends(get_current_admin)]  # Usamos get_current_admin como dependencia global
)

# Modelo Pydantic para creación de productos
class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria_id: int
    disponible: bool = True
    imagen: Optional[str] = None

@router.get("/habitaciones/", response_model=List[schemas.HabitacionResponse])
async def listar_habitaciones(db: Session = Depends(get_db)):
    """
    Lista todas las habitaciones (solo administradores)
    """
    return db.query(Habitacion).all()

@router.get("/pedidos/", response_model=List[schemas.PedidoResponse])
async def listar_pedidos(db: Session = Depends(get_db)):
    """
    Lista todos los pedidos ordenados por fecha (solo administradores)
    Incluye información completa de habitaciones y productos
    """
    return db.query(Pedido).order_by(Pedido.fecha.desc()).all()

@router.post("/productos/", response_model=schemas.ProductoResponse)
async def crear_producto(
    producto_data: ProductoCreate, 
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo producto (solo administradores)
    """
    # Verificar que la categoría existe
    categoria = db.query(Categoria).filter(Categoria.id == producto_data.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría especificada no existe"
        )
    
    # Crear el producto
    nuevo_producto = Producto(
        nombre=producto_data.nombre,
        descripcion=producto_data.descripcion,
        precio=producto_data.precio,
        categoria_id=producto_data.categoria_id,
        disponible=producto_data.disponible,
        imagen=producto_data.imagen,
    )
    
    try:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el producto: {str(e)}"
        )

@router.put("/pedidos/{pedido_id}", response_model=schemas.PedidoResponse)
async def actualizar_estado_pedido(
    pedido_id: int,
    estado: schemas.EstadoPedido,
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un pedido (solo administradores)
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    pedido.estado = estado
    if estado == "entregado":
        pedido.hora_entrega = datetime.utcnow()
    
    db.commit()
    db.refresh(pedido)
    return pedido