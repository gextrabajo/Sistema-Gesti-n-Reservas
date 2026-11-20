"""
SOFTWARE FJ
Sistema Integral de Gestión de Clientes, Servicios y Reservas.

Proyecto académico de Programación - Fase 4
Implementa abstracción, herencia, polimorfismo, encapsulación,
sobrecarga simulada, listas internas y manejo avanzado de excepciones.

No utiliza bases de datos. Los datos viven en memoria durante la ejecución.
El archivo software_fj.log conserva el registro de eventos y errores.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re


# ============================================================
# 1. CONFIGURACIÓN DEL REGISTRO DE EVENTOS (LOGS)
# ============================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


def registrar_evento(mensaje):
    """Guarda un evento normal en el archivo de registro."""
    logging.info(mensaje)


def registrar_error(mensaje):
    """Guarda un error en el archivo de registro."""
    logging.error(mensaje)


# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorSoftwareFJ(Exception):
    """Excepción base para los errores propios del sistema."""


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se utiliza cuando un dato no cumple las validaciones."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se utiliza cuando un servicio no está disponible."""


class ReservaNoPermitidaError(ErrorSoftwareFJ):
    """Se utiliza cuando una operación de reserva no está permitida."""


# ============================================================
# 3. CLASE ABSTRACTA GENERAL
# ============================================================

class EntidadSistema(ABC):
    """Representa cualquier entidad que tenga un identificador."""

    def __init__(self, identificador):
        identificador = str(identificador).strip()

        if not identificador:
            raise DatoInvalidoError("El identificador no puede estar vacío.")

        self._identificador = identificador

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Cada entidad concreta debe implementar este método."""
        pass


# ============================================================
# 4. CLASE CLIENTE
# ============================================================

class Cliente(EntidadSistema):
    """Almacena y valida la información básica de un cliente."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        nombre = str(nombre).strip()
        correo = str(correo).strip()
        telefono = str(telefono).strip()

        if len(nombre) < 3:
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")

        patron_correo = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
        if not re.match(patron_correo, correo):
            raise DatoInvalidoError(f"El correo '{correo}' no tiene un formato válido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise DatoInvalidoError("El teléfono debe contener al menos 7 dígitos.")

        self._nombre = nombre
        self._correo = correo
        self._telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    @property
    def telefono(self):
        return self._telefono

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.nombre} | ID: {self.identificador} | "
            f"Correo: {self.correo} | Teléfono: {self.telefono}"
        )


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(EntidadSistema, ABC):
    """Define las características que comparten todos los servicios."""

    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)

        nombre = str(nombre).strip()
        if not nombre:
            raise DatoInvalidoError("El nombre del servicio no puede estar vacío.")

        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool):
            raise DatoInvalidoError("La tarifa debe ser un número.")

        if tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa debe ser mayor que cero.")

        self._nombre = nombre
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = estado

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )

    @abstractmethod
    def calcular_costo(self, cantidad):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    def mostrar_informacion(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"{self.nombre} | Código: {self.identificador} | "
            f"Tarifa: ${self.tarifa_base:,.0f} | Estado: {estado}"
        )


# ============================================================
# 6. SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ============================================================

class ReservaSala(Servicio):
    """Servicio de alquiler de salas por hora."""

    def calcular_costo(self, cantidad):
        self.validar_disponibilidad()
        validar_cantidad(cantidad)
        return self.tarifa_base * cantidad

    def describir_servicio(self):
        return "Reserva de sala equipada por horas."


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por día."""

    def calcular_costo(self, cantidad):
        self.validar_disponibilidad()
        validar_cantidad(cantidad)
        return self.tarifa_base * cantidad

    def describir_servicio(self):
        return "Alquiler de equipos tecnológicos por días."


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría profesional por sesión."""

    def calcular_costo(self, cantidad):
        self.validar_disponibilidad()
        validar_cantidad(cantidad)
        return self.tarifa_base * cantidad

    def describir_servicio(self):
        return "Asesoría especializada por sesiones."


