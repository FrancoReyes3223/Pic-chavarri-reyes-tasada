"""
Atajos para instalar, entrenar y levantar el proyecto con un solo comando.
Funciona igual en Windows, Linux y Mac (solo necesita Python y Node).

    python proyecto.py instalar   crea el entorno virtual e instala las dependencias (backend y frontend)
    python proyecto.py entrenar   regenera el dataset y vuelve a entrenar el modelo (opcional)
    python proyecto.py levantar   arranca la API y el frontend juntos; Ctrl+C cierra los dos

Hace lo mismo que los comandos del README, que siguen sirviendo para hacerlo a mano.
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

CARPETA_RAIZ = Path(__file__).resolve().parent
CARPETA_BACKEND = CARPETA_RAIZ / 'backend'
CARPETA_FRONTEND = CARPETA_RAIZ / 'frontend'
CARPETA_ENTORNO = CARPETA_BACKEND / '.venv'

PUERTO_API = 8000
PUERTO_FRONTEND = 5173
PYTHON_MINIMO = (3, 10)
NODE_MINIMO = 20  # react-router-dom 7 no funciona con versiones anteriores

EN_WINDOWS = os.name == 'nt'


# --- Comprobaciones y utilidades ---

def terminar_con_error(mensaje):
    """Muestra el mensaje y corta el programa."""
    print(f'\nERROR: {mensaje}')
    sys.exit(1)


def python_del_entorno():
    """Ruta al Python del entorno virtual (en Windows y en Linux/Mac está en lugares distintos)."""
    if EN_WINDOWS:
        return CARPETA_ENTORNO / 'Scripts' / 'python.exe'
    return CARPETA_ENTORNO / 'bin' / 'python'


def comando_npm():
    """En Windows, npm es un archivo npm.cmd y hay que llamarlo con ese nombre."""
    if EN_WINDOWS:
        return 'npm.cmd'
    return 'npm'


def variables_de_entorno():
    """Variables para los procesos hijos: salida en UTF-8 (los scripts imprimen acentos)
    y matplotlib sin ventanas (los gráficos solo se guardan como imagen)."""
    variables = os.environ.copy()
    variables['PYTHONIOENCODING'] = 'utf-8'
    variables['MPLBACKEND'] = 'Agg'
    return variables


def correr(comando, carpeta):
    """Ejecuta un comando en una carpeta y corta todo si falla."""
    texto_comando = ''
    for parte in comando:
        texto_comando += str(parte) + ' '
    # flush=True: que el mensaje salga antes que la salida del comando.
    print(f'\n> {texto_comando}  (en {carpeta.name}/)', flush=True)
    resultado = subprocess.run(comando, cwd=carpeta, env=variables_de_entorno())
    if resultado.returncode != 0:
        terminar_con_error(f'el comando anterior falló (código {resultado.returncode}).')


def verificar_python():
    if sys.version_info < PYTHON_MINIMO:
        terminar_con_error(f'hace falta Python {PYTHON_MINIMO[0]}.{PYTHON_MINIMO[1]} o más '
                           f'(tenés {sys.version.split()[0]}).')


def verificar_node():
    """Comprueba que Node esté instalado y que sea la versión 20 o más."""
    try:
        resultado = subprocess.run(['node', '--version'], capture_output=True, text=True)
    except FileNotFoundError:
        terminar_con_error(f'no se encontró Node.js. Instalá Node {NODE_MINIMO} o más desde https://nodejs.org')

    version = resultado.stdout.strip()            # por ejemplo "v24.14.1"
    version_mayor = int(version.lstrip('v').split('.')[0])
    if version_mayor < NODE_MINIMO:
        terminar_con_error(f'hace falta Node {NODE_MINIMO} o más (tenés {version}).')


def puerto_ocupado(puerto):
    """True si ya hay algo escuchando en ese puerto de esta computadora."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        return conexion.connect_ex(('127.0.0.1', puerto)) == 0


# --- Comandos ---

def instalar():
    """Crea el entorno virtual del backend, instala sus paquetes e instala los del frontend."""
    verificar_python()
    verificar_node()

    if CARPETA_ENTORNO.exists():
        print('El entorno virtual ya existe en backend/.venv')
    else:
        correr([sys.executable, '-m', 'venv', '.venv'], CARPETA_BACKEND)

    correr([python_del_entorno(), '-m', 'pip', 'install', '-r', 'requirements.txt'], CARPETA_BACKEND)
    correr([comando_npm(), 'install'], CARPETA_FRONTEND)

    print('\nListo. Para levantar el proyecto: python proyecto.py levantar')


