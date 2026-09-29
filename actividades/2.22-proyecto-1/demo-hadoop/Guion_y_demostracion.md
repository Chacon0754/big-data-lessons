# Guion para presentar
Hadoop en Docker

Martín Eduardo Chacón Orduño | Proyecto 2.22 | Big Data

Duración prevista: 10 minutos 30 segundos. Reserva hasta 12 minutos para cambiar de ventana y responder una pregunta breve.

## Cómo usar este material

La presentación tiene 12 diapositivas. Las diapositivas 1 a 10 ocupan aproximadamente 6 minutos 25 segundos; la demostración, 3 minutos; el cierre, 25 segundos. Queda un margen de 40 segundos dentro del plan de 10 minutos 30 segundos.

El texto de las siguientes páginas es lo que puedes decir. También está en las notas del presentador del archivo PowerPoint. No necesitas memorizar cada frase: conserva el orden, los conceptos y las cifras.

## La idea que debes recordar

Configuré Hadoop en Docker, comparé el mismo conteo de palabras con uno y tres trabajadores y comprobé que el resultado fuera correcto. El tiempo promedio bajó de 36.17 a 20.57 segundos: una reducción de 43.12 %.

## Ensayo antes del viernes

1. Lee el guion una vez mientras avanzas las diapositivas. 2. Explica cada diapositiva con tus propias palabras. 3. Ensaya con cronómetro e incluye el cambio a la terminal. 4. Abre el PowerPoint y el PDF en el equipo que usarás para exponer. 5. Ejecuta una prueba de la demo antes de clase y conserva sus evidencias.

Los datos y capturas provienen de tu proyecto. Los promedios corresponden únicamente a las seis mediciones finales. La demo adicional no cambia esos resultados.


---

# Guion | diapositivas 1 a 3

## 01. Hadoop en Docker | 20 s

Buenos días. Soy Martín Eduardo Chacón Orduño. En este proyecto configuré Hadoop en Docker y comparé el tiempo de un conteo de palabras con uno y tres trabajadores. Les explicaré cómo funciona el proceso, los resultados que obtuve y al final mostraré una ejecución en vivo.

Recuerda: Presenta el objetivo sin leer los datos de identificación completos.

## 02. El experimento | 35 s

La pregunta fue cuánto cambia el tiempo al aumentar la cantidad de trabajadores. Generé doce archivos, con cuarenta y cinco millones de bytes y un millón ochocientas mil líneas en total. El texto es sintético y repetido. Esto me permite saber de antemano cuántas veces debe aparecer cada palabra y verificar que el programa entregue el resultado correcto.

Recuerda: Señala el número de archivos y el tamaño. MB usa millones de bytes. MiB usa potencias de 1024.

## 03. Cómo cuenta palabras MapReduce | 45 s

Para explicar el proceso usaré la frase Hadoop usa Hadoop. Mi mapper convierte el texto a minúsculas y genera una pareja de palabra y uno por cada aparición. Después Hadoop agrupa y ordena las parejas por palabra. Finalmente, el reducer suma los unos: Hadoop aparece dos veces y usa una vez. Mis programas están escritos en Python y Hadoop Streaming conecta su entrada y salida con el trabajo distribuido.

Recuerda: Recorre la tabla de izquierda a derecha. La agrupación la realiza Hadoop, no el script mapper.


---

# Guion | diapositivas 4 a 6

## 04. Las funciones del clúster | 45 s

Hadoop tiene dos partes que usamos aquí. HDFS se encarga del almacenamiento y YARN de la ejecución. El NameNode conoce la ubicación de los bloques y los DataNode los almacenan. El ResourceManager coordina los recursos y los NodeManager ejecutan tareas. En mi configuración separé los servicios en contenedores. Llamo trabajador a una pareja lógica de DataNode y NodeManager. Todos corren en la misma Mac.