def validar_cantidad(cantidad):
    if not isinstance(cantidad, (int, float)) or isinstance(cantidad, bool):
        raise DatoInvalidoError("La duración o cantidad debe ser numérica.")
    if cantidad <= 0:
        raise DatoInvalidoError("La duración o cantidad debe ser mayor que cero.")


# ============================================================
# 7. CLASE RESERVA
# ============================================================

class Reserva(EntidadSistema):
    """Relaciona un cliente con un servicio y controla su estado."""

    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada", "Procesada")

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva necesita un objeto Cliente.")

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva necesita un objeto Servicio.")

        validar_cantidad(duracion)

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Pendiente"
        self._costo_final = None

    @property
    def estado(self):
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    def confirmar(self):
        if self._estado != "Pendiente":
            raise ReservaNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        self._servicio.validar_disponibilidad()
        self._estado = "Confirmada"
        registrar_evento(f"Reserva {self.identificador} confirmada.")
        print(f"Reserva {self.identificador} confirmada correctamente.")

    def cancelar(self):
        if self._estado in ("Cancelada", "Procesada"):
            raise ReservaNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado.lower()}."
            )

        self._estado = "Cancelada"
        registrar_evento(f"Reserva {self.identificador} cancelada.")
        print(f"Reserva {self.identificador} cancelada.")

    def procesar(self, impuesto=0.19, descuento=0):
        if self._estado != "Confirmada":
            raise ReservaNoPermitidaError(
                "La reserva debe estar confirmada antes de procesarse."
            )

        if not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 1.")

        if not isinstance(descuento, (int, float)) or not 0 <= descuento <= 100:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 100.")

        subtotal = self._servicio.calcular_costo(self._duracion)
        valor_con_descuento = subtotal * (1 - descuento / 100)
        self._costo_final = valor_con_descuento * (1 + impuesto)
        self._estado = "Procesada"

        registrar_evento(
            f"Reserva {self.identificador} procesada. Total: ${self._costo_final:.2f}"
        )
        return self._costo_final

    def mostrar_informacion(self):
        total = (
            f"${self._costo_final:,.2f}"
            if self._costo_final is not None
            else "Pendiente de cálculo"
        )
        return (
            f"Reserva {self.identificador} | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion} | "
            f"Estado: {self._estado} | Total: {total}"
        )


# ============================================================
# 8. SOBRECARGA SIMULADA DE MÉTODOS EN PYTHON
# ============================================================

class CalculadoraCostos:
    """
    Python no permite sobrecarga tradicional por cantidad de parámetros.
    Por eso usamos parámetros opcionales para ofrecer varias modalidades.
    """

    @staticmethod
    def calcular(subtotal, impuesto=0.19, descuento=0):
        if not isinstance(subtotal, (int, float)) or isinstance(subtotal, bool):
            raise DatoInvalidoError("El subtotal debe ser numérico.")
        if subtotal < 0:
            raise DatoInvalidoError("El subtotal no puede ser negativo.")
        if not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 1.")
        if not isinstance(descuento, (int, float)) or not 0 <= descuento <= 100:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 100.")

        base = subtotal * (1 - descuento / 100)
        return base * (1 + impuesto)


# ============================================================
# 9. SISTEMA CENTRAL: LISTAS Y OPERACIONES
# ============================================================

