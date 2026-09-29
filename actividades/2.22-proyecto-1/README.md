# Demo manual de Hadoop: tres trabajadores

Esta guía utiliza el comando manual de Hadoop Streaming para ejecutar **tres trabajos consecutivos**, medirlos y guardar sus registros.

## 1. Entrar a la carpeta e iniciar el clúster

Abre Docker Desktop y espera a que esté listo. En la **terminal principal** ejecuta:

```bash
cd /Users/martinchacon/Documents/semestre-2026-b/big-data/actividades/2.22-proyecto-1/docker-hadoop

docker compose --profile tres-nodos up -d
docker compose --profile tres-nodos ps -a
```

```bash
docker compose exec -T namenode \
  hdfs fsck /user/hadoop/input -files -blocks -locations
```

Debes ver ocho contenedores: dos servicios centrales, tres DataNode y tres NodeManager. Son tres trabajadores lógicos en la misma Mac.

**Importante:** permanece en `docker-hadoop` para los siguientes comandos. Ejecutarlos desde `big-data` provoca el error `no configuration file provided: not found`.

## 2. Verificar los tres trabajadores y la entrada

```bash
docker compose exec -T namenode hdfs dfsadmin -report
docker compose exec -T resourcemanager yarn node -list
docker compose exec -T namenode hdfs dfs -count -v /user/hadoop/input
```

Comprueba:

- HDFS: `Live datanodes (3)`.
- YARN: `Total Nodes:3`, con los tres NodeManager en estado `RUNNING`.
- Entrada: 1 directorio, 12 archivos y 45 000 000 bytes.

Para mostrar dónde están almacenados los bloques:

```bash
docker compose exec -T namenode \
  hdfs fsck /user/hadoop/input -files -blocks -locations
```

La entrada debe estar `HEALTHY`. La distribución de cuatro bloques por DataNode corresponde a la carga del reporte; puede cambiar si vuelves a cargar los archivos.

**Qué decir:** “HDFS almacena los datos y YARN administra los recursos. Aquí vemos los tres trabajadores disponibles y los doce archivos de entrada”.

## 3. Preparar la observación en otra terminal

Abre una **segunda terminal** y ejecuta:

```bash
cd /Users/martinchacon/Documents/semestre-2026-b/big-data/actividades/2.22-proyecto-1/docker-hadoop

while true; do
  docker compose exec -T resourcemanager yarn node -list
  sleep 1
done
```

Déjala abierta mientras ejecutas los trabajos del siguiente paso. Observa la columna `Number-of-Running-Containers`. Al terminar la demo, detén esta consulta repetida con **Ctrl+C en la segunda terminal**.

También puedes abrir y actualizar estas páginas:

- YARN: <http://localhost:8088/cluster/nodes>
- HDFS: <http://localhost:9870>

**Qué decir:** “RUNNING indica que un trabajador está disponible. Esta columna muestra los contenedores de YARN activos en cada momento, que incluyen tareas y el coordinador del trabajo”.

Los contenedores de YARN son distintos de los contenedores de Docker. Las tareas pueden ser muy breves: un cero en una consulta no significa que ese trabajador nunca participó. Afirma únicamente la actividad que alcances a observar; el bloque manual no guarda automáticamente estas consultas.

## 4. Ejecutar los tres trabajos y medirlos

Vuelve a la **terminal principal**, dentro de `docker-hadoop`. Pega este bloque completo, desde `bash` hasta el último `BASH`.

Ejecuta los trabajos uno después de otro. No lances otra serie al mismo tiempo, para evitar que compitan por los recursos durante la medición.

```bash
bash <<'BASH'
set -euo pipefail

series_id="demo-3nodes-$(date +%Y%m%d-%H%M%S)-$$"
evidence_dir="../evidence/$series_id"
mkdir -p "$evidence_dir"

for number in 1 2 3; do
  demo_id="${series_id}-run${number}"

  echo
  echo "========== TRABAJO $number DE 3 =========="

  if ! /usr/bin/time -p \
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
      -output "/user/hadoop/output/$demo_id" \
      2>&1 | tee "$evidence_dir/run${number}.log"
  then
    echo "Falló el trabajo $number. Se detuvo la serie."
    exit 1
  fi
done

echo
echo "========== RESUMEN DE LAS TRES EJECUCIONES =========="
grep -H -E 'completed successfully|^real ' "$evidence_dir"/run*.log
echo
echo "Registros guardados en: $evidence_dir"
BASH
```

