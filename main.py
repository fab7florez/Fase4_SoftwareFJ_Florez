# Módulo: main.py
# Descripción: Simula 12 operaciones completas en Software FJ para validar POO y manejo de excepciones.

from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reserva import SistemaSoftwareFJ
from excepciones import ErrorCalculoCosto


def ejecutar_simulacion():
    """Ejecuta la batería de 12 operaciones válidas e inválidas sin interrumpir la aplicación."""
    print("=================================================================")
    print("   SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (FASE 4)           ")
    print("=================================================================\n")

    # Inicializamos el gestor principal del sistema
    sistema = SistemaSoftwareFJ()

    # -----------------------------------------------------------------
    # 1. REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS)
    # -----------------------------------------------------------------
    print("--- OPERACIÓN 1: Registro de cliente válido ---")
    c1 = sistema.registrar_cliente("CLI-001", "Laura Martínez", "laura.martinez@empresa.com", "3104567890")

    print("\n--- OPERACIÓN 2: Registro de cliente válido ---")
    c2 = sistema.registrar_cliente("CLI-002", "Carlos Gómez", "carlos.gomez@correo.co", "3209876543")

    print("\n--- OPERACIÓN 3: Registro de cliente INVÁLIDO (correo mal formado) ---")
    sistema.registrar_cliente("CLI-003", "Pedro Ruiz", "pedro_sin_arroba.com", "3001112233")

    print("\n--- OPERACIÓN 4: Registro de cliente INVÁLIDO (teléfono con letras) ---")
    sistema.registrar_cliente("CLI-004", "Ana Torres", "ana@dominio.com", "300ABC999")

    # -----------------------------------------------------------------
    # 2. CREACIÓN DE SERVICIOS (VÁLIDOS E INVÁLIDOS)
    # -----------------------------------------------------------------
    print("\n--- OPERACIÓN 5: Creación de servicios especializados VÁLIDOS ---")
    sala = sistema.registrar_servicio(ReservaSala, "SRV-S01", "Sala Ejecutiva Norte", 120000, 30, True)
    equipo = sistema.registrar_servicio(AlquilerEquipo, "SRV-E01", "Kit Videoconferencia 4K", 45000, 2, 50000, True)
    asesoria = sistema.registrar_servicio(
        AsesoriaEspecializada, "SRV-A01", "Auditoría de Seguridad", 180000, "Ciberseguridad", "Experto", True
    )
    sala_mantenimiento = sistema.registrar_servicio(ReservaSala, "SRV-S02", "Auditorio Principal", 300000, 100, False)

    print("\n--- OPERACIÓN 6: Creación de servicios INVÁLIDOS (parámetros fuera de rango) ---")
    # Capacidad negativa en sala
    sistema.registrar_servicio(ReservaSala, "SRV-ERR1", "Sala Imposible", 100000, -5, True)
    # Nivel de consultor inexistente
    sistema.registrar_servicio(AsesoriaEspecializada, "SRV-ERR2", "Asesoría Cloud", 150000, "AWS", "MaestroSupremo")

    # -----------------------------------------------------------------
    # 3. PRUEBA DE SOBRECARGA EN CÁLCULO DE COSTOS
    # -----------------------------------------------------------------
    print("\n--- OPERACIÓN 7: Demostración de método sobrecargado calcular_costo() ---")
    try:
        # 1 parámetro: solo duración
        print(f"Sala (2h, sin desc/imp): ${sala.calcular_costo(2):,.2f}")
        # 2 parámetros: duración y descuento
        print(f"Equipo (3h, 10% desc): ${equipo.calcular_costo(3, 10):,.2f}")
        # 3 parámetros: duración, descuento e impuesto
        print(f"Asesoría (4h, 5% desc, 19% IVA): ${asesoria.calcular_costo(4, 5, 19):,.2f}")
        # Diccionario de configuración
        print(f"Sala vía diccionario: ${sala.calcular_costo({'duracion': 3, 'descuento': 15, 'impuesto': 19}):,.2f}")
        # Provocamos error de cálculo (descuento del 90% no permitido)
        sala.calcular_costo(2, 90, 19)
    except ErrorCalculoCosto as e:
        print(f"  [ERROR CONTROLADO EN SOBRECARGA] {e}")

    # -----------------------------------------------------------------
    # 4. RESERVAS EXITOSAS Y FALLIDAS (CON ENCADENAMIENTO Y LOGS)
    # -----------------------------------------------------------------
    print("\n--- OPERACIÓN 8: Reserva exitosa de Sala + Confirmación y Procesamiento ---")
    r1 = sistema.crear_reserva("RES-001", c1, sala, duracion=3, descuento=10, impuesto=19)
    sistema.ejecutar_accion_reserva(r1, "confirmar")
    sistema.ejecutar_accion_reserva(r1, "procesar")

    print("\n--- OPERACIÓN 9: Reserva exitosa de Alquiler de Equipos + Cancelación ---")
    r2 = sistema.crear_reserva("RES-002", c2, equipo, duracion=4, descuento=5, impuesto=19)
    sistema.ejecutar_accion_reserva(r2, "cancelar", "Cambio de fecha del evento")

    print("\n--- OPERACIÓN 10: Reserva FALLIDA (servicio no disponible / en mantenimiento) ---")
    sistema.crear_reserva("RES-003", c1, sala_mantenimiento, duracion=2)

    print("\n--- OPERACIÓN 11: Reserva FALLIDA (encadenamiento por descuento inválido del 80%) ---")
    sistema.crear_reserva("RES-004", c2, asesoria, duracion=2, descuento=80, impuesto=19)

    print("\n--- OPERACIÓN 12: Operación NO PERMITIDA (intentar procesar una reserva CANCELADA) ---")
    sistema.ejecutar_accion_reserva(r2, "procesar")

    # Mostramos el resumen final comprobando que el sistema siguió operando hasta el final
    sistema.mostrar_resumen()
    print("\nRevisa el archivo 'registro_software_fj.log' generado en la carpeta del proyecto.")


if __name__ == "__main__":
    ejecutar_simulacion()