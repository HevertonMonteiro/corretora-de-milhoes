(function () {
  "use strict";

  // Menu mobile
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".navbar nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var aberto = nav.classList.toggle("aberto");
      toggle.setAttribute("aria-expanded", aberto ? "true" : "false");
    });
  }

  // Revelar elementos ao rolar a página
  var revelaveis = document.querySelectorAll(".reveal");
  if (revelaveis.length) {
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entradas) {
          entradas.forEach(function (entrada) {
            if (entrada.isIntersecting) {
              entrada.target.classList.add("is-visible");
              observer.unobserve(entrada.target);
            }
          });
        },
        { threshold: 0.15 }
      );
      revelaveis.forEach(function (el) { observer.observe(el); });
    } else {
      revelaveis.forEach(function (el) { el.classList.add("is-visible"); });
    }
  }

  // Contadores animados (estatísticas da home)
  var contadores = document.querySelectorAll("[data-contador]");
  if (contadores.length && "IntersectionObserver" in window) {
    var animarContador = function (el) {
      var alvo = parseInt(el.getAttribute("data-contador"), 10) || 0;
      var duracao = 1200;
      var inicio = null;
      var passo = function (timestamp) {
        if (!inicio) inicio = timestamp;
        var progresso = Math.min((timestamp - inicio) / duracao, 1);
        el.textContent = Math.floor(progresso * alvo);
        if (progresso < 1) {
          requestAnimationFrame(passo);
        } else {
          el.textContent = alvo;
        }
      };
      requestAnimationFrame(passo);
    };
    var observerContador = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (entrada) {
          if (entrada.isIntersecting) {
            animarContador(entrada.target);
            observerContador.unobserve(entrada.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    contadores.forEach(function (el) { observerContador.observe(el); });
  }
})();
