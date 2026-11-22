# Módulo: servicios.py
# Descripción: Define la clase abstracta Servicio y sus tres clases especializadas con polimorfismo y sobrecarga.

from abc import abstractmethod  # Decorador para métodos abstractos
from modelos_base import Entidad  # Clase abstracta base del sistema
from excepciones import (
    ErrorParametroInvalido,
    ErrorServicioNoDisponible,
    ErrorCalculoCosto,
)


class Servicio(Entidad):
    """Clase abstracta que modela cualquier servicio ofrecido por Software FJ."""

    def __init__(self, id_servicio, nombre, tarifa_base, disponible=True):
        # Inicializamos el identificador en la clase padre Entidad
        try:
            super().__init__(id_servicio)
        except ValueError as error_original:
            raise ErrorParametroInvalido(f"ID de servicio inválido: '{id_servicio}'.") from error_original

        # Validamos el nombre del servicio
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorParametroInvalido("El nombre del servicio no puede estar vacío.")

        # Validamos que la tarifa base sea un número positivo mayor a cero
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ErrorParametroInvalido(f"La tarifa base debe ser un número mayor a 0 (recibido: {tarifa_base}).")

        # Validamos que la disponibilidad sea un valor booleano
        if not isinstance(disponible, bool):
            raise ErrorParametroInvalido("El estado de disponibilidad debe ser True o False.")

        # Atributos encapsulados del servicio
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = disponible

    @property
    def nombre(self):
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def tarifa_base(self):
        """Retorna la tarifa base por hora del servicio."""
        return self._tarifa_base

    @property
    def disponible(self):
        """Retorna True si el servicio está disponible para reservar."""
        return self._disponible

    @disponible.setter
    def disponible(self, estado):
        """Actualiza el estado de disponibilidad del servicio."""
        if not isinstance(estado, bool):
            raise ErrorParametroInvalido("La disponibilidad debe ser un valor booleano (True/False).")
        self._disponible = estado

    def verificar_disponibilidad(self):
        """Lanza una excepción si el servicio no se encuentra disponible."""
        if not self._disponible:
            raise ErrorServicioNoDisponible(f"El servicio '{self._nombre}' ({self._id}) no está disponible.")

    @abstractmethod
    def calcular_subtotal(self, duracion_horas):
        """Método polimórfico que cada servicio sobrescribe para calcular su costo base según sus reglas."""
        pass

    def calcular_costo(self, *args, **kwargs):
        """
        Método sobrecargado para calcular el costo final de un servicio.
        Soporta múltiples formas de invocación:
        1. calcular_costo(duracion) -> Costo base sin descuentos ni impuestos.
        2. calcular_costo(duracion, descuento) -> Aplica porcentaje de descuento (0 a 50).
        3. calcular_costo(duracion, descuento, impuesto) -> Aplica descuento e impuesto (ej. IVA 19%).
        4. calcular_costo(config_dict) -> Recibe un diccionario con claves 'duracion', 'descuento', 'impuesto'.
        """
        # Determinamos la firma utilizada según la cantidad y tipo de argumentos
        if len(args) == 1 and isinstance(args[0], dict):
            # Firma 4: Configuración mediante diccionario
            config = args[0]
            duracion = config.get("duracion")
            descuento = config.get("descuento", 0.0)
            impuesto = config.get("impuesto", 0.0)
        elif len(args) >= 1:
            # Firmas 1, 2 y 3: Parámetros posicionales (y opcionalmente por nombre)
            duracion = args[0]
            descuento = args[1] if len(args) >= 2 else kwargs.get("descuento", 0.0)
            impuesto = args[2] if len(args) >= 3 else kwargs.get("impuesto", 0.0)
        elif "duracion" in kwargs:
            # Invocación completamente por argumentos nombrados
            duracion = kwargs["duracion"]
            descuento = kwargs.get("descuento", 0.0)
            impuesto = kwargs.get("impuesto", 0.0)
        else:
            raise ErrorCalculoCosto("Faltan parámetros obligatorios: se requiere al menos la duración en horas.")

        # Validamos que la duración sea numérica y positiva
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ErrorCalculoCosto(f"La duración debe ser un número positivo (recibido: {duracion}).")

        # Validamos que el descuento esté en un rango lógico (0% a 50%)
        if not isinstance(descuento, (int, float)) or not (0 <= descuento <= 50):
            raise ErrorCalculoCosto(f"El descuento debe estar entre 0% y 50% (recibido: {descuento}%).")

        # Validamos que el impuesto no sea negativo ni exagerado (0% a 30%)
        if not isinstance(impuesto, (int, float)) or not (0 <= impuesto <= 30):
            raise ErrorCalculoCosto(f"El impuesto debe estar entre 0% y 30% (recibido: {impuesto}%).")

        # Calculamos el subtotal llamando al método polimórfico de cada clase hija
        subtotal = self.calcular_subtotal(duracion)

        # Aplicamos descuento y luego sumamos el impuesto
        monto_descuento = subtotal * (descuento / 100.0)
        base_gravable = subtotal - monto_descuento
        monto_impuesto = base_gravable * (impuesto / 100.0)
        total = round(base_gravable + monto_impuesto, 2)

        # Verificamos consistencia matemática del total calculado
        if total < 0:
            raise ErrorCalculoCosto("Inconsistencia detectada: el costo final calculado es negativo.")

        return total


