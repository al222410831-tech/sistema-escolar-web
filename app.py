from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "siage_secret"

# CONEXIÓN A TU MONGODB (Asegúrate de que los datos sean correctos)
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]
usuarios_col = db["usuarios"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    matricula = request.form.get("matricula")
    nombre = request.form.get("nombre")
    password = request.form.get("password")
    
    datos = {
        "matricula": matricula,
        "nombre": nombre,
        "password": password
    }

    if matricula.startswith("111"):
        # Es Maestro: pedimos materias
        datos["rol"] = "maestro"
        datos["materia1"] = request.form.get("materia1")
        datos["materia2"] = request.form.get("materia2")
    elif matricula.startswith("222"):
        # Es Alumno
        datos["rol"] = "alumno"
    else:
        return "<h1>Error: La matrícula debe empezar con 111 o 222</h1><a href='/registro'>Volver</a>"

    usuarios_col.insert_one(datos)
    return "<h1>✅ Registro exitoso en MongoDB</h1><a href='/'>Ir al Inicio</a>"

@app.route("/validar", methods=["POST"])
def validar():
    matricula = request.form.get("usuario")
    user = usuarios_col.find_one({"matricula": matricula})
    
    if user:
        if matricula.startswith("111"):
            return f"<h1>Bienvenido Maestro {user['nombre']}</h1><p>Tus clases: {user['materia1']} y {user['materia2']}</p>"
        else:
            return f"<h1>Bienvenido Alumno {user['nombre']}</h1>"
    return "<h1>Usuario no encontrado</h1><a href='/'>Volver</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
