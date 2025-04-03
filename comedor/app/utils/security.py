# hotel_pedidos/app/utils/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request, Depends  # Añadido Depends aquí
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models import UsuarioAdmin, Habitacion
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su versión hasheada"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

async def authenticate_habitacion(db: AsyncSession, numero: str, apellido: str) -> Optional[Habitacion]:
    """Autentica una habitación basada en número y apellido"""
    stmt = select(Habitacion).where(
        Habitacion.numero == numero,
        Habitacion.apellido.ilike(apellido)
    )
    result = await db.execute(stmt)
    habitacion = result.scalars().first()
    return habitacion

async def get_current_habitacion(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Obtiene la habitación actual basada en el token"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    token = token.replace("Bearer ", "")
    payload = decode_access_token(token)
    numero: str = payload.get("sub")
    habitacion_id: int = payload.get("habitacion_id")
    
    stmt = select(Habitacion).where(
        Habitacion.id == habitacion_id,
        Habitacion.numero == numero
    )
    result = await db.execute(stmt)
    habitacion = result.scalars().first()
    
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Habitación no encontrada",
        )
    return {"id": habitacion.id, "numero": habitacion.numero, "apellido": habitacion.apellido}

async def get_current_admin(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UsuarioAdmin:
    """Obtiene el usuario admin actual basado en el token"""
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    
    stmt = select(UsuarioAdmin).where(UsuarioAdmin.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return user