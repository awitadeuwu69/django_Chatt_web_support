// Minimal JS for El Almacen imported sections
document.addEventListener('DOMContentLoaded', function(){
  // Simple gallery click to open image in new tab (lightweight fallback)
  document.querySelectorAll('.elal-card img').forEach(img => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', () => {
      window.open(img.src, '_blank');
    });
  });

  // Back to top button auto-create
  let back = document.createElement('button');
  back.textContent = '↑';
  back.title = 'Volver arriba';
  back.style = 'position:fixed;right:16px;bottom:80px;padding:10px 12px;border-radius:6px;border:none;background:#0078ff;color:#fff;cursor:pointer;display:none;z-index:9999;';
  document.body.appendChild(back);
  back.addEventListener('click', () => window.scrollTo({top:0,behavior:'smooth'}));
  window.addEventListener('scroll', () => {
    if(window.scrollY>300) back.style.display='block'; else back.style.display='none';
  });
});
