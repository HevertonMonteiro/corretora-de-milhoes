(function () {
  "use strict";

  // Formata campos de valor (R$) enquanto a corretora digita. Funciona só
  // com os dígitos: os 2 últimos sempre são os centavos, o resto vira a
  // parte inteira — por isso o campo precisa ser um <input type="text">
  // (marcado com data-moeda), não um <input type="number">.

  function paraDigitos(valor) {
    return (valor || "").replace(/\D/g, "");
  }

  function formatarMoeda(digitos) {
    if (!digitos) return "";
    var numero = parseInt(digitos, 10) / 100;
    return "R$ " + numero.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  // Antes de enviar o formulário, converte de volta pro formato puro que o
  // Django espera (ex: "R$ 1.234,56" -> "1234.56").
  function paraDecimalPlano(valorFormatado) {
    var digitos = paraDigitos(valorFormatado);
    if (!digitos) return "";
    return (parseInt(digitos, 10) / 100).toFixed(2);
  }

  var campos = document.querySelectorAll("[data-moeda]");
  if (!campos.length) return;

  campos.forEach(function (campo) {
    // Ao editar um imóvel já cadastrado, o valor inicial vem puro do banco
    // (ex: "450000.00") — formata assim que a página carrega.
    if (campo.value) {
      campo.value = formatarMoeda(paraDigitos(campo.value));
    }

    campo.addEventListener("input", function () {
      campo.value = formatarMoeda(paraDigitos(campo.value));
      campo.setSelectionRange(campo.value.length, campo.value.length);
    });
  });

  var form = campos[0].closest("form");
  if (form) {
    form.addEventListener("submit", function () {
      campos.forEach(function (campo) {
        campo.value = paraDecimalPlano(campo.value);
      });
    });
  }
})();