Recuerda: Distingue almacenamiento y ejecución. Los DataNode y NodeManager de una pareja están en contenedores separados. No afirmes que comparten hostname ni que son tres computadoras físicas.

## 05. Configuración en Docker | 35 s

Utilicé Docker Compose y la imagen de Hadoop 3.5.0. Con un trabajador hay cuatro contenedores: dos servicios centrales y una pareja de DataNode y NodeManager. Al activar el perfil tres-nodos, se agregan dos parejas y quedan ocho contenedores. Ocho contenedores no significa ocho trabajadores. La captura muestra la configuración ampliada en ejecución.

Recuerda: Señala los nombres datanode1, 2 y 3, y nodemanager1, 2 y 3.

## 06. Datos distribuidos en HDFS | 35 s

Cuando agregué los trabajadores, los datos seguían en el primer DataNode. Volví a cargar los mismos archivos y revisé su ubicación con fsck. En esta carga quedaron cuatro bloques en cada DataNode, con quince millones de bytes por nodo. Conservé el factor de replicación en uno. Ese valor indica cuántas copias tiene cada bloque, no cuántos trabajadores existen. HDFS reportó el estado HEALTHY.

Recuerda: La distribución 4, 4, 4 corresponde a la carga documentada. Una recarga futura puede repartir los archivos de otra manera.


---

# Guion | diapositivas 7 a 9

## 07. Tres trabajadores disponibles en YARN | 35 s

La consulta yarn node -list mostró tres NodeManager en estado RUNNING. Esto confirma que están registrados y disponibles. Para comprobar que el trabajo utiliza recursos también hay que mirar la actividad mientras se ejecuta. En la demostración mostraré los contenedores de YARN que aparecen durante el procesamiento. Son unidades de ejecución de YARN y no los contenedores de Docker.

Recuerda: No confundas disponible con procesando en ese instante. La demo observará actividad.

## 08. Una comparación con las mismas condiciones | 45 s

Para comparar mantuve los datos, los dos programas y los parámetros de Hadoop. Cada trabajo lanzó doce tareas Map y una tarea Reduce. Después de verificar el resultado hice tres ejecuciones medidas por configuración. Usé el valor real de /usr/bin/time, que mide el tiempo transcurrido del comando e incluye envío, espera y ejecución. No incluí la generación ni la carga de los datos. Cada trabajador mantuvo la misma memoria anunciada a YARN, así que al agregar trabajadores aumentaron los recursos lógicos disponibles.

Recuerda: Las mediciones finales con uno son 1node-series2. Las anteriores no entraron al promedio. No uses CPU time spent como tiempo real.

## 09. El tiempo promedio bajó 43.12 % | 50 s

Con un trabajador obtuve 34.47, 37.53 y 36.50 segundos. El promedio fue de 36.17. Con tres trabajadores los tiempos fueron 18.45, 21.41 y 21.85 segundos, con un promedio de 20.57. La diferencia es de aproximadamente 15.60 segundos por trabajo. Para obtener la reducción dividí la diferencia entre el promedio original y multipliqué por cien. Usando los promedios sin redondear, la reducción fue de 43.12 por ciento.

Recuerda: Señala primero los promedios y luego la gráfica. Aclara que el eje empieza en cero. No es tres veces más rápido.


---

# Guion | diapositivas 10 a 12

## 10. El resultado del conteo se mantuvo | 40 s

Antes de medir comprobé que el conteo fuera correcto con ambas configuraciones. El bloque de texto se repite seiscientas mil veces. Hadoop aparece dos veces por bloque, por eso suma un millón doscientas mil apariciones. Cada una de las otras siete palabras suma seiscientas mil. La mejora de tiempo corresponde a esta prueba. Todos los contenedores comparten mi Mac, mantuve un reducer y el trabajo también necesita coordinación. No puedo generalizar este porcentaje a cualquier equipo o conjunto de datos.

Recuerda: Señala el resultado de la comprobación con tres trabajadores. La corrección del resultado y la velocidad son aspectos distintos.

