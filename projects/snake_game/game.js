const canvas = document.getElementById("board");
const context = canvas.getContext("2d");
const levelDisplay = document.getElementById("level");
const scoreDisplay = document.getElementById("score");
const fruitDisplay = document.getElementById("fruit-count");
const statusDisplay = document.getElementById("status");
const overlay = document.getElementById("overlay");
const overlayIcon = document.getElementById("overlay-icon");
const overlayTitle = document.getElementById("overlay-title");
const overlayCopy = document.getElementById("overlay-copy");
const startButton = document.getElementById("start-button");
const cellSize = 20;
const columns = canvas.width / cellSize;
const rows = canvas.height / cellSize;
const fruitsPerLevel = 4;
const maximumLevel = 20;
let snake = [];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let fruit = { x: 0, y: 0 };
let level = 1;
let score = 0;
let fruitsEaten = 0;
let timer = null;
let gameState = "ready";
let touchStart = null;
function showOverlay(icon, title, copy, buttonText) {
  overlayIcon.textContent = icon;
  overlayTitle.textContent = title;
  overlayCopy.textContent = copy;
  startButton.textContent = buttonText;
  overlay.classList.remove("is-hidden");
}
function hideOverlay() {
  overlay.classList.add("is-hidden");
}
function updateDisplays() {
  levelDisplay.innerHTML = `${String(level).padStart(2, "0")} <small>/ 20</small>`;
  scoreDisplay.textContent = String(score).padStart(3, "0");
  fruitDisplay.innerHTML = `${fruitsEaten} <small>/ ${fruitsPerLevel}</small>`;
}
function randomFreeCell() {
  let position;
  do {
    position = { x: Math.floor(Math.random() * columns), y: Math.floor(Math.random() * rows) };
  } while (snake.some((segment) => segment.x === position.x && segment.y === position.y));
  return position;
}
function resetGame() {
  clearInterval(timer);
  snake = [{ x: 8, y: 10 }, { x: 7, y: 10 }, { x: 6, y: 10 }];
  direction = { x: 1, y: 0 };
  nextDirection = { x: 1, y: 0 };
  level = 1;
  score = 0;
  fruitsEaten = 0;
  fruit = randomFreeCell();
  gameState = "ready";
  statusDisplay.textContent = "Ready to play";
  updateDisplays();
  draw();
  showOverlay("↗", "Ready to play?", "Eat 4 fruits to clear a level. Beat all 20!", "Start game");
}
function startGame() {
  if (gameState === "won" || gameState === "lost") {
    resetGame();
  }
  if (gameState === "playing") {
    return;
  }
  gameState = "playing";
  statusDisplay.textContent = "Playing";
  hideOverlay();
  clearInterval(timer);
  timer = setInterval(tick, Math.max(70, 165 - (level - 1) * 5));
}
function pauseGame() {
  if (gameState !== "playing") {
    return;
  }
  clearInterval(timer);
  gameState = "paused";
  statusDisplay.textContent = "Paused";
  showOverlay("Ⅱ", "Game paused", "Take a breather — your progress is saved.", "Resume");
}
function setDirection(name) {
  const directions = { up: { x: 0, y: -1 }, down: { x: 0, y: 1 }, left: { x: -1, y: 0 }, right: { x: 1, y: 0 } };
  const chosenDirection = directions[name];
  if (!chosenDirection || gameState === "lost" || gameState === "won") {
    return;
  }
  if (chosenDirection.x + direction.x === 0 && chosenDirection.y + direction.y === 0) {
    return;
  }
  nextDirection = chosenDirection;
  if (gameState === "ready") {
    direction = chosenDirection;
  }
}
function tick() {
  direction = nextDirection;
  const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };
  const ateFruit = head.x === fruit.x && head.y === fruit.y;
  const bodyToCheck = ateFruit ? snake : snake.slice(0, -1);
  const hitWall = head.x < 0 || head.x >= columns || head.y < 0 || head.y >= rows;
  const hitSnake = bodyToCheck.some((segment) => segment.x === head.x && segment.y === head.y);
  if (hitWall || hitSnake) {
    endGame();
    return;
  }
  snake.unshift(head);
  if (ateFruit) {
    score += level * 10;
    fruitsEaten += 1;
    fruit = randomFreeCell();
    updateDisplays();
    if (fruitsEaten >= fruitsPerLevel) {
      advanceLevel();
      return;
    }
  } else {
    snake.pop();
  }
  draw();
}
function advanceLevel() {
  clearInterval(timer);
  if (level >= maximumLevel) {
    gameState = "won";
    statusDisplay.textContent = "Victory!";
    draw();
    showOverlay("★", "Total victory!", `You cleared all 20 levels and scored ${score} points.`, "Play again");
    return;
  }
  level += 1;
  fruitsEaten = 0;
  fruit = randomFreeCell();
  gameState = "playing";
  statusDisplay.textContent = `Level ${String(level).padStart(2, "0")}`;
  updateDisplays();
  draw();
  timer = setInterval(tick, Math.max(70, 165 - (level - 1) * 5));
}
function endGame() {
  clearInterval(timer);
  gameState = "lost";
  statusDisplay.textContent = "Game over";
  draw();
  showOverlay("↻", "Game over!", `You reached level ${level} with ${score} points.`, "Try again");
}
function drawRoundedCell(x, y, color, inset = 2) {
  const left = x * cellSize + inset;
  const top = y * cellSize + inset;
  const size = cellSize - inset * 2;
  context.fillStyle = color;
  context.beginPath();
  context.roundRect(left, top, size, size, 6);
  context.fill();
}
function draw() {
  context.fillStyle = "#101b20";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#ffffff08";
  context.lineWidth = 1;
  for (let x = 0; x <= canvas.width; x += cellSize) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, canvas.height);
    context.stroke();
  }
  for (let y = 0; y <= canvas.height; y += cellSize) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(canvas.width, y);
    context.stroke();
  }
  context.fillStyle = "#ff8e72";
  context.beginPath();
  context.arc(fruit.x * cellSize + cellSize / 2, fruit.y * cellSize + cellSize / 2, 7, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = "#ffd1a7";
  context.beginPath();
  context.arc(fruit.x * cellSize + 7, fruit.y * cellSize + 7, 2, 0, Math.PI * 2);
  context.fill();
  snake.forEach((segment, index) => {
    const color = index === 0 ? "#a4efb1" : "#6fce8a";
    drawRoundedCell(segment.x, segment.y, color, index === 0 ? 1 : 2);
  });
  const head = snake[0];
  if (head) {
    const eyePositions = direction.x !== 0 ? [{ x: 0, y: -4 }, { x: 0, y: 4 }] : [{ x: -4, y: 0 }, { x: 4, y: 0 }];
    context.fillStyle = "#183222";
    eyePositions.forEach((eye) => {
      context.beginPath();
      context.arc(head.x * cellSize + cellSize / 2 + eye.x, head.y * cellSize + cellSize / 2 + eye.y, 1.6, 0, Math.PI * 2);
      context.fill();
    });
  }
}
document.addEventListener("keydown", (event) => {
  const keyDirections = { ArrowUp: "up", w: "up", W: "up", ArrowDown: "down", s: "down", S: "down", ArrowLeft: "left", a: "left", A: "left", ArrowRight: "right", d: "right", D: "right" };
  if (keyDirections[event.key]) {
    event.preventDefault();
    setDirection(keyDirections[event.key]);
  }
  if (event.code === "Space") {
    event.preventDefault();
    if (gameState === "playing") {
      pauseGame();
    } else if (gameState === "paused" || gameState === "ready") {
      startGame();
    }
  }
});
startButton.addEventListener("click", startGame);
document.querySelectorAll(".mobile-controls button").forEach((button) => {
  button.addEventListener("click", () => setDirection(button.dataset.direction));
});
canvas.addEventListener("touchstart", (event) => {
  touchStart = { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
}, { passive: true });
canvas.addEventListener("touchend", (event) => {
  if (!touchStart) {
    return;
  }
  const deltaX = event.changedTouches[0].clientX - touchStart.x;
  const deltaY = event.changedTouches[0].clientY - touchStart.y;
  if (Math.max(Math.abs(deltaX), Math.abs(deltaY)) > 25) {
    setDirection(Math.abs(deltaX) > Math.abs(deltaY) ? (deltaX > 0 ? "right" : "left") : (deltaY > 0 ? "down" : "up"));
  }
  touchStart = null;
}, { passive: true });
if (!CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, width, height, radius) {
    this.beginPath();
    this.moveTo(x + radius, y);
    this.arcTo(x + width, y, x + width, y + height, radius);
    this.arcTo(x + width, y + height, x, y + height, radius);
    this.arcTo(x, y + height, x, y, radius);
    this.arcTo(x, y, x + width, y, radius);
    this.closePath();
  };
}
resetGame();