**Qué decir:** “Enviaré tres trabajos consecutivos con los mismos archivos, doce tareas Map y una tarea Reduce. Cada ejecución usa una salida nueva y conserva su registro y su tiempo”.

Al finalizar debes ver **tres mensajes `completed successfully` y tres valores `real`**. Los registros son `run1.log`, `run2.log` y `run3.log`, dentro de la carpeta que imprime el comando.

- `real`: segundos transcurridos del comando MapReduce, incluido envío, espera y ejecución.
- `user` y `sys`: CPU del cliente local; no representan la CPU total de los trabajadores.

La generación y la carga de datos quedan fuera del tiempo. Si el comando falla y muestra un valor `real`, ese tiempo no cuenta como procesamiento completado.

## 5. Consultar rápidamente los tiempos y el conteo

Este bloque encuentra la serie más reciente que tenga `run1.log`, muestra sus tiempos y consulta las salidas de los tres trabajos en HDFS. Ignora las carpetas de otras demos que no tengan ese registro.

```bash
bash <<'BASH'
set -euo pipefail
shopt -s nullglob

cd /Users/martinchacon/Documents/semestre-2026-b/big-data/actividades/2.22-proyecto-1/docker-hadoop

latest_log=""
for log in ../evidence/demo-3nodes-*/run1.log; do
  if [ -z "$latest_log" ] || [ "$log" -nt "$latest_log" ]; then
    latest_log="$log"
  fi
done

if [ -z "$latest_log" ]; then
  echo "No se encontraron registros de una serie manual."
  exit 1
fi

latest_series=$(dirname "$latest_log")
series_id=$(basename "$latest_series")
echo "Serie consultada: $series_id"
grep -H -E 'completed successfully|^real ' "$latest_series"/run*.log || true

for number in 1 2 3; do
  output_path="/user/hadoop/output/${series_id}-run${number}"
  echo
  echo "========== RESULTADO $number =========="
  if docker compose exec -T namenode hdfs dfs -test -e "$output_path/_SUCCESS"; then
    docker compose exec -T namenode hdfs dfs -cat "$output_path/part-00000"
  else
    echo "No se encontró _SUCCESS para el trabajo $number. Revisa su registro."
  fi
done
BASH
```

Las variables del bloque de ejecución no permanecen en la terminal al terminar; por eso este bloque recupera el nombre de la serie desde los registros.

Compara cada salida con estos valores:

```text
cuenta       600000
datos        600000
docker       600000
ejecuta      600000
hadoop      1200000
mapreduce    600000
palabras     600000
procesa      600000
```

`_SUCCESS` confirma que Hadoop terminó correctamente; la comparación de las ocho palabras comprueba además que el conteo coincide con lo esperado.

**Qué decir al cerrar:** “El conteo se mantiene correcto. Estas ejecuciones son una demostración adicional; los promedios del reporte son 36.17 segundos con un trabajador y 20.57 con tres, una reducción de 43.12 %”.

## Si algo falla

| Situación | Acción |
| --- | --- |
| `no configuration file provided: not found` | Entrar a `docker-hadoop` con el `cd` del paso 1. |
| No conecta a Docker | Abrir Docker Desktop y esperar a que esté listo. |
| Menos de tres nodos disponibles | Levantar el perfil `tres-nodos`, esperar y repetir el paso 2. |
| Faltan los archivos de entrada | Recuperar la entrada antes de presentar; no ejecutar la serie hasta verificar los 12 archivos. |
| La serie se detiene | Revisar el último `runN.log`; no usar su tiempo como resultado exitoso. |
| La consulta muestra menos de tres éxitos | La última serie está incompleta; no presentarla como tres pruebas terminadas. |

Si hay un problema durante la exposición, muestra las capturas de las diapositivas y explica que corresponden a las ejecuciones documentadas.

## Al terminar

Para detener el clúster conservando los contenedores, desde `docker-hadoop`:

```bash
docker compose --profile tres-nodos stop
```

Evita `docker compose down` y borrar los contenedores: en esta configuración HDFS guarda sus datos dentro de ellos. No necesitas detenerlos entre trabajos.
