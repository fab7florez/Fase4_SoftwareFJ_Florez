# Módulo: excepciones.py
# Descripción: Define las excepciones personalizadas para el sistema de Software FJ.

class ErrorSoftwareFJ(Exception):
    # Excepción base de la que heredan todos los errores propios del sistema.
    pass


class ErrorValidacionCliente(ErrorSoftwareFJ):
    # Se lanza cuando los datos personales de un cliente son inválidos o están incompletos.
    pass


class ErrorParametroInvalido(ErrorSoftwareFJ):
    # Se lanza cuando un servicio o reserva recibe parámetros fuera de rango o de tipo incorrecto.
    pass


class ErrorServicioNoDisponible(ErrorSoftwareFJ):
    # Se lanza cuando se intenta reservar un servicio que no está disponible o activo.
    pass


class ErrorReserva(ErrorSoftwareFJ):
    # Se lanza cuando ocurre un fallo al crear, confirmar, cancelar o procesar una reserva.
    pass


class ErrorCalculoCosto(ErrorSoftwareFJ):
    # Se lanza cuando se detecta una inconsistencia matemática o de reglas al calcular un costo.
    pass