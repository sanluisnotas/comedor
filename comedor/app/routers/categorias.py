from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import schemas
from app.models import Categoria
from app.database import get_db
from typing import List

router = APIRouter(
    prefix="/api/categorias",
    tags=["Categorías"]
)

@router.get("", response_model=List[schemas.CategoriaResponse])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    stmt = select(Categoria).options(
        selectinload(Categoria.productos)  # Cargar relación 'productos'
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{categoria_id}/productos", response_model=List[schemas.ProductoSimpleResponse])
async def productos_por_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Categoria).where(Categoria.id == categoria_id)
    result = await db.execute(stmt)
    categoria = result.scalars().first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    stmt = select(Producto).where(Producto.categoria_id == categoria_id)
    result = await db.execute(stmt)
    return result.scalars().all()