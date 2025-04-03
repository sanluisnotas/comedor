from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas
from app.database import get_db
from app.utils.security import authenticate_habitacion, create_access_token
from app.models import Habitacion, UsuarioAdmin

router = APIRouter(tags=["Autenticación"])

@router.post("/login", response_model=schemas.Token)
async def login_habitacion(
    form_data: schemas.HabitacionLogin,  # Cambiamos a recibir JSON directamente
    db: AsyncSession = Depends(get_db)
):
    habitacion = await authenticate_habitacion(db, form_data.numero, form_data.apellido)
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Número de habitación o apellido incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": habitacion.numero, "habitacion_id": habitacion.id, "user_type": "habitacion"}
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer", "user_type": "habitacion"}
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )
    return response

@router.post("/admin/login", response_model=schemas.Token)
async def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UsuarioAdmin).where(UsuarioAdmin.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "user_type": "admin"}
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer", "user_type": "admin"}
    )
    response.set_cookie(
        key="admin_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
        path="/"  # Aseguramos que esté disponible en todas las rutas

    )
    return response