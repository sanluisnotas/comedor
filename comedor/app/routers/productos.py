from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas
from app.models import Producto
from app.database import get_db
from typing import List

router = APIRouter(tags=["Productos"])  # Ajustado prefijo a /productos

@router.get("", response_model=List[schemas.ProductoSimpleResponse])
async def listar_productos(db: AsyncSession = Depends(get_db)):
    stmt = select(Producto)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{categoria_id}", response_model=List[schemas.ProductoSimpleResponse])
async def productos_por_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Producto).where(Producto.categoria_id == categoria_id)
    result = await db.execute(stmt)
    productos = result.scalars().all()
    if not productos:
        raise HTTPException(status_code=404, detail="No hay productos en esta categoría")
    return productos