/* ==================== PROFILE.JS ==================== */

// Obtener CSRF token
function getCSRFToken() {
  const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
  if (csrfInput) return csrfInput.value;
  
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') return decodeURIComponent(value);
  }
  return null;
}

// ==================== SUBIR FOTO DE PERFIL ====================
async function uploadPhoto(input) {
  if (!input.files || !input.files[0]) return;

  const file = input.files[0];
  
  // Validar tamaño (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('La imagen es demasiado grande. Máximo 5MB');
    input.value = '';
    return;
  }

  // Validar formato
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    alert('Formato no válido. Use: JPG, PNG, GIF o WEBP');
    input.value = '';
    return;
  }

  const formData = new FormData();
  formData.append('photo', file);

  const uploadUrl = document.querySelector('.profile-sidebar').dataset.uploadPhotoUrl;
  try {
    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      },
      body: formData
    });

    const data = await response.json();

    if (data.success) {
      // Actualizar la imagen en la página
      const photoElement = document.getElementById('profilePhoto');
      const placeholderElement = document.getElementById('profilePhotoPlaceholder');
      
      if (placeholderElement) {
        // Reemplazar placeholder con imagen
        const container = placeholderElement.parentElement;
        placeholderElement.remove();
        
        const img = document.createElement('img');
        img.src = data.photo_url + '?t=' + new Date().getTime(); // Cache bust
        img.alt = 'Foto de perfil';
        img.className = 'profile-photo';
        img.id = 'profilePhoto';
        container.insertBefore(img, container.firstChild);
      } else if (photoElement) {
        // Actualizar imagen existente
        photoElement.src = data.photo_url + '?t=' + new Date().getTime();
      }

      alert('✅ ' + data.message);
      
      // Recargar para mostrar el botón de eliminar
      setTimeout(() => location.reload(), 1000);
    } else {
      alert('❌ ' + data.error);
    }
  } catch (error) {
    console.error('Error uploading photo:', error);
    alert('Error al subir la foto. Por favor, intenta de nuevo.');
  }

  input.value = '';
}

// ==================== ELIMINAR FOTO DE PERFIL ====================
async function deletePhoto() {
  if (!confirm('¿Estás seguro de eliminar tu foto de perfil?')) return;

  const deleteUrl = document.querySelector('.profile-sidebar').dataset.deletePhotoUrl;
  try {
    const response = await fetch(deleteUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    });

    const data = await response.json();

    if (data.success) {
      alert('✅ ' + data.message);
      location.reload();
    } else {
      alert('❌ ' + data.error);
    }
  } catch (error) {
    console.error('Error deleting photo:', error);
    alert('Error al eliminar la foto.');
  }
}

// ==================== FORMULARIOS ====================

// ==================== INFORMACIÓN PERSONAL ====================
const editPersonalInfoBtn = document.getElementById('editPersonalInfoBtn');
const personalInfoForm = document.getElementById('personalInfoForm');

if (editPersonalInfoBtn && personalInfoForm) {
    const personalInfoInputs = personalInfoForm.querySelectorAll('input');
    const personalInfoActions = document.getElementById('personalInfoActions');
    const cancelPersonalInfoBtn = document.getElementById('cancelPersonalInfoBtn');
    let originalValues = {};

    editPersonalInfoBtn.addEventListener('click', () => {
        originalValues = {};
        personalInfoInputs.forEach(input => {
            originalValues[input.id] = input.value;
            input.disabled = false;
        });
        personalInfoActions.style.display = 'flex';
        editPersonalInfoBtn.style.display = 'none';
    });

    cancelPersonalInfoBtn.addEventListener('click', () => {
        personalInfoInputs.forEach(input => {
            input.value = originalValues[input.id];
            input.disabled = true;
        });
        personalInfoActions.style.display = 'none';
        editPersonalInfoBtn.style.display = 'block';
    });

    personalInfoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            nombre_completo: document.getElementById('nombreCompleto').value,
            telefono: document.getElementById('telefono').value,
            whatsapp: document.getElementById('whatsapp').value
        };

        try {
            const updateUrl = personalInfoForm.dataset.updateUrl;
            const response = await fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ ' + data.message);
                personalInfoInputs.forEach(input => {
                    input.disabled = true;
                });
                document.querySelector('.profile-username').textContent = formData.username;
                document.querySelector('.profile-email').textContent = formData.email;
                personalInfoActions.style.display = 'none';
                editPersonalInfoBtn.style.display = 'block';
            } else {
                alert('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('Error al actualizar el perfil.');
        }
    });
}


// ==================== INFORMACIÓN DEL NEGOCIO ====================
const editBusinessInfoBtn = document.getElementById('editBusinessInfoBtn');
const businessInfoForm = document.getElementById('businessInfoForm');

