import flet as ft
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

def crear_pago(monto, fecha, metodo, estado):
    cursor.execute(
        "INSERT INTO pagos (montoPago, fechaPago, metodoPago, estadoPago) VALUES (%s, %s, %s, %s)",
        (monto, fecha, metodo, estado)
    )
    db.commit()

def mostrar_pagos():
    cursor.execute("SELECT * FROM pagos ORDER BY fechaPago DESC")
    return cursor.fetchall()

def editar_pago(id_pago, monto, fecha, metodo, estado):
    cursor.execute(
        "UPDATE pagos SET montoPago=%s, fechaPago=%s, metodoPago=%s, estadoPago=%s WHERE idPagos=%s",
        (monto, fecha, metodo, estado, id_pago)
    )
    db.commit()

def eliminar_pago(id_pago):
    cursor.execute("DELETE FROM pagos WHERE idPagos=%s", (id_pago,))
    db.commit()

def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Gestión de Pagos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F1E9"
    page.padding = 20
    page.expand = True
    page.scroll = ft.ScrollMode.AUTO

    titulo = ft.Text(
        "Gestión de Pagos",
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

    id_input = ft.TextField(label="ID Pago", disabled=True, width=400, border_color="#0066CC")
    monto_input = ft.TextField(
        label="Monto",
        border_color="#0066CC",
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        suffix_text="MXN"
    )
    fecha_input = ft.TextField(
        label="Fecha y Hora (YYYY-MM-DD HH:MM:SS)",
        border_color="#0066CC",
        width=400,
        value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    metodo_input = ft.Dropdown(
        label="Método de Pago",
        border_color="#0066CC",
        width=400,
        options=[
            ft.dropdown.Option("Efectivo"),
            ft.dropdown.Option("Tarjeta de Crédito"),
            ft.dropdown.Option("Tarjeta de Débito"),
            ft.dropdown.Option("Transferencia Bancaria"),
            ft.dropdown.Option("Cheque")
        ]
    )
    estado_input = ft.Dropdown(
        label="Estado del Pago",
        border_color="#0066CC",
        width=400,
        options=[
            ft.dropdown.Option("Completado"),
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("Rechazado"),
            ft.dropdown.Option("Cancelado")
        ],
        value="Completado"
    )

    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar

    inputs = ft.Column([
        id_input,
        monto_input,
        fecha_input,
        metodo_input,
        estado_input
    ], spacing=10)

    pagos_grid = ft.Column(scroll="auto", spacing=10, expand=True)

    editando = False

    def limpiar_inputs():
        nonlocal editando
        for campo in [id_input, monto_input, fecha_input, metodo_input, estado_input]:
            campo.value = "" if campo != fecha_input and campo != estado_input else campo.value
            campo.error_text = None
        fecha_input.value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado_input.value = "Completado"
        editando = False
        boton_crear.disabled = False
        boton_guardar.disabled = True
        page.update()

    def validar_fecha(fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
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
        if not monto_input.value or not validar_numero(monto_input.value):
            monto_input.error_text = "Monto inválido."
            return False
        else:
            monto_input.error_text = None

        if not fecha_input.value or not validar_fecha(fecha_input.value):
            fecha_input.error_text = "Formato inválido. Use YYYY-MM-DD HH:MM:SS."
            return False
        else:
            fecha_input.error_text = None

        if not metodo_input.value:
            metodo_input.error_text = "Seleccione un método de pago"
            return False
        else:
            metodo_input.error_text = None

        if not estado_input.value:
            estado_input.error_text = "Seleccione un estado de pago"
            return False
        else:
            estado_input.error_text = None

        return True

    def crear_pago_action(e):
        nonlocal editando
        if editando:
            return

        if not validar_campos():
            page.update()
            return

        crear_pago(
            float(monto_input.value),
            fecha_input.value,
            metodo_input.value,
            estado_input.value
        )
        limpiar_inputs()
        mostrar_pagos_action()
        snackbar.content.value = "Pago registrado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()

    def mostrar_pagos_action(e=None):
        pagos_grid.controls.clear()
        pagos = mostrar_pagos()

        if not pagos:
            pagos_grid.controls.append(
                ft.Text("No hay pagos registrados", italic=True, color="grey")
            )
            pagos_grid.update()
            page.update()
            return

        rows = []
        current_row = None

        for i, pago in enumerate(pagos):
            if i % 3 == 0:
                current_row = ft.Row(spacing=10, wrap=True)
                rows.append(current_row)

            color_estado = {
                "Completado": ft.Colors.GREEN,
                "Pendiente": ft.Colors.ORANGE,
                "Rechazado": ft.Colors.RED,
                "Cancelado": ft.Colors.GREY
            }.get(pago[4], ft.Colors.BLUE)

            card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(f"ID Pago: {pago[0]}", weight="bold"),
                        ft.Text(f"Monto: ${float(pago[1]):,.2f} MXN"),
                        ft.Text(f"Fecha: {pago[2].strftime('%Y-%m-%d %H:%M:%S') if pago[2] else 'Sin fecha'}"),
                        ft.Text(f"Método: {pago[3]}"),
                        ft.Text(f"Estado: {pago[4]}", color=color_estado),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                on_click=lambda e, idp=pago[0]: cargar_para_editar(e, idp),
                                icon_color=ft.Colors.BLUE_600,
                                tooltip="Editar"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, idp=pago[0]: eliminar_pago_action(e, idp),
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
            pagos_grid.controls.append(row)

        pagos_grid.controls.append(
            ft.Text(f"Total de pagos: {len(pagos)}", weight="bold", color="#0066CC")
        )

        pagos_grid.update()
        page.update()

    def cargar_para_editar(e, id_pago):
        cursor.execute("SELECT * FROM pagos WHERE idPagos=%s", (id_pago,))
        pago = cursor.fetchone()
        if pago:
            id_input.value = str(pago[0])
            monto_input.value = str(pago[1])
            fecha_input.value = pago[2].strftime("%Y-%m-%d %H:%M:%S") if pago[2] else ""
            metodo_input.value = pago[3]
            estado_input.value = pago[4]
            page.update()

    def editar_pago_action(e):
        if not id_input.value:
            snackbar.content.value = "Seleccione un pago para editar"
            snackbar.bgcolor = ft.Colors.RED_400
            snackbar.open = True
            page.update()
            return

        if not validar_campos():
            page.update()
            return

        editar_pago(
            int(id_input.value),
            float(monto_input.value),
            fecha_input.value,
            metodo_input.value,
            estado_input.value
        )
        limpiar_inputs()
        mostrar_pagos_action()
        snackbar.content.value = "Pago actualizado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()

    def eliminar_pago_action(e, id_pago):
        eliminar_pago(id_pago)
        mostrar_pagos_action()
        snackbar.content.value = "Pago eliminado exitosamente"
        snackbar.bgcolor = ft.Colors.GREEN_400
        snackbar.open = True
        page.update()
        limpiar_inputs()

    boton_crear = ft.ElevatedButton("Crear", on_click=crear_pago_action, bgcolor="#795548", color="white", width=150, height=40)
    boton_guardar = ft.ElevatedButton("Guardar", on_click=editar_pago_action, bgcolor="#2196F3", color="white", width=150, height=40)

    buttons = ft.Row([boton_crear, boton_guardar], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    pagos_container = ft.Container(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Pagos Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                pagos_grid,
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
            pagos_container
        ], scroll=ft.ScrollMode.AUTO, spacing=20, expand=True)
    )

    mostrar_pagos_action()

ft.app(target=main)
