const graphElement = document.querySelector("#graph");
const adjacencyListElement = document.querySelector("#adjacency-list");
const routeResult = document.querySelector("#route-result");
const dfsResult = document.querySelector("#dfs-result");
const managementMessage = document.querySelector("#management-message");

let graph = {};
let highlightedNodes = [];
let highlightedEdges = [];

async function api(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "No se pudo completar la operación.");
  return data;
}

function updateSelects() {
  const selectors = [
    document.querySelector("#route-origin"),
    document.querySelector("#route-destination"),
    document.querySelector("#dfs-start"),
    document.querySelector("#connection-origin"),
    document.querySelector("#connection-destination"),
    document.querySelector("#remove-origin"),
    document.querySelector("#remove-destination"),
  ];
  const names = Object.keys(graph);
  for (const select of selectors) {
    const previous = select.value;
    select.replaceChildren();
    for (const name of names) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.append(option);
    }
    if (names.includes(previous)) select.value = previous;
  }
}

function edgeKey(a, b) {
  return [a, b].sort().join("\u0000");
}

function renderGraph() {
  const names = Object.keys(graph);
  const width = 620;
  const height = 340;
  const centerX = width / 2;
  const centerY = height / 2;
  const radiusX = Math.min(230, width * 0.39);
  const radiusY = Math.min(125, height * 0.37);
  const positions = new Map(
    names.map((name, index) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * index) / Math.max(names.length, 1);
      return [name, { x: centerX + radiusX * Math.cos(angle), y: centerY + radiusY * Math.sin(angle) }];
    }),
  );
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "presentation");
  const title = document.createElementNS(svg.namespaceURI, "title");
  title.textContent = "Diagrama de conexiones del campus";
  svg.append(title);

  const renderedEdges = new Set();
  for (const [origin, neighbors] of Object.entries(graph)) {
    for (const destination of neighbors) {
      const key = edgeKey(origin, destination);
      if (renderedEdges.has(key)) continue;
      renderedEdges.add(key);
      const start = positions.get(origin);
      const end = positions.get(destination);
      const line = document.createElementNS(svg.namespaceURI, "line");
      line.setAttribute("x1", start.x);
      line.setAttribute("y1", start.y);
      line.setAttribute("x2", end.x);
      line.setAttribute("y2", end.y);
      line.setAttribute("class", highlightedEdges.includes(key) ? "edge active" : "edge");
      svg.append(line);
    }
  }

  for (const name of names) {
    const { x, y } = positions.get(name);
    const group = document.createElementNS(svg.namespaceURI, "g");
    group.setAttribute("class", `node${highlightedNodes.includes(name) ? " active" : ""}`);
    const circle = document.createElementNS(svg.namespaceURI, "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", "28");
    const label = document.createElementNS(svg.namespaceURI, "text");
    label.setAttribute("x", x);
    label.setAttribute("y", y + 47);
    label.textContent = name;
    group.append(circle, label);
    svg.append(group);
  }
  graphElement.replaceChildren(svg);
}

function renderAdjacency() {
  adjacencyListElement.textContent = Object.entries(graph)
    .map(([name, neighbors]) => `${name} → ${neighbors.length ? neighbors.join(", ") : "(sin conexiones)"}`)
    .join("\n");
}

function render() {
  updateSelects();
  renderGraph();
  renderAdjacency();
}

async function loadGraph() {
  const data = await api("/api/grafo");
  graph = data.adyacencia;
  render();
}

document.querySelector("#route-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const origin = document.querySelector("#route-origin").value;
  const destination = document.querySelector("#route-destination").value;
  routeResult.textContent = "Buscando ruta…";
  try {
    const data = await api(`/api/ruta?origen=${encodeURIComponent(origin)}&destino=${encodeURIComponent(destination)}`);
    if (!data.ruta) {
      routeResult.textContent = data.mensaje;
      highlightedNodes = [];
      highlightedEdges = [];
    } else {
      routeResult.replaceChildren();
      const heading = document.createElement("strong");
      heading.textContent = "Ruta encontrada";
      const path = document.createElement("span");
      path.textContent = data.ruta.join(" → ");
      const count = document.createElement("span");
      count.textContent = `Conexiones utilizadas: ${data.conexiones}`;
      routeResult.append(heading, path, count);
      highlightedNodes = data.ruta;
      highlightedEdges = data.ruta.slice(1).map((name, index) => edgeKey(data.ruta[index], name));
    }
    renderGraph();
  } catch (error) {
    routeResult.textContent = error.message;
  }
});

document.querySelector("#dfs-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const start = document.querySelector("#dfs-start").value;
  dfsResult.textContent = "Explorando grafo…";
  try {
    const data = await api(`/api/recorrido?inicio=${encodeURIComponent(start)}`);
    dfsResult.textContent = `Orden de visita: ${data.recorrido.join(" → ")}. Vértices visitados: ${data.visitados}.`;
    highlightedNodes = data.recorrido;
    highlightedEdges = data.recorrido.slice(1).map((name, index) => edgeKey(data.recorrido[index], name));
    renderGraph();
  } catch (error) {
    dfsResult.textContent = error.message;
  }
});

document.querySelector("#building-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.querySelector("#building-name");
  try {
    const data = await api("/api/edificios", {
      method: "POST",
      body: JSON.stringify({ nombre: input.value }),
    });
    managementMessage.textContent = data.mensaje;
    managementMessage.className = "status success";
    input.value = "";
    await loadGraph();
  } catch (error) {
    managementMessage.textContent = error.message;
    managementMessage.className = "status error";
  }
});

document.querySelector("#connection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const origin = document.querySelector("#connection-origin").value;
  const destination = document.querySelector("#connection-destination").value;
  try {
    const data = await api("/api/conexiones", {
      method: "POST",
      body: JSON.stringify({ origen: origin, destino: destination }),
    });
    graph = data.adyacencia;
    highlightedNodes = [];
    highlightedEdges = [];
    managementMessage.textContent = data.mensaje;
    managementMessage.className = "status success";
    render();
  } catch (error) {
    managementMessage.textContent = error.message;
    managementMessage.className = "status error";
  }
});

document.querySelector("#remove-connection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const origin = document.querySelector("#remove-origin").value;
  const destination = document.querySelector("#remove-destination").value;
  try {
    const data = await api(
      `/api/conexiones?origen=${encodeURIComponent(origin)}&destino=${encodeURIComponent(destination)}`,
      { method: "DELETE" },
    );
    graph = data.adyacencia;
    highlightedNodes = [];
    highlightedEdges = [];
    managementMessage.textContent = data.mensaje;
    managementMessage.className = "status success";
    render();
  } catch (error) {
    managementMessage.textContent = error.message;
    managementMessage.className = "status error";
  }
});

document.querySelector("#reset-button").addEventListener("click", async () => {
  try {
    const data = await api("/api/restaurar", { method: "POST" });
    graph = data.adyacencia;
    highlightedNodes = [];
    highlightedEdges = [];
    managementMessage.textContent = data.mensaje;
    managementMessage.className = "status success";
    routeResult.textContent = "Elige un origen y un destino para comenzar.";
    dfsResult.textContent = "Selecciona un edificio para explorar sus conexiones.";
    render();
  } catch (error) {
    managementMessage.textContent = error.message;
    managementMessage.className = "status error";
  }
});

loadGraph().catch((error) => {
  graphElement.textContent = `No se pudo cargar el grafo: ${error.message}`;
});
