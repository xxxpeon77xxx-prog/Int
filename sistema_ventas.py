import os
import json
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any, Tuple

class SistemaVentas:
    # Códigos ANSI para colores (compatibles con la mayoría de las terminales)
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'
    LIGHT_GRAY = '\033[37m'
    
    # Colores específicos para la interfaz profesional
    COLOR_TITULO = BOLD + CYAN + UNDERLINE
    COLOR_SEPARADOR = LIGHT_GRAY
    COLOR_MENU = BLUE
    COLOR_EXITO = BOLD + GREEN
    COLOR_ADVERTENCIA = BOLD + YELLOW
    COLOR_ERROR = BOLD + RED
    COLOR_VALOR = BOLD + ENDC # Texto fuerte sin color

    def __init__(self):
        self.archivo_productos = "productos.json"
        self.archivo_clientes = "clientes.json"
        self.archivo_vendedores = "vendedores.json"
        self.archivo_ventas = "ventas.json"
        self.cargar_datos()
        # Muestra la pantalla de inicio al iniciar el sistema
        self.pantalla_inicio()
    
    def formato_moneda_entero(self, valor: float, ancho: int = None) -> str:
        """
        Formatea un valor numérico a un string con separador de miles (punto)
        y sin decimales, truncando la parte decimal. Ejemplo: 123456.78 -> '123.456'.
        Acepta un parámetro 'ancho' para padding.
        """
        # Truncar la parte decimal y convertir a entero para usar el especificador 'd'
        valor_entero = int(valor)
        
        # Usar el formato de entero con separador de miles (',' es el separador por defecto en f-strings)
        formato = f"{valor_entero:,}"
        
        # Reemplazar la coma (separador de miles por defecto en muchos sistemas) por el punto
        formato = formato.replace(",", ".")
        
        if ancho is not None:
             # Si se proporciona ancho, se aplica el padding de alineación derecha
            return f"{formato:>{ancho}}"
            
        return formato
    
    def cargar_datos(self):
        """Carga los datos desde los archivos JSON"""
        self.productos = self.cargar_json(self.archivo_productos)
        self.clientes = self.cargar_json(self.archivo_clientes)
        self.vendedores = self.cargar_json(self.archivo_vendedores)
        self.ventas = self.cargar_json(self.archivo_ventas)
        # ⚠️ IMPORTANTE: Corregir datos antiguos de clientes (email -> dni)
        self._corregir_datos_clientes()
    
    def _corregir_datos_clientes(self):
        """Revisa clientes y cambia la clave 'email' por 'dni' para mantener compatibilidad."""
        cambio_realizado = False
        for cliente in self.clientes:
            # Si tiene 'email' pero no 'dni', lo renombramos
            if 'email' in cliente and 'dni' not in cliente:
                cliente['dni'] = cliente.pop('email') # Mueve el valor y renombra la clave
                cambio_realizado = True
            # Aseguramos que siempre exista la clave 'dni' y 'telefono' por si es un archivo JSON nuevo
            if 'dni' not in cliente:
                 cliente['dni'] = ""
            if 'telefono' not in cliente:
                 cliente['telefono'] = ""
        
        if cambio_realizado:
            # Guardamos los datos corregidos si hubo algún cambio
            self.guardar_json(self.clientes, self.archivo_clientes)

    def cargar_json(self, archivo: str) -> List[Dict[str, Any]]:
        """Carga un archivo JSON, retorna lista vacía si no existe"""
        try:
            # Crea el archivo vacío si no existe
            if not os.path.exists(archivo):
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                return []
            
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"{self.COLOR_ADVERTENCIA}Advertencia: El archivo {archivo} está corrupto o vacío. Se inicializará vacío.{self.ENDC}")
            return []
    
    def guardar_json(self, datos: List[Dict[str, Any]], archivo: str):
        """Guarda datos en archivo JSON"""
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pausar(self):
        """Pausa la ejecución hasta que el usuario presione Enter"""
        input(f"\n{self.COLOR_SEPARADOR}Presione Enter para continuar...{self.ENDC}")
    
    def pantalla_inicio(self):
        """Muestra la pantalla de inicio con totales y fecha/hora"""
        self.limpiar_pantalla()
        
        # Reducir ancho a 45
        separador = "=" * 45
        
        fecha_actual = datetime.now().strftime("%d-%m-%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        print(self.COLOR_TITULO + separador)
        print("  SISTEMA DE GESTIÓN Y VENTAS PROFESIONAL")
        print(separador + self.ENDC)
        
        print(f"{self.COLOR_SEPARADOR}Fecha: {self.COLOR_VALOR}{fecha_actual:<15}{self.ENDC}")
        print(f"{self.COLOR_SEPARADOR}Hora:  {self.COLOR_VALOR}{hora_actual:<15}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 45 + self.ENDC)
        
        print(f"{self.COLOR_MENU}RESUMEN DE DATOS ACTUALES:{self.ENDC}")
        print(f"  {self.BLUE}Productos:{self.ENDC}   {self.COLOR_VALOR}{len(self.productos)}{self.ENDC}")
        print(f"  {self.BLUE}Clientes:{self.ENDC}    {self.COLOR_VALOR}{len(self.clientes)}{self.ENDC}")
        print(f"  {self.BLUE}Vendedores:{self.ENDC}  {self.COLOR_VALOR}{len(self.vendedores)}{self.ENDC}")
        print(f"  {self.BLUE}Ventas Reg.:{self.ENDC} {self.COLOR_VALOR}{len(self.ventas)}{self.ENDC}")
        
        print(self.COLOR_TITULO + separador + self.ENDC)
        self.pausar()


    def mostrar_menu(self):
        """Muestra el menú principal"""
        self.limpiar_pantalla()
        separador = "=" * 35 # Reducir
        
        print(self.COLOR_TITULO + separador)
        print("    MENÚ PRINCIPAL DE NAVEGACIÓN")
        print(separador + self.ENDC)
        print(f"{self.COLOR_MENU}1. VENTAS{self.ENDC}")
        print(f"{self.COLOR_MENU}2. PRODUCTOS{self.ENDC}")
        print(f"{self.COLOR_MENU}3. CLIENTES{self.ENDC}")
        print(f"{self.COLOR_MENU}4. VENDEDORES{self.ENDC}")
        print(f"{self.COLOR_ERROR}5. SALIR{self.ENDC}")
        print(self.COLOR_SEPARADOR + separador + self.ENDC)
    
    def ejecutar(self):
        """Ejecuta el sistema principal"""
        # Ya no mostramos la pantalla de inicio aquí, se hace en __init__
        while True:
            self.mostrar_menu()
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-5{self.ENDC}): ").strip()
            
            if opcion == "1":
                self.menu_ventas()
            elif opcion == "2":
                self.menu_productos()
            elif opcion == "3":
                self.menu_clientes()
            elif opcion == "4":
                self.menu_vendedores()
            elif opcion == "5":
                self.limpiar_pantalla()
                print(f"{self.COLOR_EXITO}¡Gracias por usar el sistema! Vuelva pronto.{self.ENDC}")
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida. Intente nuevamente.{self.ENDC}")
                self.pausar()
    
    # ===== MÓDULO DE VENTAS =====
    def menu_ventas(self):
        """Menú del módulo de ventas"""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 35 # Reducir
            print(self.COLOR_TITULO + separador)
            print("     MÓDULO DE VENTAS")
            print(separador + self.ENDC)
            print(f"{self.COLOR_MENU}1. Registrar Venta{self.ENDC}")
            print(f"{self.COLOR_MENU}2. Listar Ventas (Histórico){self.ENDC}")
            print(f"{self.COLOR_MENU}3. Reportes{self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}4. Volver al Menú Principal{self.ENDC}")
            print(self.COLOR_SEPARADOR + separador + self.ENDC)
            
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-4{self.ENDC}): ").strip()
            
            if opcion == "1":
                self.registrar_venta()
            elif opcion == "2":
                self.listar_ventas()
            elif opcion == "3":
                self.menu_reportes_ventas()
            elif opcion == "4":
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida.{self.ENDC}")
                self.pausar()

    def menu_reportes_ventas(self):
        """Menú de reportes de ventas (Semanal y Semanas Pasadas)"""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 55 # Aumentar un poco el ancho
            print(self.COLOR_TITULO + separador)
            print("      REPORTES DE VENTAS Y RENDIMIENTO")
            print(separador + self.ENDC)
            
            # --- OPCIONES MEJORADAS ---
            print(f"{self.COLOR_MENU}1. Ventas de la Semana Actual (Beneficio y Rentabilidad){self.ENDC}")
            print(f"{self.COLOR_MENU}2. Top Clientes y Productos (Total Histórico){self.ENDC}")
            print(f"{self.COLOR_MENU}3. Pago a Vendedores (Semanal){self.ENDC}")
            print(f"{self.COLOR_MENU}4. Registro de Ventas de Semanas Pasadas{self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}5. Volver al Menú de Ventas{self.ENDC}")
            print(self.COLOR_SEPARADOR + separador + self.ENDC)

            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-5{self.ENDC}): ").strip()

            if opcion == "1":
                self.reporte_ventas_periodo()
            elif opcion == "2":
                self.reporte_top_clientes_productos()
            elif opcion == "3":
                self.reporte_pago_vendedores()
            elif opcion == "4":
                self.menu_ventas_semanas_pasadas() # Nueva función
            elif opcion == "5":
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida.{self.ENDC}")
                self.pausar()
    
    def registrar_venta(self):
        """Registra una nueva venta"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("        REGISTRAR NUEVA VENTA")
        print(separador + self.ENDC)
        
        # Mostrar productos disponibles
        if not self.productos:
            print(f"{self.COLOR_ADVERTENCIA}No hay productos registrados.{self.ENDC}")
            self.pausar()
            return
        
        print(f"\n{self.COLOR_MENU}Productos disponibles:{self.ENDC}")
        self.listar_productos_tabla(self.productos) # Aquí uso self.productos directamente
        
        # Seleccionar producto
        try:
            id_producto = int(input(f"\nID del producto a vender ({self.COLOR_VALOR}ID{self.ENDC}): "))
            producto = next((p for p in self.productos if p['id'] == id_producto), None)
            if not producto:
                print(f"{self.COLOR_ERROR}Producto no encontrado.{self.ENDC}")
                self.pausar()
                return
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
            self.pausar()
            return
        
        # Seleccionar cliente
        if not self.clientes:
            print(f"{self.COLOR_ADVERTENCIA}No hay clientes registrados. Se registrará como 'Cliente General'{self.ENDC}")
            cliente_id = 0
            cliente_nombre = "Cliente General"
        else:
            print(f"\n{self.COLOR_MENU}Clientes disponibles (ID/Nombre):{self.ENDC}")
            self.listar_clientes_tabla_simple()
            
            try:
                cliente_id_input = input(f"\nID del cliente ({self.COLOR_VALOR}0 para General{self.ENDC}): ").strip()
                if cliente_id_input == '0':
                    cliente_id = 0
                    cliente_nombre = "Cliente General"
                else:
                    cliente_id = int(cliente_id_input)
                    cliente = next((c for c in self.clientes if c['id'] == cliente_id), None)
                    if not cliente:
                        print(f"{self.COLOR_ERROR}Cliente no encontrado.{self.ENDC}")
                        self.pausar()
                        return
                    cliente_nombre = cliente['nombre']
            except ValueError:
                print(f"{self.COLOR_ERROR}ID debe ser un número o 0.{self.ENDC}")
                self.pausar()
                return
        
        # Seleccionar vendedor
        if not self.vendedores:
            print(f"{self.COLOR_ERROR}No hay vendedores registrados.{self.ENDC}")
            self.pausar()
            return
        
        print(f"\n{self.COLOR_MENU}Vendedores disponibles (ID/Comisión %):{self.ENDC}")
        # Compactar la lista de vendedores
        for vendedor in self.vendedores:
            comision = vendedor.get('comision_beneficio', 0)
            print(f"ID: {vendedor['id']} - {vendedor['nombre'][:15]} - Com: {comision:.1f}%")

        try:
            vendedor_id = int(input("\nID del vendedor: "))
            vendedor = next((v for v in self.vendedores if v['id'] == vendedor_id), None)
            if not vendedor:
                print(f"{self.COLOR_ERROR}Vendedor no encontrado.{self.ENDC}")
                self.pausar()
                return
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
            self.pausar()
            return
        
        # Cantidad (Validación de 1 a 999 y vs Stock)
        try:
            # --- VALIDACIÓN DE CANTIDAD (1 a 999 y vs Stock) ---
            while True:
                cantidad_input = input("Cantidad (máx 999): ")
                if not cantidad_input.isdigit():
                    print(f"{self.COLOR_ERROR}❌ Error: La cantidad debe ser un número entero.{self.ENDC}")
                    continue
                
                cantidad = int(cantidad_input)
                
                if not (1 <= cantidad <= 999): # La cantidad no puede ser 0
                    print(f"{self.COLOR_ERROR}❌ Error: La cantidad a vender debe ser entre 1 y 999.{self.ENDC}")
                    continue
                
                stock_actual = producto.get('stock', 0)
                if cantidad > stock_actual:
                     print(f"{self.COLOR_ERROR}❌ Error: Solo quedan {stock_actual} unidades de {producto['nombre']} en stock.{self.ENDC}")
                     continue # Pide la cantidad de nuevo
                     
                break # Sale del bucle si la cantidad es válida y hay stock
            # --- FIN VALIDACIÓN ---

        except Exception: # Captura si el input no es un número y la validación falla antes de llegar al while
            print(f"{self.COLOR_ERROR}Cantidad debe ser un número.{self.ENDC}")
            self.pausar()
            return
        
        # Calcular totales
        subtotal = producto['precio_venta'] * cantidad
        beneficio_total = producto['beneficio'] * cantidad
        
        # Comisión se calcula sobre el BENEFICIO
        comision_porcentaje = vendedor.get('comision_beneficio', 0)
        comision_vendedor = (beneficio_total * comision_porcentaje) / 100
        
        total = subtotal
        
        # Mostrar resumen - APLICANDO FORMATO_MONEDA_ENTERO
        # Reducir ancho a 40
        print("\n" + self.COLOR_SEPARADOR + "=" * 40 + self.ENDC)
        print(f"{self.COLOR_TITULO}   RESUMEN DE VENTA{self.ENDC}")
        print(self.COLOR_SEPARADOR + "=" * 40 + self.ENDC)
        print(f"Producto:        {self.COLOR_VALOR}{producto['nombre'][:20]}{self.ENDC}")
        print(f"Cliente:         {self.COLOR_VALOR}{cliente_nombre[:20]}{self.ENDC}")
        print(f"Vendedor:        {self.COLOR_VALOR}{vendedor['nombre'][:20]}{self.ENDC}")
        print(f"Cantidad:        {self.COLOR_VALOR}{cantidad}{self.ENDC}")
        # APLICACIÓN DE CAMBIO
        print(f"Precio Unit.:    {self.COLOR_VALOR}${self.formato_moneda_entero(producto['precio_venta'])}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 40 + self.ENDC)
        # APLICACIÓN DE CAMBIO
        print(f"Subtotal:        {self.COLOR_VALOR}${self.formato_moneda_entero(subtotal)}{self.ENDC}")
        # APLICACIÓN DE CAMBIO
        print(f"Beneficio Total: {self.COLOR_VALOR}{self.GREEN}${self.formato_moneda_entero(beneficio_total)}{self.ENDC}") # Se resalta el beneficio
        # APLICACIÓN DE CAMBIO
        print(f"Comisión ({comision_porcentaje:.1f}%):{self.COLOR_VALOR}${self.formato_moneda_entero(comision_vendedor)}{self.ENDC}")
        # APLICACIÓN DE CAMBIO
        print(f"{self.COLOR_TITULO}TOTAL A PAGAR:   ${self.formato_moneda_entero(total)}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "=" * 40 + self.ENDC)
        
        confirmar = input(f"\n¿Confirmar venta? ({self.COLOR_VALOR}s/n{self.ENDC}): ").lower().strip()
        if confirmar == 's':
            # Generar ID de venta
            venta_id = max([v['id'] for v in self.ventas]) + 1 if self.ventas else 1
            
            nueva_venta = {
                'id': venta_id,
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'producto_id': producto['id'],
                'producto_nombre': producto['nombre'],
                'precio_compra': producto['precio_compra'],
                'beneficio_unitario': producto['beneficio'],
                'cliente_id': cliente_id,
                'cliente_nombre': cliente_nombre,
                'vendedor_id': vendedor_id,
                'vendedor_nombre': vendedor['nombre'],
                'cantidad': cantidad,
                'precio_unitario': producto['precio_venta'],
                'subtotal': subtotal,
                'beneficio_total': beneficio_total,
                'comision': comision_vendedor,
                'porcentaje_comision': comision_porcentaje,
                'total': total
            }
            
            self.ventas.append(nueva_venta)
            self.guardar_json(self.ventas, self.archivo_ventas)
            
            # --- DESCUENTO DE STOCK ---
            producto['stock'] = producto.get('stock', 0) - cantidad # Asegura que el campo existe
            self.guardar_json(self.productos, self.archivo_productos) # Guardar productos actualizados
            # --- FIN DESCUENTO DE STOCK ---

            print(f"\n{self.COLOR_EXITO}✅ Venta registrada exitosamente!{self.ENDC}")
        else:
            print(f"\n{self.COLOR_ADVERTENCIA}Venta cancelada.{self.ENDC}")
        
        self.pausar()
    
    def listar_ventas(self):
        """Lista todas las ventas (Compacta la tabla) - MODIFICADO PARA MOSTRAR BENEFICIO"""
        self.limpiar_pantalla()
        separador = "=" * 88 # Reducción drástica del ancho
        print(self.COLOR_TITULO + separador)
        print(" " * 35 + "LISTA DE VENTAS (HISTÓRICO)")
        print(separador + self.ENDC)
        
        if not self.ventas:
            print(f"{self.COLOR_ADVERTENCIA}No hay ventas registradas.{self.ENDC}")
            self.pausar()
            return
        
        # Compactación: Ahora muestra SubTotal, Beneficio, Comisión y Total
        print(f"{self.COLOR_MENU}{'ID':<4} {'Fecha-Hora':<10} {'Producto':<15} "
              f"{'Cant':<4} {'SubTotal':<10} {'Beneficio':<10} {'Comisión':<10} {'Total':<10}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 88 + self.ENDC)
        
        total_ventas = 0
        total_comisiones = 0
        total_beneficios = 0 # Nuevo contador
        
        for venta in self.ventas:
            # Asegurar que beneficio_total exista para evitar errores
            beneficio_total_venta = venta.get('beneficio_total', 0)

            total_ventas += venta['total']
            total_comisiones += venta['comision']
            total_beneficios += beneficio_total_venta
            
            # Formato de moneda con padding
            subtotal_str = self.formato_moneda_entero(venta['subtotal'], ancho=9)
            beneficio_str = self.formato_moneda_entero(beneficio_total_venta, ancho=9)
            comision_str = self.formato_moneda_entero(venta['comision'], ancho=9)
            total_str = self.formato_moneda_entero(venta['total'], ancho=9)

            # Uso de los primeros 10 caracteres para fecha y solo 15 para producto
            print(f"{venta['id']:<4} {venta['fecha'][5:16]:<10} {venta['producto_nombre'][:14]:<15} "
                  f"{venta['cantidad']:<4} ${subtotal_str} {self.GREEN}${beneficio_str}{self.ENDC} ${comision_str} {self.COLOR_VALOR}${total_str}{self.ENDC}")
        
        # Totales compactos
        total_ventas_str = self.formato_moneda_entero(total_ventas)
        total_beneficios_str = self.formato_moneda_entero(total_beneficios)
        total_comisiones_str = self.formato_moneda_entero(total_comisiones)

        print(self.COLOR_SEPARADOR + "-" * 88 + self.ENDC)
        # Se muestra claramente el Total Ingresos, el Beneficio y las Comisiones
        print(f"{self.COLOR_MENU}Total Ingresos Histórico: {self.COLOR_VALOR}${total_ventas_str}{self.ENDC} | {self.GREEN}Beneficio: ${total_beneficios_str}{self.ENDC} | {self.RED}Comisiones: ${total_comisiones_str}{self.ENDC}")
        print(self.COLOR_TITULO + separador + self.ENDC)
        
        self.pausar()
    
    def obtener_ventas_semanales(self) -> Tuple[List[Dict[str, Any]], Tuple[str, str]]:
        """
        Filtra las ventas para la semana actual (Domingo a Sábado).
        Retorna la lista de ventas y el rango de fechas (inicio_str, fin_str).
        """
        ahora = datetime.now()
        
        # 0 es lunes, 6 es domingo
        dia_semana_actual = ahora.weekday() 
        
        # Se necesita restar (dia_semana_actual + 1) % 7 para ir al domingo (6) anterior/actual.
        dias_a_restar = (dia_semana_actual + 1) % 7
        
        inicio_periodo = ahora - timedelta(days=dias_a_restar)
        inicio_periodo = inicio_periodo.replace(hour=0, minute=0, second=0, microsecond=0)
        
        fin_periodo = inicio_periodo + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        ventas_filtradas = []
        for venta in self.ventas:
            try:
                fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S")
                if inicio_periodo <= fecha_venta <= fin_periodo:
                    ventas_filtradas.append(venta)
            except ValueError:
                continue
                
        inicio_fmt = inicio_periodo.strftime('%d/%m/%Y')
        fin_fmt = fin_periodo.strftime('%d/%m/%Y')
        
        return ventas_filtradas, (inicio_fmt, fin_fmt)

    def reporte_ventas_periodo(self):
        """Genera el reporte de ventas semanal y muestra el total pagado a vendedores. (Compacta la tabla) - SOLO SEMANAL"""

        ventas_periodo, rango_fechas = self.obtener_ventas_semanales()
        
        if not ventas_periodo:
            self.limpiar_pantalla()
            print(f"{self.COLOR_TITULO}== REPORTE SEMANAL =={self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}No hay ventas registradas en la semana actual ({rango_fechas[0]} - {rango_fechas[1]}).{self.ENDC}")
            self.pausar()
            return
        
        # Reutilizamos la función de reporte personalizado
        self.mostrar_reporte_ventas_personalizado(ventas_periodo, rango_fechas)

    def mostrar_reporte_ventas_personalizado(self, ventas_periodo: List[Dict[str, Any]], inicio_fin_str: Tuple[str, str]):
        """Genera y muestra el reporte de ventas para un período personalizado."""
        self.limpiar_pantalla()
        inicio, fin = inicio_fin_str
        titulo = f"VENTAS REGISTRADAS: {inicio} a {fin}"
        separador = "=" * 88 
        print(self.COLOR_TITULO + separador)
        print(f"{titulo.center(88)}")
        print(separador + self.ENDC)

        # Mismo formato compacto de la tabla semanal
        print(f"{self.COLOR_MENU}{'ID':<4} {'Fecha-Hora':<10} {'Producto':<15} "
              f"{'Cant':<4} {'SubTotal':<10} {'Beneficio':<10} {'Comisión':<10} {'Total':<10}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 88 + self.ENDC)
        
        total_ingresos = 0
        total_comisiones = 0
        total_beneficios = 0 
        
        for venta in ventas_periodo:
            beneficio_total_venta = venta.get('beneficio_total', 0)
            
            total_ingresos += venta['total']
            total_comisiones += venta['comision']
            total_beneficios += beneficio_total_venta 
            
            # Formato de moneda con padding
            subtotal_str = self.formato_moneda_entero(venta['subtotal'], ancho=9)
            beneficio_str = self.formato_moneda_entero(beneficio_total_venta, ancho=9) 
            comision_str = self.formato_moneda_entero(venta['comision'], ancho=9)
            total_str = self.formato_moneda_entero(venta['total'], ancho=9)

            print(f"{venta['id']:<4} {venta['fecha'][5:16]:<10} {venta['producto_nombre'][:14]:<15} "
                  f"{venta['cantidad']:<4} ${subtotal_str} {self.GREEN}${beneficio_str}{self.ENDC} {self.RED}${comision_str}{self.ENDC} {self.COLOR_VALOR}${total_str}{self.ENDC}")
        
        # Totales compactos
        total_ingresos_str = self.formato_moneda_entero(total_ingresos)
        total_comisiones_str = self.formato_moneda_entero(total_comisiones)
        total_beneficios_str = self.formato_moneda_entero(total_beneficios)

        print(self.COLOR_SEPARADOR + "-" * 88 + self.ENDC)
        print(f"{self.COLOR_MENU}Total Ingresos del Período: {self.COLOR_VALOR}${total_ingresos_str}{self.ENDC} | {self.GREEN}Beneficio Neto: ${total_beneficios_str}{self.ENDC} | {self.RED}Comisiones: ${total_comisiones_str}{self.ENDC}")
        print(self.COLOR_TITULO + separador + self.ENDC)

        self.pausar()

    def reporte_pago_vendedores(self):
        """Reporte de comisiones a pagar a vendedores por período (SOLO SEMANAL) (Compacta la tabla)"""
        self.limpiar_pantalla()
        separador = "=" * 45 # Reducción
        print(self.COLOR_TITULO + separador)
        print("  PAGO DE COMISIONES A VENDEDORES")
        print(separador + self.ENDC)

        ventas_semana, rango_fechas = self.obtener_ventas_semanales() # Solo ventas semanales

        # Acumular comisiones por vendedor
        pago_vendedores_semanal = {}

        for venta in ventas_semana:
            vendedor_id = venta['vendedor_id']
            nombre = venta['vendedor_nombre']
            comision = venta['comision']
            pago_vendedores_semanal.setdefault((vendedor_id, nombre), 0)
            pago_vendedores_semanal[(vendedor_id, nombre)] += comision
            
        print(f"{self.COLOR_MENU}Período: {rango_fechas[0]} - {rango_fechas[1]}{self.ENDC}")

        print(f"\n{self.COLOR_MENU}--- PAGO SEMANAL ---{self.ENDC}")
        if pago_vendedores_semanal:
            print(f"{self.COLOR_MENU}{'Vendedor':<20} {'Comisión a Pagar':<18}{self.ENDC}")
            print(self.COLOR_SEPARADOR + "-" * 40 + self.ENDC) # Reducción
            for (v_id, v_nombre), comision in pago_vendedores_semanal.items():
                # APLICACIÓN DE CAMBIO
                comision_str = self.formato_moneda_entero(comision, ancho=17) # Reducción
                print(f"{v_nombre[:19]:<20} {self.RED}${comision_str}{self.ENDC}") # Reducción
            print(self.COLOR_SEPARADOR + "-" * 40 + self.ENDC) # Reducción
            # APLICACIÓN DE CAMBIO
            total_com_sem_str = self.formato_moneda_entero(sum(pago_vendedores_semanal.values()))
            print(f"{self.COLOR_MENU}Total Comisiones Semana:{self.ENDC} {self.RED}${total_com_sem_str}{self.ENDC}")
        else:
            print(f"{self.COLOR_ADVERTENCIA}No hay comisiones a pagar esta semana.{self.ENDC}")

        # Se elimina el bloque de '--- PAGO MENSUAL ---'

        print(self.COLOR_TITULO + separador + self.ENDC)
        self.pausar()

    def reporte_top_clientes_productos(self):
        """Reporte de clientes que más compraron y productos más vendidos (por cantidad) (Compacta la tabla)"""
        self.limpiar_pantalla()
        separador = "=" * 45 # Reducción
        print(self.COLOR_TITULO + separador)
        print("  TOP CLIENTES Y PRODUCTOS VENDIDOS")
        print(separador + self.ENDC)

        if not self.ventas:
            print(f"{self.COLOR_ADVERTENCIA}No hay ventas registradas para generar el reporte.{self.ENDC}")
            self.pausar()
            return

        # 1. Top Clientes (por total gastado)
        ventas_por_cliente = {}
        for venta in self.ventas:
            c_id = venta['cliente_id']
            c_nombre = venta['cliente_nombre']
            total = venta['total']
            ventas_por_cliente.setdefault((c_id, c_nombre), 0)
            ventas_por_cliente[(c_id, c_nombre)] += total
        
        top_clientes = sorted(ventas_por_cliente.items(), key=lambda item: item[1], reverse=True)[:5]
        
        print(f"\n{self.COLOR_MENU}--- TOP 5 CLIENTES (Total Gastado - Histórico) ---{self.ENDC}")
        if top_clientes:
            print(f"{self.COLOR_MENU}{'Cliente':<20} {'Total Gastado':<18}{self.ENDC}") # Reducción
            print(self.COLOR_SEPARADOR + "-" * 40 + self.ENDC) # Reducción
            for (c_id, c_nombre), total in top_clientes:
                # APLICACIÓN DE CAMBIO
                total_str = self.formato_moneda_entero(total, ancho=17) # Reducción
                print(f"{c_nombre[:19]:<20} {self.COLOR_VALOR}${total_str}{self.ENDC}") # Reducción
        else:
            print(f"{self.COLOR_ADVERTENCIA}No hay datos de clientes.{self.ENDC}")

        # 2. Top Productos (por cantidad vendida)
        ventas_por_producto = {}
        for venta in self.ventas:
            p_id = venta['producto_id']
            p_nombre = venta['producto_nombre']
            cantidad = venta['cantidad']
            ventas_por_producto.setdefault((p_id, p_nombre), 0)
            ventas_por_producto[(p_id, p_nombre)] += cantidad
        
        top_productos = sorted(ventas_por_producto.items(), key=lambda item: item[1], reverse=True)[:5]
        
        print(f"\n{self.COLOR_MENU}--- TOP 5 PRODUCTOS (Cantidad Vendida - Histórico) ---{self.ENDC}")
        if top_productos:
            print(f"{self.COLOR_MENU}{'Producto':<25} {'Cantidad Total':<15}{self.ENDC}") # Reducción
            print(self.COLOR_SEPARADOR + "-" * 40 + self.ENDC) # Reducción
            for (p_id, p_nombre), cantidad in top_productos:
                print(f"{p_nombre[:24]:<25} {self.COLOR_VALOR}{cantidad:<15}{self.ENDC}") # Reducción
        else:
            print(f"{self.COLOR_ADVERTENCIA}No hay datos de productos.{self.ENDC}")

        print(self.COLOR_TITULO + separador + self.ENDC)
        self.pausar()
        
    def obtener_semanas_disponibles(self) -> List[Tuple[Tuple[str, str], List[Dict[str, Any]]]]:
        """
        Retorna una lista de tuplas ((semana_inicio_str, semana_fin_str), ventas_filtradas)
        con todas las semanas pasadas que tienen ventas registradas.
        La semana actual NO se incluye.
        """
        if not self.ventas:
            return []

        # Convertir todas las fechas de venta a objetos datetime y ordenarlas
        ventas_con_fecha = []
        for venta in self.ventas:
            try:
                fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S")
                ventas_con_fecha.append((fecha_venta, venta))
            except ValueError:
                continue
        
        if not ventas_con_fecha:
            return []
            
        # Determinar el inicio de la semana actual (Domingo 00:00:00)
        ahora = datetime.now()
        dia_semana_actual = ahora.weekday() # 0 es lunes, 6 es domingo
        dias_a_restar = (dia_semana_actual + 1) % 7
        inicio_semana_actual = ahora - timedelta(days=dias_a_restar)
        inicio_semana_actual = inicio_semana_actual.replace(hour=0, minute=0, second=0, microsecond=0)

        # Agrupar las ventas por semana (usando el domingo de inicio de la semana como clave)
        ventas_por_semana = {}
        for fecha_venta, venta in ventas_con_fecha:
            if fecha_venta < inicio_semana_actual: # Solo ventas pasadas
                
                # Calcular el inicio de la semana de la venta (el domingo)
                dia_semana_venta = fecha_venta.weekday()
                dias_a_restar_venta = (dia_semana_venta + 1) % 7
                inicio_semana_venta = fecha_venta - timedelta(days=dias_a_restar_venta)
                inicio_semana_venta = inicio_semana_venta.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Usar el string de inicio de semana como clave
                inicio_semana_str = inicio_semana_venta.strftime("%Y-%m-%d")
                
                if inicio_semana_str not in ventas_por_semana:
                    ventas_por_semana[inicio_semana_str] = []
                ventas_por_semana[inicio_semana_str].append(venta)

        # Generar la lista final de semanas disponibles y ordenarlas
        semanas_disponibles = []
        for inicio_str, ventas in sorted(ventas_por_semana.items(), reverse=True):
            inicio_dt = datetime.strptime(inicio_str, "%Y-%m-%d")
            fin_dt = inicio_dt + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            # Formato legible: DD/MM/AAAA
            inicio_fmt = inicio_dt.strftime("%d/%m/%Y")
            fin_fmt = fin_dt.strftime("%d/%m/%Y")
            
            semanas_disponibles.append(((inicio_fmt, fin_fmt), ventas))
            
        return semanas_disponibles
        
    def menu_ventas_semanas_pasadas(self):
        """Menú para seleccionar y ver el registro de ventas de semanas pasadas."""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 50
            print(self.COLOR_TITULO + separador)
            print("   REGISTRO DE VENTAS DE SEMANAS PASADAS")
            print(separador + self.ENDC)
            
            semanas_disponibles = self.obtener_semanas_disponibles()
            
            if not semanas_disponibles:
                print(f"{self.COLOR_ADVERTENCIA}No hay ventas registradas en semanas anteriores.{self.ENDC}")
                self.pausar()
                return

            print(f"{self.COLOR_MENU}Seleccione el período (Domingo a Sábado):{self.ENDC}")
            
            # Mostrar las opciones de semanas pasadas
            opciones_validas = {}
            for i, ((inicio, fin), ventas) in enumerate(semanas_disponibles):
                opcion_num = i + 1
                opciones_validas[str(opcion_num)] = ((inicio, fin), ventas)
                print(f"{self.COLOR_MENU}{opcion_num}. {inicio} - {fin} ({len(ventas)} Ventas){self.ENDC}")
            
            print(f"\n{self.COLOR_ADVERTENCIA}0. Volver a Reportes{self.ENDC}")
            print(self.COLOR_SEPARADOR + "-" * 50 + self.ENDC)
            
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}0-{len(semanas_disponibles)}{self.ENDC}): ").strip()

            if opcion == "0":
                break
            elif opcion in opciones_validas:
                # Mostrar el reporte detallado de la semana seleccionada
                rango_fechas, ventas_periodo = opciones_validas[opcion]
                self.mostrar_reporte_ventas_personalizado(ventas_periodo, rango_fechas)
            else:
                print(f"{self.COLOR_ERROR}Opción inválida. Intente nuevamente.{self.ENDC}")
                self.pausar()

    # ===== MÓDULO DE PRODUCTOS =====
    def menu_productos(self):
        """Menú del módulo de productos"""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 35 # Reducir
            print(self.COLOR_TITULO + separador)
            print("     MÓDULO DE PRODUCTOS")
            print(separador + self.ENDC)
            print(f"{self.COLOR_MENU}1. Listar Productos{self.ENDC}")
            print(f"{self.COLOR_MENU}2. Agregar Producto{self.ENDC}")
            print(f"{self.COLOR_MENU}3. Editar Producto{self.ENDC}")
            print(f"{self.COLOR_MENU}4. Actualizar Costo (Masivo - %){self.ENDC}")
            print(f"{self.COLOR_MENU}5. Buscar Productos{self.ENDC}")
            print(f"{self.COLOR_ERROR}6. Eliminar Producto{self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}7. Volver al Menú Principal{self.ENDC}")
            print(self.COLOR_SEPARADOR + separador + self.ENDC)
            
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-7{self.ENDC}): ").strip()
            
            if opcion == "1":
                self.listar_productos()
            elif opcion == "2":
                self.agregar_producto()
            elif opcion == "3":
                self.editar_producto()
            elif opcion == "4":
                self.actualizar_costo_masivo()
            elif opcion == "5":
                self.buscar_productos()
            elif opcion == "6":
                self.eliminar_producto()
            elif opcion == "7":
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida.{self.ENDC}")
                self.pausar()
    
    def listar_productos(self, productos_a_mostrar=None):
        """Lista productos en formato tabla. Usa 'productos_a_mostrar' o todos."""
        self.limpiar_pantalla()
        separador = "=" * 60 # Reducción del ancho
        print(self.COLOR_TITULO + separador)
        print("           LISTA DE PRODUCTOS")
        print(separador + self.ENDC)
        
        lista = productos_a_mostrar if productos_a_mostrar is not None else self.productos
        
        if not lista:
            print(f"{self.COLOR_ADVERTENCIA}No hay productos registrados o que coincidan con la búsqueda.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_productos_tabla(lista)
        self.pausar()
    
    def listar_productos_tabla(self, lista_productos):
        """
        Muestra los productos en formato de tabla profesional. Recibe una lista.
        COMPACTADO: Ancho 60, campos acortados.
        """
        # Compactación: anchos reducidos
        print(f"{self.COLOR_MENU}{'ID':<4} {'Producto':<15} {'Compra':<8} {'Benef.':<7} {'Venta':<8} {'Stock':<6}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 60 + self.ENDC)
        
        for producto in lista_productos:
                
            # Formato de moneda con padding ajustado
            compra_str = self.formato_moneda_entero(producto['precio_compra'], ancho=7)
            beneficio_str = self.formato_moneda_entero(producto['beneficio'], ancho=6)
            venta_str = self.formato_moneda_entero(producto['precio_venta'], ancho=7)

            stock_actual = producto.get('stock', 0) 

            # Compactación: Nombre a 15, campos numéricos ajustados
            print(f"{producto['id']:<4} {producto['nombre'][:14]:<15} {self.COLOR_VALOR}${compra_str}{self.ENDC} "
                  f"{self.GREEN}${beneficio_str}{self.ENDC} {self.CYAN}${venta_str}{self.ENDC} {stock_actual:<6}") 
        
        print(self.COLOR_SEPARADOR + "-" * 60 + self.ENDC)

    def buscar_productos(self):
        """Permite buscar productos por ID o Nombre."""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("     BUSCAR PRODUCTOS")
        print(separador + self.ENDC)
        
        termino = input(f"Ingrese ID o nombre (coincidencia): ").strip()
        if not termino:
            print(f"{self.COLOR_ADVERTENCIA}Búsqueda cancelada.{self.ENDC}")
            self.pausar()
            return
        
        resultados = []
        termino_lower = termino.lower()
        
        for producto in self.productos:
            # Búsqueda por ID
            if termino.isdigit() and str(producto['id']) == termino:
                resultados.append(producto)
                break 
            # Búsqueda por Nombre (coincidencia parcial)
            elif termino_lower in producto['nombre'].lower():
                resultados.append(producto)

        if resultados:
            self.listar_productos(resultados)
        else:
            print(f"{self.COLOR_ADVERTENCIA}No se encontraron productos con el término '{termino}'.{self.ENDC}")
            self.pausar()
    
    def agregar_producto(self):
        """Agrega un nuevo producto"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         AGREGAR PRODUCTO")
        print(separador + self.ENDC)
        
        try:
            nombre = input("Nombre del producto: ").strip()
            if not nombre:
                print(f"{self.COLOR_ERROR}El nombre no puede estar vacío.{self.ENDC}")
                self.pausar()
                return
            
            precio_compra = float(input(f"Precio de compra ({self.COLOR_VALOR}$){self.ENDC}: "))
            beneficio = float(input(f"Beneficio (Ganancia fija) ({self.COLOR_VALOR}$){self.ENDC}: "))
            
            if precio_compra <= 0 or beneficio < 0:
                print(f"{self.COLOR_ERROR}El precio de compra debe ser positivo y el beneficio no puede ser negativo.{self.ENDC}")
                self.pausar()
                return

            # --- VALIDACIÓN DE STOCK (0 a 999) ---
            while True:
                try:
                    stock_inicial = int(input("Stock inicial (máx 999): "))
                    if 0 <= stock_inicial <= 999:
                        break
                    else:
                        print(f"{self.COLOR_ERROR}❌ Error: El stock debe ser un número entre 0 y 999.{self.ENDC}")
                except ValueError:
                    print(f"{self.COLOR_ERROR}❌ Error: Ingrese un valor numérico entero.{self.ENDC}")
            # --- FIN VALIDACIÓN ---
            
            precio_venta = precio_compra + beneficio
            
            # Generar ID
            producto_id = max([p['id'] for p in self.productos]) + 1 if self.productos else 1
            
            nuevo_producto = {
                'id': producto_id,
                'nombre': nombre,
                'precio_compra': precio_compra,
                'beneficio': beneficio,
                'precio_venta': precio_venta,
                'stock': stock_inicial # <-- Se añade el stock
            }
            
            self.productos.append(nuevo_producto)
            self.guardar_json(self.productos, self.archivo_productos)
            
            # APLICACIÓN DE CAMBIO
            precio_venta_str = self.formato_moneda_entero(precio_venta)
            
            print(f"\n{self.COLOR_EXITO}✅ Producto '{nombre}' agregado exitosamente!{self.ENDC}")
            print(f"Stock inicial: {self.COLOR_VALOR}{stock_inicial}{self.ENDC}")
            print(f"P. Venta: {self.COLOR_VALOR}${precio_venta_str}{self.ENDC}")
            
        except ValueError:
            print(f"{self.COLOR_ERROR}Error: Ingrese valores numéricos válidos para los precios.{self.ENDC}")
        
        self.pausar()
    
    def editar_producto(self):
        """Edita un producto existente"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         EDITAR PRODUCTO")
        print(separador + self.ENDC)
        
        if not self.productos:
            print(f"{self.COLOR_ADVERTENCIA}No hay productos registrados.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_productos_tabla(self.productos)
        
        try:
            id_producto = int(input(f"\nID del producto a editar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            producto = next((p for p in self.productos if p['id'] == id_producto), None)
            
            if not producto:
                print(f"{self.COLOR_ERROR}Producto no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            print(f"\n{self.COLOR_MENU}Editando: {producto['nombre']}{self.ENDC}")
            print(f"{self.COLOR_SEPARADOR}(Deje en blanco para mantener){self.ENDC}")
            
            nuevo_nombre = input(f"Nuevo nombre [{producto['nombre']}]: ").strip()
            if nuevo_nombre:
                producto['nombre'] = nuevo_nombre
            
            try:
                # Edición de precio de compra
                compra_actual_str = self.formato_moneda_entero(producto['precio_compra'])
                nuevo_compra_str = input(f"Nuevo P. Compra [${compra_actual_str}]: $").strip()
                if nuevo_compra_str:
                    nuevo_compra = float(nuevo_compra_str)
                    if nuevo_compra <= 0:
                        print(f"{self.COLOR_ADVERTENCIA}El P. Compra debe ser positivo. No se modificó.{self.ENDC}")
                    else:
                        producto['precio_compra'] = nuevo_compra

                # Edición de beneficio
                beneficio_actual_str = self.formato_moneda_entero(producto['beneficio'])
                nuevo_beneficio_str = input(f"Nuevo Beneficio [${beneficio_actual_str}]: $").strip()
                if nuevo_beneficio_str:
                    nuevo_beneficio = float(nuevo_beneficio_str)
                    if nuevo_beneficio < 0:
                        print(f"{self.COLOR_ADVERTENCIA}El beneficio no puede ser negativo. No se modificó.{self.ENDC}")
                    else:
                        producto['beneficio'] = nuevo_beneficio
                
                # --- NUEVO CAMPO: EDICIÓN DE STOCK (0 a 999) ---
                stock_actual = producto.get('stock', 0)
                nuevo_stock_str = input(f"Nuevo Stock [{stock_actual}] (máx 999): ").strip()
                if nuevo_stock_str:
                    try:
                        nuevo_stock = int(nuevo_stock_str)
                        if 0 <= nuevo_stock <= 999:
                            producto['stock'] = nuevo_stock
                        else:
                            print(f"{self.COLOR_ADVERTENCIA}El stock debe ser un número entre 0 y 999. No se modificó.{self.ENDC}")
                    except ValueError:
                        print(f"{self.COLOR_ERROR}Error: Ingrese un valor numérico entero para el stock. No se modificó.{self.ENDC}")
                # --- FIN NUEVO CAMPO: EDICIÓN DE STOCK ---
                
                producto['precio_venta'] = producto['precio_compra'] + producto['beneficio']
                
                self.guardar_json(self.productos, self.archivo_productos)
                
                # APLICACIÓN DE CAMBIO
                nuevo_venta_str = self.formato_moneda_entero(producto['precio_venta'])
                
                print(f"\n{self.COLOR_EXITO}✅ Producto actualizado exitosamente!{self.ENDC}")
                print(f"Nuevo Stock: {self.COLOR_VALOR}{producto.get('stock', 'N/A')}{self.ENDC}")
                print(f"Nuevo P. Venta: {self.COLOR_VALOR}${nuevo_venta_str}{self.ENDC}")
                
            except ValueError:
                print(f"{self.COLOR_ERROR}Error: Ingrese valores numéricos válidos.{self.ENDC}")
        
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
        
        self.pausar()
    
    # NUEVA FUNCIÓN: ACTUALIZACIÓN MASIVA DE PRECIO DE COSTO
    def actualizar_costo_masivo(self):
        """
        Actualiza el precio de compra (costo) de todos los productos
        en un porcentaje dado y recalcula el precio de venta.
        """
        self.limpiar_pantalla()
        separador = "=" * 45
        print(self.COLOR_TITULO + separador)
        print(" ACTUALIZACIÓN MASIVA DE COSTO")
        print(separador + self.ENDC)

        if not self.productos:
            print(f"{self.COLOR_ADVERTENCIA}No hay productos registrados para actualizar.{self.ENDC}")
            self.pausar()
            return

        try:
            porcentaje_subida = float(input(f"Porcentaje de aumento/disminución de costo ({self.COLOR_VALOR}%){self.ENDC}: "))
            
            if porcentaje_subida == 0:
                print(f"{self.COLOR_ADVERTENCIA}Porcentaje de 0%. No se realizará ninguna modificación.{self.ENDC}")
                self.pausar()
                return

            confirmar = input(f"\n¿Aplicar cambio del {self.COLOR_VALOR}{porcentaje_subida:.2f}%{self.ENDC} a {len(self.productos)} productos? ({self.COLOR_VALOR}s/n{self.ENDC}): ").lower().strip()
            
            if confirmar != 's':
                print(f"{self.COLOR_ADVERTENCIA}Actualización masiva cancelada.{self.ENDC}")
                self.pausar()
                return

            productos_actualizados = 0
            for producto in self.productos:
                
                # Solo actualizar si el precio de compra es positivo
                if producto['precio_compra'] > 0:
                    
                    factor = 1 + (porcentaje_subida / 100)
                    
                    # 1. Aplicar cambio al precio de compra
                    nuevo_precio_compra = producto['precio_compra'] * factor
                    
                    # Aseguramos que el precio no caiga por debajo de un umbral si hay una disminución
                    if nuevo_precio_compra < 0.01 and porcentaje_subida < 0:
                         nuevo_precio_compra = 0.01 
                         
                    producto['precio_compra'] = nuevo_precio_compra
                    
                    # 2. Recalcular precio de venta (Costo + Beneficio Fijo)
                    producto['precio_venta'] = producto['precio_compra'] + producto['beneficio']
                    
                    productos_actualizados += 1
            
            self.guardar_json(self.productos, self.archivo_productos)
            
            print(f"\n{self.COLOR_EXITO}✅ Actualización masiva completada!{self.ENDC}")
            print(f"Se actualizaron {self.COLOR_VALOR}{productos_actualizados}{self.ENDC} productos.")
            
        except ValueError:
            print(f"{self.COLOR_ERROR}Error: Ingrese un valor numérico válido para el porcentaje.{self.ENDC}")

        self.pausar()
    # FIN NUEVA FUNCIÓN: ACTUALIZACIÓN MASIVA DE PRECIO DE COSTO

    def eliminar_producto(self):
        """Elimina un producto por ID"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         ELIMINAR PRODUCTO")
        print(separador + self.ENDC)
        
        if not self.productos:
            print(f"{self.COLOR_ADVERTENCIA}No hay productos registrados.{self.ENDC}")
            self.pausar()
            return

        self.listar_productos_tabla(self.productos)
        
        try:
            id_producto = int(input(f"\nID del producto a eliminar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            
            # Comprobar si existe en ventas
            if any(v['producto_id'] == id_producto for v in self.ventas):
                 print(f"{self.COLOR_ERROR}❌ ERROR: El producto ID {id_producto} tiene ventas asociadas y no puede ser eliminado.{self.ENDC}")
                 self.pausar()
                 return

            producto_a_eliminar = next((p for p in self.productos if p['id'] == id_producto), None)
            
            if not producto_a_eliminar:
                print(f"{self.COLOR_ERROR}Producto no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            confirmar = input(f"¿Eliminar '{producto_a_eliminar['nombre']}'? ({self.COLOR_VALOR}s/n{self.ENDC}): ").lower().strip()
            
            if confirmar == 's':
                self.productos.remove(producto_a_eliminar)
                self.guardar_json(self.productos, self.archivo_productos)
                print(f"\n{self.COLOR_EXITO}✅ Producto '{producto_a_eliminar['nombre']}' eliminado exitosamente.{self.ENDC}")
            else:
                print(f"\n{self.COLOR_ADVERTENCIA}Eliminación cancelada.{self.ENDC}")
                
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
        
        self.pausar()
        
    # ===== MÓDULO DE CLIENTES =====
    def menu_clientes(self):
        """Menú del módulo de clientes"""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 35 # Reducir
            print(self.COLOR_TITULO + separador)
            print("     MÓDULO DE CLIENTES")
            print(separador + self.ENDC)
            print(f"{self.COLOR_MENU}1. Listar Clientes{self.ENDC}")
            print(f"{self.COLOR_MENU}2. Agregar Cliente{self.ENDC}")
            print(f"{self.COLOR_MENU}3. Editar Cliente{self.ENDC}")
            print(f"{self.COLOR_MENU}4. Buscar Cliente{self.ENDC}")
            print(f"{self.COLOR_ERROR}5. Eliminar Cliente{self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}6. Volver al Menú Principal{self.ENDC}")
            print(self.COLOR_SEPARADOR + separador + self.ENDC)
            
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-6{self.ENDC}): ").strip()
            
            if opcion == "1":
                self.listar_clientes()
            elif opcion == "2":
                self.agregar_cliente()
            elif opcion == "3":
                self.editar_cliente()
            elif opcion == "4":
                self.buscar_clientes()
            elif opcion == "5":
                self.eliminar_cliente()
            elif opcion == "6":
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida.{self.ENDC}")
                self.pausar()

    def listar_clientes(self, clientes_a_mostrar=None):
        """Lista clientes en formato tabla. Usa 'clientes_a_mostrar' o todos. (Compacta la tabla)"""
        self.limpiar_pantalla()
        # Aumentamos el ancho del separador de 60 a 75 para acomodar el nuevo campo
        separador = "=" * 75
        print(self.COLOR_TITULO + separador)
        print("                        LISTA DE CLIENTES")
        print(separador + self.ENDC)
        
        lista = clientes_a_mostrar if clientes_a_mostrar is not None else self.clientes
        
        if not lista:
            print(f"{self.COLOR_ADVERTENCIA}No hay clientes registrados o que coincidan con la búsqueda.{self.ENDC}")
            self.pausar()
            return
        
        # Compactación: Títulos con el nuevo campo "Teléfono"
        # Ajustamos anchos: Nombre (25), DNI/ID Fiscal (15), Teléfono (15)
        print(f"{self.COLOR_MENU}{'ID':<4} {'Nombre':<25} {'DNI/ID Fiscal':<15} {'Teléfono':<15}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 75 + self.ENDC)
        
        for cliente in lista:
            # Compactación: Nombre a 25, DNI a 15, Teléfono a 15
            print(f"{cliente['id']:<4} {cliente['nombre'][:24]:<25} {cliente.get('dni', ''):<15} {cliente.get('telefono', ''):<15}")
        
        print(self.COLOR_SEPARADOR + "-" * 75 + self.ENDC)
        self.pausar()
    
    def listar_clientes_tabla_simple(self):
        """Muestra solo ID y Nombre para seleccionar en Venta. (Compactada)"""
        print(f"{self.COLOR_MENU}{'ID':<4} {'Nombre':<20}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 25 + self.ENDC) # Reducción
        
        for cliente in self.clientes:
            print(f"{cliente['id']:<4} {cliente['nombre'][:19]:<20}") # Reducción
        
        print(self.COLOR_SEPARADOR + "-" * 25 + self.ENDC) # Reducción

    def agregar_cliente(self):
        """Agrega un nuevo cliente"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         AGREGAR CLIENTE")
        print(separador + self.ENDC)
        
        nombre = input("Nombre del cliente: ").strip()
        if not nombre:
            print(f"{self.COLOR_ERROR}El nombre no puede estar vacío.{self.ENDC}")
            self.pausar()
            return
            
        dni = input("DNI/ID Fiscal (Opcional): ").strip()
        telefono = input("Teléfono (Opcional): ").strip()
        
        # Generar ID
        cliente_id = max([c['id'] for c in self.clientes]) + 1 if self.clientes else 1
        
        nuevo_cliente = {
            'id': cliente_id,
            'nombre': nombre,
            'dni': dni,
            'telefono': telefono
        }
        
        self.clientes.append(nuevo_cliente)
        self.guardar_json(self.clientes, self.archivo_clientes)
        
        print(f"\n{self.COLOR_EXITO}✅ Cliente '{nombre}' agregado exitosamente!{self.ENDC}")
        self.pausar()

    def editar_cliente(self):
        """Edita un cliente existente"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         EDITAR CLIENTE")
        print(separador + self.ENDC)
        
        if not self.clientes:
            print(f"{self.COLOR_ADVERTENCIA}No hay clientes registrados.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_clientes_tabla_simple()
        
        try:
            id_cliente = int(input(f"\nID del cliente a editar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            cliente = next((c for c in self.clientes if c['id'] == id_cliente), None)
            
            if not cliente:
                print(f"{self.COLOR_ERROR}Cliente no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            print(f"\n{self.COLOR_MENU}Editando: {cliente['nombre']}{self.ENDC}")
            print(f"{self.COLOR_SEPARADOR}(Deje en blanco para mantener){self.ENDC}")
            
            nuevo_nombre = input(f"Nuevo nombre [{cliente['nombre']}]: ").strip()
            if nuevo_nombre:
                cliente['nombre'] = nuevo_nombre
            
            # Usar .get para compatibilidad con datos antiguos que podrían no tener 'dni' o 'telefono'
            dni_actual = cliente.get('dni', '')
            nuevo_dni = input(f"Nuevo DNI/ID Fiscal [{dni_actual}]: ").strip()
            if nuevo_dni:
                cliente['dni'] = nuevo_dni
            
            telefono_actual = cliente.get('telefono', '')
            nuevo_telefono = input(f"Nuevo Teléfono [{telefono_actual}]: ").strip()
            if nuevo_telefono:
                cliente['telefono'] = nuevo_telefono
            
            self.guardar_json(self.clientes, self.archivo_clientes)
            print(f"\n{self.COLOR_EXITO}✅ Cliente '{cliente['nombre']}' actualizado exitosamente!{self.ENDC}")
        
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
            
        self.pausar()

    def buscar_clientes(self):
        """Permite buscar clientes por ID, Nombre, DNI o Teléfono."""
        self.limpiar_pantalla()
        separador = "=" * 45
        print(self.COLOR_TITULO + separador)
        print("     BUSCAR CLIENTES")
        print(separador + self.ENDC)
        
        termino = input(f"Ingrese ID, Nombre, DNI o Teléfono: ").strip()
        if not termino:
            print(f"{self.COLOR_ADVERTENCIA}Búsqueda cancelada.{self.ENDC}")
            self.pausar()
            return
        
        resultados = []
        termino_lower = termino.lower()
        
        for cliente in self.clientes:
            # Búsqueda por ID (si el término es un número)
            if termino.isdigit() and str(cliente['id']) == termino:
                resultados.append(cliente)
                break 
            # Búsqueda por Nombre (coincidencia parcial)
            elif termino_lower in cliente['nombre'].lower():
                resultados.append(cliente)
            # Búsqueda por DNI
            elif termino_lower in cliente.get('dni', '').lower():
                resultados.append(cliente)
            # Búsqueda por Teléfono
            elif termino_lower in cliente.get('telefono', '').lower():
                resultados.append(cliente)

        if resultados:
            # Usar un set para evitar duplicados si un cliente coincide por varios campos
            clientes_unicos = []
            ids_vistos = set()
            for cliente in resultados:
                if cliente['id'] not in ids_vistos:
                    clientes_unicos.append(cliente)
                    ids_vistos.add(cliente['id'])

            self.listar_clientes(clientes_unicos)
        else:
            print(f"{self.COLOR_ADVERTENCIA}No se encontraron clientes con el término '{termino}'.{self.ENDC}")
            self.pausar()
            
    def eliminar_cliente(self):
        """Elimina un cliente por ID"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         ELIMINAR CLIENTE")
        print(separador + self.ENDC)
        
        if not self.clientes:
            print(f"{self.COLOR_ADVERTENCIA}No hay clientes registrados.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_clientes_tabla_simple()
        
        try:
            id_cliente = int(input(f"\nID del cliente a eliminar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            
            # Comprobar si existe en ventas
            if any(v['cliente_id'] == id_cliente for v in self.ventas):
                 print(f"{self.COLOR_ERROR}❌ ERROR: El cliente ID {id_cliente} tiene ventas asociadas y no puede ser eliminado.{self.ENDC}")
                 self.pausar()
                 return
            
            cliente_a_eliminar = next((c for c in self.clientes if c['id'] == id_cliente), None)
            
            if not cliente_a_eliminar:
                print(f"{self.COLOR_ERROR}Cliente no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            confirmar = input(f"¿Eliminar '{cliente_a_eliminar['nombre']}'? ({self.COLOR_VALOR}s/n{self.ENDC}): ").lower().strip()
            
            if confirmar == 's':
                self.clientes.remove(cliente_a_eliminar)
                self.guardar_json(self.clientes, self.archivo_clientes)
                print(f"\n{self.COLOR_EXITO}✅ Cliente '{cliente_a_eliminar['nombre']}' eliminado exitosamente.{self.ENDC}")
            else:
                print(f"\n{self.COLOR_ADVERTENCIA}Eliminación cancelada.{self.ENDC}")
                
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
        
        self.pausar()
        
    # ===== MÓDULO DE VENDEDORES =====
    def menu_vendedores(self):
        """Menú del módulo de vendedores"""
        while True:
            self.limpiar_pantalla()
            separador = "=" * 35 # Reducir
            print(self.COLOR_TITULO + separador)
            print("     MÓDULO DE VENDEDORES")
            print(separador + self.ENDC)
            print(f"{self.COLOR_MENU}1. Listar Vendedores{self.ENDC}")
            print(f"{self.COLOR_MENU}2. Agregar Vendedor{self.ENDC}")
            print(f"{self.COLOR_MENU}3. Editar Vendedor{self.ENDC}")
            print(f"{self.COLOR_ERROR}4. Eliminar Vendedor{self.ENDC}")
            print(f"{self.COLOR_ADVERTENCIA}5. Volver al Menú Principal{self.ENDC}")
            print(self.COLOR_SEPARADOR + separador + self.ENDC)
            
            opcion = input(f"Seleccione una opción ({self.COLOR_VALOR}1-5{self.ENDC}): ").strip()
            
            if opcion == "1":
                self.listar_vendedores()
            elif opcion == "2":
                self.agregar_vendedor()
            elif opcion == "3":
                self.editar_vendedor()
            elif opcion == "4":
                self.eliminar_vendedor()
            elif opcion == "5":
                break
            else:
                print(f"{self.COLOR_ERROR}Opción inválida.{self.ENDC}")
                self.pausar()
    
    def listar_vendedores(self):
        """Lista vendedores en formato tabla (Compacta la tabla)"""
        self.limpiar_pantalla()
        separador = "=" * 60 # Reducción
        print(self.COLOR_TITULO + separador)
        print("          LISTA DE VENDEDORES")
        print(separador + self.ENDC)
        
        if not self.vendedores:
            print(f"{self.COLOR_ADVERTENCIA}No hay vendedores registrados.{self.ENDC}")
            self.pausar()
            return
        
        # Compactación: Título acortado, ancho reducido
        print(f"{self.COLOR_MENU}{'ID':<4} {'Nombre':<25} {'Comisión Beneficio (%)':<25}{self.ENDC}")
        print(self.COLOR_SEPARADOR + "-" * 60 + self.ENDC)
        
        for vendedor in self.vendedores:
            # Aseguramos que la comisión esté presente (por si el JSON es antiguo)
            comision = vendedor.get('comision_beneficio', 0)
            # Compactación: Nombre a 25, Comisión a 25
            print(f"{vendedor['id']:<4} {vendedor['nombre'][:24]:<25} {self.COLOR_VALOR}{comision:>23.2f}%{self.ENDC}")
        
        print(self.COLOR_SEPARADOR + "-" * 60 + self.ENDC)
        self.pausar()
    
    def agregar_vendedor(self):
        """Agrega un nuevo vendedor"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("       AGREGAR VENDEDOR")
        print(separador + self.ENDC)
        
        try:
            nombre = input("Nombre del vendedor: ").strip()
            if not nombre:
                print(f"{self.COLOR_ERROR}El nombre no puede estar vacío.{self.ENDC}")
                self.pausar()
                return
            
            comision_beneficio = float(input("Comisión sobre beneficio (ej: 10.5%): "))
            
            if comision_beneficio < 0:
                print(f"{self.COLOR_ERROR}La comisión no puede ser negativa.{self.ENDC}")
                self.pausar()
                return
            
            # Generar ID
            vendedor_id = max([v['id'] for v in self.vendedores]) + 1 if self.vendedores else 1
            
            nuevo_vendedor = {
                'id': vendedor_id,
                'nombre': nombre,
                'comision_beneficio': comision_beneficio
            }
            
            self.vendedores.append(nuevo_vendedor)
            self.guardar_json(self.vendedores, self.archivo_vendedores)
            
            print(f"\n{self.COLOR_EXITO}✅ Vendedor '{nombre}' agregado exitosamente con {comision_beneficio:.2f}% de comisión.{self.ENDC}")
            
        except ValueError:
            print(f"{self.COLOR_ERROR}Error: Ingrese un valor numérico válido para la comisión.{self.ENDC}")
        
        self.pausar()

    def editar_vendedor(self):
        """Edita un vendedor existente"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         EDITAR VENDEDOR")
        print(separador + self.ENDC)
        
        if not self.vendedores:
            print(f"{self.COLOR_ADVERTENCIA}No hay vendedores registrados.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_vendedores() # Muestra la lista de vendedores
        
        try:
            id_vendedor = int(input(f"\nID del vendedor a editar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            vendedor = next((v for v in self.vendedores if v['id'] == id_vendedor), None)
            
            if not vendedor:
                print(f"{self.COLOR_ERROR}Vendedor no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            print(f"\n{self.COLOR_MENU}Editando: {vendedor['nombre']}{self.ENDC}")
            print(f"{self.COLOR_SEPARADOR}(Deje en blanco para mantener){self.ENDC}")
            
            nuevo_nombre = input(f"Nuevo nombre [{vendedor['nombre']}]: ").strip()
            if nuevo_nombre:
                vendedor['nombre'] = nuevo_nombre
            
            try:
                comision_actual = vendedor.get('comision_beneficio', 0)
                nuevo_comision_str = input(f"Nuevo % de comisión [{comision_actual:.2f}%]: ").strip()
                if nuevo_comision_str:
                    nuevo_comision = float(nuevo_comision_str)
                    if nuevo_comision < 0:
                        print(f"{self.COLOR_ADVERTENCIA}La comisión no puede ser negativa. No se modificó.{self.ENDC}")
                    else:
                        vendedor['comision_beneficio'] = nuevo_comision
                
                self.guardar_json(self.vendedores, self.archivo_vendedores)
                
                print(f"\n{self.COLOR_EXITO}✅ Vendedor actualizado exitosamente!{self.ENDC}")
                print(f"Nueva comisión: {self.COLOR_VALOR}{vendedor['comision_beneficio']:.2f}%{self.ENDC}")
                
            except ValueError:
                print(f"{self.COLOR_ERROR}Error: Ingrese un valor numérico válido para la comisión.{self.ENDC}")
        
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
        
        self.pausar()

    def eliminar_vendedor(self):
        """Elimina un vendedor por ID"""
        self.limpiar_pantalla()
        separador = "=" * 40
        print(self.COLOR_TITULO + separador)
        print("         ELIMINAR VENDEDOR")
        print(separador + self.ENDC)
        
        if not self.vendedores:
            print(f"{self.COLOR_ADVERTENCIA}No hay vendedores registrados.{self.ENDC}")
            self.pausar()
            return
        
        self.listar_vendedores()
        
        try:
            id_vendedor = int(input(f"\nID del vendedor a eliminar ({self.COLOR_VALOR}ID{self.ENDC}): "))
            
            # Comprobar si existe en ventas
            if any(v['vendedor_id'] == id_vendedor for v in self.ventas):
                 print(f"{self.COLOR_ERROR}❌ ERROR: El vendedor ID {id_vendedor} tiene ventas asociadas y no puede ser eliminado.{self.ENDC}")
                 self.pausar()
                 return
            
            vendedor_a_eliminar = next((v for v in self.vendedores if v['id'] == id_vendedor), None)
            
            if not vendedor_a_eliminar:
                print(f"{self.COLOR_ERROR}Vendedor no encontrado.{self.ENDC}")
                self.pausar()
                return
            
            confirmar = input(f"¿Eliminar '{vendedor_a_eliminar['nombre']}'? ({self.COLOR_VALOR}s/n{self.ENDC}): ").lower().strip()
            
            if confirmar == 's':
                self.vendedores.remove(vendedor_a_eliminar)
                self.guardar_json(self.vendedores, self.archivo_vendedores)
                print(f"\n{self.COLOR_EXITO}✅ Vendedor '{vendedor_a_eliminar['nombre']}' eliminado exitosamente.{self.ENDC}")
            else:
                print(f"\n{self.COLOR_ADVERTENCIA}Eliminación cancelada.{self.ENDC}")
                
        except ValueError:
            print(f"{self.COLOR_ERROR}ID debe ser un número.{self.ENDC}")
        
        self.pausar()

# Inicialización y ejecución del sistema
if __name__ == "__main__":
    try:
        sistema = SistemaVentas()
        sistema.ejecutar()
    except KeyboardInterrupt:
        print(f"\n{SistemaVentas.COLOR_ADVERTENCIA}Programa interrumpido por el usuario.{SistemaVentas.ENDC}")
