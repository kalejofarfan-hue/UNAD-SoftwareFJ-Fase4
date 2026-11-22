"""
Módulo de modelos orientados a objetos para Software FJ.
Implementa abstracción, encapsulación, herencia, polimorfismo y sobrecarga lógica de métodos.
"""

from abc import ABC, abstractmethod
import re
from src.excepciones import (
    DatoInvalidoError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)


class EntidadBase(ABC):
    """
    Clase abstracta base que representa cualquier entidad general del sistema.
    Obliga a las clases hijas a implementar un identificador y una descripción.
    """

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio y debe ser texto no vacío.")
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._id_entidad

    @abstractmethod
    def describir(self) -> str:
        """Método abstracto que describe la entidad."""
        pass


class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ con encapsulación de datos personales
    y validaciones estrictas mediante propiedades y setters.
    """

    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 6:
            raise DatoInvalidoError("El documento debe contener únicamente dígitos (mínimo 6).")
        self.__documento = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not valor or not isinstance(valor, str) or not re.match(patron_correo, valor.strip()):
            raise DatoInvalidoError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self.__correo = valor.strip()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 7:
            raise DatoInvalidoError("El teléfono debe contener solo números y al menos 7 dígitos.")
        self.__telefono = valor.strip()

    def describir(self) -> str:
        return f"Cliente [{self.id_entidad}] {self.nombre} | Doc: {self.documento} | Correo: {self.correo}"


class Servicio(EntidadBase, ABC):
    """
    Clase abstracta base para los servicios ofrecidos por Software FJ.
    Define la interfaz común que será sobrescrita mediante polimorfismo.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre or not isinstance(nombre, str) or not nombre.strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise DatoInvalidoError("La tarifa por hora debe ser un número positivo mayor que cero.")

        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion_horas: float) -> None:
        """Valida los parámetros específicos del servicio antes de calcular costos."""
        pass

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        """
        Calcula el costo total del servicio.
        Implementa sobrecarga mediante parámetros opcionales (descuento e IVA).
        """
        pass

    def _aplicar_ajustes(self, subtotal: float, descuento: float, aplicar_iva: bool) -> float:
        """Método auxiliar protegido para validar y aplicar descuentos e IVA (19%)."""
        if not isinstance(descuento, (int, float)) or not (0 <= descuento <= 0.5):
            raise CalculoInconsistenteError(
                f"Descuento inválido ({descuento}). Debe estar entre 0.0 (0%) y 0.5 (50%)."
            )
        if subtotal <= 0:
            raise CalculoInconsistenteError("El subtotal calculado no puede ser menor o igual a cero.")

        total_con_descuento = subtotal * (1 - descuento)
        total_final = total_con_descuento * 1.19 if aplicar_iva else total_con_descuento
        return round(total_final, 2)


class ReservaSala(Servicio):
    """Servicio especializado: Reserva de salas de reuniones o capacitación."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self._capacidad = capacidad

    def validar_parametros(self, duracion_horas: float) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 1 or duracion_horas > 12:
            raise DatoInvalidoError("La reserva de sala debe tener una duración entre 1 y 12 horas.")

    def calcular_costo(self, duracion_horas: float, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion_horas)
        recargo = 1.10 if self._capacidad > 20 else 1.0
        subtotal = self._tarifa_hora * duracion_horas * recargo
        return self._aplicar_ajustes(subtotal, descuento, aplicar_iva)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"ReservaSala [{self.id_entidad}] {self._nombre} | "
            f"Capacidad: {self._capacidad} personas | Tarifa: ${self._tarifa_hora:,.0f}/h | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de equipos tecnológicos (portátiles, proyectores, cámaras)."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, deposito_seguridad: float, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if not isinstance(deposito_seguridad, (int, float)) or deposito_seguridad < 0:
            raise DatoInvalidoError("El depósito de seguridad no puede ser negativo.")
        self._deposito_seguridad = float(deposito_seguridad)

    def validar_parametros(self, duracion_horas: float) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 1 or duracion_horas > 72:
            raise DatoInvalidoError("El alquiler de equipos debe ser entre 1 y 72 horas.")

    def calcular_costo(self, duracion_horas: float, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion_horas)
        subtotal = (self._tarifa_hora * duracion_horas) + self._deposito_seguridad
        return self._aplicar_ajustes(subtotal, descuento, aplicar_iva)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"AlquilerEquipo [{self.id_entidad}] {self._nombre} | "
            f"Depósito: ${self._deposito_seguridad:,.0f} | Tarifa: ${self._tarifa_hora:,.0f}/h | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Consultoría y asesoría técnica por expertos."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, especialidad: str, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if not especialidad or not isinstance(especialidad, str) or not especialidad.strip():
            raise ParametroFaltanteError("Debe especificar el área de especialidad de la asesoría.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, duracion_horas: float) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 0.5 or duracion_horas > 8:
            raise DatoInvalidoError("La asesoría especializada debe durar entre 0.5 y 8 horas.")

    def calcular_costo(self, duracion_horas: float, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        self.validar_parametros(duracion_horas)
        subtotal = self._tarifa_hora * duracion_horas
        return self._aplicar_ajustes(subtotal, descuento, aplicar_iva)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"AsesoriaEspecializada [{self.id_entidad}] {self._nombre} | "
            f"Área: {self._especialidad} | Tarifa: ${self._tarifa_hora:,.0f}/h | {estado}"
        )
