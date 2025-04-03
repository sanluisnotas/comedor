from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums para valores predefinidos
class EstadoPedido(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    entregado = "entregado"
    cancelado = "cancelado"

# --------------------------
# Modelos de Autenticación
# --------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: Optional[str] = Field(None, description="Tipo de usuario (admin/habitacion)")

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[str] = None

class HabitacionLogin(BaseModel):  # Añadido para el login de habitación
    numero: str = Field(..., max_length=10, example="101")
    apellido: str = Field(..., max_length=50, example="Gomez")

# --------------------------
# Modelos para Habitación
# --------------------------
class HabitacionBase(BaseModel):
    numero: str = Field(..., max_length=10, example="101")
    apellido: str = Field(..., max_length=50, example="García")
    telefono: Optional[str] = Field(None, max_length=20, example="+5491122334455")
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

class HabitacionCreate(HabitacionBase):
    pass

class HabitacionResponse(HabitacionBase):
    id: int
    activa: bool = True
    pedidos: List['PedidoResponse'] = []
    
    model_config = ConfigDict(from_attributes=True)

# --------------------------
# Modelos para Administradores
# --------------------------
class UsuarioAdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="admin")
    email: EmailStr = Field(..., example="admin@hotel.com")
    nombre: Optional[str] = Field(None, max_length=100, example="Administrador Principal")

class UsuarioAdminCreate(UsuarioAdminBase):
    password: str = Field(..., min_length=6, example="securepassword123")

class UsuarioAdminResponse(UsuarioAdminBase):
    id: int
    activo: bool = True
    es_superadmin: bool = False
    ultimo_acceso: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioAdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    activo: Optional[bool] = None
    es_superadmin: Optional[bool] = None

# --------------------------
# Modelos para Categoría
# --------------------------
class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=50, example="Bebidas")
    icono: Optional[str] = Field(None, max_length=30, example="local_bar")
    orden: Optional[int] = Field(0, ge=0, example=1)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    productos: List['ProductoSimpleResponse'] = []
    
    model_config = ConfigDict(from_attributes=True)

# --------------------------
# Modelos para Producto
# --------------------------
class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=100, example="Coca Cola")
    descripcion: Optional[str] = Field(None, max_length=255, example="Refresco de cola 500ml")
    precio: float = Field(..., gt=0, example=2.5)
    disponible: bool = Field(default=True)
    imagen: Optional[str] = Field(None, max_length=255, example="coca-cola.png")
    categoria_id: int = Field(..., gt=0, example=1)

class ProductoCreate(ProductoBase):
    pass

class ProductoSimpleResponse(BaseModel):
    id: int
    nombre: str
    precio: float
    imagen: Optional[str] = None
    disponible: bool
    
    model_config = ConfigDict(from_attributes=True)

class ProductoResponse(ProductoBase):
    id: int
    categoria: Optional[CategoriaResponse] = None
    pedidos: List['PedidoSimpleResponse'] = []
    
    model_config = ConfigDict(from_attributes=True)

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    disponible: Optional[bool] = None
    imagen: Optional[str] = None
    categoria_id: Optional[int] = None

# --------------------------
# Modelos para Pedido
# --------------------------
class PedidoCreateFrontend(BaseModel):
    producto_id: int = Field(..., gt=0, example=1)
    cantidad: int = Field(1, gt=0, example=2)
    notas: Optional[str] = Field(None, max_length=255, example="Sin hielo")

class PedidoBase(BaseModel):
    habitacion_id: int = Field(..., gt=0, example=1)
    producto_id: int = Field(..., gt=0, example=1)
    cantidad: int = Field(1, gt=0, example=2)
    notas: Optional[str] = Field(None, max_length=255, example="Sin hielo")
    estado: EstadoPedido = Field(default=EstadoPedido.pendiente)

class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, gt=0)
    notas: Optional[str] = Field(None, max_length=255)
    estado: Optional[EstadoPedido] = None

class PedidoSimpleResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    estado: EstadoPedido
    fecha: datetime
    hora_entrega: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PedidoResponse(PedidoBase):
    id: int
    fecha: datetime
    hora_entrega: Optional[datetime] = None
    producto: ProductoSimpleResponse
    habitacion: Optional[HabitacionResponse] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        exclude=["habitacion__pedidos"]  # Excluir explícitamente pedidos de habitacion
    )
    

# --------------------------
# Resolver referencias circulares
# --------------------------
HabitacionResponse.model_rebuild()
CategoriaResponse.model_rebuild()
ProductoResponse.model_rebuild()
PedidoResponse.model_rebuild()