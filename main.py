"""
Archivo principal de ejecución y simulación - Software FJ.
Universidad Nacional Abierta y a Distancia (UNAD) - Programación 213023 - Fase 4.
Estudiante: Kevin Alejandro Farfán Fernández.
Ejecuta 12 operaciones completas (válidas y fallidas) demostrando estabilidad,
manejo avanzado de excepciones y registro en archivo de logs sin base de datos.
"""

from src.logger import configurar_logger
from src.modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from src.reservas import GestorSoftwareFJ
from src.excepciones import ErrorSoftwareFJ


def ejecutar_simulacion():
    logger = configurar_logger("logs/sistema.log")
    gestor = GestorSoftwareFJ(logger)

    logger.info("=== INICIO DE SIMULACIÓN: SISTEMA INTEGRAL SOFTWARE FJ ===")

    # OPERACIÓN 1: Registro válido de Cliente 1
    logger.info("--- Operación 1: Registro válido de Cliente 1 ---")
    cliente_1 = None
    try:
        cliente_1 = Cliente("CLI-001", "Laura Martínez", "1023456789", "laura.martinez@empresa.com", "3104567890")
        gestor.registrar_cliente(cliente_1)
    except ErrorSoftwareFJ as e:
        logger.error(f"Fallo en Operación 1: {e}")

    # OPERACIÓN 2: Registro válido de Cliente 2
    logger.info("--- Operación 2: Registro válido de Cliente 2 ---")
    cliente_2 = None
    try:
        cliente_2 = Cliente("CLI-002", "Carlos Gómez", "1098765432", "carlos.gomez@tech.co", "3209876543")
        gestor.registrar_cliente(cliente_2)
    except ErrorSoftwareFJ as e:
        logger.error(f"Fallo en Operación 2: {e}")

    # OPERACIÓN 3: Registro INVÁLIDO de Cliente (correo mal formado)
    logger.info("--- Operación 3: Registro inválido de Cliente (correo incorrecto) ---")
    try:
        cliente_invalido = Cliente("CLI-003", "Andrés Ruiz", "1045678901", "correo_sin_arroba.com", "3112223344")
        gestor.registrar_cliente(cliente_invalido)
    except ErrorSoftwareFJ as e:
        logger.error(f"Excepción controlada en Operación 3 ({type(e).__name__}): {e}")
    finally:
        logger.debug("Operación 3 verificada: el sistema continúa en ejecución.")

    # OPERACIÓN 4: Registro INVÁLIDO de Cliente (documento duplicado)
    logger.info("--- Operación 4: Registro inválido de Cliente (documento duplicado) ---")
    try:
        cliente_duplicado = Cliente("CLI-004", "Laura Clon", "1023456789", "clon@empresa.com", "3001112233")
        gestor.registrar_cliente(cliente_duplicado)
    except ErrorSoftwareFJ as e:
        logger.error(f"Excepción controlada en Operación 4 ({type(e).__name__}): {e}")

    # OPERACIÓN 5: Creación válida de 3 servicios especializados (Polimorfismo)
    logger.info("--- Operación 5: Creación válida de servicios especializados ---")
    sala_juntas = None
    equipo_proyector = None
    asesoria_arquitectura = None
    try:
        sala_juntas = ReservaSala("SRV-001", "Sala Innovación A", 80000, capacidad=25)
        equipo_proyector = AlquilerEquipo("SRV-002", "Proyector 4K Epson", 45000, deposito_seguridad=50000)
        asesoria_arquitectura = AsesoriaEspecializada("SRV-003", "Consultoría Cloud", 150000, especialidad="Arquitectura AWS")

        gestor.registrar_servicio(sala_juntas)
        gestor.registrar_servicio(equipo_proyector)
        gestor.registrar_servicio(asesoria_arquitectura)
    except ErrorSoftwareFJ as e:
        logger.error(f"Fallo en Operación 5: {e}")

    # OPERACIÓN 6: Creación INVÁLIDA de Servicio (tarifa negativa)
    logger.info("--- Operación 6: Creación inválida de Servicio (tarifa negativa) ---")
    try:
        servicio_malo = AlquilerEquipo("SRV-004", "Portátil Gamer", -30000, deposito_seguridad=20000)
        gestor.registrar_servicio(servicio_malo)
    except ErrorSoftwareFJ as e:
        logger.error(f"Excepción controlada en Operación 6 ({type(e).__name__}): {e}")

    # OPERACIÓN 7: Creación INVÁLIDA de Servicio (parámetro faltante)
    logger.info("--- Operación 7: Creación inválida de Servicio (especialidad vacía) ---")
    try:
        asesoria_mala = AsesoriaEspecializada("SRV-005", "Asesoría General", 100000, especialidad="   ")
        gestor.registrar_servicio(asesoria_mala)
    except ErrorSoftwareFJ as e:
        logger.error(f"Excepción controlada en Operación 7 ({type(e).__name__}): {e}")

    # OPERACIÓN 8: Reserva EXITOSA de Sala (con descuento 10% e IVA)
    logger.info("--- Operación 8: Reserva exitosa de Sala (con descuento e IVA) ---")
    reserva_1 = gestor.crear_y_confirmar_reserva(
        "RES-001", cliente_1, sala_juntas, duracion_horas=4, descuento=0.10, aplicar_iva=True
    )

    # OPERACIÓN 9: Reserva FALLIDA (intento de reservar la misma sala ya ocupada)
    logger.info("--- Operación 9: Reserva fallida (servicio no disponible) ---")
    gestor.crear_y_confirmar_reserva(
        "RES-002", cliente_2, sala_juntas, duracion_horas=2
    )

    # OPERACIÓN 10: Reserva FALLIDA con encadenamiento (descuento inconsistente 80%)
    logger.info("--- Operación 10: Reserva fallida con encadenamiento (descuento > 50%) ---")
    gestor.crear_y_confirmar_reserva(
        "RES-003", cliente_2, equipo_proyector, duracion_horas=5, descuento=0.80
    )

    # OPERACIÓN 11: Reserva EXITOSA de Asesoría (sin IVA - sobrecarga de parámetros)
    logger.info("--- Operación 11: Reserva exitosa de Asesoría (sin IVA) ---")
    gestor.crear_y_confirmar_reserva(
        "RES-004", cliente_2, asesoria_arquitectura, duracion_horas=3, descuento=0.0, aplicar_iva=False
    )

    # OPERACIÓN 12: Cancelación exitosa y posterior intento de doble cancelación
    logger.info("--- Operación 12: Cancelación de reserva y control de doble cancelación ---")
    if reserva_1:
        gestor.cancelar_reserva(reserva_1)   # Exitosa -> libera la sala
        gestor.cancelar_reserva(reserva_1)   # Fallida -> OperacionNoPermitidaError controlada

    logger.info(f"=== FIN DE SIMULACIÓN | {gestor.resumen_estado()} ===")


if __name__ == "__main__":
    ejecutar_simulacion()
