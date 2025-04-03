# hotel_pedidos/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import create_access_token, authenticate_habitacion
from app.models import Habitacion
from jose import jwt, JWTError
from app.config import settings

router = APIRouter(
    prefix="/api",
    tags=["Autenticación"]
)

@router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Inicia sesión para una habitación usando número y apellido.
    Devuelve un token JWT y lo establece como cookie.
    """
    habitacion = authenticate_habitacion(db, form_data.username, form_data.password)
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Número o apellido incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": habitacion.numero, "habitacion_id": habitacion.id}
    )
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600,  # 1 hora
        secure=False,  # Cambiar a True en producción con HTTPS
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """
    Cierra la sesión eliminando la cookie de autenticación.
    """
    response.delete_cookie("access_token")
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/check")
async def check_auth(
    token: str = Depends(lambda x: x.cookies.get("access_token")),
    db: Session = Depends(get_db)
):
    """
    Verifica si el usuario está autenticado basado en el token de la cookie.
    """
    if not token:
        return {"authenticated": False}
    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        numero: str = payload.get("sub")
        habitacion_id: int = payload.get("habitacion_id")
        habitacion = db.query(Habitacion).filter(
            Habitacion.numero == numero,
            Habitacion.id == habitacion_id
        ).first()
        if habitacion:
            return {"authenticated": True, "habitacion": {"id": habitacion.id, "numero": habitacion.numero}}
        return {"authenticated": False}
    except JWTError:
        return {"authenticated": False}