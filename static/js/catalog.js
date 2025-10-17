document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const cartPopup = document.getElementById('cartPopup');
    const cartCloseBtn = document.getElementById('cartCloseBtn');
    const loginModal = document.getElementById('loginModal');
    const loginOverlay = document.getElementById('loginOverlay');
    const registerModal = document.getElementById('registerModal');
    const registerOverlay = document.getElementById('registerOverlay');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const addButtons = document.querySelectorAll('.btn-add-quote');
    let isAuthenticated = false;

    // Event Listeners para modales
    document.getElementById('closeLogin')?.addEventListener('click', () => closeModal('login'));
    document.getElementById('closeRegister')?.addEventListener('click', () => closeModal('register'));
    cartCloseBtn?.addEventListener('click', () => {
        cartPopup.style.display = 'none';
    });

    // Funciones de autenticación
    document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const emailInput = document.getElementById('loginEmail');
        const passwordInput = document.getElementById('loginPassword');
        
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        // Validación básica
        if (!email) {
            alert('Por favor ingresa tu email');
            emailInput.focus();
            return;
        }
        if (!password) {
            alert('Por favor ingresa tu contraseña');
            passwordInput.focus();
            return;
        }

        // Obtener el token CSRF
        const csrfToken = getCSRFToken();
        if (!csrfToken) {
            alert('Error de seguridad: Token CSRF no encontrado');
            return;
        }

        try {
            const response = await fetch('/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            // Primero verificar si la respuesta es JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('Respuesta no es JSON:', contentType);
                alert('Error del servidor: Respuesta inválida');
                return;
            }

            const data = await response.json();
            
            if (response.ok) {
                isAuthenticated = true;
                closeModal('login');
                updateButtonsState();
                await loadCart();
                window.location.reload();
            } else {
                const message = data.message || (response.status === 401 
                    ? 'Email o contraseña incorrectos' 
                    : 'Error al iniciar sesión');
                alert(message);
                
                if (response.status === 401) {
                    passwordInput.value = '';
                    passwordInput.focus();
                }
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            alert('Error de conexión. Por favor, verifica tu conexión a internet e intenta nuevamente.');
        }
    });

    document.getElementById('registerForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value;

        if (password !== passwordConfirm) {
            alert('Las contraseñas no coinciden');
            return;
        }

        try {
            const response = await fetch('/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();
            if (response.ok) {
                isAuthenticated = true;
                closeModal('register');
                updateButtonsState();
                await loadCart();
            } else {
                alert(data.message || 'Error al registrarse');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar la solicitud');
        }
    });

    // Manejo del carrito
    async function loadCart() {
        try {
            const response = await fetch('/cart/', {
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                updateCartUI(data);
            } else {
                console.error('Error al cargar el carrito');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function updateCartUI(data) {
        if (!cartItems || !cartTotal) return;

        cartItems.innerHTML = '';
        let total = 0;

        data.items.forEach(item => {
            const li = document.createElement('li');
            li.className = 'cart-item';
            li.innerHTML = `
                <span>${item.product_name}</span>
                <span>${item.cantidad}x</span>
                <button onclick="removeFromCart(${item.id})" class="remove-btn">✕</button>
            `;
            cartItems.appendChild(li);
            total += item.precio * item.cantidad;
        });

        cartTotal.textContent = `Total: $${total.toFixed(2)}`;
        
        // Actualizar contador del carrito
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = data.items.length.toString();
        }
    }

    // Event listeners para botones de añadir al carrito
    addButtons.forEach(button => {
        button.addEventListener('click', async function() {
            if (!isAuthenticated) {
                showModal('login');
                return;
            }

            const productId = this.dataset.product;
            try {
                const response = await fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        cantidad: 1
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    // Feedback visual
                    button.textContent = '¡Añadido!';
                    button.style.background = '#27ae60';
                    setTimeout(() => {
                        button.textContent = 'Añadir al Presupuesto';
                        button.style.background = '';
                    }, 2000);

                    await loadCart();
                } else {
                    alert(data.message || 'Error al añadir al presupuesto');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al procesar la solicitud');
            }
        });
    });

    // Funciones auxiliares
    function getCSRFToken() {
        // Primero buscar en el formulario oculto
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        
        // Luego buscar en las cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        
        console.error('CSRF token no encontrado');
        return null;
    }

    function showModal(type) {
        const modal = type === 'login' ? loginModal : registerModal;
        const overlay = type === 'login' ? loginOverlay : registerOverlay;
        if (modal && overlay) {
            modal.style.display = 'block';
            overlay.style.display = 'block';
        }
    }

    function closeModal(type) {
        const modal = type === 'login' ? loginModal : registerModal;
        const overlay = type === 'login' ? loginOverlay : registerOverlay;
        if (modal && overlay) {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }
    }

    function updateButtonsState() {
        addButtons.forEach(button => {
            button.classList.toggle('login-required', !isAuthenticated);
        });
    }

    // Función para alternar visibilidad de contraseña
    window.togglePasswordVisibility = function(inputId, confirmInputId = null) {
        const input = document.getElementById(inputId);
        input.type = input.type === 'password' ? 'text' : 'password';
        
        if (confirmInputId) {
            const confirmInput = document.getElementById(confirmInputId);
            confirmInput.type = confirmInput.type === 'password' ? 'text' : 'password';
        }
    };

    // Cargar carrito inicial si está autenticado
    loadCart();
});