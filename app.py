from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from tabulate import tabulate
import os

# Conexión MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["comerciotech"]

# Colecciones
clientes = db["clientes"]
productos = db["productos"]
pedidos = db["pedidos"]

# ========================= CLIENTES =========================

def agregar_cliente():
    identificador = input("Identificador del cliente: ").strip()
    nombres = input("Nombres: ").strip()
    apellidos = input("Apellidos: ").strip()
    calle = input("Calle: ").strip()
    numero = input("Número: ").strip()
    ciudad = input("Ciudad: ").strip()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if identificador and nombres and apellidos and calle and numero and ciudad:
        cliente = {
            "identificador_cliente": identificador,
            "nombres": nombres,
            "apellidos": apellidos,
            "direccion": {
                "calle": calle,
                "numero": numero,
                "ciudad": ciudad
            },
            "fecha_registro": fecha
        }
        clientes.insert_one(cliente)
        print("✅ Cliente agregado.")
    else:
        print("❌ Todos los campos son obligatorios.")

def listar_clientes():
    print("\n📋 Lista de Clientes:")
    datos = []
    for cliente in clientes.find():
        fila = [
            cliente.get("identificador_cliente", ""),
            cliente.get("nombres", ""),
            cliente.get("apellidos", ""),
            cliente.get("direccion", {}).get("calle", ""),
            cliente.get("direccion", {}).get("numero", ""),
            cliente.get("direccion", {}).get("ciudad", ""),
            cliente.get("fecha_registro", "")
        ]
        datos.append(fila)

    headers = ["ID Cliente", "Nombres", "Apellidos", "Calle", "Número", "Ciudad", "Fecha Registro"]
    print(tabulate(datos, headers=headers, tablefmt="grid"))


def eliminar_cliente():
    identificador = input("Identificador del cliente a eliminar: ").strip()
    cliente = clientes.find_one({"identificador_cliente": identificador})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    print(f"\nCliente encontrado: {cliente['nombres']} {cliente['apellidos']}")
    confirmacion = input("¿Estás seguro que deseas eliminar este cliente? (s/n): ").strip().lower()
    if confirmacion == "s":
        clientes.delete_one({"identificador_cliente": identificador})
        print("🗑️ Cliente eliminado.")
    else:
        print("❌ Eliminación cancelada.")


def modificar_cliente():
    identificador = input("Identificador del cliente a modificar: ").strip()
    cliente = clientes.find_one({"identificador_cliente": identificador})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    print("Deja en blanco si no deseas cambiar un campo.")
    nuevo_identificador = input(f"Identificador [{cliente.get('identificador_cliente', '')}]: ").strip() or cliente.get('identificador_cliente', '')
    nombres = input(f"Nombres [{cliente['nombres']}]: ").strip() or cliente['nombres']
    apellidos = input(f"Apellidos [{cliente['apellidos']}]: ").strip() or cliente['apellidos']
    calle = input(f"Calle [{cliente['direccion']['calle']}]: ").strip() or cliente['direccion']['calle']
    numero = input(f"Número [{cliente['direccion']['numero']}]: ").strip() or cliente['direccion']['numero']
    ciudad = input(f"Ciudad [{cliente['direccion']['ciudad']}]: ").strip() or cliente['direccion']['ciudad']

    nuevos_datos = {
        "identificador_cliente": nuevo_identificador,
        "nombres": nombres,
        "apellidos": apellidos,
        "direccion": {
            "calle": calle,
            "numero": numero,
            "ciudad": ciudad
        }
    }

    clientes.update_one({"identificador_cliente": identificador}, {"$set": nuevos_datos})
    print("✏️ Cliente actualizado.")


# ========================= PRODUCTOS =========================

def agregar_producto():
    codigo = input("Código del producto: ").strip()
    nombre = input("Nombre del producto: ").strip()
    precio = input("Precio: ").strip()
    stock = input("Stock: ").strip()
    vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ").strip()
    estado = input("Estado del producto (activo/inactivo): ").strip().lower()

    if not all([codigo, nombre, precio, stock, vencimiento, estado]):
        print("❌ Todos los campos son obligatorios.")
        return

    try:
        producto = {
            "codigo_producto": codigo,
            "nombre": nombre,
            "precio": float(precio),
            "stock": int(stock),
            "fecha_vencimiento": vencimiento,
            "estado": estado
        }
        productos.insert_one(producto)
        print("✅ Producto agregado correctamente.")
    except Exception as e:
        print("❌ Error al agregar producto:", e)

