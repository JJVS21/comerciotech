from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

# Conexión MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["comerciotech"]

clientes = db.clientes
productos = db.producto
pedidos = db.pedidos

# ──────── CLIENTES ────────
@app.route("/clientes")
def ver_clientes():
    lista = list(clientes.find())
    return render_template("clientes.html", clientes=lista)

@app.route("/clientes/agregar", methods=["POST"])
def agregar_cliente():
    nombres = request.form["nombres"]
    apellidos = request.form["apellidos"]
    calle = request.form["calle"]
    numero = request.form["numero"]
    ciudad = request.form["ciudad"]

    if not nombres or not apellidos or not ciudad or not numero.isdigit():
        return "Datos inválidos."

    cliente = {
        "nombres": nombres,
        "apellidos": apellidos,
        "direccion": {"calle": calle, "numero": numero, "ciudad": ciudad},
        "fecha_registro": datetime.datetime.now()
    }
    clientes.insert_one(cliente)
    return redirect(url_for("ver_clientes"))

@app.route("/clientes/eliminar/<id>")
def eliminar_cliente(id):
    clientes.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_clientes"))

# ──────── PRODUCTOS ────────
@app.route("/productos")
def ver_productos():
    lista = list(productos.find())
    return render_template("productos.html", productos=lista)

@app.route("/productos/agregar", methods=["POST"])
def agregar_producto():
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    vencimiento = request.form["vencimiento"]
    estado = request.form["estado"]

    if not codigo or not nombre or not precio or not stock or not estado:
        return "Todos los campos son obligatorios."

    try:
        precio = float(precio)
        stock = int(stock)
    except:
        return "Precio debe ser numérico y stock entero."

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "fecha_vencimiento": vencimiento,
        "estado": estado
    }
    productos.insert_one(producto)
    return redirect(url_for("ver_productos"))

@app.route("/productos/eliminar/<id>")
def eliminar_producto(id):
    productos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_productos"))

# ──────── PEDIDOS ────────
@app.route("/pedidos")
def ver_pedidos():
    lista = list(pedidos.find())
    clientes_lista = list(clientes.find())
    productos_lista = list(productos.find())
    return render_template("pedidos.html", pedidos=lista, clientes=clientes_lista, productos=productos_lista)

@app.route("/pedidos/agregar", methods=["POST"])
def agregar_pedido():
    cliente_id = request.form["cliente_id"]
    producto_id = request.form["producto_id"]
    cantidad = request.form["cantidad"]
    metodo_pago = request.form["metodo_pago"]

    if not cliente_id or not producto_id or not cantidad or not metodo_pago:
        return "Faltan datos obligatorios."

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return "La cantidad debe ser mayor que 0."
    except:
        return "Cantidad inválida."

    producto = productos.find_one({"_id": ObjectId(producto_id)})
    if not producto:
        return "Producto no encontrado."

    precio = producto["precio"]
    subtotal = precio * cantidad

    pedido = {
        "codigo_cliente": cliente_id,
        "fecha_pedido": datetime.datetime.now(),
        "productos": [{
            "codigo_producto": producto["codigo"],
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total_comprado": subtotal
        }],
        "monto_total": subtotal,
        "metodo_pago": metodo_pago
    }

    pedidos.insert_one(pedido)
    return redirect(url_for("ver_pedidos"))

@app.route("/pedidos/eliminar/<id>")
def eliminar_pedido(id):
    pedidos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_pedidos"))

# ──────── CONSULTAS ────────
@app.route("/consultas")
def consultas():
    return render_template("consultas.html")

@app.route("/consultas/producto_en_pedido", methods=["POST"])
def producto_en_pedido():
    codigo = request.form["codigo_producto"]
    resultados = pedidos.find({"productos.codigo_producto": codigo})
    return render_template("consultas_resultado.html", resultados=resultados, tipo=f"Pedidos con producto {codigo}")

@app.route("/consultas/pedidos_por_fecha", methods=["POST"])
def pedidos_por_fecha():
    fecha = request.form["fecha"]
    try:
        fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        fecha_fin = fecha_dt + datetime.timedelta(days=1)
    except:
        return "Formato de fecha incorrecto. Usa YYYY-MM-DD."

    resultados = pedidos.find({"fecha_pedido": {"$gte": fecha_dt, "$lt": fecha_fin}})
    return render_template("consultas_resultado.html", resultados=resultados, tipo=f"Pedidos del {fecha}")

@app.route("/consultas/por_ciudad", methods=["POST"])
def por_ciudad():
    ciudad = request.form["ciudad"]
    resultados = clientes.find({"direccion.ciudad": ciudad})
    return render_template("consultas_resultado.html", resultados=resultados, tipo=f"Clientes en {ciudad}")

@app.route("/consultas/pedidos_por_cliente", methods=["POST"])
def pedidos_por_cliente():
    cliente_id = request.form["cliente_id"]
    resultados = pedidos.find({"codigo_cliente": cliente_id})
    return render_template("consultas_resultado.html", resultados=resultados, tipo=f"Pedidos del cliente {cliente_id}")

# ──────── MAIN ────────
if __name__ == "__main__":
    app.run(debug=True)