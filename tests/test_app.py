import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as app_module
from grafo import (
    agregar_arista,
    agregar_vertice,
    bfs,
    crear_grafo_ejemplo,
    dfs,
    eliminar_arista,
)


def crear_cliente():
    app_module.app.config["TESTING"] = True
    app_module.grafo = crear_grafo_ejemplo()
    return app_module.app.test_client()


def test_bfs_encuentra_la_ruta_mas_corta():
    grafo = crear_grafo_ejemplo()
    assert bfs(grafo, "Cafetería", "Aulas") == ["Cafetería", "Aulas"]


def test_bfs_informa_si_no_hay_ruta():
    grafo = crear_grafo_ejemplo()
    agregar_vertice(grafo, "Gimnasio")
    assert bfs(grafo, "Administración", "Gimnasio") is None


def test_dfs_visita_cada_edificio_conectado_una_vez():
    recorrido = dfs(crear_grafo_ejemplo(), "Cafetería")
    assert len(recorrido) == 6
    assert len(set(recorrido)) == 6


def test_conexiones_bidireccionales_y_sin_duplicados():
    grafo = crear_grafo_ejemplo()
    agregar_arista(grafo, "Administración", "Aulas")
    agregar_arista(grafo, "Aulas", "Administración")
    assert grafo["Administración"].count("Aulas") == 1
    assert grafo["Aulas"].count("Administración") == 1


def test_no_permite_conectar_un_edificio_consigo_mismo():
    try:
        agregar_arista(crear_grafo_ejemplo(), "Aulas", "Aulas")
    except ValueError:
        return
    raise AssertionError("Se esperaba rechazar una conexión del edificio consigo mismo.")


def test_eliminar_conexion_actualiza_las_dos_direcciones():
    grafo = crear_grafo_ejemplo()
    eliminar_arista(grafo, "Biblioteca", "Laboratorio")
    assert "Laboratorio" not in grafo["Biblioteca"]
    assert "Biblioteca" not in grafo["Laboratorio"]
    assert bfs(grafo, "Biblioteca", "Laboratorio") == [
        "Biblioteca",
        "Cafetería",
        "Aulas",
        "Laboratorio",
    ]


def test_inicio_y_consulta_del_grafo():
    cliente = crear_cliente()
    assert cliente.get("/").status_code == 200
    respuesta = cliente.get("/api/grafo")
    assert respuesta.status_code == 200
    assert "Biblioteca" in respuesta.json["adyacencia"]


def test_api_agrega_edificio_y_conexion_bidireccional():
    cliente = crear_cliente()
    respuesta = cliente.post("/api/edificios", json={"nombre": "Gimnasio"})
    assert respuesta.status_code == 201
    respuesta = cliente.post(
        "/api/conexiones",
        json={"origen": "Gimnasio", "destino": "Aulas"},
    )
    assert respuesta.status_code == 201
    assert "Gimnasio" in respuesta.json["adyacencia"]["Aulas"]
    respuesta = cliente.post(
        "/api/conexiones",
        json={"origen": "Administración", "destino": "Aulas"},
    )
    assert respuesta.status_code == 201
    ruta = cliente.get("/api/ruta?origen=Administración&destino=Aulas")
    assert ruta.json["ruta"] == ["Administración", "Aulas"]


def test_api_rechaza_conexion_invalida_y_edificio_inexistente():
    cliente = crear_cliente()
    respuesta = cliente.post(
        "/api/conexiones",
        json={"origen": "Aulas", "destino": "Aulas"},
    )
    assert respuesta.status_code == 400
    respuesta = cliente.get("/api/ruta?origen=Inventado&destino=Aulas")
    assert respuesta.status_code == 404


def test_api_informa_si_no_hay_ruta():
    cliente = crear_cliente()
    cliente.post("/api/edificios", json={"nombre": "Gimnasio"})
    respuesta = cliente.get("/api/ruta?origen=Administración&destino=Gimnasio")
    assert respuesta.status_code == 200
    assert respuesta.json["ruta"] is None


def test_api_ejecuta_dfs_y_restaura_el_ejemplo():
    cliente = crear_cliente()
    respuesta = cliente.get("/api/recorrido?inicio=Cafetería")
    assert respuesta.status_code == 200
    assert respuesta.json["visitados"] == 6
    cliente.post("/api/edificios", json={"nombre": "Gimnasio"})
    respuesta = cliente.post("/api/restaurar")
    assert respuesta.status_code == 200
    assert "Gimnasio" not in respuesta.json["adyacencia"]


def test_api_elimina_conexion_y_reporta_si_no_existe():
    cliente = crear_cliente()
    respuesta = cliente.delete(
        "/api/conexiones?origen=Biblioteca&destino=Laboratorio"
    )
    assert respuesta.status_code == 200
    assert "Laboratorio" not in respuesta.json["adyacencia"]["Biblioteca"]
    respuesta = cliente.delete(
        "/api/conexiones?origen=Biblioteca&destino=Laboratorio"
    )
    assert respuesta.status_code == 404


if __name__ == "__main__":
    pruebas = [
        test_bfs_encuentra_la_ruta_mas_corta,
        test_bfs_informa_si_no_hay_ruta,
        test_dfs_visita_cada_edificio_conectado_una_vez,
        test_conexiones_bidireccionales_y_sin_duplicados,
        test_no_permite_conectar_un_edificio_consigo_mismo,
        test_eliminar_conexion_actualiza_las_dos_direcciones,
        test_inicio_y_consulta_del_grafo,
        test_api_agrega_edificio_y_conexion_bidireccional,
        test_api_rechaza_conexion_invalida_y_edificio_inexistente,
        test_api_informa_si_no_hay_ruta,
        test_api_ejecuta_dfs_y_restaura_el_ejemplo,
        test_api_elimina_conexion_y_reporta_si_no_existe,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK: {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas completadas.")
