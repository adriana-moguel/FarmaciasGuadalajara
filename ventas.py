import flet as ft
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)

def obtener_ventas():
    cursor = db.cursor()
    cursor.execute("SELECT idVentas, fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos FROM ventas")
    resultados = cursor.fetchall()
    cursor.close()
    print("Ventas cargadas:", resultados)  
    return resultados

def crear_venta(fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ventas (fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos) VALUES (%s, %s, %s, %s, %s)",
        (fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos)
    )
    db.commit()
    cursor.close()

def editar_venta(idVentas, fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ventas SET fechaVenta=%s, montoTotal=%s, fk_idClientes=%s, fk_idEmpleados=%s, fk_idPagos=%s WHERE idVentas=%s",
        (fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos, idVentas)
    )
    db.commit()
    cursor.close()

def eliminar_venta(idVentas):
    cursor = db.cursor()
    cursor.execute("DELETE FROM ventas WHERE idVentas=%s", (idVentas,))
    db.commit()
    cursor.close()

def main(page: ft.Page):

    page.title = "Farmacias Guadalajara - Ventas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True
    page.scroll = "auto"

    titulo = ft.Text(
        "Gestión de Ventas",
        size=28,
        weight="bold",
        color="#795548",
        text_align=ft.TextAlign.CENTER
    )

    header = ft.Container(
        ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        bgcolor="#F5F1E9",
        border_radius=10
    )

    id_venta = ft.TextField(label="ID Venta", disabled=True, width=400, border_color="#0066CC")
    fecha_venta = ft.TextField(label="Fecha Venta (YYYY-MM-DD)", width=400, border_color="#0066CC", hint_text="Ejemplo: 2025-05-16")
    monto_total = ft.TextField(label="Monto Total", width=400, border_color="#0066CC", hint_text="Ej: 1000.00")
    fk_cliente = ft.TextField(label="ID Cliente", width=400, border_color="#0066CC", hint_text="Máx 10 caracteres", max_length=10)
    fk_empleado = ft.TextField(label="ID Empleado", width=400, border_color="#0066CC", hint_text="Máx 10 caracteres", max_length=10)
    fk_pago = ft.TextField(label="ID Pago", width=400, border_color="#0066CC", hint_text="Número entero")

    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar

    inputs = ft.Column([
        id_venta,
        fecha_venta,
        monto_total,
        fk_cliente,
        fk_empleado,
        fk_pago
    ], spacing=10)

    ventas_grid = ft.Column(scroll="auto", spacing=10, expand=True)

    editando = False

    def limpiar_inputs():
        nonlocal editando
        for campo in [id_venta, fecha_venta, monto_total, fk_cliente, fk_empleado, fk_pago]:
            campo.value = ""
            campo.error_text = None
        editando = False
        boton_crear.disabled = False
        boton_guardar.disabled = True
        page.update()

    def validar_fecha(fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except:
            return False

    def validar_numero(valor):
        try:
            float(valor)
            return True
        except:
            return False

    def validar_campos():
        if fecha_venta.value and not validar_fecha(fecha_venta.value):
            fecha_venta.error_text = "Formato inválido. Use YYYY-MM-DD."
            return False
        else:
            fecha_venta.error_text = None

        if monto_total.value and not validar_numero(monto_total.value):
            monto_total.error_text = "Monto inválido."
            return False
        else:
            monto_total.error_text = None

        if fk_pago.value and not fk_pago.value.isdigit():
            fk_pago.error_text = "ID Pago debe ser entero."
            return False
        else:
            fk_pago.error_text = None

        return True

    def crear_venta_action(e):
        nonlocal editando
        if editando:
            return

        if not validar_campos():
            page.update()
            return

        crear_venta(
            fecha_venta.value or None,
            float(monto_total.value) if monto_total.value else None,
            fk_cliente.value or None,
            fk_empleado.value or None,
            int(fk_pago.value) if fk_pago.value else None
        )
        limpiar_inputs()
        mostrar_ventas_action()
        snackbar.content.value = "Venta creada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()

    def mostrar_ventas_action(e=None):
        ventas_grid.controls.clear()
        ventas = obtener_ventas()

        if not ventas:
            ventas_grid.controls.append(
                ft.Text("No hay ventas registradas", italic=True, color="grey")
            )
            ventas_grid.update()
            page.update()
            return

        rows = []
        current_row = None

        for i, v in enumerate(ventas):
            if i % 3 == 0:
                current_row = ft.Row(spacing=10, wrap=True)
                rows.append(current_row)

            card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(f"ID Venta: {v[0]}", weight="bold"),
                        ft.Text(f"Fecha: {v[1]}"),
                        ft.Text(f"Monto Total: ${v[2]:,.2f}" if v[2] else "Monto Total: N/A"),
                        ft.Text(f"Cliente ID: {v[3]}"),
                        ft.Text(f"Empleado ID: {v[4]}"),
                        ft.Text(f"Pago ID: {v[5]}"),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                on_click=lambda e, idv=v[0]: cargar_para_editar(idv),
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Editar"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, idv=v[0]: eliminar_venta_action(idv),
                                icon_color=ft.Colors.RED_600,
                                tooltip="Eliminar"
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=5),
                    padding=15,
                    width=350,
                ),
                color=ft.Colors.BLUE_50
            )
            current_row.controls.append(card)

        for row in rows:
            ventas_grid.controls.append(row)

        ventas_grid.controls.append(
            ft.Text(f"Total de ventas: {len(ventas)}", weight="bold", color="#0066CC")
        )

        ventas_grid.update()
        page.update()

    def cargar_para_editar(idVenta):
        nonlocal editando
        cursor = db.cursor()
        cursor.execute("SELECT idVentas, fechaVenta, montoTotal, fk_idClientes, fk_idEmpleados, fk_idPagos FROM ventas WHERE idVentas=%s", (idVenta,))
        v = cursor.fetchone()
        cursor.close()
        if v:
            id_venta.value = str(v[0])
            fecha_venta.value = str(v[1])
            monto_total.value = str(v[2]) if v[2] is not None else ""
            fk_cliente.value = v[3] if v[3] else ""
            fk_empleado.value = v[4] if v[4] else ""
            fk_pago.value = str(v[5]) if v[5] is not None else ""
            editando = True
            boton_crear.disabled = True
            boton_guardar.disabled = False
            page.update()

    def editar_venta_action(e):
        nonlocal editando
        if not validar_campos():
            page.update()
            return

        editar_venta(
            int(id_venta.value),
            fecha_venta.value or None,
            float(monto_total.value) if monto_total.value else None,
            fk_cliente.value or None,
            fk_empleado.value or None,
            int(fk_pago.value) if fk_pago.value else None
        )
        limpiar_inputs()
        mostrar_ventas_action()
        snackbar.content.value = "Venta actualizada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        editando = False
        boton_crear.disabled = False
        boton_guardar.disabled = True

    def eliminar_venta_action(idVenta):
        eliminar_venta(idVenta)
        mostrar_ventas_action()
        snackbar.content.value = "Venta eliminada exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        limpiar_inputs()

    def create_button(text, action, color, disabled=False):
        return ft.ElevatedButton(
            text,
            on_click=action,
            bgcolor=color,
            color="white",
            height=40,
            width=150,
            disabled=disabled
        )

    boton_crear = create_button("Crear", crear_venta_action, "#795548")
    boton_guardar = create_button("Guardar", editar_venta_action, "#2196F3", disabled=True)

    buttons = ft.Row([boton_crear, boton_guardar], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    ventas_container = ft.Container(
        ft.Column([
            ft.Text("Ventas Registradas", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                ventas_grid,
                padding=10,
                border_radius=10,
                bgcolor="#F5F5F5",
                expand=True,
            )
        ]),
        padding=10,
        expand=True,
    )

    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ventas_container
        ], scroll="auto", spacing=20, expand=True)
    )

    mostrar_ventas_action()

ft.app(target=main)
