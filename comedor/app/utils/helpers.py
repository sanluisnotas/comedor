from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from app.models import Habitacion, Producto, Pedido, Categoria
import re

# Helper para respuestas API estandarizadas
def format_response(
    data: Any = None,
    message: str = "Operación exitosa",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict] = None
) -> Dict:
    """Formatea respuestas API consistentes"""
    response = {
        "success": status_code < 400,
        "message": message,
        "data": data
    }
    
    if meta:
        response["meta"] = meta
    
    return response

# Helpers para validación
def validate_phone_number(phone: str) -> bool:
    """Valida un número de teléfono internacional básico"""
    pattern = r'^\+?[1-9]\d{1,14}$'  # E.164 format
    return re.match(pattern, phone) is not None

def validate_room_number(number: str) -> bool:
    """Valida que el número de habitación tenga formato válido"""
    return number.isalnum() and 1 <= len(number) <= 10

# Helpers para operaciones comunes
def get_habitacion_by_numero(db: Session, numero: str) -> Habitacion:
    """Obtiene una habitación por su número"""
    habitacion = db.query(Habitacion).filter(Habitacion.numero == numero).first()
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitación {numero} no encontrada"
        )
    return habitacion

def get_producto_by_id(db: Session, producto_id: int) -> Producto:
    """Obtiene un producto por ID"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto or not producto.disponible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no disponible o no encontrado"
        )
    return producto

def calcular_total_pedido(pedidos: List[Pedido]) -> float:
    """Calcula el total de un conjunto de pedidos"""
    return sum(pedido.producto.precio * pedido.cantidad for pedido in pedidos)

def generar_codigo_pedido(habitacion_numero: str) -> str:
    """Genera un código único para un pedido"""
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    return f"PED-{habitacion_numero}-{timestamp}"

# Helper para paginación
def paginate_query(query, page: int = 1, per_page: int = 10):
    """Aplica paginación a una consulta SQLAlchemy"""
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Página y por página deben ser mayores a 0"
        )
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

# Helper para manejo de fechas
def parse_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    default_days: int = 7
) -> tuple[datetime, datetime]:
    """Parsea y valida un rango de fechas"""
    now = datetime.utcnow()
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else now - timedelta(days=default_days)
        end = datetime.fromisoformat(end_date) if end_date else now
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use ISO format (YYYY-MM-DD)"
        )
    
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fecha de inicio no puede ser mayor a fecha final"
        )
    
    return start, end
