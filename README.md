# Rutas y conexiones del campus

Aplicación web para administrar edificios y conexiones bidireccionales de un campus, visualizar el grafo, consultar rutas con BFS y recorrerlo con DFS. El grafo está implementado sin clases: `grafo.py` contiene funciones que operan sobre un diccionario de listas de adyacencia.

## Ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`. El grafo de ejemplo contiene seis edificios y conexiones bidireccionales. Los cambios se mantienen en memoria y se pierden al reiniciar el servidor.

## API

- `GET /api/grafo`: lista de adyacencia.
- `POST /api/edificios`: agrega un vértice con `{"nombre":"Gimnasio"}`.
- `POST /api/conexiones`: agrega una arista con `{"origen":"Biblioteca","destino":"Aulas"}`.
- `DELETE /api/conexiones?origen=Biblioteca&destino=Laboratorio`: elimina esa conexión bidireccional.
- `GET /api/ruta?origen=Cafetería&destino=Aulas`: ruta más corta en cantidad de aristas mediante BFS; devuelve `ruta: null` si no existe.
- `GET /api/recorrido?inicio=Cafetería`: recorrido DFS.
- `POST /api/restaurar`: restaura el ejemplo inicial.

## Pruebas

```powershell
python tests/test_app.py
```

La salida debe confirmar que se completaron 12 pruebas.
