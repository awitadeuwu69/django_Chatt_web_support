/* ========================================
   UTILIDADES GLOBALES
======================================== */

/* Leer cookie */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}

/* CSRF token */
const _csrfInput = document.querySelector(
  'input[name="csrfmiddlewaretoken"]'
);
let csrftoken =
  getCookie("csrftoken") || (_csrfInput ? _csrfInput.value : null);

if (!csrftoken) {
  setTimeout(() => {
    try {
      const _delayedInput = document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
      );
      csrftoken =
        getCookie("csrftoken") || (_delayedInput ? _delayedInput.value : null);
      console.log("csrf token (delayed):", csrftoken);
    } catch (err) {
      console.warn("Error while trying to read delayed CSRF token:", err);
    }
  }, 50);
}

function getCSRFToken() {
  return csrftoken || document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}

/* Escape HTML */
function escapeHtml(unsafe) {
  if (!unsafe) return '';
  return String(unsafe).replace(/[&<>"']/g, function (m) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[m];
  });
}

// Exportar funciones globales
window.getCSRFToken = getCSRFToken;
window.escapeHtml = escapeHtml;

/* ========================================
   MENÚ HAMBURGUESA - CORREGIDO
======================================== */
document.addEventListener('DOMContentLoaded', function() {
  
  const menuBtn = document.getElementById("menuBtn");
  const menuDropdown = document.getElementById("menuDropdown");
  const cartBtn = document.getElementById("cartBtn");
  const cartPopup = document.getElementById("cartPopup");
  const cartCloseBtn = document.getElementById("cartCloseBtn");

  // Toggle menú hamburguesa
  if (menuBtn && menuDropdown) {
    menuBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      menuDropdown.classList.toggle("active");
      // Cerrar carrito si está abierto
      if (cartPopup) {
        cartPopup.classList.remove("active");
      }
    });
  }

  // Toggle carrito
  if (cartBtn && cartPopup) {
    cartBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      cartPopup.classList.toggle("active");
      loadCart();
      // Cerrar menú si está abierto
      if (menuDropdown) {
        menuDropdown.classList.remove("active");
      }
    });
  }

  // Cerrar carrito con botón X
  if (cartCloseBtn && cartPopup) {
    cartCloseBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      cartPopup.classList.remove("active");
    });
  }

  // Cerrar menú y carrito al hacer clic fuera
  document.addEventListener("click", function(e) {
    if (menuDropdown && menuBtn && !menuBtn.contains(e.target) && !menuDropdown.contains(e.target)) {
      menuDropdown.classList.remove("active");
    }
    if (cartPopup && cartBtn && !cartBtn.contains(e.target) && !cartPopup.contains(e.target)) {
      cartPopup.classList.remove("active");
    }
  });

  /* ========================================
     CARRITO
  ======================================== */
  async function addToCart(productId) {
    try {
      const res = await fetch("/cart/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ product_id: productId, cantidad: 1 }),
      });
      
      if (res.status === 401) {
        const loginModal = document.getElementById("loginModal");
        const loginOverlay = document.getElementById("loginOverlay");
        if (loginModal) loginModal.style.display = "block";
        if (loginOverlay) loginOverlay.style.display = "block";
        alert("Debes iniciar sesión para agregar al carrito");
        return;
      }
      
      const data = await res.json();
      if (res.ok && data.success) {
        alert("Producto agregado al carrito ✅");
        await loadCart();
      } else {
        alert(data.error || "Error al agregar al carrito");
      }
    } catch (err) {
      console.error("Error adding to cart:", err);
      alert("Error de conexión al agregar producto");
    }
  }

  async function loadCart() {
    try {
      const res = await fetch("/cart/");
      
      if (res.status === 401) {
        const ul = document.getElementById("cartItems");
        if (ul) {
          ul.innerHTML = '<li style="text-align: center; padding: 20px;">Inicia sesión para ver tu carrito</li>';
        }
        return;
      }
      
      const data = await res.json();
      const ul = document.getElementById("cartItems");
      
      if (!ul) return;
      
      ul.innerHTML = "";
      
      if (!data.items || data.items.length === 0) {
        ul.innerHTML = '<li style="text-align: center; padding: 20px; color: #999;">Carrito vacío</li>';
        return;
      }
      
      data.items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.nombre} (${item.cantidad}) - $${item.subtotal}`;
        ul.appendChild(li);
      });
      
      // Agregar total si existe
      if (data.total) {
        const totalLi = document.createElement("li");
        totalLi.style.fontWeight = "bold";
        totalLi.style.borderTop = "2px solid #ddd";
        totalLi.style.marginTop = "10px";
        totalLi.style.paddingTop = "10px";
        totalLi.textContent = `Total: $${data.total}`;
        ul.appendChild(totalLi);
      }
    } catch (err) {
      console.error("Error loading cart:", err);
      const ul = document.getElementById("cartItems");
      if (ul) {
        ul.innerHTML = '<li style="color: red;">Error al cargar carrito</li>';
      }
    }
  }

  // Event listeners para botones de agregar al carrito
  document.querySelectorAll(".add-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const productCard = e.target.closest(".product-card");
      if (productCard) {
        const id = productCard.dataset.id;
        if (id) {
          addToCart(id);
        }
      }
    });
  });

  /* ========================================
     LOGIN Y REGISTRO - MODALES
  ======================================== */
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const loginModal = document.getElementById("loginModal");
  const registerModal = document.getElementById("registerModal");
  const loginOverlay = document.getElementById("loginOverlay");
  const registerOverlay = document.getElementById("registerOverlay");

  // LOGIN FORM
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const email = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;
      const username = document.getElementById("loginUsername")?.value || email.split('@')[0];

      try {
  const response = await fetch("/auth/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        
        if (data.success) {
          alert("Inicio de sesión exitoso ✅");
          location.reload();
        } else {
          alert(data.error || "Error al iniciar sesión");
        }
      } catch (err) {
        console.error("Login error:", err);
        alert("Error de conexión al iniciar sesión");
      }
    });
  }

  // REGISTRO FORM
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const name = document.getElementById("registerName")?.value;
      const email = document.getElementById("registerEmail").value;
      const whatsapp = document.getElementById("registerWhatsapp")?.value;
      const role = document.getElementById("registerRole")?.value;
      const businessType = document.getElementById("registerType")?.value;
      const password = document.getElementById("registerPassword").value;
      const passwordConfirm = document.getElementById("registerPasswordConfirm").value;
      const username = document.getElementById("registerUsername")?.value || email.split('@')[0];

      // Validaciones
      if (password !== passwordConfirm) {
        alert("Las contraseñas no coinciden");
        return;
      }
      
      if (password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres");
        return;
      }

      try {
  const response = await fetch("/auth/register/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({
            username,
            email,
            password,
            name,
            whatsapp,
            role,
            business_type: businessType
          }),
        });

        const data = await response.json();
        
        if (data.success) {
          // Intentar login automático
          try {
              const loginRes = await fetch("/auth/login/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
              },
              body: JSON.stringify({ username, email, password }),
            });
            
            const loginData = await loginRes.json();
            
            if (loginData.success) {
              alert("Registro exitoso ✅ Bienvenido a Club Almacén");
              location.reload();
            } else {
              alert("Registro exitoso. Por favor inicia sesión.");
              if (registerModal) registerModal.style.display = "none";
              if (registerOverlay) registerOverlay.style.display = "none";
              if (loginModal) loginModal.style.display = "block";
              if (loginOverlay) loginOverlay.style.display = "block";
            }
          } catch (err) {
            console.error("Auto-login failed:", err);
            alert("Registro exitoso. Por favor inicia sesión.");
            if (registerModal) registerModal.style.display = "none";
            if (registerOverlay) registerOverlay.style.display = "none";
          }
        } else {
          alert(data.error || "Error al registrarse");
        }
      } catch (err) {
        console.error("Registration error:", err);
        alert("Error de conexión al registrarse");
      }
    });
  }

  /* ========================================
     TOGGLE PASSWORD VISIBILITY
  ======================================== */
  function togglePasswordVisibility(...args) {
    if (args.length < 1) return;
    
    args.forEach(id => {
      const input = document.getElementById(id);
      if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
      }
    });
  }

  // Exportar función globalmente
  window.togglePasswordVisibility = togglePasswordVisibility;

  /* ========================================
     BOTONES DE MODALES
  ======================================== */
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  const closeLogin = document.getElementById("closeLogin");
  const closeRegister = document.getElementById("closeRegister");
  const logoutBtn = document.getElementById("logoutBtn");

  // Abrir modal de login
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      if (loginModal) loginModal.style.display = "block";
      if (loginOverlay) loginOverlay.style.display = "block";
      if (menuDropdown) menuDropdown.classList.remove("active");
    });
  }

  // Abrir modal de registro
  if (registerBtn) {
    registerBtn.addEventListener("click", () => {
      if (registerModal) registerModal.style.display = "block";
      if (registerOverlay) registerOverlay.style.display = "block";
      if (menuDropdown) menuDropdown.classList.remove("active");
    });
  }

  // Cerrar modal de login
  if (closeLogin) {
    closeLogin.addEventListener("click", () => {
      if (loginModal) loginModal.style.display = "none";
      if (loginOverlay) loginOverlay.style.display = "none";
    });
  }

  // Cerrar modal de registro
  if (closeRegister) {
    closeRegister.addEventListener("click", () => {
      if (registerModal) registerModal.style.display = "none";
      if (registerOverlay) registerOverlay.style.display = "none";
    });
  }

  // Cerrar modales al hacer clic en overlay
  if (loginOverlay) {
    loginOverlay.addEventListener("click", () => {
      if (loginModal) loginModal.style.display = "none";
      loginOverlay.style.display = "none";
    });
  }

  if (registerOverlay) {
    registerOverlay.addEventListener("click", () => {
      if (registerModal) registerModal.style.display = "none";
      registerOverlay.style.display = "none";
    });
  }

  // Logout
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      if (!confirm("¿Estás seguro de cerrar sesión?")) return;
      
      try {
        const response = await fetch("/logout/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCSRFToken(),
          },
        });
        
        if (response.ok) {
          alert("Sesión cerrada exitosamente");
          location.reload();
        } else {
          alert("Error al cerrar sesión");
        }
      } catch (err) {
        console.error("Logout error:", err);
        alert("Error de conexión al cerrar sesión");
      }
    });
  }

  /* ========================================
     SMOOTH SCROLL
  ======================================== */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      e.preventDefault();
      const target = document.querySelector(href);
      
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

});