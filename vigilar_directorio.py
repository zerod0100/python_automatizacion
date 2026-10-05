#instalar watchdog con pip

import logging
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# Cambia esta ruta por el directorio que quieres vigilar.
DIRECTORIO = Path.home() / "Documentos" / "entrada"

# El registro queda fuera del directorio vigilado.
ARCHIVO_LOG = Path.home() / "eventos_directorio.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(ARCHIVO_LOG, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


class DetectarCreaciones(FileSystemEventHandler):
    def on_created(self, event):
        tipo = "Carpeta" if event.is_directory else "Archivo"

        logging.info("%s creada: %s", tipo, event.src_path)

        # Aquí puedes agregar tu automatización:
        # enviar una notificación, generar un respaldo, etc.


def main():
    DIRECTORIO.mkdir(parents=True, exist_ok=True)

    observador = Observer()
    observador.schedule(
        DetectarCreaciones(),
        str(DIRECTORIO),
        recursive=True
    )
    observador.start()

    print(f"Vigilando: {DIRECTORIO}")
    print("Presiona Ctrl+C para detener.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")
    finally:
        observador.stop()
        observador.join()


if __name__ == "__main__":
    main()