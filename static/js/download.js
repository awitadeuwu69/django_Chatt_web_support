document.addEventListener('DOMContentLoaded', function() {
    const licenseForm = document.getElementById('licenseForm');
    
    if (licenseForm) {
        licenseForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Recolectar datos del formulario
            const formData = new FormData(licenseForm);
            const data = {};
            formData.forEach((value, key) => data[key] = value);
            
            try {
                // Aquí puedes agregar la lógica para enviar los datos al servidor
                // Por ahora solo mostraremos un mensaje de éxito
                alert('Gracias por registrarse. Recibirá la licencia temporal en su correo electrónico.');
                licenseForm.reset();
            } catch (error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar su solicitud. Por favor intente nuevamente.');
            }
        });
    }

    // Validación de celular (formato chileno)
    const celularInput = document.getElementById('celular');
    if (celularInput) {
        celularInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0 && !value.startsWith('569')) {
                value = '569' + value;
            }
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
            e.target.value = '+' + value;
        });
    }
});