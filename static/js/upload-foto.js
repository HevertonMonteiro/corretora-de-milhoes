(function () {
  "use strict";

  var LADO_MAXIMO = 1920;
  var QUALIDADE_JPEG = 0.82;

  function tokenCsrf() {
    var campo = document.querySelector("input[name=csrfmiddlewaretoken]");
    return campo ? campo.value : "";
  }

  function reduzirFoto(arquivo) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(arquivo);
      var img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        var escala = Math.min(1, LADO_MAXIMO / Math.max(img.width, img.height));
        var canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * escala);
        canvas.height = Math.round(img.height * escala);
        canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(function (blob) {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error("Não foi possível preparar a foto."));
          }
        }, "image/jpeg", QUALIDADE_JPEG);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("O arquivo escolhido não é uma imagem válida."));
      };
      img.src = url;
    });
  }

  function enviarFoto(input) {
    var arquivo = input.files && input.files[0];
    if (!arquivo) return;

    var oculto = input.parentNode.querySelector("input[data-caminho-imagem]");
    var status = input.parentNode.querySelector("[data-upload-status]");
    var caminhoAnterior = oculto.value;

    input.dataset.pendente = "1";
    status.textContent = "Enviando foto...";

    reduzirFoto(arquivo)
      .then(function (blob) {
        var dados = new FormData();
        dados.append("arquivo", blob, "foto.jpg");
        dados.append("pasta", input.dataset.pasta);
        return fetch(input.dataset.uploadUrl, {
          method: "POST",
          body: dados,
          credentials: "same-origin",
          headers: { "X-CSRFToken": tokenCsrf() },
        });
      })
      .then(function (resposta) {
        return resposta.json().catch(function () { return {}; }).then(function (corpo) {
          if (!resposta.ok) throw new Error(corpo.erro || "Falha ao enviar a foto.");
          return corpo;
        });
      })
      .then(function (corpo) {
        oculto.value = corpo.caminho;
        status.textContent = "Foto pronta.";
      })
      .catch(function (erro) {
        oculto.value = caminhoAnterior;
        input.value = "";
        status.textContent = erro.message || "Não foi possível enviar a foto.";
      })
      .then(function () {
        input.dataset.pendente = "";
      });
  }

  document.querySelectorAll("input[data-upload-foto]").forEach(function (input) {
    var oculto = input.parentNode.querySelector("input[data-caminho-imagem]");
    var status = input.parentNode.querySelector("[data-upload-status]");
    if (oculto && oculto.value && status) {
      status.textContent = "Foto atual mantida. Escolha outra para trocar.";
    }
    input.addEventListener("change", function () {
      enviarFoto(input);
    });
  });

  // Captura no document para rodar antes do listener de main.js, que
  // desabilita o botão de enviar; se houver upload em andamento, o
  // formulário não pode ser enviado com o caminho ainda vazio.
  document.addEventListener(
    "submit",
    function (evento) {
      if (evento.target.querySelector("input[data-upload-foto][data-pendente='1']")) {
        evento.preventDefault();
        evento.stopImmediatePropagation();
        window.alert("Aguarde o envio da foto terminar antes de salvar.");
      }
    },
    true
  );
})();
