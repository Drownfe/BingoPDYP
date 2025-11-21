// static/js/admin.js

// Conexión como ADMIN (role="admin")
const adminSocket = io({
    auth: { role: "admin" }
});

const startBtn = document.getElementById("start-btn");
const lastBallDiv = document.getElementById("admin-last-ball");
const historyDiv = document.getElementById("admin-history");
const statusDiv = document.getElementById("admin-status");
const playersCountDiv = document.getElementById("players-count");

// Botón: iniciar juego
startBtn.addEventListener("click", () => {
    adminSocket.emit("start_game");
});

// Confirmación de inicio
adminSocket.on("game_started", () => {
    statusDiv.textContent = "Juego en curso...";
    historyDiv.textContent = "";
    lastBallDiv.textContent = "-";
});

// Balotas
adminSocket.on("ball", (data) => {
    const token = `${data.letter}${data.number}`;
    lastBallDiv.textContent = token;

    if (historyDiv.textContent.trim().length > 0) {
        historyDiv.textContent += ", " + token;
    } else {
        historyDiv.textContent = token;
    }
});

// Ganador
adminSocket.on("winner", (data) => {
    const msg = data.message || "¡Hay un ganador!";
    statusDiv.textContent = msg;
});

// Fin del juego
adminSocket.on("game_over", (data) => {
    const msg = data.message || "Fin del juego.";
    statusDiv.textContent = msg;
});

// Conteo de jugadores reales (solo pestañas de /)
adminSocket.on("players_count", (data) => {
    playersCountDiv.textContent = data.count ?? 0;
});
