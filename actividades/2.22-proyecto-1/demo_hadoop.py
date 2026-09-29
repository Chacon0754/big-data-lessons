#!/usr/bin/env python3
"""Demostración adicional. No borra datos ni modifica las mediciones del reporte."""
import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
from pathlib import Path

DEFAULT_PROJECT = Path('/Users/martinchacon/Documents/semestre-2026-b/big-data/actividades/2.22-proyecto-1/docker-hadoop')
EXPECTED = {'cuenta': 600000, 'datos': 600000, 'docker': 600000,
            'ejecuta': 600000, 'hadoop': 1200000, 'mapreduce': 600000,
            'palabras': 600000, 'procesa': 600000}
RM = 'http://localhost:8088/ws/v1/cluster'

def api(route):
    request = urllib.request.Request(RM + route, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=4) as response:
        return json.load(response)

def nodes():
    data = (api('/nodes').get('nodes') or {}).get('node', [])
    if isinstance(data, dict):
        data = [data]
    return sorted(data, key=lambda n: n.get('nodeHostName', n['id']))

def command(project, args, timeout=40):
    result = subprocess.run(['docker', 'compose', *args], cwd=project,
                            text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result.stdout

def check(project):
    if not (project / 'docker-compose.yml').exists():
        raise RuntimeError(f'No se encontró docker-compose.yml en {project}')
    print('VERIFICACIÓN DEL CLÚSTER', flush=True)
    print(command(project, ['--profile', 'tres-nodos', 'ps']), flush=True)
    report = command(project, ['exec', '-T', 'namenode', 'hdfs', 'dfsadmin', '-report'])
    match = re.search(r'Live datanodes \((\d+)\)', report)
    if not match or int(match.group(1)) != 3:
        raise RuntimeError('Se requieren 3 DataNode activos. Revisa el arranque antes de continuar.')
    print('HDFS: 3 DataNode activos')
    count = command(project, ['exec', '-T', 'namenode', 'hdfs', 'dfs', '-count', '/user/hadoop/input']).split()
    if len(count) < 4 or count[:3] != ['1', '12', '45000000']:
        raise RuntimeError(f'La entrada debe contener 12 archivos y 45000000 bytes. Recibido: {count}')
    print('Entrada: 12 archivos, 45 000 000 bytes')
    running = [n for n in nodes() if n.get('state') == 'RUNNING']
    if len(running) != 3:
        raise RuntimeError(f'YARN muestra {len(running)} trabajadores RUNNING; se requieren 3.')
    for node in running:
        print(f"YARN: {node.get('nodeHostName', node['id'])}  RUNNING")
    active = (api('/apps?states=NEW,NEW_SAVING,SUBMITTED,ACCEPTED,RUNNING').get('apps') or {}).get('app', [])
    if active:
        raise RuntimeError('Hay otro trabajo pendiente o en ejecución. Espera a que termine antes de la demo.')
    print('Listo. No hay otros trabajos pendientes o en ejecución.\n', flush=True)

def job_command(name):
    return ['docker', 'compose', 'exec', '-T', 'namenode', 'hadoop', 'jar',
            '/opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.5.0.jar',
            '-D', f'mapreduce.job.name={name}',
            '-D', 'mapreduce.job.reduces=1',
            '-D', 'mapreduce.job.reduce.slowstart.completedmaps=1.0',
            '-D', 'mapreduce.map.speculative=false',
            '-D', 'mapreduce.reduce.speculative=false',
            '-files', '/workspace/mapper.py,/workspace/reducer.py',
            '-mapper', 'python3 mapper.py', '-reducer', 'python3 reducer.py',
            '-input', '/user/hadoop/input', '-output', f'/user/hadoop/output/{name}']

def parse_counts(text):
    result = {}
    for line in text.strip().splitlines():
        key, value = line.split()
        if key in result:
            raise ValueError(f'Palabra duplicada en el resultado: {key}')
        result[key] = int(value)
    return result

def parse_time_line(line):
    match = re.fullmatch(r'(real|user|sys)\s+([0-9]+(?:\.[0-9]+)?)', line.strip())
    return (match.group(1), float(match.group(2))) if match else None

def show_timing(timing):
    print('\nTIEMPOS DEL COMANDO MAPREDUCE (segundos)', flush=True)
    for label in ('real', 'user', 'sys'):
        if label in timing:
            print(f'{label} {timing[label]:.2f}', flush=True)
    print('real = tiempo transcurrido del comando; user/sys = CPU del cliente local.')
    print('No incluye la verificación inicial ni las consultas posteriores de resultados.')

def run(project):
    check(project)
    name = 'demo-3nodes-' + dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:4]
    evidence = project.parent / 'evidence' / name
    evidence.mkdir(parents=True, exist_ok=False)
    print('Trabajo:', name)
    print('Observa también http://localhost:8088/cluster/nodes')
    print('ACTIVIDAD = contenedores YARN activos (tareas o coordinador).', flush=True)
    stop = threading.Event()
    samples, peaks, errors = [], {}, []

    def observe():
        last = None
        while not stop.is_set():
            try:
                snapshot = {}
                for node in nodes():
                    if node.get('state') != 'RUNNING':
                        continue
                    host = node.get('nodeHostName', node['id'].split(':')[0])
                    count = int(node.get('numContainers', 0))
                    snapshot[host] = count
                    peaks[host] = max(peaks.get(host, 0), count)
                samples.append({'time': dt.datetime.now().isoformat(), 'active': snapshot})
                if snapshot != last:
                    print('ACTIVIDAD: ' + ' / '.join(f'{n}: {v}' for n, v in snapshot.items()), flush=True)
                    last = snapshot
            except Exception as exc:
                errors.append(str(exc))
            stop.wait(0.35)

    monitor = threading.Thread(target=observe, daemon=True)
    monitor.start()
    start = time.perf_counter()
    app_id = None
    timing = {}
    try:
        with (evidence / 'job.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(['/usr/bin/time', '-p', *job_command(name)],
                                       cwd=project, text=True, env={**os.environ, 'LC_ALL': 'C'},
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
            for line in process.stdout:
                log.write(line)
                measured = parse_time_line(line)
                if measured:
                    timing[measured[0]] = measured[1]
                match = re.search(r'application_\d+_\d+', line)
                if match:
                    app_id = match.group(0)
                if re.search(r'Submitted application|map \d+% reduce|completed successfully|ERROR|FAILED', line):
                    print(line.rstrip(), flush=True)
            code = process.wait()
    finally:
        elapsed = time.perf_counter() - start
        stop.set()
        monitor.join(timeout=5)
        (evidence / 'activity.json').write_text(json.dumps({'samples': samples, 'peaks': peaks, 'monitor_errors': errors}, indent=2), encoding='utf-8')
    # Preserve and display times before result validation, even if the job failed.
    timing['command_exit_code'] = code
    timing['observer_elapsed_seconds'] = elapsed
    (evidence / 'timing.json').write_text(json.dumps(timing, indent=2), encoding='utf-8')
    (evidence / 'timing.txt').write_text(''.join(f'{key} {timing[key]:.2f}\n' for key in ('real', 'user', 'sys') if key in timing), encoding='utf-8')
    show_timing(timing)
    print('Tiempos guardados en:', evidence / 'timing.txt', flush=True)
    if 'real' not in timing:
        print(f'No se recibió real de /usr/bin/time. Duración observada por Python: {elapsed:.2f} s.')
    if code:
        raise RuntimeError(f'El trabajo falló. Revisa {evidence / "job.log"}. No uses su tiempo como resultado válido.')
    command(project, ['exec', '-T', 'namenode', 'hdfs', 'dfs', '-test', '-e', f'/user/hadoop/output/{name}/_SUCCESS'])
    result = command(project, ['exec', '-T', 'namenode', 'hdfs', 'dfs', '-cat', f'/user/hadoop/output/{name}/part-00000'])
    if parse_counts(result) != EXPECTED:
        raise RuntimeError('El trabajo terminó, pero el conteo no coincide con los valores esperados.')
    (evidence / 'result.txt').write_text(result, encoding='utf-8')
    print('\nRESULTADO CORRECTO\n' + result)
    print('\nMáximo de contenedores YARN activos observado por trabajador:')
    for host, peak in sorted(peaks.items()):
        print(f'  {host}: {peak}')

    # Corroborate the specific application in each NodeManager's logs.
    started_by_node = {}
    if app_id:
        epoch, sequence = app_id.split('_')[1:]
        container_pattern = re.compile(r'container_(?:e\d+_)?' + re.escape(epoch + '_' + sequence) + r'_\d+_\d+')
        for service in ['nodemanager1', 'nodemanager2', 'nodemanager3']:
            try:
                logs = command(project, ['--profile', 'tres-nodos', 'logs', '--no-color', service])
                lines = [line for line in logs.splitlines() if container_pattern.search(line)]
                started = {cid for line in lines if re.search(r'RUNNING|Launching container|Container launched', line, re.I)
                           for cid in container_pattern.findall(line)}
                started_by_node[service] = sorted(started)
                (evidence / f'{service}.log').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            except Exception as exc:
                print(f'No se pudo consultar el registro de {service}: {exc}')
        print('\nContenedores del trabajo con arranque reportado por NodeManager (incluye coordinador):')
        for service, ids in started_by_node.items():
            print(f'  {service}: {len(ids)}')
    if len([v for v in started_by_node.values() if v]) == 3:
        print('Los tres NodeManager reportaron ejecución de contenedores de este trabajo.')
    else:
        print('No se obtuvo evidencia de arranque en los tres NodeManager. No afirmes una distribución que no se observó.')
        print('Revisa los registros: YARN decide la asignación; tres nodos disponibles no garantiza el mismo reparto en cada ejecución.')
    summary = {'job': name, 'application': app_id, 'elapsed_seconds': timing.get('real', elapsed), 'timing': timing,
               'result_matches_expected': True, 'node_peaks': peaks, 'started_containers': started_by_node}
    (evidence / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('\nEvidencias:', evidence)
    show_timing(timing)
    print('La demo no reemplaza ninguna medición del reporte.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'run', 'dry-run'])
    parser.add_argument('--project', type=Path, default=DEFAULT_PROJECT, help='Carpeta que contiene docker-compose.yml')
    args = parser.parse_args()
    try:
        if args.action == 'dry-run':
            print('Comando de ejemplo, sin ejecutar Docker:')
            print(shlex.join(['/usr/bin/time', '-p', *job_command('demo-3nodes-EJEMPLO')]))
        elif args.action == 'check':
            check(args.project)
        else:
            run(args.project)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'\nATENCIÓN: {exc}', file=sys.stderr)
        return 1
    except Exception as exc:
        print(f'\nNo se completó la demo: {exc}', file=sys.stderr)
        print('Comprueba Docker Desktop y los servicios del clúster. Consulta la guía.', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
