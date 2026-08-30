(function () {
  "use strict";

  var principal = document.getElementById("galeria-principal");
  if (!principal) return;

  var imagemAtual = document.getElementById("galeria-imagem-atual");
  var legenda = document.getElementById("galeria-legenda");
  var miniaturas = document.querySelectorAll("#galeria-miniaturas img");
  var fotos = Array.from(miniaturas).map(function (img) {
    return { src: img.src, alt: img.alt, titulo: img.getAttribute("data-titulo") || "" };
  });
  if (!fotos.length) {
    fotos = [{
      src: imagemAtual.src,
      alt: imagemAtual.alt,
      titulo: imagemAtual.getAttribute("data-titulo") || "",
    }];
  }

  var lightbox = document.getElementById("lightbox");
  var lightboxImagem = document.getElementById("lightbox-imagem");
  var indiceAtual = 0;

  function mostrarNaPrincipal(indice) {
    indiceAtual = indice;
    imagemAtual.src = fotos[indice].src;
    imagemAtual.alt = fotos[indice].alt;
    if (legenda) legenda.textContent = fotos[indice].titulo;
    miniaturas.forEach(function (img, i) {
      img.classList.toggle("ativa", i === indice);
    });
  }

  function abrirLightbox(indice) {
    indiceAtual = indice;
    lightboxImagem.src = fotos[indice].src;
    lightboxImagem.alt = fotos[indice].alt;
    lightbox.classList.add("aberto");
    document.body.style.overflow = "hidden";
  }

  function fecharLightbox() {
    lightbox.classList.remove("aberto");
    document.body.style.overflow = "";
  }

  function navegar(delta) {
    indiceAtual = (indiceAtual + delta + fotos.length) % fotos.length;
    lightboxImagem.src = fotos[indiceAtual].src;
    lightboxImagem.alt = fotos[indiceAtual].alt;
    mostrarNaPrincipal(indiceAtual);
  }

  principal.addEventListener("click", function () { abrirLightbox(indiceAtual); });

  miniaturas.forEach(function (img, i) {
    img.addEventListener("click", function () { mostrarNaPrincipal(i); });
  });

  var fechar = document.getElementById("lightbox-fechar");
  var anterior = document.getElementById("lightbox-prev");
  var proximo = document.getElementById("lightbox-next");
  if (fechar) fechar.addEventListener("click", fecharLightbox);
  if (anterior) anterior.addEventListener("click", function () { navegar(-1); });
  if (proximo) proximo.addEventListener("click", function () { navegar(1); });

  lightbox.addEventListener("click", function (evento) {
    if (evento.target === lightbox) fecharLightbox();
  });

  document.addEventListener("keydown", function (evento) {
    if (!lightbox.classList.contains("aberto")) return;
    if (evento.key === "Escape") fecharLightbox();
    if (evento.key === "ArrowLeft") navegar(-1);
    if (evento.key === "ArrowRight") navegar(1);
  });
})();
