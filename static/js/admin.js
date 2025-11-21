// static/js/admin.js

const adminSocket = io();

const startBtn = document.getElementById("start-btn");
const lastBallDiv = document.getElementById("admin-last-ball");
const historyDiv = document.getElementById("admin-history");
const statusDiv = document.getElementById("admin-status");

startBtn.addEventListener("click", () => {
    adminSocket.emit("start_game");
});

adminSocket.on("game_started", () => {
    statusDiv.textContent = "Juego en curso...";
});

// Balotas que ve también el panel
adminSocket.on("ball", (data) => {
    lastBallDiv.textContent = `${data.letter}${data.number}`;
    historyDiv.textContent += (historyDiv.textContent ? ", " : "") + `${data.letter}${data.number}`;
});

// Ganador
adminSocket.on("winner", (data) => {
    statusDiv.textContent = data.message || "¡Hay un ganador!";
});