## 11. Demostración en vivo | 180 s

Ahora mostraré el clúster. Primero verifico que los tres trabajadores estén disponibles y que existan los doce archivos. Después envío un trabajo con un nombre de salida nuevo. Mientras corre, observamos la actividad que reporta YARN. Al terminar, verifico que Hadoop haya marcado éxito y que el conteo siga siendo el esperado. Esta es una demostración adicional y no modifica los promedios del reporte.

Recuerda: Cambia a la terminal. Ejecuta python3 demo_hadoop.py check y python3 demo_hadoop.py run desde la carpeta entregada. Consulta la guía para preparación y recuperación.

## 12. Conclusión | 25 s

En conclusión, logré configurar Hadoop con uno y tres trabajadores, comprobar el almacenamiento y ejecutar MapReduce correctamente. En estas condiciones, pasar a tres trabajadores redujo el tiempo promedio de 36.17 a 20.57 segundos, una reducción del 43.12 por ciento. El resultado del conteo se mantuvo correcto. Gracias.

Recuerda: Cierra con el resultado y deja espacio para preguntas.


---

# Preparación de la demo

Haz esta preparación antes de entrar a clase. El script demo_hadoop.py incluido usa Python 3 y no necesita instalar librerías adicionales. Lanza tu trabajo original y consulta YARN para mostrar actividad.

## 1. Inicia Docker Desktop y levanta el clúster

Abre una terminal dentro de tu carpeta docker-hadoop. Puedes entrar con estos comandos:

```bash
cd /Users/martinchacon/Documents/semestre-2026-b/big-data
cd actividades/2.22-proyecto-1/docker-hadoop
docker compose --profile tres-nodos up -d
```

Espera a que los servicios se registren. No uses docker compose down ni borres contenedores: en tu configuración los datos HDFS están dentro de ellos.

## 2. Comprueba la configuración

```bash
docker compose exec -T namenode hdfs dfsadmin -report
docker compose exec -T resourcemanager yarn node -list
docker compose exec -T namenode \
  hdfs dfs -count -v /user/hadoop/input
```

Debes ver 3 DataNode activos, 3 NodeManager RUNNING y 12 archivos con 45 000 000 bytes. Que estén RUNNING significa que están disponibles; todavía no demuestra que recibieron tareas.

## 3. Deja listas las ventanas

Abre la presentación y una terminal en la carpeta entregada que contiene demo_hadoop.py. En otra pestaña del navegador abre http://localhost:8088/cluster/nodes para mostrar YARN. Si quieres mostrar HDFS, abre http://localhost:9870.

```bash
python3 demo_hadoop.py check
```

El script ya contiene la ruta actual de tu proyecto. Si cambias la carpeta, usa la opción --project seguida de la nueva ruta a docker-hadoop. El comando check solo consulta el estado.


---

# Demo en vivo | 3 minutos

## 00:00 a 00:35 | Mostrar los trabajadores

```bash
python3 demo_hadoop.py check
```

Di: “HDFS tiene tres DataNode activos y YARN reconoce tres NodeManager. También verifico que siguen presentes los doce archivos de entrada.”

## 00:35 a 01:00 | Enviar el trabajo

```bash
python3 demo_hadoop.py run
```

Di: “Ahora envío el conteo de palabras. Uso los mismos programas y datos, y una carpeta de salida nueva para conservar los resultados anteriores.”

## 01:00 a 02:15 | Observar la ejecución

El script imprime ACTIVIDAD con el número de contenedores YARN activos por NodeManager. También muestra el avance Map y Reduce. Puedes actualizar la página de YARN mientras corre el trabajo.

Di: “Estos números corresponden a unidades de ejecución de YARN; incluyen tareas y el coordinador del trabajo. No son los ocho contenedores de Docker. El planificador decide dónde ejecutar cada unidad.”

