# Módulo: logger.py
# Descripción: Configura el registro de eventos y errores en un archivo de logs.

import logging  # Biblioteca estándar de Python para manejo profesional de logs


def configurar_logger(nombre_archivo="registro_software_fj.log"):
    """
    Configura y retorna un logger que guarda todos los eventos y errores
    en un archivo de texto plano sin detener la ejecución del programa.
    """
    # Obtenemos o creamos un logger con el nombre del sistema
    logger = logging.getLogger("SoftwareFJ")
    # Definimos el nivel mínimo de registro (INFO captura eventos normales, advertencias y errores)
    logger.setLevel(logging.INFO)

    # Evitamos duplicar manejadores si la función se llama más de una vez
    if not logger.handlers:
        # Creamos el manejador que escribe en el archivo de logs con codificación UTF-8
        manejador_archivo = logging.FileHandler(nombre_archivo, mode="a", encoding="utf-8")
        # Definimos el formato: Fecha y hora | Nivel | Mensaje
        formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        # Asociamos el formato al manejador de archivo
        manejador_archivo.setFormatter(formato)
        # Registramos el manejador en el logger principal
        logger.addHandler(manejador_archivo)

    # Retornamos el objeto logger listo para usar en los demás módulos
    return logger