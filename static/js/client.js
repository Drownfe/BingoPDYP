/* =======================================================
   CLIENT.JS — LÓGICA DEL JUGADOR
   ======================================================= */

const socket = io("/", {
    auth: { role: "player" }
});

/* =======================================================
   ELEMENTOS DEL DOM
   ======================================================= */

const playerNameEl = document.getElementById("player-name");
const cardGridEl = document.getElementById("card-grid");
const lastBallEl = document.getElementById("last-ball");
const statusEl = document.getElementById("bingo-status");

/* Global board columns */
const globalColumns = {
    B: document.getElementById("global-col-B"),
    I: document.getElementById("global-col-I"),
    N: document.getElementById("global-col-N"),
    G: document.getElementById("global-col-G"),
    O: document.getElementById("global-col-O")
};

/* Guardar cartón actual en memoria */
let currentCard = [];

/* =======================================================
   CONSTRUIR CARTÓN DESDE TEXTO
   ======================================================= */

function drawCardFromText(textGrid) {
    const lines = textGrid.trim().split("\n").slice(1); // Ignorar encabezado B I N G O

    currentCard = []; // Reiniciar estructura local
    cardGridEl.innerHTML = ""; // Limpiar UI

    lines.forEach((line, rowIndex) => {
        const nums = line.split(/\s+/).map(v => (v === "*" ? 0 : parseInt(v)));
        currentCard.push(nums);

        nums.forEach(num => {
            const cell = document.createElement("div");
            cell.classList.add("cell");

            if (num === 0) {
                cell.classList.add("free");
                cell.textContent = "*";
            } else {
                cell.textContent = num;
            }

            cardGridEl.appendChild(cell);
        });
    });
}

/* =======================================================
   CONSTRUIR TABLERO GENERAL (1–75)
   ======================================================= */

function buildGlobalBoard() {
    const ranges = {
        B: [1, 15],
        I: [16, 30],
        N: [31, 45],
        G: [46, 60],
        O: [61, 75]
    };

    for (let col in ranges) {
        const [start, end] = ranges[col];

        for (let n = start; n <= end; n++) {
            const div = document.createElement("div");
            div.classList.add("global-cell");
            div.dataset.number = n;
            div.textContent = n;
            globalColumns[col].appendChild(div);
        }
    }
}

buildGlobalBoard();

/* =======================================================
   MARCAR NÚMERO EN TABLERO GENERAL
   ======================================================= */

function markOnGlobalBoard(num) {
    const cell = document.querySelector(`.global-cell[data-number='${num}']`);
    if (cell) cell.classList.add("marked");
}

/* =======================================================
   MARCAR NÚMEROS EN EL CARTÓN DEL JUGADOR
   ======================================================= */

function markCard(num) {
    const cardCells = Array.from(cardGridEl.children);

    for (let r = 0; r < 5; r++) {
        for (let c = 0; c < 5; c++) {
            if (currentCard[r][c] === num) {
                const index = r * 5 + c;
                cardCells[index].classList.add("marked");
            }
        }
    }
}

/* =======================================================
   EVENTO: RECIBIR CARTÓN NUEVO
   ======================================================= */

socket.on("card", (data) => {
    console.log("[CLIENT] Nuevo cartón recibido");
    playerNameEl.textContent = data.name;
    drawCardFromText(data.text);
});

/* =======================================================
   EVENTO: BALOTA NUEVA
   ======================================================= */

socket.on("ball", (data) => {
    const text = `${data.letter}${data.number}`;
    lastBallEl.textContent = text;

    markOnGlobalBoard(data.number);
    markCard(data.number);
});

/* =======================================================
   EVENTO: RESET COMPLETO
   ======================================================= */

socket.on("reset", () => {
    console.log("[CLIENT] Reset recibido");

    // Reset balota
    lastBallEl.textContent = "-";

    // Reset tablero general
    document.querySelectorAll(".global-cell").forEach(c => c.classList.remove("marked"));

    // Reset cartón
    cardGridEl.innerHTML = "";
    currentCard = [];

    statusEl.textContent = "En espera…";
});

/* =======================================================
   EVENTO: FIN DEL JUEGO
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