def listar_productos():
    try:
        datos = []
        for p in productos.find():
            datos.append([
                p.get("codigo_producto", ""),
                p.get("nombre", ""),
                p.get("precio", ""),
                p.get("stock", ""),
                p.get("fecha_vencimiento", ""),
                p.get("estado", "")
            ])
        if datos:
            headers = ["Código", "Nombre", "Precio", "Stock", "Vencimiento", "Estado"]
            print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))
        else:
            print("⚠️ No hay productos registrados.")
    except Exception as e:
        print("❌ Error al listar productos:", e)


def eliminar_producto():
    codigo = input("Código del producto a eliminar: ").strip()
    producto = productos.find_one({"codigo_producto": codigo})

    if not producto:
        print("❌ Producto no encontrado.")
        return

    confirmacion = input(f"¿Seguro que deseas eliminar el producto '{producto.get('nombre')}'? (s/n): ").lower()
    if confirmacion == "s":
        productos.delete_one({"codigo_producto": codigo})
        print("🗑️ Producto eliminado.")
    else:
        print("❌ Eliminación cancelada.")




def modificar_producto():
    codigo = input("Código del producto a modificar: ").strip()
    producto = productos.find_one({"codigo_producto": codigo})

    if not producto:
        print("❌ Producto no encontrado.")
        return

    print("🔄 Deja en blanco los campos que no quieras modificar.")
    nombre = input(f"Nuevo nombre [{producto.get('nombre')}]: ").strip()
    precio = input(f"Nuevo precio [{producto.get('precio')}]: ").strip()
    stock = input(f"Nuevo stock [{producto.get('stock')}]: ").strip()
    vencimiento = input(f"Nueva fecha de vencimiento [{producto.get('fecha_vencimiento')}]: ").strip()
    estado = input(f"Nuevo estado [{producto.get('estado')}]: ").strip()

    update = {}
    if nombre: update["nombre"] = nombre
    if precio:
        try:
            update["precio"] = float(precio)
        except:
            print("⚠️ Precio inválido. No se actualizará.")
    if stock:
        try:
            update["stock"] = int(stock)
        except:
            print("⚠️ Stock inválido. No se actualizará.")
    if vencimiento: update["fecha_vencimiento"] = vencimiento
    if estado: update["estado"] = estado

    if update:
        productos.update_one({"codigo_producto": codigo}, {"$set": update})
        print("✅ Producto actualizado.")
    else:
        print("⚠️ No se realizaron cambios.")


# ========================= PEDIDOS =========================

def agregar_pedido():
    codigo = input("Código del pedido: ").strip()

    # Validación de código de pedido duplicado
    if pedidos.find_one({"codigo_pedido": codigo}):
        print("❌ Ya existe un pedido con ese código.")
        return

    id_cliente = input("Identificador del cliente (identificador_cliente): ").strip()
    cliente = clientes.find_one({"identificador_cliente": id_cliente})
    
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    fecha = input("Fecha del pedido (YYYY-MM-DD): ").strip()
    productos_pedido = []

    while True:
        codigo_producto = input("Código del producto (ENTER para terminar): ").strip()
        if not codigo_producto:
            break
        try:
            cantidad = int(input("Cantidad: "))
        except:
            print("❌ Cantidad inválida.")
            continue

        producto = productos.find_one({"codigo_producto": codigo_producto})
        if not producto:
            print("❌ Producto no encontrado.")
            continue

        productos_pedido.append({
            "codigo_producto": codigo_producto,
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "precio": producto["precio"]
        })

    if not productos_pedido:
        print("❌ No se agregaron productos.")
        return

    monto_total = sum(p["cantidad"] * p["precio"] for p in productos_pedido)

    pedido = {
        "codigo_pedido": codigo,
        "cliente_id": cliente["identificador_cliente"],
        "fecha_pedido": fecha,
        "monto_total": monto_total,
        "productos": productos_pedido
    }

    pedidos.insert_one(pedido)
    print("✅ Pedido agregado.")