def entrenar():
    """Regenera el dataset sintético y vuelve a entrenar y guardar el modelo."""
    verificar_que_esta_instalado()
    correr([python_del_entorno(), 'data/generar_dataset.py'], CARPETA_BACKEND)
    correr([python_del_entorno(), 'entrenamiento.py'], CARPETA_BACKEND)


def verificar_que_esta_instalado():
    if not python_del_entorno().exists():
        terminar_con_error('falta el entorno virtual. Corré primero: python proyecto.py instalar')
    if not (CARPETA_FRONTEND / 'node_modules').exists():
        terminar_con_error('faltan los paquetes del frontend. Corré primero: python proyecto.py instalar')


def arrancar_proceso(comando, carpeta):
    """Arranca un servidor en segundo plano, en su propio grupo de procesos.
    Así el Ctrl+C lo recibe solo este script, que después cierra los servidores en orden."""
    if EN_WINDOWS:
        return subprocess.Popen(comando, cwd=carpeta, env=variables_de_entorno(),
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen(comando, cwd=carpeta, env=variables_de_entorno(), start_new_session=True)


def cerrar_proceso(proceso):
    """Cierra el servidor y todos los procesos que haya abierto (npm, por ejemplo, abre node)."""
    if proceso.poll() is not None:
        return  # ya había terminado
    if EN_WINDOWS:
        # /T cierra también los procesos hijos; /F los fuerza a cerrarse.
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(proceso.pid)], capture_output=True)
    else:
        os.killpg(proceso.pid, signal.SIGTERM)
    proceso.wait()


def levantar():
    """Arranca la API y el frontend; con Ctrl+C se cierran los dos."""
    verificar_que_esta_instalado()
    verificar_node()
    if not (CARPETA_BACKEND / 'app' / 'modelo.pkl').exists():
        terminar_con_error('falta backend/app/modelo.pkl. Corré: python proyecto.py entrenar')

    for puerto in [PUERTO_API, PUERTO_FRONTEND]:
        if puerto_ocupado(puerto):
            terminar_con_error(f'el puerto {puerto} ya está en uso. ¿Quedó el proyecto abierto en otra terminal?')

    api = arrancar_proceso(
        [python_del_entorno(), '-m', 'uvicorn', 'app.main:app', '--port', str(PUERTO_API)],
        CARPETA_BACKEND,
    )
    frontend = arrancar_proceso(
        [comando_npm(), 'run', 'dev', '--', '--port', str(PUERTO_FRONTEND), '--strictPort'],
        CARPETA_FRONTEND,
    )

    print('\nProyecto levantado:')
    print(f'  Aplicación web: http://localhost:{PUERTO_FRONTEND}')
    print(f'  API:            http://localhost:{PUERTO_API}  (documentación en /docs)')
    print('Ctrl+C para cerrar los dos.\n')

    try:
        # Esperamos mientras los dos sigan andando. Si uno se cae, cerramos el otro.
        while api.poll() is None and frontend.poll() is None:
            time.sleep(1)
        if api.poll() is not None:
            print('\nLa API se cerró sola (revisá el error de arriba).')
        else:
            print('\nEl frontend se cerró solo (revisá el error de arriba).')
    except KeyboardInterrupt:
        print('\nCerrando...')
    finally:
        cerrar_proceso(api)
        cerrar_proceso(frontend)
        print('API y frontend cerrados.')


COMANDOS = {
    'instalar': instalar,
    'entrenar': entrenar,
    'levantar': levantar,
}

if __name__ == '__main__':
    # Escribimos en UTF-8 para que los acentos se vean bien también en Git Bash
    # (en Windows, fuera de la consola, Python usaría otra codificación).
    sys.stdout.reconfigure(encoding='utf-8')

    lector = argparse.ArgumentParser(description='Atajos para instalar, entrenar y levantar el proyecto.')
    lector.add_argument('comando', choices=COMANDOS.keys(),
                        help='instalar: dependencias | entrenar: dataset y modelo | levantar: API y frontend')
    argumentos = lector.parse_args()
    COMANDOS[argumentos.comando]()