Las tareas pueden terminar rápido. Al finalizar, el script consulta los registros de cada NodeManager y busca contenedores de esta aplicación. Solo afirma que participaron los tres si la evidencia lo confirma.

## 02:15 a 03:00 | Comprobar el resultado y volver

Muestra RESULTADO CORRECTO: hadoop debe tener 1 200 000; las otras siete palabras, 600 000 cada una. El script también comprueba el archivo _SUCCESS y guarda las evidencias en una nueva subcarpeta de evidence.

Di: “El conteo coincide con lo esperado. Esta ejecución es una demostración adicional. Los promedios de la presentación vienen de las tres mediciones originales por configuración.”

Vuelve a la diapositiva 12 y lee el cierre. Si la demo tarda más de lo previsto, explica que los tiempos varían y utiliza las capturas documentadas para concluir.


---

# Comandos del trabajo

Esta es la alternativa manual y también permite explicar qué hace el script. Ejecútala desde docker-hadoop. La salida usa un nombre nuevo; no reutilices uno de las mediciones.

```bash
demo_id="demo-3nodes-$(date +%Y%m%d-%H%M%S)"
docker compose exec -T namenode hadoop jar \
  /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.5.0.jar \
  -D mapreduce.job.name="$demo_id" \
  -D mapreduce.job.reduces=1 \
  -D mapreduce.job.reduce.slowstart.completedmaps=1.0 \
  -D mapreduce.map.speculative=false \
  -D mapreduce.reduce.speculative=false \
  -files /workspace/mapper.py,/workspace/reducer.py \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input /user/hadoop/input \
  -output "/user/hadoop/output/$demo_id"
```

## Mientras corre: observa YARN en otra terminal

```bash
docker compose exec -T resourcemanager yarn node -list
```

Repite la consulta durante el trabajo y observa Number-of-Running-Containers por nodo. Un cero en una consulta aislada no demuestra que ese trabajador nunca participó. El script automático conserva muestras y registros para revisar el trabajo completo.

## Al terminar: consulta la salida

```bash
docker compose exec -T namenode \
  hdfs dfs -cat "/user/hadoop/output/$demo_id/part-00000"
```

Ejecuta esta consulta en la misma terminal donde definiste demo_id. La demostración manual no mide los tiempos de la comparación ni modifica los registros originales.


---

# Si algo falla

## No se conecta a Docker o a YARN

Abre Docker Desktop, espera a que esté listo y vuelve a levantar el perfil tres-nodos. Consulta docker compose --profile tres-nodos ps -a. Repite check cuando los servicios hayan arrancado; si falla, conserva el mensaje para revisarlo antes de clase.

## Faltan los archivos de entrada

Si los contenedores fueron recreados, vuelve a subir los archivos originales. Hazlo antes de exponer, desde docker-hadoop. El volumen de src está disponible como /workspace en namenode.

```bash
docker compose exec -T namenode \
  hdfs dfs -mkdir -p /user/hadoop/input
docker compose exec -T namenode bash -lc \
  'hdfs dfs -put -f /workspace/data/input-*.txt /user/hadoop/input/'
docker compose exec -T namenode \
  hdfs fsck /user/hadoop/input -files -blocks -locations
```

Repite check y exige 12 archivos y 45 000 000 bytes. Una nueva carga puede repartir los bloques de manera distinta; la tabla 4, 4, 4 de las diapositivas describe la carga documentada, no una garantía para cualquier recarga.

## No se observó actividad en los tres trabajadores

No lo presentes como si hubiera ocurrido. Revisa el resumen y los registros que guardó el script. YARN decide la asignación y las tareas son breves. Puedes repetir el ensayo antes de clase; cada ejecución utiliza una salida distinta. Evita cambiar los datos o introducir pausas para aparentar participación.

## Plan de respaldo durante la exposición

Si no puedes resolver el problema en unos 30 segundos, di: “La demostración en vivo tuvo un problema; estas capturas corresponden a la ejecución que sí documenté”. Muestra las diapositivas 7 y 10, explica los resultados y termina con la conclusión. Lleva también el PDF de la presentación.