if (editBusinessInfoBtn && businessInfoForm) {
    const businessInfoInputs = businessInfoForm.querySelectorAll('input, select');
    const businessInfoActions = document.getElementById('businessInfoActions');
    const cancelBusinessInfoBtn = document.getElementById('cancelBusinessInfoBtn');
    let originalValues = {};

    editBusinessInfoBtn.addEventListener('click', () => {
        originalValues = {};
        businessInfoInputs.forEach(input => {
            originalValues[input.id] = input.value;
            input.disabled = false;
        });
        businessInfoActions.style.display = 'flex';
        editBusinessInfoBtn.style.display = 'none';
    });

    cancelBusinessInfoBtn.addEventListener('click', () => {
        businessInfoInputs.forEach(input => {
            input.value = originalValues[input.id];
            input.disabled = true;
        });
        businessInfoActions.style.display = 'none';
        editBusinessInfoBtn.style.display = 'block';
    });

    businessInfoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            nombre_negocio: document.getElementById('nombreNegocio').value,
            tipo_negocio: document.getElementById('tipoNegocio').value,
            relacion_negocio: document.getElementById('relacionNegocio').value,
            comuna: document.getElementById('comuna').value,
            region: document.getElementById('region').value,
            direccion: document.getElementById('direccion').value
        };

        const updateUrl = businessInfoForm.dataset.updateUrl;
        try {
            const response = await fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ ' + data.message);
                businessInfoInputs.forEach(input => {
                    input.disabled = true;
                });
                businessInfoActions.style.display = 'none';
                editBusinessInfoBtn.style.display = 'block';
            } else {
                alert('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error updating business info:', error);
            alert('Error al actualizar la información del negocio.');
        }
    });
}

// Preferencias
document.getElementById('preferencesForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = {
    recibir_notificaciones: document.getElementById('notificaciones').checked,
    recibir_newsletter: document.getElementById('newsletter').checked
  };

  const updateUrl = document.getElementById('preferencesForm').dataset.updateUrl;
  try {
    const response = await fetch(updateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (data.success) {
      alert('✅ Preferencias guardadas correctamente');
    } else {
      alert('❌ ' + data.error);
    }
  } catch (error) {
    console.error('Error updating preferences:', error);
    alert('Error al actualizar las preferencias.');
  }
});


// ==================== CAMBIAR CONTRASEÑA ====================
const editPasswordBtn = document.getElementById('editPasswordBtn');
const passwordForm = document.getElementById('passwordForm');

if (editPasswordBtn && passwordForm) {
    const passwordInputs = passwordForm.querySelectorAll('input');
    const passwordActions = document.getElementById('passwordActions');
    const cancelPasswordBtn = document.getElementById('cancelPasswordBtn');

    editPasswordBtn.addEventListener('click', () => {
        passwordInputs.forEach(input => {
            input.disabled = false;
        });
        passwordActions.style.display = 'flex';
        editPasswordBtn.style.display = 'none';
    });

    cancelPasswordBtn.addEventListener('click', () => {
        passwordInputs.forEach(input => {
            input.disabled = true;
            input.value = ''; // Clear password fields
        });
        passwordActions.style.display = 'none';
        editPasswordBtn.style.display = 'block';
    });

    passwordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            alert('❌ Las contraseñas nuevas no coinciden');
            return;
        }

        if (newPassword.length < 6) {
            alert('❌ La contraseña debe tener al menos 6 caracteres');
            return;
        }

        const changePasswordUrl = passwordForm.dataset.changePasswordUrl;
        try {
            const response = await fetch(changePasswordUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ ' + data.message);
                passwordInputs.forEach(input => {
                    input.disabled = true;
                    input.value = '';
                });
                passwordActions.style.display = 'none';
                editPasswordBtn.style.display = 'block';
            } else {
                alert('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error changing password:', error);
            alert('Error al cambiar la contraseña.');
        }
    });
}


// ==================== MODAL HANDLERS ====================
const openModal = (modal) => {
    if (!modal) return;
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('active'), 10);
};

const closeModal = (modal) => {
    if (!modal) return;
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = 'none';
        // Reset password field and error on close
        const passwordInput = document.getElementById('deletePassword');
        const passwordError = document.getElementById('passwordError');
        if (modal.id === 'passwordModal' && passwordInput && passwordError) {
            passwordInput.value = '';
            passwordError.style.display = 'none';
        }
    }, 300);
};

