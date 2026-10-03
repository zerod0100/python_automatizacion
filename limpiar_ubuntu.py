#!/usr/bin/env python3
"""Limpieza conservadora de Ubuntu. Ejecutar como root solo con --aplicar."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

APT_CACHE = Path('/var/cache/apt/archives')


def apt_cache_bytes():
    total = 0
    for folder, _, files in os.walk(APT_CACHE, followlinks=False):
        for name in files:
            path = Path(folder) / name
            try:
                if not path.is_symlink() and path.is_file():
                    total += path.stat().st_size
            except OSError:
                pass
    return total


def run(command):
    print('+', ' '.join(command), flush=True)
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise RuntimeError(f'Comando falló ({result.returncode}): {command[0]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true', help='Ejecuta la limpieza; sin esta opción solo muestra una vista previa')
    parser.add_argument('--dias-logs', type=int, default=14, help='Conservar registros de los últimos N días (mínimo 7)')
    args = parser.parse_args()
    if args.dias_logs < 7:
        parser.error('--dias-logs debe ser 7 o más')
    for executable in ('apt-get', 'journalctl'):
        if shutil.which(executable) is None:
            parser.error(f'No se encontró {executable}; este script requiere Ubuntu con APT y systemd')

    print(f'Caché APT actual: {apt_cache_bytes() / 1048576:.1f} MiB (la limpieza real puede liberar menos).')
    print('Acciones: apt-get autoclean; journalctl --vacuum-time=' + str(args.dias_logs) + 'd')
    print('journalctl elimina únicamente archivos de registro archivados; no todos los registros antiguos activos.')
    if not args.aplicar:
        print('Vista previa. Para ejecutar: sudo python3 limpiar_ubuntu.py --aplicar')
        return 0
    if os.geteuid() != 0:
        parser.error('--aplicar requiere permisos de administrador (sudo)')
    try:
        run(['apt-get', 'autoclean'])
        run(['journalctl', f'--vacuum-time={args.dias_logs}d'])
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    print(f'Limpieza terminada. Caché APT restante: {apt_cache_bytes() / 1048576:.1f} MiB.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
