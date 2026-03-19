from fastapi import FastAPI
import mysql.connector
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()


conn = mysql.connector.connect(
    host="localhost", user="root", password="", port=3307, database="facturacion"
)


# clase cliente
class Cliente(BaseModel):
    Nombre: str
    Apellido: str
    Telefono: str
    Nit: str


# clase prdoucto
class Producto(BaseModel):
    Nombre: str
    Precio: float
    Existencia: int


# clase factura
class ItemDetalle(BaseModel):
    id_producto: int
    Cantidad: int


class Factura(BaseModel):
    id_cliente: int
    productos: List[ItemDetalle]


@app.get("/")
def get():
    return "Bienvenidos a FastAPI con MySQL"


# clientes
# obtener clientes
@app.get("/clientes")
def getClientes():
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# get cliente por id
@app.get("/clientes/{id_cliente}")
def getIdCliente(id_cliente: int):
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM clientes WHERE id_cliente = %s"
        cursor.execute(sql, (id_cliente,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# agregar cliente
@app.post("/crear_cliente")
def addCliente(Cliente: Cliente):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO clientes (Nombre, Apellido, Telefono, Nit) VALUES (%s, %s, %s, %s)"
        values = (Cliente.Nombre, Cliente.Apellido, Cliente.Telefono, Cliente.Nit)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        return {"message": "Cliente agregado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


# actualizar cliente
@app.put("/actualizar_cliente/{id_cliente}")
def updateCliente(id_cliente: int, Cliente: Cliente):
    try:
        cursor = conn.cursor()
        sql = "UPDATE clientes SET Nombre = %s, Apellido = %s, Telefono = %s, Nit = %s WHERE id_cliente = %s"
        values = (
            Cliente.Nombre,
            Cliente.Apellido,
            Cliente.Telefono,
            Cliente.Nit,
            id_cliente,
        )
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        return {"message": "Cliente actualizado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


# eliminar cliente
@app.delete("/eliminar_cliente/{id_cliente}")
def deleteCliente(id_cliente: int):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM clientes WHERE id_cliente = %s"
        cursor.execute(sql, (id_cliente,))
        conn.commit()
        cursor.close()
        return {"message": "Cliente eliminado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


#
#
#
#

# productos


# get productos
@app.get("/Productos")
def getProductos():
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# get producto por id
@app.get("/Productos/{id_producto}")
def getIdProducto(id_producto: int):
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM productos WHERE id_producto = %s"
        cursor.execute(sql, (id_producto,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# agregar producto
@app.post("/crear_producto")
def addProducto(Producto: Producto):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO productos (Nombre, Precio, Existencia) VALUES (%s, %s, %s)"
        values = (Producto.Nombre, Producto.Precio, Producto.Existencia)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        return {"message": "Producto agregado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


# actualizar producto
@app.put("/actualizar_producto/{id_producto}")
def updateProducto(id_producto: int, Producto: Producto):
    try:
        cursor = conn.cursor()
        sql = "UPDATE productos SET Nombre = %s, Precio = %s, Existencia = %s WHERE id_producto = %s"
        values = (
            Producto.Nombre,
            Producto.Precio,
            Producto.Existencia,
            id_producto,
        )
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        return {"message": "Producto actualizado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


# eliminar producto
@app.delete("/eliminar_producto/{id_producto}")
def deleteProducto(id_producto: int):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM productos WHERE id_producto = %s"
        cursor.execute(sql, (id_producto,))
        conn.commit()
        cursor.close()
        return {"message": "Producto eliminado exitosamente"}
    except Exception as e:
        return {"error": str(e)}


# factura
# get facturas
@app.get("/facturas")
def getFacturas():
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM factura")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# get factura por id
@app.get("/facturas/{id_factura}")
def getIdFactura(id_factura: int):
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM factura WHERE id_factura = %s "
        cursor.execute(sql, (id_factura,))
        factura = cursor.fetchone()
        if not factura:
            return {"error": "Factura no encontrada"}

        # obtener detalles de la factura
        sql_detalle = "SELECT df.id_producto, p.Nombre, df.Cantidad, df.Precio_unitario FROM detalle_factura df JOIN productos p ON df.id_producto = p.id_producto WHERE df.id_factura = %s"
        cursor.execute(sql_detalle, (id_factura,))
        detalles = cursor.fetchall()
        cursor.close()
        # return {"factura": factura, "detalles": detalles}
        factura["productos"] = detalles
        return factura
    except Exception as e:
        return {"error": str(e)}


# crear factura


@app.post("/crear_factura")
def addFactura(factura: Factura):
    try:
        cursor = conn.cursor(dictionary=True)
        # ver si el cliente existe
        cursor.execute(
            "SELECT id_cliente FROM clientes WHERE id_cliente = %s",
            (factura.id_cliente,),
        )
        if not cursor.fetchone():
            return {
                "error": f"El cliente con ID {factura.id_cliente} no existe. Créalo primero."
            }

        sql = "INSERT INTO factura (id_cliente, Total, Fecha) VALUES (%s, %s, %s)"
        values = (factura.id_cliente, 0, datetime.now())
        cursor.execute(sql, values)
        id_de_factura = cursor.lastrowid

        total = 0

        for item in factura.productos:
            # obtener precio y existencia del producto
            cursor.execute(
                "SELECT Precio, Existencia FROM productos WHERE id_producto = %s",
                (item.id_producto,),
            )
            producto = cursor.fetchone()
            if not producto or producto["Existencia"] < item.Cantidad:
                conn.rollback()
                return {
                    "error": f"Producto con id {item.id_producto} no disponible en cantidad suficiente"
                }

            subtotal = producto["Precio"] * item.Cantidad
            total += subtotal
            # insertar detalle de factura
            cursor.execute(
                "INSERT INTO detalle_factura (id_factura, id_producto, Cantidad, Precio_unitario) VALUES (%s, %s, %s, %s)",
                (id_de_factura, item.id_producto, item.Cantidad, producto["Precio"]),
            )
            # actualizar existencia del producto
            nueva_existencia = producto["Existencia"] - item.Cantidad
            cursor.execute(
                "UPDATE productos SET Existencia = %s WHERE id_producto = %s",
                (nueva_existencia, item.id_producto),
            )

            # actualizar total de la factura
        cursor.execute(
            "UPDATE factura SET Total = %s WHERE id_factura = %s",
            (total, id_de_factura),
        )
        conn.commit()
        cursor.close()
        return {"message": "Factura creada exitosamente", "id_factura": id_de_factura}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# actualizar factura
@app.put("/actualizar_factura/{id_factura}")
def updateFactura(id_factura: int, factura: Factura):
    try:
        cursor = conn.cursor(dictionary=True)
        # ver si la factura existe
        cursor.execute(
            "SELECT id_factura FROM factura WHERE id_factura = %s", (id_factura,)
        )
        if not cursor.fetchone():
            return {"error": f"Factura con ID {id_factura} no existe."}

        # actualizar cliente de la factura
        cursor.execute(
            "UPDATE factura SET id_cliente = %s, Fecha = %s WHERE id_factura = %s",
            (factura.id_cliente, datetime.now(), id_factura),
        )

        # eliminar detalles anteriores
        cursor.execute(
            "DELETE FROM detalle_factura WHERE id_factura = %s", (id_factura,)
        )

        total = 0

        for item in factura.productos:
            # obtener precio y existencia del producto
            cursor.execute(
                "SELECT Precio, Existencia FROM productos WHERE id_producto = %s",
                (item.id_producto,),
            )
            producto = cursor.fetchone()
            if not producto or producto["Existencia"] < item.Cantidad:
                conn.rollback()
                return {
                    "error": f"Producto con id {item.id_producto} no disponible en cantidad suficiente"
                }

            subtotal = producto["Precio"] * item.Cantidad
            total += subtotal
            # insertar nuevo detalle de factura
            cursor.execute(
                "INSERT INTO detalle_factura (id_factura, id_producto, Cantidad, Precio_unitario) VALUES (%s, %s, %s, %s)",
                (id_factura, item.id_producto, item.Cantidad, producto["Precio"]),
            )
            # actualizar existencia del producto
            nueva_existencia = producto["Existencia"] - item.Cantidad
            cursor.execute(
                "UPDATE productos SET Existencia = %s WHERE id_producto = %s",
                (nueva_existencia, item.id_producto),
            )

        # actualizar total de la factura
        cursor.execute(
            "UPDATE factura SET Total = %s WHERE id_factura = %s",
            (total, id_factura),
        )
        conn.commit()
        cursor.close()
        return {"message": "Factura actualizada exitosamente"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


# eliminar factura
@app.delete("/eliminar_factura/{id_factura}")
def deleteFactura(id_factura: int):
    try:
        cursor = conn.cursor()
        # eliminar detalles de la factura
        cursor.execute(
            "DELETE FROM detalle_factura WHERE id_factura = %s", (id_factura,)
        )
        # eliminar factura
        cursor.execute("DELETE FROM factura WHERE id_factura = %s", (id_factura,))
        conn.commit()
        cursor.close()
        return {"message": "Factura eliminada exitosamente"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
