document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorElement = document.getElementById('login-error');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const numero = document.getElementById('numero').value.trim(); // Elimina espacios al inicio y final
        const apellido = document.getElementById('apellido').value.trim().toLowerCase(); // Normaliza a minúsculas

        try {
            console.log('Iniciando sesión con:', { numero, apellido });
            const response = await axios.post('/api/auth/login', { numero, apellido }, { withCredentials: true });
            console.log('Login exitoso:', response.data);
            window.location.href = '/productos';
        } catch (error) {
            const errorMsg = error.response ? error.response.data.detail || error.response.statusText : error.message;
            console.error('Error en login:', errorMsg);
            errorElement.textContent = `Error: ${errorMsg}`;
        }
    });
});

async function loadProducts() {
    try {
        console.log('Cargando productos...');
        const response = await axios.get('/api/productos', { withCredentials: true });
        console.log('Productos recibidos:', response.data);
        renderProducts(response.data);
    } catch (error) {
        const errorMsg = error.response ? error.response.data.detail || error.response.statusText : error.message;
        console.error('Error al cargar productos:', errorMsg);
        alert(`Error al cargar productos: ${errorMsg}`);
    }
}

function renderProducts(productos) {
    const menuProductos = document.getElementById('menu-productos');
    menuProductos.innerHTML = '';
    productos.forEach(producto => {
        const item = document.createElement('div');
        item.className = 'producto-item';
        item.innerHTML = `
            <h4>${producto.nombre}</h4>
            <p>$${producto.precio.toFixed(2)}</p>
            <button class="add-to-cart" data-product-id="${producto.id}">Agregar al carrito</button>
        `;
        menuProductos.appendChild(item);
    });

    // Agregar eventos a los botones después de renderizar
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', (e) => {
            const productId = parseInt(e.target.getAttribute('data-product-id'));
            console.log('Botón clicado, ID:', productId);
            addToCart(productId);
        });
    });
}

async function addToCart(productoId) {
    try {
        console.log('Añadiendo al carrito:', productoId);
        const response = await axios.post('/api/pedidos/', {
            producto_id: productoId,
            cantidad: 1,
            notas: "Añadido desde el frontend"
        }, { withCredentials: true });
        console.log('Respuesta del servidor:', response.data);
        alert(`Producto añadido al carrito (Pedido ID: ${response.data.pedido_id})`);
    } catch (error) {
        const errorMsg = error.response ? error.response.data.detail || error.response.statusText : error.message;
        console.error('Error al añadir al carrito:', errorMsg);
        alert(`Error al añadir al carrito: ${errorMsg}`);
    }
}