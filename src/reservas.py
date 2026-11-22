"""
Módulo de gestión de reservas y administración en memoria de Software FJ.
Implementa manejo avanzado de excepciones: try/except, try/except/else,
try/except/finally y encadenamiento de excepciones (raise ... from e).
"""

import logging
from typing import List, Optional
from src.modelos import EntidadBase, Cliente, Servicio
from src.excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    CalculoInconsistenteError,
)


class Reserva(EntidadBase):
    """
    Integra un Cliente, un Servicio, la duración en horas y el estado de la reserva.
    Controla confirmación, cancelación y procesamiento con manejo robusto de errores.
    """

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_horas: float):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Servicio.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = "PENDIENTE"
        self._costo_total: Optional[float] = None

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> Optional[float]:
        return self._costo_total

    def procesar(self, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        """
        Valida disponibilidad, calcula el costo y prepara la reserva.
        Demuestra encadenamiento de excepciones (raise ... from e).
        """
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' no se encuentra disponible actualmente."
            )

        try:
            costo = self._servicio.calcular_costo(
                self._duracion_horas,
                descuento=descuento,
                aplicar_iva=aplicar_iva,
            )
        except (DatoInvalidoError, CalculoInconsistenteError) as error_origen:
            raise ReservaInvalidaError(
                f"No fue posible procesar la reserva {self.id_entidad}: fallo en validación o cálculo."
            ) from error_origen
        else:
            self._costo_total = costo
            return self._costo_total

    def confirmar(self) -> None:
        """Confirma la reserva y bloquea la disponibilidad del servicio."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(f"La reserva {self.id_entidad} ya fue cancelada y no puede confirmarse.")
        if self._estado == "CONFIRMADA":
            raise OperacionNoPermitidaError(f"La reserva {self.id_entidad} ya se encuentra confirmada.")
        if self._costo_total is None:
            raise OperacionNoPermitidaError(f"Debe procesar el costo de la reserva {self.id_entidad} antes de confirmar.")

        self._estado = "CONFIRMADA"
        self._servicio.disponible = False

    def cancelar(self) -> None:
        """Cancela la reserva y libera el servicio si estaba bloqueado."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(f"La reserva {self.id_entidad} ya estaba cancelada.")

        if self._estado == "CONFIRMADA":
            self._servicio.disponible = True
        self._estado = "CANCELADA"

    def describir(self) -> str:
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total is not None else "Sin calcular"
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self._estado} | "
            f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion_horas}h | Total: {costo_str}"
        )


class GestorSoftwareFJ:
    """
    Controlador principal del sistema en memoria (sin bases de datos).
    Almacena clientes, servicios y reservas en listas internas y registra todo en el log.
    """

    def __init__(self, logger: logging.Logger):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._logger = logger

    def registrar_cliente(self, cliente: Cliente) -> None:
        """Agrega un cliente validando que no exista documento duplicado."""
        for existente in self._clientes:
            if existente.documento == cliente.documento:
                raise OperacionNoPermitidaError(
                    f"Ya existe un cliente registrado con el documento {cliente.documento}."
                )
        self._clientes.append(cliente)
        self._logger.info(f"Cliente registrado exitosamente -> {cliente.describir()}")

    def registrar_servicio(self, servicio: Servicio) -> None:
        """Agrega un servicio al catálogo interno."""
        for existente in self._servicios:
            if existente.id_entidad == servicio.id_entidad:
                raise OperacionNoPermitidaError(
                    f"Ya existe un servicio con el ID {servicio.id_entidad}."
                )
        self._servicios.append(servicio)
        self._logger.info(f"Servicio registrado exitosamente -> {servicio.describir()}")

    def crear_y_confirmar_reserva(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        descuento: float = 0.0,
        aplicar_iva: bool = True,
    ) -> Optional[Reserva]:
        """
        Crea, procesa y confirma una reserva usando try/except/else/finally
        para asegurar que el sistema continúe estable ante cualquier fallo.
        """
        reserva = None
        try:
            reserva = Reserva(id_reserva, cliente, servicio, duracion_horas)
            reserva.procesar(descuento=descuento, aplicar_iva=aplicar_iva)
            reserva.confirmar()
        except Exception as e:
            causa = f" | Causa original: {e.__cause__}" if e.__cause__ else ""
            self._logger.error(f"Error al gestionar reserva [{id_reserva}]: {type(e).__name__} - {e}{causa}")
            return None
        else:
            self._reservas.append(reserva)
            self._logger.info(f"Reserva confirmada exitosamente -> {reserva.describir()}")
            return reserva
        finally:
            self._logger.debug(f"Finalizó intento de transacción para la reserva [{id_reserva}].")

    def cancelar_reserva(self, reserva: Reserva) -> bool:
        """Cancela una reserva existente controlando errores de estado."""
        try:
            reserva.cancelar()
        except OperacionNoPermitidaError as e:
            self._logger.error(f"Error al cancelar reserva [{reserva.id_entidad}]: {e}")
            return False
        else:
            self._logger.info(f"Reserva cancelada exitosamente -> {reserva.describir()}")
            return True
        finally:
            self._logger.debug(f"Auditoría de cancelación completada para [{reserva.id_entidad}].")

    def resumen_estado(self) -> str:
        """Genera un resumen del estado final en memoria."""
        return (
            f"Resumen Software FJ -> Clientes: {len(self._clientes)} | "
            f"Servicios: {len(self._servicios)} | Reservas registradas: {len(self._reservas)}"
        )
