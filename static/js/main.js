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
    return unsafe.replace(/[&<>"']/g, function (m) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[m];
    });
  }
  
  /* ========================================
     MENÚ
  ======================================== */
  const menuBtn = document.getElementById("menuBtn");
  const menuDropdown = document.getElementById("menuDropdown");
  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      menuDropdown.classList.toggle("active");
    });
  }
  
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
        if (loginModal) loginModal.style.display = "block";
        alert("Debes iniciar sesión para agregar al carrito");
        return;
      }
      const data = await res.json();
      if (res.ok && data.success) {
        alert("Producto agregado al carrito");
        await loadCart();
      } else {
        alert(data.error || "Error al agregar al carrito");
      }
    } catch (err) {
      console.error(err);
    }
  }
  
  async function loadCart() {
    try {
      const res = await fetch("/cart/");
      if (res.status === 401) {
        const loginModal = document.getElementById("loginModal");
        if (loginModal) loginModal.style.display = "block";
        return;
      }
      const data = await res.json();
      const ul = document.getElementById("cartItems");
      ul.innerHTML = "";
      data.items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.nombre} (${item.cantidad}) - $${item.subtotal}`;
        ul.appendChild(li);
      });
    } catch (err) {
      console.error("Error loading cart", err);
    }
  }
  
  document.querySelectorAll(".add-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const id = e.target.closest(".product-card").dataset.id;
      addToCart(id);
    });
  });
  
  const cartBtn = document.getElementById("cartBtn");
  if (cartBtn) {
    cartBtn.addEventListener("click", () => {
      document.getElementById("cartPopup").classList.toggle("active");
      loadCart();
    });
  }
  
  const cartCloseBtn = document.getElementById("cartCloseBtn");
  if (cartCloseBtn) {
    cartCloseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      document.getElementById("cartPopup").classList.remove("active");
    });
  }
  
  /* ========================================
     LOGIN Y REGISTRO
  ======================================== */
  document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const loginModal = document.getElementById("loginModal");
    const registerModal = document.getElementById("registerModal");
  
    // LOGIN
    if (loginForm) {
      loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("loginUsername").value;
        const password = document.getElementById("loginPassword").value;
  
        try {
          const response = await fetch("/login/", {
            method: "POST",
            headers: { 
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ username, password }),
          });
  
          const data = await response.json();
          if (data.success) {
            alert("Inicio de sesión exitoso ✅");
            location.reload();
          } else {
            alert(data.error || "Error al iniciar sesión");
          }
        } catch (err) {
          console.error(err);
          alert("Error de conexión");
        }
      });
    }
  
    // REGISTRO
    if (registerForm) {
      registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("registerUsername").value;
        const password = document.getElementById("registerPassword").value;
        const passwordConfirm = document.getElementById(
          "registerPasswordConfirm"
        ).value;
  
        if (password !== passwordConfirm) {
          alert("Las contraseñas no coinciden");
          return;
        }
  
        try {
          const response = await fetch("/register/", {
            method: "POST",
            headers: { 
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ username, password }),
          });
  
          const data = await response.json();
          if (data.success) {
            try {
              const loginRes = await fetch("/login/", {
                method: "POST",
                headers: { 
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({ username, password }),
              });
              const loginData = await loginRes.json();
              if (loginData.success) {
                alert("Registro y login exitoso ✅");
                location.reload();
              } else {
                alert("Registro exitoso. Por favor inicia sesión.");
                if (registerModal) registerModal.style.display = "none";
              }
            } catch (err) {
              console.error("Auto-login failed", err);
              alert("Registro exitoso. Por favor inicia sesión.");
              if (registerModal) registerModal.style.display = "none";
            }
          } else {
            alert(data.error || "Error al registrarse");
          }
        } catch (err) {
          console.error(err);
          alert("Error de conexión");
        }
      });
    }
  
    // MODALES - BOTONES
    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");
    const closeLogin = document.getElementById("closeLogin");
    const closeRegister = document.getElementById("closeRegister");
    const logoutBtn = document.getElementById("logoutBtn");
  
    if (loginBtn)
      loginBtn.addEventListener(
        "click",
        () => (loginModal.style.display = "block")
      );
    if (registerBtn)
      registerBtn.addEventListener(
        "click",
        () => (registerModal.style.display = "block")
      );
    if (closeLogin)
      closeLogin.addEventListener(
        "click",
        () => (loginModal.style.display = "none")
      );
    if (closeRegister)
      closeRegister.addEventListener(
        "click",
        () => (registerModal.style.display = "none")
      );
    if (logoutBtn) {
      logoutBtn.addEventListener("click", async () => {
        try {
          await fetch("/logout/", { 
            method: "POST",
            headers: {
              "X-CSRFToken": getCSRFToken()
            }
          });
          location.reload();
        } catch (err) {
          console.error(err);
          alert("Error al cerrar sesión");
        }
      });
    }
  });