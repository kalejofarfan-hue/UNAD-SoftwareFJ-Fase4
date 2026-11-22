"""
Módulo de configuración del sistema de registro (logging).
Guarda todos los eventos relevantes y errores en un archivo de texto plano (logs/sistema.log).
"""

import logging
import os


def configurar_logger(ruta_archivo: str = "logs/sistema.log") -> logging.Logger:
    """
    Configura y retorna un logger que escribe tanto en archivo como en consola.
    """
    directorio = os.path.dirname(ruta_archivo)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(ruta_archivo, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formato)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formato)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