El script fue revisado sin lanzar nuevos trabajos en tu clúster. Ensáyalo en tu Mac antes del viernes.


---

# Preguntas que podrían hacerte

¿Por qué hay ocho contenedores y tres trabajadores?

Hay dos servicios centrales y seis servicios de trabajo. Cada trabajador es una pareja lógica de DataNode y NodeManager en contenedores separados.

¿Qué diferencia hay entre HDFS y YARN?

HDFS almacena los archivos distribuidos. YARN administra los recursos con los que se ejecutan las tareas.

¿El mapper agrupa las palabras?

No. Emite palabra y uno. Hadoop ordena y agrupa las claves; el reducer suma los valores.

¿Por qué Hadoop aparece el doble?

El bloque tiene dos apariciones de Hadoop y una de cada otra palabra. Hay 600 000 repeticiones del bloque entre los doce archivos.

¿Por qué no fue tres veces más rápido?

Todos los contenedores comparten una Mac. Hay coordinación, inicio de tareas, transferencia de datos y un solo reducer. Aumentar trabajadores no elimina esos costos.

¿Cómo calculaste el porcentaje?

Promedio de un trabajador: 108.50/3. Promedio de tres: 61.71/3. La reducción es (promedio original menos promedio nuevo) dividido entre el original, por 100: 43.12 %. La aceleración es aproximadamente 1.76 veces.

¿Replicación uno significa un nodo?

No. Significa una copia de cada bloque. Se mantuvo ese factor con uno y tres trabajadores.

¿45 MB es Big Data?

Es un conjunto pequeño y sintético para una práctica de arquitectura y procesamiento distribuido. Permite validar el procedimiento, pero no representa por sí solo una carga masiva real.

¿Qué mide real?

El tiempo transcurrido del comando, incluido el envío, la espera y la ejecución. No es la suma del tiempo CPU de las tareas.


---

# Tarjeta de repaso

## Cinco ideas para entrar con confianza

1. HDFS almacena; YARN organiza la ejecución.
2. Tres trabajadores lógicos, ocho contenedores y una Mac.
3. Doce archivos, 45 000 000 bytes, 1 800 000 líneas.
4. Doce tareas Map y una Reduce; ocho palabras diferentes.
5. Promedios de 36.17 y 20.57 segundos: reducción de 43.12 %.

## Una frase para cada parte

Inicio: “Comparé el mismo conteo con uno y tres trabajadores”.
Proceso: “El mapper emite, Hadoop agrupa y el reducer suma”.
Validación: “El resultado esperado coincide con el obtenido”.
Resultado: “El promedio disminuyó 15.60 segundos en estas condiciones”.
Límite: “Este porcentaje corresponde a mi prueba en una sola Mac”.

## Archivos de la entrega

Hadoop_MapReduce_presentacion.pptx: presentación editable y notas.
Hadoop_MapReduce_presentacion.pdf: copia para exponer si falla PowerPoint.
Guion_y_demostracion.pdf: este material de estudio.
Guion_y_demostracion.md: texto y comandos para copiar.
demo_hadoop.py: ayuda para verificar y ejecutar la demo.

## Referencias técnicas

La evidencia experimental proviene del reporte, el código, las capturas y los seis registros finales de tu proyecto. Los enlaces técnicos están en las notas de las diapositivas y en la versión de texto de esta guía.


## Enlaces técnicos

- https://docs.docker.com/compose/how-tos/profiles/
- https://hadoop.apache.org/docs/r3.5.0/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html
- https://hadoop.apache.org/docs/r3.5.0/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html#fsck
- https://hadoop.apache.org/docs/r3.5.0/hadoop-streaming/HadoopStreaming.html
- https://hadoop.apache.org/docs/r3.5.0/hadoop-yarn/hadoop-yarn-site/ResourceManagerRest.html