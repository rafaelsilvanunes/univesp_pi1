console.log("App carregado");

document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", () => {
            console.log("Form enviado");
        });
    });
});

console.log("Rodando...");