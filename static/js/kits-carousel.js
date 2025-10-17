/* ==================== CARRUSEL DE KITS POS ==================== */

document.addEventListener("DOMContentLoaded", function () {
  const track = document.querySelector(".kits-carousel-track");
  const slides = document.querySelectorAll(".kit-slide");
  const prevBtn = document.querySelector(".carousel-btn.prev");
  const nextBtn = document.querySelector(".carousel-btn.next");
  const indicators = document.querySelectorAll(".indicator");

  if (!track || slides.length === 0) return;

  let currentIndex = 0;
  const totalSlides = slides.length;
  let autoplayInterval;

  // Función para ir a un slide específico
  function goToSlide(index) {
    if (index < 0) {
      currentIndex = totalSlides - 1;
    } else if (index >= totalSlides) {
      currentIndex = 0;
    } else {
      currentIndex = index;
    }

    // Mover el track
    const offset = -currentIndex * 100;
    track.style.transform = `translateX(${offset}%)`;

    // Actualizar indicadores
    indicators.forEach((indicator, i) => {
      if (i === currentIndex) {
        indicator.classList.add("active");
      } else {
        indicator.classList.remove("active");
      }
    });
  }

  // Siguiente slide
  function nextSlide() {
    goToSlide(currentIndex + 1);
  }

  // Slide anterior
  function prevSlide() {
    goToSlide(currentIndex - 1);
  }

  // Event listeners para botones
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      nextSlide();
      resetAutoplay();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      prevSlide();
      resetAutoplay();
    });
  }

  // Event listeners para indicadores
  indicators.forEach((indicator, index) => {
    indicator.addEventListener("click", () => {
      goToSlide(index);
      resetAutoplay();
    });
  });

  // Autoplay
  function startAutoplay() {
    autoplayInterval = setInterval(nextSlide, 10000); // Cambiar cada 5 segundos
  }

  function stopAutoplay() {
    if (autoplayInterval) {
      clearInterval(autoplayInterval);
    }
  }

  function resetAutoplay() {
    stopAutoplay();
    startAutoplay();
  }

  // Pausar autoplay al hacer hover
  const carouselWrapper = document.querySelector(".kits-carousel");
  if (carouselWrapper) {
    carouselWrapper.addEventListener("mouseenter", stopAutoplay);
    carouselWrapper.addEventListener("mouseleave", startAutoplay);
  }

  // Soporte para gestos táctiles (swipe)
  let touchStartX = 0;
  let touchEndX = 0;

  if (track) {
    track.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });

    track.addEventListener("touchend", (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        // Swipe left - next slide
        nextSlide();
      } else {
        // Swipe right - prev slide
        prevSlide();
      }
      resetAutoplay();
    }
  }

  // Soporte para teclado
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      prevSlide();
      resetAutoplay();
    } else if (e.key === "ArrowRight") {
      nextSlide();
      resetAutoplay();
    }
  });



  // Inicializar el primer slide
  goToSlide(0);
});
