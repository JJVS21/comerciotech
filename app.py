from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secreto"

# Conexión a MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["comerciotech"]

# Colecciones
clientes = db["clientes"]
productos = db["productos"]
pedidos = db["pedidos"]

# -------------------- RUTA: Página principal --------------------

@app.route("/")
def index():
    return render_template("index.html")

# -------------------- CLIENTES --------------------

@app.route("/clientes")
def mostrar_clientes():
    lista_clientes = list(clientes.find())
    return render_template("clientes.html", clientes=lista_clientes)

@app.route("/clientes/agregar", methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        calle = request.form.get("calle", "").strip()
        numero = request.form.get("numero", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        
        # Validaciones
        if not (nombres and apellidos and calle and numero and ciudad):
            flash("Todos los campos son obligatorios", "error")
            return redirect(url_for("mostrar_clientes"))

        if len(nombres) < 2 or len(apellidos) < 2:
            flash("Nombres y apellidos deben tener al menos 2 caracteres", "error")
            return redirect(url_for("mostrar_clientes"))

        if not numero.isdigit():
            flash("El número de calle debe ser numérico", "error")
            return redirect(url_for("mostrar_clientes"))

        cliente = {
            "nombres": nombres,
            "apellidos": apellidos,
            "calle": calle,
            "numero": int(numero),
            "ciudad": ciudad,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        clientes.insert_one(cliente)
        flash("Cliente agregado correctamente", "success")
        return redirect(url_for("mostrar_clientes"))

    return render_template("clientes.html")

@app.route("/clientes/eliminar/<cliente_id>", methods=["POST"])
def eliminar_cliente(cliente_id):
    clientes.delete_one({"_id": ObjectId(cliente_id)})
    flash("Cliente eliminado exitosamente", "success")
    return redirect(url_for("mostrar_clientes"))


# -------------------- PRODUCTOS --------------------

@app.route("/productos")
def mostrar_productos():
    lista_productos = list(productos.find())
    return render_template("productos.html", productos=lista_productos)

@app.route("/productos/agregar", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()

    if not nombre or not precio:
        flash("Todos los campos son obligatorios", "error")
        return redirect(url_for("mostrar_productos"))

    try:
        precio = float(precio)
    except ValueError:
        flash("El precio debe ser un número", "error")
        return redirect(url_for("mostrar_productos"))

    producto = {"nombre": nombre, "precio": precio}
    productos.insert_one(producto)
    flash("Producto agregado", "success")
    return redirect(url_for("mostrar_productos"))

# -------------------- PEDIDOS --------------------

@app.route("/pedidos")
def mostrar_pedidos():
    lista_pedidos = list(pedidos.find())
    lista_clientes = list(clientes.find())
    lista_productos = list(productos.find())
    return render_template("pedidos.html", pedidos=lista_pedidos, clientes=lista_clientes, productos=lista_productos)

@app.route("/pedidos/agregar", methods=["POST"])
def agregar_pedido():
    cliente_id = request.form.get("cliente")
    producto_id = request.form.get("producto")

    if not cliente_id or not producto_id:
        flash("Debes seleccionar cliente y producto", "error")
        return redirect(url_for("mostrar_pedidos"))

    cliente = clientes.find_one({"_id": ObjectId(cliente_id)})
    producto = productos.find_one({"_id": ObjectId(producto_id)})

    if not cliente or not producto:
        flash("Cliente o producto no encontrados", "error")
        return redirect(url_for("mostrar_pedidos"))

    pedido = {
        "cliente": f"{cliente['nombre']} {cliente['apellidos']}",
        "producto": producto["nombre"],
        "precio": producto["precio"]
    }

    pedidos.insert_one(pedido)
    flash("Pedido registrado exitosamente", "success")
    return redirect(url_for("mostrar_pedidos"))

# -------------------- CONSULTAS --------------------

@app.route("/consultas")
def consultas():
    return render_template("consultas.html")

@app.route("/consultas/resultado", methods=["POST"])
def consultas_resultado():
    nombre_cliente = request.form.get("nombre", "").strip()
    resultados = list(pedidos.find({"cliente": {"$regex": nombre_cliente, "$options": "i"}}))
    return render_template("consultas_resultado.html", pedidos=resultados, nombre=nombre_cliente)

# -------------------- MAIN --------------------

if __name__ == "__main__":
    app.run(debug=True)