// ==================== ELIMINAR CUENTA (CON MODAL) ====================
document.addEventListener('DOMContentLoaded', () => {
    const deleteAccountBtn = document.querySelector('.btn-danger[onclick="confirmDeleteAccount()"]');
    if (!deleteAccountBtn) return;

    const deleteAccountModal = document.getElementById('deleteAccountModal');
    const passwordModal = document.getElementById('passwordModal');
    const closeDeleteModal = document.getElementById('closeDeleteModal');
    const closePasswordModal = document.getElementById('closePasswordModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelPasswordBtnModal = document.getElementById('cancelPasswordBtnModal');
    const confirmPasswordDeletionBtn = document.getElementById('confirmPasswordDeletionBtn');
    const passwordInput = document.getElementById('deletePassword');
    const passwordError = document.getElementById('passwordError');

    // Re-bind the main delete button to open the first modal
    deleteAccountBtn.onclick = (e) => {
        e.preventDefault(); // Prevent any default behavior
        openModal(deleteAccountModal);
    };

    // --- Modal Listeners ---
    closeDeleteModal.addEventListener('click', () => closeModal(deleteAccountModal));
    cancelDeleteBtn.addEventListener('click', () => closeModal(deleteAccountModal));
    closePasswordModal.addEventListener('click', () => closeModal(passwordModal));
    cancelPasswordBtnModal.addEventListener('click', () => closeModal(passwordModal));

    window.addEventListener('click', (e) => {
        if (e.target === deleteAccountModal) closeModal(deleteAccountModal);
        if (e.target === passwordModal) closeModal(passwordModal);
    });

    confirmDeleteBtn.addEventListener('click', () => {
        closeModal(deleteAccountModal);
        openModal(passwordModal);
        passwordInput.focus();
    });

    const handlePasswordSubmit = () => {
        const password = passwordInput.value;
        if (!password) {
            passwordError.textContent = 'Por favor, ingresa tu contraseña.';
            passwordError.style.display = 'block';
            return;
        }
        passwordError.style.display = 'none';
        deleteAccount(password);
    };

    confirmPasswordDeletionBtn.addEventListener('click', handlePasswordSubmit);
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handlePasswordSubmit();
        }
    });
});

async function deleteAccount(password) {
    const deleteAccountUrl = document.querySelector('.btn-danger[data-delete-account-url]').dataset.deleteAccountUrl;
    const passwordModal = document.getElementById('passwordModal');
    const passwordError = document.getElementById('passwordError');
    let response;

    try {
        response = await fetch(deleteAccountUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ password: password })
        });
    } catch (error) {
        console.error('Network error during account deletion:', error);
        passwordError.textContent = 'Error de conexión al eliminar la cuenta.';
        passwordError.style.display = 'block';
        return;
    }

    if (response.ok) {
        // Success case: The server responded with a 2xx status.
        // The account is deleted, and the session is likely terminated.
        // We don't need to parse JSON, just redirect.
        closeModal(passwordModal);
        alert('✅ Cuenta eliminada exitosamente.');
        window.location.href = '/';
    } else {
        // Error case: The server responded with a 4xx or 5xx status.
        // Now we can safely try to parse the JSON error message.
        try {
            const data = await response.json();
            passwordError.textContent = data.error || 'La contraseña es incorrecta o ha ocurrido un error.';
            passwordError.style.display = 'block';
        } catch (e) {
            console.error('Could not parse error JSON:', e);
            passwordError.textContent = 'Ha ocurrido un error inesperado al procesar la respuesta.';
            passwordError.style.display = 'block';
        }
    }
}


// ==================== PREVIEW DE IMAGEN ====================
document.getElementById('photoInput')?.addEventListener('change', function(e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      const photoElement = document.getElementById('profilePhoto');
      const placeholderElement = document.getElementById('profilePhotoPlaceholder');
      
      if (placeholderElement) {
        placeholderElement.style.backgroundImage = `url(${e.target.result})`;
        placeholderElement.style.backgroundSize = 'cover';
        placeholderElement.style.backgroundPosition = 'center';
        placeholderElement.textContent = '';
      } else if (photoElement) {
        photoElement.src = e.target.result;
      }
    };
    reader.readAsDataURL(file);
  }
});

console.log('✅ Profile.js loaded successfully');

// ==================== PESTAÑAS DE PRÓXIMOS EVENTOS ====================
function openTab(evt, tabName) {
    // Ocultar todo el contenido de las pestañas
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Quitar la clase "active" de todos los botones de pestaña
    const tablinks = document.getElementsByClassName("tab-link");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Mostrar la pestaña actual y agregar una clase "active" al botón que abrió la pestaña
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Por defecto, abrir la primera pestaña
document.addEventListener('DOMContentLoaded', () => {
    // Si existen las pestañas, simula un clic en la primera para abrirla
    const firstTab = document.querySelector(".tab-link");
    if (firstTab) {
        firstTab.click();
    }
});