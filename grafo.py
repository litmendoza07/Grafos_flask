"""Operaciones del grafo no ponderado del campus con lista de adyacencia."""

from collections import deque


def crear_grafo():
    """Crea un grafo vacío como diccionario de listas de adyacencia."""
    return {}


def agregar_vertice(grafo, vertice):
    """Agrega un edificio al grafo si todavía no está registrado."""
    if vertice not in grafo:
        grafo[vertice] = []


def agregar_arista(grafo, origen, destino):
    """Agrega una conexión bidireccional sin duplicar vecinos."""
    if origen == destino:
        raise ValueError("No se puede conectar un edificio consigo mismo.")

    agregar_vertice(grafo, origen)
    agregar_vertice(grafo, destino)
    if destino not in grafo[origen]:
        grafo[origen].append(destino)
    if origen not in grafo[destino]:
        grafo[destino].append(origen)


def eliminar_arista(grafo, origen, destino):
    """Elimina la conexión en ambos sentidos o informa si no existe."""
    validar_vertice(grafo, origen)
    validar_vertice(grafo, destino)
    if destino not in grafo[origen]:
        raise ValueError("No existe una conexión entre esos edificios.")
    grafo[origen].remove(destino)
    grafo[destino].remove(origen)


def bfs(grafo, origen, destino):
    """Devuelve la ruta más corta en cantidad de aristas o None si no existe."""
    validar_vertice(grafo, origen)
    validar_vertice(grafo, destino)

    cola = deque([origen])
    anteriores = {origen: None}
    while cola:
        actual = cola.popleft()
        if actual == destino:
            ruta = []
            while actual is not None:
                ruta.append(actual)
                actual = anteriores[actual]
            return list(reversed(ruta))

        for vecino in grafo[actual]:
            if vecino not in anteriores:
                anteriores[vecino] = actual
                cola.append(vecino)
    return None


def dfs(grafo, inicio):
    """Devuelve el orden de visita en profundidad desde el edificio inicial."""
    validar_vertice(grafo, inicio)

    visitados = set()
    recorrido = []
    pila = [inicio]
    while pila:
        actual = pila.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        recorrido.append(actual)
        pila.extend(
            reversed([vecino for vecino in grafo[actual] if vecino not in visitados])
        )
    return recorrido


def validar_vertice(grafo, vertice):
    """Verifica que el edificio exista y lanza KeyError si falta."""
    if vertice not in grafo:
        raise KeyError(vertice)


def crear_grafo_ejemplo():
    """Construye el grafo inicial del campus usado por la aplicación."""
    grafo = crear_grafo()
    edificios = [
        "Administración",
        "Biblioteca",
        "Auditorio",
        "Laboratorio",
        "Cafetería",
        "Aulas",
    ]
    for edificio in edificios:
        agregar_vertice(grafo, edificio)

    conexiones = [
        ("Administración", "Biblioteca"),
        ("Administración", "Auditorio"),
        ("Biblioteca", "Laboratorio"),
        ("Biblioteca", "Cafetería"),
        ("Biblioteca", "Auditorio"),
        ("Auditorio", "Cafetería"),
        ("Laboratorio", "Aulas"),
        ("Cafetería", "Aulas"),
    ]
    for origen, destino in conexiones:
        agregar_arista(grafo, origen, destino)
    return grafo
