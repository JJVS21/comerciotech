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
    print("\n📦 Lista de Productos:")
    datos = []
    for p in productos.find():
        fila = [
            p.get("codigo_producto", ""),
            p.get("nombre", ""),
            p.get("tipo", ""),
            p.get("precio", 0)
        ]
        datos.append(fila)

    headers = ["Código", "Nombre", "Tipo", "Precio"]
    print(tabulate(datos, headers=headers, tablefmt="grid"))


def eliminar_producto():
    codigo = input("Código del producto a eliminar: ").strip()
    producto = productos.find_one({"codigo_producto": codigo})
    if not producto:
        print("❌ Producto no encontrado.")
        return

    print(f"\nProducto encontrado: {producto['nombre']}, Tipo: {producto['tipo']}, Precio: {producto['precio']}")
    confirmacion = input("¿Estás seguro que deseas eliminar este producto? (s/n): ").strip().lower()
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

    print("Deja en blanco si no deseas cambiar un campo.")
    nuevo_codigo = input(f"Código [{producto['codigo_producto']}]: ").strip() or producto['codigo_producto']
    nombre = input(f"Nombre [{producto['nombre']}]: ").strip() or producto['nombre']
    tipo = input(f"Tipo [{producto['tipo']}]: ").strip() or producto['tipo']
    precio_input = input(f"Precio [{producto['precio']}]: ").strip()
    precio = float(precio_input) if precio_input else producto['precio']

    nuevos_datos = {
        "codigo_producto": nuevo_codigo,
        "nombre": nombre,
        "tipo": tipo,
        "precio": precio
    }

    productos.update_one({"codigo_producto": codigo}, {"$set": nuevos_datos})

# ========================= PEDIDOS =========================

def agregar_pedido():
    codigo = input("Código del pedido: ").strip()
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


    fecha = input("Fecha del pedido (YYYY-MM-DD): ").strip()
    productos_pedido = []
    while True:
        id_producto = input("ID de producto (ENTER para terminar): ").strip()
        if not id_producto:
            break
        cantidad = int(input("Cantidad: "))
        prod = productos.find_one({"_id": ObjectId(id_producto)})
        if not prod:
            print("❌ Producto no encontrado.")
            continue
        productos_pedido.append({
            "producto_id": prod["_id"],
            "nombre": prod["nombre"],
            "cantidad": cantidad,
            "precio": prod["precio"]
        })

    monto_total = sum(p["cantidad"] * p["precio"] for p in productos_pedido)

    pedido = {
        "cliente_id": cliente["_id"],
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

def mostrar_pedidos_por_cliente():
    id_cliente = input("ID del cliente: ").strip()
    try:
        cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
        if not cliente:
            print("❌ Cliente no encontrado.")
            return
        print(f"📦 Pedidos de {cliente['nombres']} {cliente['apellidos']}:")
        for p in pedidos.find({"cliente_id": ObjectId(id_cliente)}):
            print(p)
    except:
        print("❌ Error al buscar pedidos.")

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
        print("\n--- Submenú Consultas ---")
        print("1. Mostrar pedidos por cliente")
        print("0. Volver")
        opcion = input("Opción: ")
        if opcion == "1":
            mostrar_pedidos_por_cliente()
        elif opcion == "0":
            break
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