class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas mediante listas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto que intenta registrar no es un cliente.")

        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatoInvalidoError("Ya existe un cliente con ese identificador.")

        self.clientes.append(cliente)
        registrar_evento(f"Cliente registrado: {cliente.identificador}")
        print(f"Cliente '{cliente.nombre}' registrado correctamente.")

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto que intenta registrar no es un servicio.")

        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatoInvalidoError("Ya existe un servicio con ese código.")

        self.servicios.append(servicio)
        registrar_evento(f"Servicio registrado: {servicio.identificador}")
        print(f"Servicio '{servicio.nombre}' registrado correctamente.")

    def crear_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise DatoInvalidoError("Debe proporcionar un objeto Reserva.")

        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise DatoInvalidoError("Ya existe una reserva con ese identificador.")

        if not any(c is reserva._cliente for c in self.clientes):
            raise DatoInvalidoError("El cliente no está registrado en el sistema.")

        if not any(s is reserva._servicio for s in self.servicios):
            raise DatoInvalidoError("El servicio no está registrado en el sistema.")

        self.reservas.append(reserva)
        registrar_evento(f"Reserva creada: {reserva.identificador}")
        print(f"Reserva {reserva.identificador} creada correctamente.")

    def mostrar_resumen(self):
        print("\n" + "=" * 62)
        print("              RESUMEN GENERAL - SOFTWARE FJ")
        print("=" * 62)

        print(f"\nCLIENTES REGISTRADOS: {len(self.clientes)}")
        for cliente in self.clientes:
            print(" -", cliente.mostrar_informacion())

        print(f"\nSERVICIOS REGISTRADOS: {len(self.servicios)}")
        for servicio in self.servicios:
            print(" -", servicio.mostrar_informacion())
            print("   Descripción:", servicio.describir_servicio())

        print(f"\nRESERVAS REGISTRADAS: {len(self.reservas)}")
        for reserva in self.reservas:
            print(" -", reserva.mostrar_informacion())

        print("=" * 62)


# ============================================================
# 10. FUNCIONES DE PRUEBA Y MANEJO DE EXCEPCIONES
# ============================================================

def ejecutar_operacion(numero, descripcion, funcion):
    """
    Ejecuta una operación aislada.
    Si ocurre un error, lo registra y permite continuar con la siguiente.
    """
    print(f"\nOPERACIÓN {numero}: {descripcion}")

    try:
        funcion()
    except ErrorSoftwareFJ as error:
        print(f"Error controlado: {error}")
        registrar_error(f"Operación {numero}: {error}")
    except Exception as error:
        print(f"Error inesperado controlado: {error}")
        registrar_error(f"Operación {numero}, error inesperado: {error}")
    else:
        print("Operación finalizada sin errores.")
    finally:
        print(f"Fin de la operación {numero}.")


