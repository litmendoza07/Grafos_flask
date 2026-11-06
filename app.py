"""Rutas HTTP de Flask para administrar el grafo y servir la interfaz."""

from flask import Flask, jsonify, render_template, request

from grafo import (
    agregar_arista,
    agregar_vertice,
    bfs,
    crear_grafo_ejemplo,
    dfs,
    eliminar_arista,
)

app = Flask(__name__)
grafo = crear_grafo_ejemplo()


def error(mensaje, estado):
    """Construye una respuesta JSON de error con su código HTTP."""
    return jsonify({"error": mensaje}), estado


def obtener_campo(data, campo):
    """Obtiene un texto obligatorio del objeto JSON recibido."""
    valor = data.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo '{campo}' es obligatorio.")
    return valor.strip()


@app.get("/")
def inicio():
    """Muestra la aplicación web."""
    return render_template("index.html")


@app.get("/api/grafo")
def consultar_grafo():
    """Devuelve la lista de adyacencia completa."""
    return jsonify({"adyacencia": grafo})


@app.post("/api/edificios")
def agregar_edificio():
    """Valida y agrega un vértice nuevo."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Envía un objeto JSON válido.", 400)
    try:
        nombre = obtener_campo(data, "nombre")
    except ValueError as exc:
        return error(str(exc), 400)
    if len(nombre) > 60:
        return error("El nombre no puede superar 60 caracteres.", 400)
    if nombre in grafo:
        return error("Ese edificio ya está registrado.", 409)

    agregar_vertice(grafo, nombre)
    return jsonify({"mensaje": "Edificio agregado.", "nombre": nombre}), 201


@app.post("/api/conexiones")
def agregar_conexion():
    """Valida y agrega una conexión bidireccional."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Envía un objeto JSON válido.", 400)
    try:
        origen = obtener_campo(data, "origen")
        destino = obtener_campo(data, "destino")
    except ValueError as exc:
        return error(str(exc), 400)
    if len(origen) > 60 or len(destino) > 60:
        return error("Los nombres no pueden superar 60 caracteres.", 400)
    if origen == destino:
        return error("Selecciona dos edificios distintos.", 400)

    agregar_arista(grafo, origen, destino)
    return jsonify(
        {
            "mensaje": "Conexión bidireccional agregada.",
            "origen": origen,
            "destino": destino,
            "adyacencia": grafo,
        }
    ), 201


@app.delete("/api/conexiones")
def eliminar_conexion():
    """Elimina una conexión bidireccional existente."""
    origen = request.args.get("origen", "").strip()
    destino = request.args.get("destino", "").strip()
    if not origen or not destino:
        return error("Indica el origen y el destino.", 400)
    if origen == destino:
        return error("Selecciona dos edificios distintos.", 400)
    try:
        eliminar_arista(grafo, origen, destino)
    except KeyError as exc:
        return error(f"El edificio '{exc.args[0]}' no existe.", 404)
    except ValueError as exc:
        return error(str(exc), 404)
    return jsonify(
        {
            "mensaje": "Conexión bidireccional eliminada.",
            "adyacencia": grafo,
        }
    )


@app.get("/api/ruta")
def consultar_ruta():
    """Calcula con BFS la ruta de menor número de conexiones."""
    origen = request.args.get("origen", "").strip()
    destino = request.args.get("destino", "").strip()
    if not origen or not destino:
        return error("Indica el origen y el destino.", 400)
    try:
        ruta = bfs(grafo, origen, destino)
    except KeyError as exc:
        return error(f"El edificio '{exc.args[0]}' no existe.", 404)
    if ruta is None:
        return jsonify({"ruta": None, "conexiones": None, "mensaje": "No existe una ruta entre esos edificios."})
    return jsonify(
        {
            "ruta": ruta,
            "conexiones": len(ruta) - 1,
            "mensaje": "Ruta encontrada.",
        }
    )


@app.get("/api/recorrido")
def consultar_recorrido():
    """Devuelve el orden de recorrido DFS desde un edificio."""
    inicio = request.args.get("inicio", "").strip()
    if not inicio:
        return error("Indica el edificio inicial.", 400)
    try:
        recorrido = dfs(grafo, inicio)
    except KeyError as exc:
        return error(f"El edificio '{exc.args[0]}' no existe.", 404)
    return jsonify({"recorrido": recorrido, "visitados": len(recorrido)})


@app.post("/api/restaurar")
def restaurar_ejemplo():
    """Restaura el grafo de ejemplo para iniciar nuevamente."""
    global grafo
    grafo = crear_grafo_ejemplo()
    return jsonify({"mensaje": "Se restauró el grafo de ejemplo.", "adyacencia": grafo})


if __name__ == "__main__":
    app.run(debug=True)
