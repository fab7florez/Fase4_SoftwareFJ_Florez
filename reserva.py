# Módulo: reserva.py
# Descripción: Implementa la clase Reserva y el gestor SistemaSoftwareFJ con manejo avanzado de excepciones y logs.

from modelos_base import Entidad, Cliente
from servicios import Servicio
from excepciones import (
    ErrorSoftwareFJ,
    ErrorValidacionCliente,
    ErrorParametroInvalido,
    ErrorServicioNoDisponible,
    ErrorReserva,
    ErrorCalculoCosto,
)
from logger import configurar_logger


class Reserva(Entidad):
    """Integra un cliente, un servicio, una duracion y un estado, controlando su ciclo de vida."""

    # Estados permitidos dentro del flujo de una reserva
    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(self, id_reserva, cliente, servicio, duracion_horas, descuento=0.0, impuesto=19.0):
        # Inicializamos el identificador en la clase padre Entidad
        try:
            super().__init__(id_reserva)
        except ValueError as error_original:
            # Encadenamiento de excepciones: convertimos el ValueError en ErrorReserva
            raise ErrorReserva(f"ID de reserva invalido: '{id_reserva}'.") from error_original

        # Validamos que el objeto cliente sea una instancia real de Cliente
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("La reserva debe estar asociada a un objeto Cliente valido.")

        # Validamos que el objeto servicio herede de la clase abstracta Servicio
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("La reserva debe estar asociada a un objeto Servicio valido.")

        # Validamos que la duración sea un número positivo
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorParametroInvalido(f"La duracion de la reserva debe ser mayor a 0 (recibido: {duracion_horas}).")

        # Atributos encapsulados de la reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._descuento = descuento
        self._impuesto = impuesto
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

        # Validamos la reserva y calculamos su costo inicial
        self.validar()

    @property
    def estado(self):
        """Retorna el estado actual de la reserva."""
        return self._estado

    @property
    def costo_total(self):
        """Retorna el costo total calculado de la reserva."""
        return self._costo_total

    def validar(self):
        """Verifica disponibilidad del servicio y consistencia del calculo de costo."""
        # Comprobamos si el servicio está disponible (puede lanzar ErrorServicioNoDisponible)
        self._servicio.verificar_disponibilidad()
        try:
            # Usamos el método sobrecargado calcular_costo con duración, descuento e impuesto
            self._costo_total = self._servicio.calcular_costo(
                self._duracion_horas, self._descuento, self._impuesto
            )
        except ErrorCalculoCosto as error_original:
            # Encadenamiento de excepciones para conservar la causa raíz del fallo matemático
            raise ErrorReserva(
                f"No se pudo calcular el costo de la reserva '{self._id}'."
            ) from error_original
        return True

    def confirmar(self):
        """Cambia el estado de la reserva a CONFIRMADA si esta PENDIENTE."""
        if self._estado != "PENDIENTE":
            raise ErrorReserva(
                f"Operacion no permitida: no se puede confirmar la reserva '{self._id}' en estado {self._estado}."
            )
        self._estado = "CONFIRMADA"
        return f"Reserva [{self._id}] confirmada exitosamente. Total a pagar: ${self._costo_total:,.2f}"

    def cancelar(self, motivo="Solicitud del cliente"):
        """Cancela la reserva siempre que no haya sido procesada o cancelada previamente."""
        if self._estado == "PROCESADA":
            raise ErrorReserva(f"No se puede cancelar la reserva '{self._id}' porque ya fue PROCESADA.")
        if self._estado == "CANCELADA":
            raise ErrorReserva(f"La reserva '{self._id}' ya se encuentra CANCELADA.")
        self._estado = "CANCELADA"
        return f"Reserva [{self._id}] cancelada. Motivo: {motivo}"

    def procesar(self):
        """Procesa y finaliza una reserva que se encuentre CONFIRMADA."""
        if self._estado != "CONFIRMADA":
            raise ErrorReserva(
                f"No se puede procesar la reserva '{self._id}': debe estar CONFIRMADA (estado actual: {self._estado})."
            )
        self._estado = "PROCESADA"
        return f"Reserva [{self._id}] procesada y facturada por ${self._costo_total:,.2f}."

    def describir(self):
        """Devuelve un resumen completo de la reserva."""
        return (
            f"Reserva [{self._id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion_horas}h | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado}"
        )


