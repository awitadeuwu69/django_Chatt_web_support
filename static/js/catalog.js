document.addEventListener('DOMContentLoaded', function() {
    // Get all "Añadir al Presupuesto" buttons
    const addButtons = document.querySelectorAll('.btn-add-quote');
    
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.product-card');
            const version = card.querySelector('.version').textContent;
            const features = Array.from(card.querySelectorAll('.product-features li'))
                                .map(li => li.textContent)
                                .join('\n');
            
            // For now, just show a confirmation - this could be expanded to actually add to a quote
            alert('Producto añadido al presupuesto:\n' + version + '\n\nCaracterísticas:\n' + features);
            
            // Add visual feedback
            button.textContent = '¡Añadido!';
            button.style.background = '#27ae60';
            setTimeout(() => {
                button.textContent = 'Añadir al Presupuesto';
                button.style.background = '';
            }, 2000);
        });
    });
});