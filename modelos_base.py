# Módulo: modelos_base.py
# Descripción: Define la clase abstracta general Entidad y la clase Cliente con encapsulación y validaciones.

from abc import ABC, abstractmethod  # Herramientas para definir clases y métodos abstractos
import re  # Biblioteca de expresiones regulares para validar correos electrónicos
from excepciones import ErrorValidacionCliente  # Excepción personalizada para datos de clientes


class Entidad(ABC):
    """Clase abstracta base que representa cualquier entidad general del sistema Software FJ."""

    def __init__(self, id_entidad):
        # Validamos que el identificador no esté vacío ni sea solo espacios
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El ID de la entidad debe ser una cadena de texto no vacía.")
        # Atributo protegido que almacena el identificador único de la entidad
        self._id = id_entidad.strip()

    @property
    def id(self):
        """Propiedad de solo lectura para consultar el ID de la entidad."""
        return self._id

    @abstractmethod
    def validar(self):
        """Método abstracto que obliga a las clases hijas a validar su estado interno."""
        pass

    @abstractmethod
    def describir(self):
        """Método abstracto que obliga a las clases hijas a devolver su descripción textual."""
        pass


class Cliente(Entidad):
    """Representa un cliente de Software FJ con encapsulación y validación de datos personales."""

    def __init__(self, id_cliente, nombre, correo, telefono):
        # Inicializamos el ID llamando al constructor de la clase padre Entidad
        try:
            super().__init__(id_cliente)
        except ValueError as error_original:
            # Encadenamos el error base en nuestra excepción personalizada de cliente
            raise ErrorValidacionCliente(f"ID de cliente inválido: '{id_cliente}'.") from error_original

        # Inicializamos los atributos privados usando los setters para garantizar validación inmediata
        self.__nombre = None
        self.__correo = None
        self.__telefono = None

        # Asignamos los valores pasando por las propiedades validadoras
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

        # Ejecutamos la validación general del objeto cliente
        self.validar()

    @property
    def nombre(self):
        """Retorna el nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        """Valida y asigna el nombre del cliente."""
        # Verificamos que sea texto y tenga al menos 3 caracteres reales
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacionCliente("El nombre del cliente debe ser un texto de al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def correo(self):
        """Retorna el correo electrónico del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor):
        """Valida el formato del correo electrónico y lo asigna."""
        # Patrón estándar para validar estructura usuario@dominio.extension
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron_correo, valor.strip()):
            raise ErrorValidacionCliente(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self.__correo = valor.strip().lower()

    @property
    def telefono(self):
        """Retorna el número telefónico del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        """Valida que el teléfono contenga solo dígitos y tenga entre 7 y 15 caracteres."""
        # Convertimos a texto limpio y validamos que sean únicamente dígitos
        if not isinstance(valor, str) or not valor.strip().isdigit() or not (7 <= len(valor.strip()) <= 15):
            raise ErrorValidacionCliente(f"El teléfono '{valor}' debe contener entre 7 y 15 dígitos numéricos.")
        self.__telefono = valor.strip()

    def validar(self):
        """Verifica que todos los campos obligatorios del cliente estén correctamente cargados."""
        if not all([self._id, self.__nombre, self.__correo, self.__telefono]):
            raise ErrorValidacionCliente("Faltan datos obligatorios en el registro del cliente.")
        return True

    def describir(self):
        """Devuelve una representación legible con los datos del cliente."""
        return f"Cliente [{self._id}] {self.__nombre} | Correo: {self.__correo} | Tel: {self.__telefono}"