def listar_pedidos():
    print("\n📄 Lista de Pedidos:")
    datos = []
    for p in pedidos.find():
        fila = [
            p.get("codigo_pedido", ""),
            p.get("fecha_pedido", ""),
            p.get("monto_total", 0),
            str(p.get("cliente_id", ""))
        ]
        datos.append(fila)

    headers = ["Código Pedido", "Fecha", "Monto Total", "Cliente ID"]
    print(tabulate(datos, headers=headers, tablefmt="grid"))


def eliminar_pedido():
    codigo = input("Código del pedido a eliminar: ").strip()
    pedido = pedidos.find_one({"codigo_pedido": codigo})
    if not pedido:
        print("❌ Pedido no encontrado.")
        return

    print(f"\nPedido encontrado: Fecha: {pedido['fecha_pedido']}, Total: ${pedido['monto_total']}")
    confirmacion = input("¿Estás seguro que deseas eliminar este pedido? (s/n): ").strip().lower()
    if confirmacion == "s":
        pedidos.delete_one({"codigo_pedido": codigo})
        print("🗑️ Pedido eliminado.")
    else:
        print("❌ Eliminación cancelada.")



def modificar_pedido():
    codigo = input("Código del pedido a modificar: ").strip()
    pedido = pedidos.find_one({"codigo_pedido": codigo})
    if not pedido:
        print("❌ Pedido no encontrado.")
        return

    fecha = input(f"Fecha del pedido [{pedido['fecha_pedido']}]: ").strip() or pedido["fecha_pedido"]

    modificar = input("¿Deseas modificar los productos del pedido? (s/n): ").strip().lower()
    productos_pedido = pedido["productos"]

    if modificar == "s":
        productos_pedido = []
        while True:
            codigo_producto = input("Código de producto (ENTER para terminar): ").strip()
            if not codigo_producto:
                break
            try:
                cantidad = int(input("Cantidad: "))
            except:
                print("❌ Cantidad inválida.")
                continue

            producto = productos.find_one({"codigo_producto": codigo_producto})
            if not producto:
                print("❌ Producto no encontrado.")
                continue

            productos_pedido.append({
                "codigo_producto": codigo_producto,
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"]
            })

    monto_total = sum(p["cantidad"] * p["precio"] for p in productos_pedido)

    nuevos_datos = {
        "fecha_pedido": fecha,
        "productos": productos_pedido,
        "monto_total": monto_total
    }

    pedidos.update_one({"codigo_pedido": codigo}, {"$set": nuevos_datos})
    print("✏️ Pedido actualizado.")


# ========================= CONSULTAS =========================

def buscar_producto_en_pedido():
    codigo_pedido = input("Código del pedido: ").strip()
    pedido = pedidos.find_one({"codigo_pedido": codigo_pedido})

    if not pedido:
        print("❌ Pedido no encontrado.")
        return

    print(f"📦 Productos del pedido {codigo_pedido}:")
    datos = []
    for item in pedido.get("productos", []):
        producto = productos.find_one({"codigo_producto": item.get("producto_id")})
        if producto:
            datos.append([
                producto.get("codigo_producto"),
                producto.get("nombre"),
                item.get("cantidad"),
                item.get("precio")
            ])
    if datos:
        headers = ["Código", "Nombre", "Cantidad", "Precio"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))
    else:
        print("⚠️ No hay productos registrados en este pedido.")

def buscar_pedidos_por_fecha():
    fecha = input("Ingrese la fecha (YYYY-MM-DD): ").strip()
    resultados = pedidos.find({"fecha_pedido": fecha})

    datos = []
    for p in resultados:
        datos.append([
            p.get("codigo_pedido"),
            p.get("cliente_id"),
            p.get("fecha_pedido"),
            p.get("monto_total")
        ])

    if datos:
        headers = ["Código Pedido", "ID Cliente", "Fecha", "Monto Total"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))
    else:
        print("⚠️ No se encontraron pedidos en esa fecha.")

