# coding: utf-8

from flask import Flask
from flask import json, jsonify, request, abort
import pymongo
import datetime
from bson.objectid import ObjectId
from werkzeug import Response
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.exceptions import default_exceptions
from pymongo.errors import InvalidId
from pymongo import ReturnDocument

################################################################################

"""
START IGNORE
"""
# From: https://gist.github.com/akhenakh/2954605
class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    return Response(
        json.dumps(
            dict(*args, **kwargs),
            cls=MongoJsonEncoder
        ),
        mimetype='application/json'
    )

def make_json_response(status_code, description):
    return jsonify({
        'status_code': status_code,
        'description': description
    })

def error_json_handler(exception):
    response = make_json_response(exception.code, exception.description)
    response.status_code = (exception.code
                            if isinstance(exception, HTTPException)
                            else 500)
    return response

def validate(dict, mandatory_keys):
    for key in mandatory_keys:
        if (key not in dict):
            raise BadRequest("The {0} field is mandatory.".format(key))
    return True

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

# From: http://flask.pocoo.org/snippets/56/ (modified)
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Headers'] = 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__)

app.debug = True

for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = error_json_handler

"""
END IGNORE
"""

################################################################################

# Setup PyMongo
client = pymongo.MongoClient("0.0.0.0", 27017)

# Variable que contiene la base de datos
db = client.shop

# Variables que contienen cada una de las colecciones
catalog_col = db.catalog
cart_col = db.carts

# Indexes
catalog_col.create_index([("type", 1)])


"""
CATALOG RESOURCE
"""

# Campos obligatorios para cada uno de los tipos de documento
mandatory_product_fields = ['title', 'type', 'stock', 'price']
mandatory_cart_fields = ['session']
mandatory_cart_product_fields = ['_id', 'quantity']

######
# [GET] /catalog/<id>
# Devuelve un documento dentro de la colección 'catalog'.
######
@app.route('/catalog/<id>', methods=['GET'])
@crossdomain(origin='*')
def catalog_get_single(id):
    # Llamanda a PyMongo
    product = catalog_col.find_one({'_id': ObjectId(id)})

    # Comprobamos si existe, si no lanzamos excepción.
    if product == None:
        abort(404)

    # Devolvemos el resultado convertido en JSON.
    return jsonify(product)

######
# [PUT] /catalog
# Añade un documento a la colección 'catalog'.
# Debe devolver el documento recién insertado.
# Debe comprobar que los campos obligatorios se especifican.
######
@app.route('/catalog', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*')
def catalog_create():
    # Obtenemos el 'body' de la petición HTTP
    data = request.get_json()

    # Validamos si los campos son obligatorios
    validate(data, mandatory_product_fields)

    # Insertamos el documento
    object_id = catalog_col.insert_one(data)

    # Devolvemos el elemento recién insertado
    return jsonify(data)

######
# [GET] /catalog[?type=<type_id>]
# Devuelve todo el catálogo.
# Se puede filtrar por categoría usando p.ej. /catalog?type=book
# No debe devolver todos los datos. Por cada documento debe devolver:
#    -> _id
#    -> title
#    -> price
#    -> stock
######
@app.route('/catalog', methods=['GET'])
@crossdomain(origin='*')
def catalog_get_list():
    return "To Do"

######
# [DELETE] /catalog/<id>
# Borra un documento de la colección 'catalog'.
# Si el documento no existe debe dar un error 404.
# Al borrar un producto, hay que borrarlo de todos los carritos.
######
@app.route('/catalog/<id>', methods=['DELETE'])
@crossdomain(origin='*')
def catalog_delete(id):
    return "To Do"

######
# [POST] /catalog/<id>
# Modifica un documento de la colección 'catalog'.
# Se debe reemplazar el documento.
# Debe comprobar que el documento tiene los campos obligatorios.
# Debe devolver el documento actualizado.
# Al editar un producto, hay que borrarlo de todos los carritos.
######
@app.route('/catalog/<id>', methods=['POST'])
@crossdomain(origin='*')
def catalog_update(id):
    return "To Do"

######
# [GET] /platform
# Devuelve las plataformas de videojuegos disponibles que hay en el catálogo y la suma de sus juegos.
######
@app.route('/platform', methods=['GET'])
@crossdomain(origin='*')
def get_types():
    return "To Do"

"""
CART RESOURCE
"""

######
# [PUT] /cart
# Añade un documento a la colección 'carts'.
# Debe devolver el documento recién insertado.
# Debe comprobar que los campos obligatorios se especifican ('session').
# Automáticamente debe iniciar los campos:
#   - 'products' con el valor de un array vacio ([]).
#   - 'status' con el valor 'active'.
######
@app.route('/cart', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*')
def cart_create():
    return "To Do"

######
# [GET] /cart
# Devuelve todo los carros.
######
@app.route('/cart', methods=['GET'])
@crossdomain(origin='*')
def cart_get_list():
    return "To Do"

######
# [GET] /cart/<id>
# Devuelve un documento dentro de la colección 'cart'.
######
@app.route('/cart/<id>', methods=['GET'])
@crossdomain(origin='*')
def cart_get_single(id):
    return "To Do"

######
# [DELETE] /cart/<id>
# Borra un documento de la colección 'cart'.
# Si el documento no existe debe dar un error 404.
# Al borrar un carro, hay que actualizar el stock del catálogo (devolver el stock).
######
@app.route('/cart/<id>', methods=['DELETE'])
@crossdomain(origin='*')
def cart_delete(id):
    return "To Do"

######
# [POST] /cart/<id>
# Borra un documento de la colección 'cart'.
# Si el documento no existe debe dar un error 404.
# NOTA: Este método debe ignorar las modificaciones sobre 'products'.
######
@app.route('/cart/<id>', methods=['POST'])
@crossdomain(origin='*')
def cart_update(id):
    return "To Do"

######
# [PUT] /cart/<id>/product
# Añade un producto a un carrito (al array 'products' de un documento de 'carts')
# Debe devolver el documento recién insertado.
# Debe comprobar que los campos obligatorios se especifican ('_id', 'title', 'quantity').
# Si el producto indicado no existe, debe dar un error 400.
# Si el carrito no existe debe dar un error 404.
# Debe modificar el stock del producto añadido.
######
@app.route('/cart/<id>/product', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*')
def add_cart_product(id):
    return "To Do"

######
# [DELETE] /cart/<id>/product/<product_id>
# Borra un producto de un carrito.
# Si el carrito no existe debe dar un error 404.
# Al borrar un producto, hay que borrarlo de todos los carritos.
# Debe modificar el stock del producto añadido (devolverlo).
######
@app.route('/cart/<id>/product/<product_id>', methods=['DELETE'])
@crossdomain(origin='*')
def delete_cart_product(id, product_id):
    return "To Do"

################################################################################

@app.errorhandler(InvalidId)
def all_exception_handler(error):
    return make_json_response(400, 'Invalid ID')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