def programa_principal():
    print("\n" + "=" * 62)
    print("       SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("=" * 62)

    sistema = SistemaSoftwareFJ()

    # Objetos iniciales para las demostraciones.
    cliente_ana = Cliente(
        "C001", "Ana Martínez", "ana.martinez@email.com", "3001234567"
    )
    cliente_luis = Cliente(
        "C002", "Luis Herrera", "luis.herrera@email.com", "3107654321"
    )

    sala = ReservaSala("S001", "Sala de reuniones", 45000)
    equipo = AlquilerEquipo("S002", "Computador portátil", 60000)
    asesoria = AsesoriaEspecializada("S003", "Asesoría de software", 80000)
    servicio_suspendido = ReservaSala(
        "S004", "Sala en mantenimiento", 35000, disponible=False
    )

    # 1. Registrar un cliente válido.
    ejecutar_operacion(
        1, "Registro de cliente válido",
        lambda: sistema.registrar_cliente(cliente_ana)
    )

    # 2. Registrar otro cliente válido.
    ejecutar_operacion(
        2, "Registro de un segundo cliente",
        lambda: sistema.registrar_cliente(cliente_luis)
    )

    # 3. Intentar registrar un correo inválido.
    ejecutar_operacion(
        3, "Registro de cliente con correo incorrecto",
        lambda: Cliente("C003", "Carlos Pérez", "correo_invalido", "3001112222")
    )

    # 4. Registrar servicio de sala.
    ejecutar_operacion(
        4, "Creación de servicio de reserva de sala",
        lambda: sistema.registrar_servicio(sala)
    )

    # 5. Registrar servicio de alquiler de equipos.
    ejecutar_operacion(
        5, "Creación de servicio de alquiler de equipos",
        lambda: sistema.registrar_servicio(equipo)
    )

    # 6. Registrar servicio de asesoría.
    ejecutar_operacion(
        6, "Creación de servicio de asesoría especializada",
        lambda: sistema.registrar_servicio(asesoria)
    )

    # 7. Intentar crear un servicio con tarifa inválida.
    ejecutar_operacion(
        7, "Creación incorrecta de servicio con tarifa negativa",
        lambda: ReservaSala("S005", "Sala inválida", -10000)
    )

    # 8. Crear una reserva válida.
    reserva_1 = Reserva("R001", cliente_ana, sala, 3)
    ejecutar_operacion(
        8, "Creación de una reserva válida",
        lambda: sistema.crear_reserva(reserva_1)
    )

    # 9. Confirmar la reserva.
    ejecutar_operacion(
        9, "Confirmación de la reserva R001",
        reserva_1.confirmar
    )

    # 10. Procesar la reserva con impuesto y descuento.
    def procesar_reserva():
        total = reserva_1.procesar(impuesto=0.19, descuento=10)
        print(f"Total de la reserva R001: ${total:,.2f}")

    ejecutar_operacion(
        10, "Procesamiento de reserva con impuesto y descuento",
        procesar_reserva
    )

    # 11. Intentar cancelar una reserva que ya fue procesada.
    ejecutar_operacion(
        11, "Intento de cancelar una reserva procesada",
        reserva_1.cancelar
    )

    # 12. Crear una reserva con duración inválida.
    ejecutar_operacion(
        12, "Intento de reserva con duración negativa",
        lambda: Reserva("R002", cliente_luis, equipo, -2)
    )

    # 13. Intentar confirmar una reserva de un servicio no disponible.
    reserva_3 = Reserva("R003", cliente_luis, servicio_suspendido, 2)
    ejecutar_operacion(
        13, "Intento de confirmar un servicio no disponible",
        lambda: reserva_3.confirmar()
    )

    # 14. Demostrar otra modalidad del cálculo de costos.
    def demostrar_calculo():
        total = CalculadoraCostos.calcular(100000)
        print(f"Total con impuesto predeterminado: ${total:,.2f}")

        total_descuento = CalculadoraCostos.calcular(
            100000, impuesto=0.19, descuento=15
        )
        print(f"Total con 15% de descuento e impuesto: ${total_descuento:,.2f}")

    ejecutar_operacion(
        14, "Cálculo de costos con distintas combinaciones de parámetros",
        demostrar_calculo
    )

    # 15. Demostrar encadenamiento de excepciones.
    def demostrar_encadenamiento():
        try:
            int("dato-no-numerico")
        except ValueError as error_original:
            raise DatoInvalidoError(
                "No fue posible convertir el dato recibido a número."
            ) from error_original

    ejecutar_operacion(
        15, "Demostración de encadenamiento de excepciones",
        demostrar_encadenamiento
    )

    # 16. Demostrar try/except/else/finally y conservar el funcionamiento.
    def demostrar_bloques():
        try:
            resultado = 120 / 4
        except ZeroDivisionError as error:
            registrar_error(f"Error matemático: {error}")
            print("No se puede dividir entre cero.")
        else:
            print(f"Resultado de la operación: {resultado}")
        finally:
            print("El bloque de control de la operación matemática terminó.")

    ejecutar_operacion(
        16, "Demostración de bloques try, except, else y finally",
        demostrar_bloques
    )

    # Resumen final.
    sistema.mostrar_resumen()

    registrar_evento("Ejecución de Software FJ finalizada.")
    print("\nEl programa terminó correctamente.")
    print("Los eventos y errores quedaron registrados en software_fj.log.")


if __name__ == "__main__":
    programa_principal()