def buscar_clientes_por_ciudad():
    ciudad = input("Ingrese la ciudad: ").strip().lower()
    resultados = clientes.find({"direccion.ciudad": {"$regex": f"^{ciudad}$", "$options": "i"}})

    datos = []
    for c in resultados:
        datos.append([
            c.get("identificador_cliente"),
            c.get("nombres"),
            c.get("apellidos"),
            c.get("direccion", {}).get("calle", ""),
            c.get("direccion", {}).get("numero", ""),
            c.get("direccion", {}).get("ciudad", "")
        ])

    if datos:
        headers = ["ID Cliente", "Nombres", "Apellidos", "Calle", "Número", "Ciudad"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))
    else:
        print("⚠️ No se encontraron clientes en esa ciudad.")

def mostrar_pedidos_por_cliente():
    id_cliente = input("Ingrese el ID del cliente: ").strip()
    resultado = pedidos.find({"cliente_id": id_cliente})

    datos = []
    for p in resultado:
        datos.append([
            p.get("codigo_pedido"),
            p.get("fecha_pedido"),
            p.get("monto_total")
        ])

    if datos:
        headers = ["Código Pedido", "Fecha", "Monto Total"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))
    else:
        print("⚠️ El cliente no tiene pedidos registrados.")



# ========================= SUBMENÚS =========================

def menu_clientes():
    while True:
        print("\n--- Submenú Clientes ---")
        print("1. Agregar cliente")
        print("2. Mostrar clientes")
        print("3. Modificar cliente")
        print("4. Eliminar cliente")
        print("0. Volver")
        opcion = input("Opción: ")
        if opcion == "1":
            agregar_cliente()
        elif opcion == "2":
            listar_clientes()
        elif opcion == "3":
            modificar_cliente()
        elif opcion == "4":
            eliminar_cliente()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def menu_productos():
    while True:
        print("\n--- Submenú Productos ---")
        print("1. Agregar producto")
        print("2. Mostrar productos")
        print("3. Modificar producto")
        print("4. Eliminar producto")
        print("0. Volver")
        opcion = input("Opción: ")
        if opcion == "1":
            agregar_producto()
        elif opcion == "2":
            listar_productos()
        elif opcion == "3":
            modificar_producto()
        elif opcion == "4":
            eliminar_producto()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def menu_pedidos():
    while True:
        print("\n--- Submenú Pedidos ---")
        print("1. Agregar pedido")
        print("2. Mostrar pedidos")
        print("3. Modificar pedido")
        print("4. Eliminar pedido")
        print("0. Volver")
        opcion = input("Opción: ")
        if opcion == "1":
            agregar_pedido()
        elif opcion == "2":
            listar_pedidos()
        elif opcion == "3":
            modificar_pedido()
        elif opcion == "4":
            eliminar_pedido()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def menu_consultas():
    while True:
        print("\n📊 SUBMENÚ DE CONSULTAS")
        print("1. Buscar producto de un pedido")
        print("2. Buscar pedidos por fecha")
        print("3. Buscar clientes por ciudad")
        print("4. Mostrar pedidos por cliente")
        print("5. Volver al menú principal")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            buscar_producto_en_pedido()
        elif opcion == "2":
            buscar_pedidos_por_fecha()
        elif opcion == "3":
            buscar_clientes_por_ciudad()
        elif opcion == "4":
            mostrar_pedidos_por_cliente()
        elif opcion == "5":
            return
        else:
            print("❌ Opción inválida.")


# ========================= MENÚ PRINCIPAL =========================

def menu():
    while True:
        print("\n=== Menú ComercioTech ===")
        print("1. Clientes")
        print("2. Productos")
        print("3. Pedidos")
        print("4. Consultas")
        print("0. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            menu_clientes()
        elif opcion == "2":
            menu_productos()
        elif opcion == "3":
            menu_pedidos()
        elif opcion == "4":
            menu_consultas()
        elif opcion == "0":
            print("👋 Cerrando ComercioTech...")
            break
        else:
            print("❌ Opción no válida.")

if __name__ == "__main__":
    menu()
