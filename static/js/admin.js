/* =======================================================
   ADMIN.JS — LÓGICA DEL PANEL DE ADMINISTRACIÓN
   ======================================================= */

const socket = io("/", {
    auth: { role: "admin" }
});

/* =======================================================
   ELEMENTOS DEL DOM
   ======================================================= */

const startBtn = document.getElementById("start-game-btn");
const resetBtn = document.getElementById("reset-game-btn");
const statusEl = document.getElementById("admin-game-status");
const lastBallEl = document.getElementById("admin-last-ball");
const playerCountEl = document.getElementById("admin-player-count");

/* =======================================================
   BOTÓN: INICIAR JUEGO
   ======================================================= */

startBtn.addEventListener("click", () => {
    console.log("[ADMIN] Inicio solicitado");
    socket.emit("admin_start");
});

/* =======================================================
   BOTÓN: REINICIAR JUEGO
   ======================================================= */

resetBtn.addEventListener("click", () => {
    console.log("[ADMIN] Reinicio solicitado");
    socket.emit("reset_game");
});

/* =======================================================
   EVENTO: ACTUALIZACIONES DE ESTADO DEL ADMIN
   ======================================================= */

socket.on("admin_status", (data) => {
    console.log("[ADMIN] Estado recibido", data);

    if (data.running) {
        statusEl.textContent = "Juego en curso…";
    } else {
        statusEl.textContent = "En espera…";
        lastBallEl.textContent = "-";
    }

    if (data.players !== undefined) {
        playerCountEl.textContent = `${data.players} jugadores`;
    }
});

/* =======================================================
   EVENTO: NUEVA BALOTA
   ======================================================= */

socket.on("ball", (data) => {
    const label = `${data.letter}${data.number}`;
    lastBallEl.textContent = label;
});

/* =======================================================
   EVENTO: JUEGO FINALIZADO
   ======================================================= */

socket.on("game_over", (data) => {
    statusEl.textContent = data.message;
});

/* =======================================================
   EVENTO: GANADOR
   ======================================================= */

socket.on("winner", (data) => {
    statusEl.textContent = data.message;
});

/* =======================================================
   EVENTO: CAMBIO DE JUGADORES
   ======================================================= */

socket.on("players_count", (data) => {
    playerCountEl.textContent = `${data.count} jugadores`;
});
