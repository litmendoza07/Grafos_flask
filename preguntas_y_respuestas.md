# Preguntas y respuestas

1. ¿Qué sucede si eliminas la conexión entre Biblioteca y Laboratorio?
   - Respuesta: La ruta entre Biblioteca y Laboratorio ya no puede ir directamente, así que el sistema podría necesitar otra ruta alternativa, como Biblioteca → Auditorio → Laboratorio o Biblioteca → Administración → Laboratorio.

2. ¿Puede existir más de una ruta entre dos edificios? Compruébalo.
   - Respuesta: Sí. Por ejemplo, entre Biblioteca y Aulas hay varias rutas posibles, como Biblioteca → Laboratorio → Aulas y Biblioteca → Auditorio → Cafetería → Aulas.

3. ¿Cuál es la diferencia entre el resultado de BFS y el de DFS?
   - Respuesta: BFS explora por niveles y siempre encuentra la ruta más corta en número de conexiones. DFS explora una rama profunda antes de volver atrás; por eso su recorrido puede ser completamente distinto aunque llegue al mismo destino.

4. ¿Qué cambio realizarías para que cada camino tenga una distancia en metros?
   - Respuesta: Se podría representar cada conexión como un par (vecino, peso), por ejemplo {"Laboratorio": 60}. Luego se usaría un algoritmo como Dijkstra para hallar la ruta con menor costo.

5. ¿Qué estructura de datos utilizarías para evitar visitar un edificio más de una vez?
   - Respuesta: Un conjunto (set) o una lista de visitados. En BFS y DFS se usa un conjunto para guardar los nodos ya explorados y evitar ciclos o repeticiones.
   