(function () {
  "use strict";

  var form = document.getElementById("form-filtros");
  var grid = document.getElementById("resultados-grid");
  var wrapper = document.getElementById("resultados-imoveis");
  var status = document.getElementById("resultados-status");
  if (!form || !grid) return;

  var url = form.getAttribute("data-url");
  var debounceId = null;
  var requisicaoAtual = null;

  function buscar(empurrarHistorico) {
    var params = new URLSearchParams(new FormData(form));
    // remove campos vazios para manter a URL limpa
    Array.from(params.keys()).forEach(function (chave) {
      if (!params.get(chave)) params.delete(chave);
    });
    var queryString = params.toString();
    var urlCompleta = url + (queryString ? "?" + queryString : "");

    if (empurrarHistorico) {
      history.pushState({}, "", urlCompleta);
    }

    if (requisicaoAtual) requisicaoAtual.abort();
    var controlador = new AbortController();
    requisicaoAtual = controlador;

    wrapper.classList.add("resultados-carregando");
    status.textContent = "Buscando imóveis...";

    fetch(urlCompleta, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      signal: controlador.signal,
    })
      .then(function (resposta) { return resposta.text(); })
      .then(function (html) {
        grid.innerHTML = html;
        var total = grid.querySelectorAll(".card").length;
        status.textContent = total
          ? total + " imóvel(is) encontrado(s)."
          : "Nenhum imóvel encontrado com esses filtros.";
      })
      .catch(function (erro) {
        if (erro.name !== "AbortError") {
          status.textContent = "Não foi possível atualizar os resultados agora.";
        }
      })
      .finally(function () {
        wrapper.classList.remove("resultados-carregando");
      });
  }

  form.addEventListener("submit", function (evento) {
    evento.preventDefault();
    buscar(true);
  });

  form.querySelectorAll("select").forEach(function (campo) {
    campo.addEventListener("change", function () { buscar(true); });
  });

  form.querySelectorAll('input[type="text"], input[type="number"]').forEach(function (campo) {
    campo.addEventListener("input", function () {
      clearTimeout(debounceId);
      debounceId = setTimeout(function () { buscar(true); }, 400);
    });
  });

  window.addEventListener("popstate", function () {
    var params = new URLSearchParams(location.search);
    Array.from(form.elements).forEach(function (campo) {
      if (!campo.name) return;
      campo.value = params.get(campo.name) || "";
    });
    buscar(false);
  });
})();
