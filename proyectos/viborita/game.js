const canvas = document.getElementById("board"); // Encuentra el tablero donde se dibuja el juego.
const context = canvas.getContext("2d"); // Prepara las herramientas para dibujar dentro del tablero.
const levelDisplay = document.getElementById("level"); // Encuentra el espacio donde se muestra el nivel.
const scoreDisplay = document.getElementById("score"); // Encuentra el espacio donde se muestran los puntos.
const fruitDisplay = document.getElementById("fruit-count"); // Encuentra el espacio donde se cuentan las frutas.
const statusDisplay = document.getElementById("status"); // Encuentra el texto que explica el estado.
const overlay = document.getElementById("overlay"); // Encuentra la capa de mensajes sobre el tablero.
const overlayIcon = document.getElementById("overlay-icon"); // Encuentra el icono del mensaje.
const overlayTitle = document.getElementById("overlay-title"); // Encuentra el título del mensaje.
const overlayCopy = document.getElementById("overlay-copy"); // Encuentra la explicación del mensaje.
const startButton = document.getElementById("start-button"); // Encuentra el botón que inicia o continúa la partida.
const cellSize = 20; // Define el tamaño en píxeles de cada casilla.
const columns = canvas.width / cellSize; // Calcula cuántas casillas caben a lo ancho.
const rows = canvas.height / cellSize; // Calcula cuántas casillas caben a lo alto.
const fruitsPerLevel = 4; // Define cuántas frutas hacen falta para superar un nivel.
const maximumLevel = 20; // Define que la partida tiene veinte niveles.
let snake = []; // Guarda las casillas que ocupa la viborita.
let direction = { x: 1, y: 0 }; // Guarda la dirección actual de movimiento.
let nextDirection = { x: 1, y: 0 }; // Guarda la dirección que se aplicará en el siguiente paso.
let fruit = { x: 0, y: 0 }; // Guarda la posición de la fruta actual.
let level = 1; // Guarda el nivel actual de la partida.
let score = 0; // Guarda los puntos acumulados.
let fruitsEaten = 0; // Cuenta cuántas frutas se han comido en este nivel.
let timer = null; // Guarda el reloj que mueve la viborita.
let gameState = "ready"; // Indica si el juego está listo, jugando, pausado o terminado.
let touchStart = null; // Guarda el punto inicial de un gesto táctil.
function showOverlay(icon, title, copy, buttonText) { // Prepara y muestra un mensaje en el tablero.
  overlayIcon.textContent = icon; // Coloca el símbolo elegido en el mensaje.
  overlayTitle.textContent = title; // Coloca el título elegido en el mensaje.
  overlayCopy.textContent = copy; // Coloca la explicación elegida en el mensaje.
  startButton.textContent = buttonText; // Cambia el texto del botón para indicar su acción.
  overlay.classList.remove("is-hidden"); // Hace visible la capa del mensaje.
} // Termina la función que muestra mensajes.
function hideOverlay() { // Oculta el mensaje para dejar ver el tablero.
  overlay.classList.add("is-hidden"); // Esconde la capa del mensaje.
} // Termina la función que oculta mensajes.
function updateDisplays() { // Actualiza los números que ve quien juega.
  levelDisplay.innerHTML = `${String(level).padStart(2, "0")} <small>/ 20</small>`; // Muestra el nivel con dos dígitos y la meta.
  scoreDisplay.textContent = String(score).padStart(3, "0"); // Muestra los puntos con tres dígitos.
  fruitDisplay.innerHTML = `${fruitsEaten} <small>/ ${fruitsPerLevel}</small>`; // Muestra las frutas comidas y las que faltan.
} // Termina la actualización de los números.
function randomFreeCell() { // Busca una casilla vacía para colocar la fruta.
  let position; // Reserva espacio para la posición que se va a probar.
  do { // Repite la búsqueda hasta encontrar un lugar libre.
    position = { x: Math.floor(Math.random() * columns), y: Math.floor(Math.random() * rows) }; // Elige una casilla al azar dentro del tablero.
  } while (snake.some((segment) => segment.x === position.x && segment.y === position.y)); // Repite si la casilla está ocupada por la viborita.
  return position; // Devuelve la casilla vacía encontrada.
} // Termina la búsqueda de casillas libres.
function resetGame() { // Prepara una partida nueva desde el nivel uno.
  clearInterval(timer); // Detiene cualquier movimiento que haya quedado de una partida anterior.
  snake = [{ x: 8, y: 10 }, { x: 7, y: 10 }, { x: 6, y: 10 }]; // Coloca la viborita corta en el centro.
  direction = { x: 1, y: 0 }; // Hace que la viborita empiece mirando a la derecha.
  nextDirection = { x: 1, y: 0 }; // Prepara el primer movimiento hacia la derecha.
  level = 1; // Vuelve al primer nivel.
  score = 0; // Borra los puntos de la partida anterior.
  fruitsEaten = 0; // Reinicia el contador de frutas del nivel.
  fruit = randomFreeCell(); // Coloca una fruta en una casilla vacía.
  gameState = "ready"; // Indica que todavía no se ha iniciado el movimiento.
  statusDisplay.textContent = "Lista para jugar"; // Informa de que se puede empezar.
  updateDisplays(); // Refresca el nivel, los puntos y las frutas.
  draw(); // Dibuja el tablero inicial.
  showOverlay("↗", "¿Listo para jugar?", "Come 4 frutas para pasar de nivel. ¡Completa los 20!", "Empezar partida"); // Explica cómo empezar la partida.
} // Termina la preparación de una partida.
function startGame() { // Inicia una partida o la continúa después de una pausa.
  if (gameState === "won" || gameState === "lost") { // Comprueba si la partida anterior ya terminó.
    resetGame(); // Prepara una partida nueva si la anterior terminó.
  } // Termina la comprobación de partida terminada.
  if (gameState === "playing") { // Comprueba si la viborita ya se está moviendo.
    return; // Evita crear más de un reloj de movimiento.
  } // Termina la comprobación de partida en curso.
  gameState = "playing"; // Indica que la partida está en marcha.
  statusDisplay.textContent = "En juego"; // Actualiza el estado que se ve en pantalla.
  hideOverlay(); // Quita el mensaje para mostrar todo el tablero.
  clearInterval(timer); // Evita que quede activo un reloj anterior.
  timer = setInterval(tick, Math.max(70, 165 - (level - 1) * 5)); // Mueve la viborita cada vez más rápido según el nivel.
} // Termina el inicio de la partida.
function pauseGame() { // Detiene temporalmente una partida activa.
  if (gameState !== "playing") { // Comprueba que la partida esté realmente en marcha.
    return; // No hace nada si ya está pausada o terminó.
  } // Termina la comprobación del estado.
  clearInterval(timer); // Detiene el reloj que mueve la viborita.
  gameState = "paused"; // Guarda que la partida está pausada.
  statusDisplay.textContent = "En pausa"; // Informa de que la partida está detenida.
  showOverlay("Ⅱ", "Partida en pausa", "Tómate un respiro; tu progreso sigue guardado.", "Continuar"); // Muestra cómo seguir jugando.
} // Termina la pausa.
function setDirection(name) { // Cambia el rumbo de la viborita de forma segura.
  const directions = { up: { x: 0, y: -1 }, down: { x: 0, y: 1 }, left: { x: -1, y: 0 }, right: { x: 1, y: 0 } }; // Relaciona cada nombre con su movimiento.
  const chosenDirection = directions[name]; // Busca la dirección que se pidió.
  if (!chosenDirection || gameState === "lost" || gameState === "won") { // Comprueba que el rumbo exista y se pueda cambiar.
    return; // Ignora direcciones desconocidas o partidas terminadas.
  } // Termina la comprobación de la dirección.
  if (chosenDirection.x + direction.x === 0 && chosenDirection.y + direction.y === 0) { // Comprueba si el rumbo es justo al contrario.
    return; // Evita que la viborita se dé la vuelta y choque consigo misma.
  } // Termina la comprobación del rumbo contrario.
  nextDirection = chosenDirection; // Guarda el rumbo elegido para el siguiente movimiento.
  if (gameState === "ready") { // Comprueba si se está eligiendo rumbo antes de empezar.
    direction = chosenDirection; // Deja que la primera dirección se aplique sin retraso.
  } // Termina la comprobación del inicio.
} // Termina el cambio de dirección.
function tick() { // Realiza un paso de movimiento de la viborita.
  direction = nextDirection; // Aplica el rumbo elegido para este paso.
  const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y }; // Calcula dónde quedará la cabeza.
  const ateFruit = head.x === fruit.x && head.y === fruit.y; // Comprueba si la cabeza llega a la fruta.
  const bodyToCheck = ateFruit ? snake : snake.slice(0, -1); // No cuenta la cola como choque si va a moverse.
  const hitWall = head.x < 0 || head.x >= columns || head.y < 0 || head.y >= rows; // Comprueba si la cabeza sale del tablero.
  const hitSnake = bodyToCheck.some((segment) => segment.x === head.x && segment.y === head.y); // Comprueba si la cabeza toca el cuerpo.
  if (hitWall || hitSnake) { // Comprueba si ocurrió un choque.
    endGame(); // Termina la partida después del choque.
    return; // Evita mover la viborita tras perder.
  } // Termina la comprobación de choques.
  snake.unshift(head); // Añade la nueva cabeza al principio del cuerpo.
  if (ateFruit) { // Comprueba si la viborita comió la fruta.
    score += level * 10; // Añade más puntos conforme sube el nivel.
    fruitsEaten += 1; // Cuenta la fruta que acaba de comer.
    fruit = randomFreeCell(); // Coloca otra fruta en un lugar libre.
    updateDisplays(); // Actualiza los puntos y las frutas en pantalla.
    if (fruitsEaten >= fruitsPerLevel) { // Comprueba si ya se alcanzó la meta del nivel.
      advanceLevel(); // Pasa al nivel siguiente o celebra la victoria.
      return; // Deja que el nuevo nivel dibuje el tablero.
    } // Termina la comprobación de la meta.
  } else { // Si no comió fruta, la viborita no debe crecer.
    snake.pop(); // Quita la última casilla para conservar el mismo largo.
  } // Termina el crecimiento de la viborita.
  draw(); // Dibuja el tablero con la nueva posición.
} // Termina el paso de movimiento.
function advanceLevel() { // Sube un nivel al completar la meta de frutas.
  clearInterval(timer); // Para el ritmo anterior antes de cambiar de nivel.
  if (level >= maximumLevel) { // Comprueba si se terminó el último nivel.
    gameState = "won"; // Guarda que se ganó la partida completa.
    statusDisplay.textContent = "¡Victoria!"; // Muestra que se completaron los niveles.
    draw(); // Dibuja el tablero final.
    showOverlay("★", "¡Victoria total!", `Has completado los 20 niveles y conseguido ${score} puntos.`, "Jugar de nuevo"); // Celebra que se hayan acabado todos los niveles.
    return; // Evita iniciar un nivel que no existe.
  } // Termina la comprobación del último nivel.
  level += 1; // Avanza al siguiente nivel.
  fruitsEaten = 0; // Empieza de nuevo el contador de frutas de este nivel.
  fruit = randomFreeCell(); // Coloca una fruta para el nivel nuevo.
  gameState = "playing"; // Mantiene la partida en curso.
  statusDisplay.textContent = `Nivel ${String(level).padStart(2, "0")}`; // Anuncia el nuevo nivel.
  updateDisplays(); // Actualiza el nivel y la meta de frutas.
  draw(); // Dibuja la viborita y la nueva fruta.
  timer = setInterval(tick, Math.max(70, 165 - (level - 1) * 5)); // Aumenta la velocidad para el nuevo nivel.
} // Termina el cambio de nivel.
function endGame() { // Termina la partida cuando la viborita choca.
  clearInterval(timer); // Detiene el movimiento.
  gameState = "lost"; // Guarda que la partida se perdió.
  statusDisplay.textContent = "Fin de la partida"; // Informa del final de la partida.
  draw(); // Dibuja el último estado del tablero.
  showOverlay("↻", "¡Fin de la partida!", `Llegaste al nivel ${level} y sumaste ${score} puntos.`, "Intentar de nuevo"); // Muestra el resultado y cómo volver a probar.
} // Termina el final de la partida.
function drawRoundedCell(x, y, color, inset = 2) { // Dibuja una casilla con esquinas suaves.
  const left = x * cellSize + inset; // Calcula el borde izquierdo de la casilla.
  const top = y * cellSize + inset; // Calcula el borde superior de la casilla.
  const size = cellSize - inset * 2; // Calcula el tamaño de la casilla sin sus márgenes.
  context.fillStyle = color; // Elige el color de relleno.
  context.beginPath(); // Empieza una forma nueva.
  context.roundRect(left, top, size, size, 6); // Dibuja el rectángulo redondeado.
  context.fill(); // Rellena la forma con el color elegido.
} // Termina el dibujo de casillas redondeadas.
function draw() { // Vuelve a dibujar el tablero entero.
  context.fillStyle = "#101b20"; // Elige el color de fondo del tablero.
  context.fillRect(0, 0, canvas.width, canvas.height); // Limpia el tablero y pinta el fondo.
  context.strokeStyle = "#ffffff08"; // Elige un color muy suave para la cuadrícula.
  context.lineWidth = 1; // Mantiene fina la línea de la cuadrícula.
  for (let x = 0; x <= canvas.width; x += cellSize) { // Recorre las posiciones verticales del tablero.
    context.beginPath(); // Empieza una línea vertical.
    context.moveTo(x, 0); // Sitúa el inicio de la línea arriba.
    context.lineTo(x, canvas.height); // Sitúa el final de la línea abajo.
    context.stroke(); // Dibuja la línea vertical.
  } // Termina el dibujo de las líneas verticales.
  for (let y = 0; y <= canvas.height; y += cellSize) { // Recorre las posiciones horizontales del tablero.
    context.beginPath(); // Empieza una línea horizontal.
    context.moveTo(0, y); // Sitúa el inicio de la línea a la izquierda.
    context.lineTo(canvas.width, y); // Sitúa el final de la línea a la derecha.
    context.stroke(); // Dibuja la línea horizontal.
  } // Termina el dibujo de las líneas horizontales.
  context.fillStyle = "#ff8e72"; // Elige el color de la fruta.
  context.beginPath(); // Empieza la forma redonda de la fruta.
  context.arc(fruit.x * cellSize + cellSize / 2, fruit.y * cellSize + cellSize / 2, 7, 0, Math.PI * 2); // Dibuja la fruta en el centro de su casilla.
  context.fill(); // Rellena la fruta.
  context.fillStyle = "#ffd1a7"; // Elige un color claro para el brillo de la fruta.
  context.beginPath(); // Empieza la forma del brillo.
  context.arc(fruit.x * cellSize + 7, fruit.y * cellSize + 7, 2, 0, Math.PI * 2); // Dibuja el brillo pequeño de la fruta.
  context.fill(); // Rellena el brillo.
  snake.forEach((segment, index) => { // Recorre cada trozo del cuerpo de la viborita.
    const color = index === 0 ? "#a4efb1" : "#6fce8a"; // Da un tono más claro a la cabeza.
    drawRoundedCell(segment.x, segment.y, color, index === 0 ? 1 : 2); // Dibuja cada trozo en su casilla.
  }); // Termina el dibujo del cuerpo.
  const head = snake[0]; // Guarda la posición de la cabeza para dibujar sus ojos.
  if (head) { // Comprueba que la viborita tenga cabeza.
    const eyePositions = direction.x !== 0 ? [{ x: 0, y: -4 }, { x: 0, y: 4 }] : [{ x: -4, y: 0 }, { x: 4, y: 0 }]; // Coloca los ojos mirando hacia el frente.
    context.fillStyle = "#183222"; // Elige un color oscuro para los ojos.
    eyePositions.forEach((eye) => { // Recorre las dos posiciones de los ojos.
      context.beginPath(); // Empieza la forma de un ojo.
      context.arc(head.x * cellSize + cellSize / 2 + eye.x, head.y * cellSize + cellSize / 2 + eye.y, 1.6, 0, Math.PI * 2); // Dibuja un ojo pequeño.
      context.fill(); // Rellena el ojo.
    }); // Termina el dibujo de los ojos.
  } // Termina la comprobación de la cabeza.
} // Termina el dibujo del tablero.
document.addEventListener("keydown", (event) => { // Escucha las teclas que se pulsan.
  const keyDirections = { ArrowUp: "up", w: "up", W: "up", ArrowDown: "down", s: "down", S: "down", ArrowLeft: "left", a: "left", A: "left", ArrowRight: "right", d: "right", D: "right" }; // Permite jugar con flechas o con WASD.
  if (keyDirections[event.key]) { // Comprueba si se ha pulsado una tecla de movimiento.
    event.preventDefault(); // Evita que la página se desplace con las flechas.
    setDirection(keyDirections[event.key]); // Cambia el rumbo según la tecla.
  } // Termina la comprobación de movimiento.
  if (event.code === "Space") { // Comprueba si se pulsó la barra espaciadora.
    event.preventDefault(); // Evita que la página se desplace hacia abajo.
    if (gameState === "playing") { // Comprueba si la partida está en marcha.
      pauseGame(); // Pausa el juego cuando está en marcha.
    } else if (gameState === "paused" || gameState === "ready") { // Comprueba si el juego se puede continuar.
      startGame(); // Inicia o continúa la partida.
    } // Termina la decisión de pausa o continuación.
  } // Termina la comprobación de la barra espaciadora.
}); // Termina la escucha del teclado.
startButton.addEventListener("click", startGame); // Inicia o continúa la partida al pulsar el botón.
document.querySelectorAll(".mobile-controls button").forEach((button) => { // Prepara cada botón táctil.
  button.addEventListener("click", () => setDirection(button.dataset.direction)); // Cambia el rumbo al pulsar una flecha táctil.
}); // Termina la preparación de los botones táctiles.
canvas.addEventListener("touchstart", (event) => { // Recuerda dónde empieza un gesto sobre el tablero.
  touchStart = { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY }; // Guarda la posición inicial del dedo.
}, { passive: true }); // Permite que el navegador procese el gesto sin bloquearse.
canvas.addEventListener("touchend", (event) => { // Detecta la dirección del gesto al levantar el dedo.
  if (!touchStart) { // Comprueba que exista una posición inicial guardada.
    return; // Ignora el gesto si no se guardó su inicio.
  } // Termina la comprobación del inicio del gesto.
  const deltaX = event.changedTouches[0].clientX - touchStart.x; // Calcula cuánto se movió el dedo de lado a lado.
  const deltaY = event.changedTouches[0].clientY - touchStart.y; // Calcula cuánto se movió el dedo de arriba abajo.
  if (Math.max(Math.abs(deltaX), Math.abs(deltaY)) > 25) { // Ignora movimientos táctiles demasiado pequeños.
    setDirection(Math.abs(deltaX) > Math.abs(deltaY) ? (deltaX > 0 ? "right" : "left") : (deltaY > 0 ? "down" : "up")); // Elige la dirección principal del gesto.
  } // Termina la comprobación del movimiento del dedo.
  touchStart = null; // Borra la posición para el siguiente gesto.
}, { passive: true }); // Permite que el navegador procese el gesto sin bloquearse.
if (!CanvasRenderingContext2D.prototype.roundRect) { // Comprueba si el navegador puede dibujar esquinas redondeadas.
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, width, height, radius) { // Añade una versión sencilla si falta esa función.
    this.beginPath(); // Empieza el contorno del rectángulo.
    this.moveTo(x + radius, y); // Empieza después de la esquina superior izquierda.
    this.arcTo(x + width, y, x + width, y + height, radius); // Redondea la esquina superior derecha.
    this.arcTo(x + width, y + height, x, y + height, radius); // Redondea la esquina inferior derecha.
    this.arcTo(x, y + height, x, y, radius); // Redondea la esquina inferior izquierda.
    this.arcTo(x, y, x + width, y, radius); // Redondea la esquina superior izquierda.
    this.closePath(); // Cierra la forma para poder rellenarla.
  }; // Termina la función de compatibilidad.
} // Termina la comprobación de compatibilidad.
resetGame(); // Prepara el tablero para que se pueda empezar a jugar.
