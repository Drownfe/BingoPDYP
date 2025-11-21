// static/js/client.js

// Conexión como JUGADOR (enviamos role="player")
const socket = io({
    auth: { role: "player" }
});

// Referencias a elementos
const cardGridDiv = document.getElementById("card-grid");
const cardPre = document.getElementById("card-text");
const lastBallDiv = document.getElementById("last-ball");
const historyDiv = document.getElementById("history");
const bingoStatusDiv = document.getElementById("bingo-status");
const playerNameP = document.getElementById("player-name");

// Matrices internas
let cardGrid = null;   // [[int]]
let markedGrid = null; // [[bool]]


// -----------------------------
// Helpers
// -----------------------------

// Parsea el texto del cartón que viene del servidor a una matriz 5x5 de ints
function parseCardText(text) {
    // Limpiamos y separamos líneas
    const lines = text.split("\n").map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length < 6) {
        console.error("Texto de cartón inesperado:", text);
        return null;
    }

    // Primera línea es el encabezado B I N G O -> la ignoramos
    const rowLines = lines.slice(1, 6); // 5 filas

    const grid = [];

    for (let i = 0; i < 5; i++) {
        const row = rowLines[i];
        const tokens = row.split(/\s+/); // separa por espacios
        if (tokens.length < 5) {
            console.error("Fila inesperada en cartón:", row);
            return null;
        }

        const rowNums = tokens.slice(0, 5).map(tok => {
            if (tok === "*" || tok === "X") {
                return 0; // centro libre
            }
            const n = parseInt(tok, 10);
            return isNaN(n) ? 0 : n;
        });

        grid.push(rowNums);
    }

    return grid;
}

// Dibuja el cartón visual en la grilla
function renderCard() {
    if (!cardGrid) return;

    cardGridDiv.innerHTML = "";

    for (let i = 0; i < 5; i++) {
        for (let j = 0; j < 5; j++) {
            const val = cardGrid[i][j];
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.id = `cell-${i}-${j}`;

            if (val === 0 && i === 2 && j === 2) {
                cell.textContent = "*";
                cell.classList.add("free");
            } else {
                cell.textContent = String(val);
            }

            if (markedGrid && markedGrid[i][j]) {
                cell.classList.add("marked");
            }

            cardGridDiv.appendChild(cell);
        }
    }
}

// Marca una celda que tenga el número de la balota
function markNumberOnCard(number) {
    if (!cardGrid || !markedGrid) return;

    for (let i = 0; i < 5; i++) {
        for (let j = 0; j < 5; j++) {
            if (cardGrid[i][j] === number) {
                markedGrid[i][j] = true;
                const cell = document.getElementById(`cell-${i}-${j}`);
                if (cell) {
                    cell.classList.add("marked");
                }
            }
        }
    }
}


// -----------------------------
// Eventos desde el servidor
// -----------------------------

// Cartón inicial
socket.on("card", (data) => {
    // data.name -> "Jugador X"
    // data.text -> cartón en texto plano
    playerNameP.textContent = data.name || "";
    cardPre.textContent = data.text || "";

    // Construimos matriz a partir del texto
    const grid = parseCardText(data.text || "");
    if (!grid) {
        bingoStatusDiv.textContent = "Error generando el cartón.";
        return;
    }

    cardGrid = grid;

    // Inicializamos matriz de marcados
    markedGrid = Array.from({ length: 5 }, () => Array(5).fill(false));
    // Casilla central libre se marca desde el inicio
    markedGrid[2][2] = true;

    renderCard();
    bingoStatusDiv.textContent = "Cartón listo. Esperando balotas...";
});

// Historial inicial (si entras cuando el juego ya empezó)
socket.on("history", (data) => {
    const nums = data.numbers || [];

    const pretty = nums.map((n) => {
        if (n >= 1 && n <= 15) return "B" + n;
        if (n >= 16 && n <= 30) return "I" + n;
        if (n >= 31 && n <= 45) return "N" + n;
        if (n >= 46 && n <= 60) return "G" + n;
        return "O" + n;
    });

    historyDiv.textContent = pretty.join(", ");

    // Marcamos todas las balotas del historial en el cartón
    nums.forEach((n) => markNumberOnCard(n));
    renderCard();
});

// Nueva balota
socket.on("ball", (data) => {
    const token = `${data.letter}${data.number}`;

    lastBallDiv.textContent = token;

    if (historyDiv.textContent.trim().length > 0) {
        historyDiv.textContent += ", " + token;
    } else {
        historyDiv.textContent = token;
    }

    // Marcamos y refrescamos
    markNumberOnCard(data.number);
    renderCard();

    bingoStatusDiv.textContent = "Balotas en curso...";
});

// Ganador global
socket.on("winner", (data) => {
    const msg = data.message || "¡Hay un ganador!";
    alert(msg);
    bingoStatusDiv.textContent = msg;
});

// Fin del juego
socket.on("game_over", (data) => {
    const msg = data.message || "Fin del juego.";
    bingoStatusDiv.textContent = msg;
});
