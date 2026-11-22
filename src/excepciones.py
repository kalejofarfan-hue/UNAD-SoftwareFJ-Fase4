"""
Módulo de excepciones personalizadas para el sistema de Software FJ.
Define una jerarquía de errores específicos para garantizar estabilidad y robustez.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base para todos los errores controlados del sistema Software FJ."""
    pass


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato ingresado no cumple el formato o rango esperado."""
    pass


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio para crear o procesar una entidad."""
    pass


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta ejecutar una acción inválida según el estado actual."""
    pass


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta reservar un servicio que no tiene disponibilidad."""
    pass


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un fallo al crear, confirmar, cancelar o procesar una reserva."""
    pass


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce un valor ilógico o fuera de rango."""
    pass
