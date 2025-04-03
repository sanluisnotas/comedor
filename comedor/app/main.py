from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, habitaciones, productos, pedidos, categorias, admin
from app.config import settings
from app.models import Habitacion, Categoria, Producto
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

app = FastAPI(
    title="Sistema de Gestión de Pedidos - Hotel",
    description="API para gestión integral de pedidos en hotel",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        # Insertar habitaciones de demo si no existen
        if not (await session.execute(text("SELECT * FROM habitaciones LIMIT 1"))).first():
            for room in settings.DEMO_ROOMS.split(","):
                numero, apellido = room.split(":")
                session.add(Habitacion(numero=numero, apellido=apellido))
        
        # Insertar categorías si no existen
        if not (await session.execute(text("SELECT * FROM categorias LIMIT 1"))).first():
            categorias_iniciales = [
                Categoria(nombre="Vinos", orden=1),
                Categoria(nombre="Cafés", orden=2),
                Categoria(nombre="Zumos", orden=3),
                Categoria(nombre="Aguas", orden=4),
                Categoria(nombre="Cervezas", orden=5),
                Categoria(nombre="Infusiones", orden=6),
                Categoria(nombre="Refrescos", orden=7),
            ]
            session.add_all(categorias_iniciales)
        
        # Insertar productos de demo si no existen
        if not (await session.execute(text("SELECT * FROM productos LIMIT 1"))).first():
            productos_iniciales = [
                Producto(nombre="Vino Tinto", precio=10.0, categoria_id=1),
                Producto(nombre="Café Espresso", precio=2.0, categoria_id=2),
                Producto(nombre="Zumo de Naranja", precio=3.0, categoria_id=3),
                Producto(nombre="Agua Mineral", precio=1.5, categoria_id=4),
                Producto(nombre="Cerveza Lager", precio=2.5, categoria_id=5),
                Producto(nombre="Té Verde", precio=2.0, categoria_id=6),
                Producto(nombre="Coca Cola", precio=2.5, categoria_id=7),
            ]
            session.add_all(productos_iniciales)
        
        await session.commit()

app.add_event_handler("startup", init_db)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router, prefix="/api/auth")
app.include_router(habitaciones.router, prefix="/api")
app.include_router(productos.router, prefix="/api/productos")
app.include_router(pedidos.router, prefix="/api/pedidos")
app.include_router(categorias.router, prefix="/api")
app.include_router(admin.router, prefix="/api/admin")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("app/templates/index.html")

@app.get("/productos", response_class=HTMLResponse)
async def serve_productos(request: Request):
    if not request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=303)
    return FileResponse("app/templates/productos.html")

@app.get("/carrito", response_class=HTMLResponse)
async def serve_carrito(request: Request):
    if not request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=303)
    return FileResponse("app/templates/carrito.html")   

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin_panel(request: Request):
    if not request.cookies.get("admin_token"):
        return RedirectResponse(url="/", status_code=303)
    return FileResponse("app/templates/admin/index.html")

@app.get("/carrito", response_class=HTMLResponse)
async def serve_carrito(request: Request):
    print("Cookies recibidas:", request.cookies)  # Depuración
    if not request.cookies.get("access_token"):
        print("No se encontró access_token, redirigiendo a /")
        return RedirectResponse(url="/", status_code=303)
    return FileResponse("app/templates/carrito.html")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith('/api'):
        return JSONResponse(status_code=404, content={"detail": "Recurso no encontrado"})
    return RedirectResponse(url="/")

@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith('/api'):
        return JSONResponse(status_code=401, content={"detail": "No autorizado"}, headers={"WWW-Authenticate": "Bearer"})
    return RedirectResponse(url="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)