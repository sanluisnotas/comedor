from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from enum import Enum as PythonEnum

# Enums para valores predefinidos (coincide con tus schemas)
class EstadoPedidoDB(PythonEnum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    entregado = "entregado"
    cancelado = "cancelado"

# Modelo Habitación
class Habitacion(Base):
    __tablename__ = 'habitaciones'
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, index=True)
    apellido = Column(String(50))
    telefono = Column(String(20), nullable=True)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    activa = Column(Boolean, default=True)
    
    # Relación con Pedidos
    pedidos = relationship("Pedido", back_populates="habitacion")

# Modelo Categoría
class Categoria(Base):
    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    icono = Column(String(30), nullable=True)
    orden = Column(Integer, default=0)
    
    # Relación con Productos
    productos = relationship("Producto", back_populates="categoria")

# Modelo Producto
class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    descripcion = Column(String(255), nullable=True)
    precio = Column(Float)
    disponible = Column(Boolean, default=True)
    imagen = Column(String(255), nullable=True)
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    pedidos = relationship("Pedido", back_populates="producto")

# Modelo Pedido
class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True, index=True)
    habitacion_id = Column(Integer, ForeignKey('habitaciones.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, default=1)
    notas = Column(String(255), nullable=True)
    estado = Column(SQLEnum(EstadoPedidoDB), default=EstadoPedidoDB.pendiente)
    fecha = Column(DateTime, default=datetime.utcnow)
    hora_entrega = Column(DateTime, nullable=True)
    
    # Relaciones
    habitacion = relationship("Habitacion", back_populates="pedidos")
    producto = relationship("Producto", back_populates="pedidos")

# Modelo Usuario Admin
class UsuarioAdmin(Base):
    __tablename__ = 'usuarios_admin'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    nombre = Column(String(100), nullable=True)
    password_hash = Column(String(255))
    activo = Column(Boolean, default=True)
    es_superadmin = Column(Boolean, default=False)