class ReservaSala(Servicio):
    """Servicio especializado para la reserva de salas de reuniones o conferencias."""

    def __init__(self, id_servicio, nombre, tarifa_base, capacidad_personas, disponible=True):
        # Inicializamos los atributos comunes en Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Atributo propio de las salas: capacidad máxima de asistentes
        self._capacidad = capacidad_personas
        # Validamos los parámetros específicos de la sala
        self.validar()

    def validar(self):
        """Valida que la capacidad de la sala sea un entero positivo entre 2 y 200 personas."""
        if not isinstance(self._capacidad, int) or not (2 <= self._capacidad <= 200):
            raise ErrorParametroInvalido(
                f"La capacidad de la sala debe ser un entero entre 2 y 200 personas (recibido: {self._capacidad})."
            )
        return True

    def calcular_subtotal(self, duracion_horas):
        """Polimorfismo: las salas con más de 20 personas tienen un recargo operativo del 15%."""
        subtotal = self._tarifa_base * duracion_horas
        if self._capacidad > 20:
            subtotal *= 1.15  # Recargo por logística y climatización de sala grande
        return round(subtotal, 2)

    def describir(self):
        """Devuelve la descripción detallada de la sala."""
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Sala [{self._id}] {self._nombre} | Capacidad: {self._capacidad} personas | "
            f"Tarifa: ${self._tarifa_base:,.2f}/h | Estado: {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para el alquiler de equipos tecnológicos."""

    def __init__(self, id_servicio, nombre, tarifa_base, cantidad_unidades, deposito_seguridad, disponible=True):
        # Inicializamos los atributos comunes en Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Atributos específicos del alquiler de equipos
        self._cantidad_unidades = cantidad_unidades
        self._deposito_seguridad = deposito_seguridad
        # Validamos los parámetros propios
        self.validar()

    def validar(self):
        """Valida que haya al menos 1 unidad y que el depósito de seguridad no sea negativo."""
        if not isinstance(self._cantidad_unidades, int) or self._cantidad_unidades <= 0:
            raise ErrorParametroInvalido(
                f"La cantidad de unidades debe ser un entero mayor a 0 (recibido: {self._cantidad_unidades})."
            )
        if not isinstance(self._deposito_seguridad, (int, float)) or self._deposito_seguridad < 0:
            raise ErrorParametroInvalido(
                f"El depósito de seguridad no puede ser negativo (recibido: {self._deposito_seguridad})."
            )
        return True

    def calcular_subtotal(self, duracion_horas):
        """Polimorfismo: multiplica tarifa por horas y unidades, sumando el depósito de seguridad."""
        return round((self._tarifa_base * duracion_horas * self._cantidad_unidades) + self._deposito_seguridad, 2)

    def describir(self):
        """Devuelve la descripción detallada del alquiler de equipos."""
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Equipo [{self._id}] {self._nombre} | Unidades: {self._cantidad_unidades} | "
            f"Depósito: ${self._deposito_seguridad:,.2f} | Tarifa: ${self._tarifa_base:,.2f}/h | Estado: {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para consultorías y asesorías técnicas de Software FJ."""

    NIVELES_VALIDOS = ("Basico", "Intermedio", "Experto")  # Niveles permitidos para el consultor

    def __init__(self, id_servicio, nombre, tarifa_base, especialidad, nivel="Intermedio", disponible=True):
        # Inicializamos los atributos comunes en Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Atributos específicos de la asesoría
        self._especialidad = especialidad
        self._nivel = nivel
        # Validamos los parámetros específicos
        self.validar()

    def validar(self):
        """Valida que la especialidad sea texto no vacío y que el nivel pertenezca a los permitidos."""
        if not isinstance(self._especialidad, str) or not self._especialidad.strip():
            raise ErrorParametroInvalido("La especialidad de la asesoría no puede estar vacía.")
        if self._nivel not in self.NIVELES_VALIDOS:
            raise ErrorParametroInvalido(
                f"Nivel '{self._nivel}' inválido. Niveles permitidos: {self.NIVELES_VALIDOS}."
            )
        return True

    def calcular_subtotal(self, duracion_horas):
        """Polimorfismo: aplica un multiplicador según el nivel del consultor asignado."""
        factores = {"Basico": 1.0, "Intermedio": 1.25, "Experto": 1.5}
        return round(self._tarifa_base * duracion_horas * factores[self._nivel], 2)

    def describir(self):
        """Devuelve la descripción detallada de la asesoría."""
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Asesoría [{self._id}] {self._nombre} | Área: {self._especialidad} ({self._nivel}) | "
            f"Tarifa: ${self._tarifa_base:,.2f}/h | Estado: {estado}"
        )