class SistemaSoftwareFJ:
    """Gestor central en memoria (sin base de datos) para clientes, servicios y reservas."""

    def __init__(self):
        # Listas internas para almacenar los objetos del sistema en memoria
        self._clientes = []
        self._servicios = []
        self._reservas = []
        # Logger centralizado para registrar eventos y excepciones en archivo
        self._logger = configurar_logger()
        self._logger.info("Sistema Software FJ inicializado correctamente.")

    def registrar_cliente(self, id_cliente, nombre, correo, telefono):
        """Registra un cliente aplicando bloque try / except / else."""
        try:
            # Verificamos que no exista un cliente con el mismo ID
            if any(c.id == id_cliente for c in self._clientes):
                raise ErrorValidacionCliente(f"Ya existe un cliente registrado con el ID '{id_cliente}'.")
            # Creamos la instancia de Cliente (ejecuta validaciones internas)
            cliente = Cliente(id_cliente, nombre, correo, telefono)
        except ErrorValidacionCliente as e:
            # Registramos el error en el archivo de logs y mantenemos el sistema activo
            self._logger.error(f"[CLIENTE FALLIDO] {e}")
            print(f"[ERROR] No se pudo registrar el cliente: {e}")
            return None
        else:
            # Solo se ejecuta si no ocurrió ninguna excepción en el bloque try
            self._clientes.append(cliente)
            self._logger.info(f"[CLIENTE REGISTRADO] {cliente.describir()}")
            print(f"[OK] {cliente.describir()}")
            return cliente

    def registrar_servicio(self, servicio_callable, *args, **kwargs):
        """Instancia y registra cualquier subclase de Servicio usando try / except / else."""
        try:
            # Instanciamos el servicio (ReservaSala, AlquilerEquipo o AsesoriaEspecializada)
            servicio = servicio_callable(*args, **kwargs)
            # Validamos que el ID de servicio no esté duplicado
            if any(s.id == servicio.id for s in self._servicios):
                raise ErrorParametroInvalido(f"Ya existe un servicio con el ID '{servicio.id}'.")
        except (ErrorParametroInvalido, TypeError, ValueError) as e:
            self._logger.error(f"[SERVICIO FALLIDO] {e}")
            print(f"[ERROR] No se pudo crear el servicio: {e}")
            return None
        else:
            self._servicios.append(servicio)
            self._logger.info(f"[SERVICIO REGISTRADO] {servicio.describir()}")
            print(f"[OK] {servicio.describir()}")
            return servicio

    def crear_reserva(self, id_reserva, cliente, servicio, duracion, descuento=0.0, impuesto=19.0):
        """Crea una reserva aplicando try / except / else / finally."""
        reserva = None
        try:
            # Intentamos instanciar la reserva (valida cliente, servicio, disponibilidad y costo)
            reserva = Reserva(id_reserva, cliente, servicio, duracion, descuento, impuesto)
        except (ErrorReserva, ErrorServicioNoDisponible, ErrorParametroInvalido) as e:
            # Si hubo encadenamiento (__cause__), también registramos la causa original en el log
            causa = f" | Causa original: {e.__cause__}" if e.__cause__ else ""
            self._logger.error(f"[RESERVA FALLIDA] {e}{causa}")
            print(f"[ERROR] Fallo al crear reserva '{id_reserva}': {e}{causa}")
        else:
            # Si la creación fue exitosa, se agrega a la lista de reservas
            self._reservas.append(reserva)
            self._logger.info(f"[RESERVA CREADA] {reserva.describir()}")
            print(f"[OK] {reserva.describir()}")
        finally:
            # Bloque finally: siempre se ejecuta para dejar trazabilidad del intento de operación
            self._logger.info(f"[AUDITORIA] Intento de creación de reserva '{id_reserva}' finalizado.")
        return reserva

    def ejecutar_accion_reserva(self, reserva, accion, *args):
        """Ejecuta confirmar, cancelar o procesar sobre una reserva con manejo controlado de errores."""
        try:
            if reserva is None:
                raise ErrorReserva("No se puede ejecutar una accion sobre una reserva inexistente (None).")
            # Obtenemos dinámicamente el método solicitado ('confirmar', 'cancelar' o 'procesar')
            metodo = getattr(reserva, accion)
            mensaje = metodo(*args)
        except (ErrorReserva, AttributeError) as e:
            self._logger.error(f"[ACCION FALLIDA] Accion '{accion}': {e}")
            print(f"[ERROR] {e}")
            return False
        else:
            self._logger.info(f"[ACCION EXITOSA] {mensaje}")
            print(f"[OK] {mensaje}")
            return True
        finally:
            # Garantiza el cierre ordenado del registro de la operación
            self._logger.info(f"[AUDITORIA] Cierre de operacion '{accion}' en reserva.")

    def mostrar_resumen(self):
        """Imprime el estado final del sistema demostrando estabilidad tras todos los errores."""
        print("\n" + "=" * 65)
        print("RESUMEN FINAL DEL SISTEMA - SOFTWARE FJ")
        print("=" * 65)
        print(f"Clientes validos registrados  : {len(self._clientes)}")
        print(f"Servicios validos registrados : {len(self._servicios)}")
        print(f"Reservas validas registradas  : {len(self._reservas)}")
        print("-" * 65)
        for reserva in self._reservas:
            print(" •", reserva.describir())
        print("=" * 65)
        self._logger.info(
            f"Resumen final -> Clientes: {len(self._clientes)}, "
            f"Servicios: {len(self._servicios)}, Reservas: {len(self._reservas)}."
        )