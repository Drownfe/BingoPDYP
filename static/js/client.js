// static/js/client.js

const socket = io();

// Recibir cartón enviado por el servidor
socket.on("card", (data) => {
    const pre = document.getElementById("card-text");
    pre.textContent = data.text || "Cartón recibido.";
});

// Recibir historial inicial
socket.on("history", (data) => {
    const historyDiv = document.getElementById("history");
    historyDiv.textContent = data.numbers.join(", ");
});

// Recibir balota nueva
socket.on("ball", (data) => {
    const lastBallDiv = document.getElementById("last-ball");
    lastBallDiv.textContent = `${data.letter}${data.number}`;

    const historyDiv = document.getElementById("history");
    historyDiv.textContent += (historyDiv.textContent ? ", " : "") + `${data.letter}${data.number}`;
});

// Recibir anuncio de ganador
socket.on("winner", (data) => {
    alert(data.message || "¡Hay un ganador!");
});
