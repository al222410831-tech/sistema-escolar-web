from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# CONEXIÓN MONGODB
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]
usuarios_col = db["usuarios"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route("/validar", methods=["POST"])
def validar():
    matricula = request.form.get("usuario")
    password = request.form.get("password")
    user = usuarios_col.find_one({"matricula": matricula, "password": password})
    
    if user:
        if user.get("rol") == "maestro":
            # Filtramos alumnos por el mismo cuatrimestre que el maestro
            cuatri = user.get("semestre")
            alumnos = list(usuarios_col.find({"rol": "alumno", "semestre": cuatri}))
            return render_template("menu_maestro.html", user=user, alumnos=alumnos)
        else:
            return render_template("menu_alumno.html", user=user)
    return "<h1>❌ Datos incorrectos</h1><a href='/login'>Volver</a>"

@app.route("/guardar_nota", methods=["POST"])
def guardar_nota():
    matricula = request.form.get("matricula")
    calificacion = request.form.get("calificacion")
    reporte = request.form.get("reporte")
    
    usuarios_col.update_one(
        {"matricula": matricula},
        {"$set": {"calificacion": calificacion, "reporte": reporte}}
    )
    # Redirigir al inicio para evitar reenvío de formulario
    return "<h1>✅ Datos guardados correctamente</h1><a href='/'>Volver al Menú Principal</a>"

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    matricula = request.form.get("matricula")
    nombre = request.form.get("nombre")
    password = request.form.get("password")
    datos = {"matricula": matricula, "nombre": nombre, "password": password}
    
    if matricula.startswith("111"):
        datos.update({
            "rol": "maestro", 
            "materia1": request.form.get("materia1"), 
            "materia2": request.form.get("materia2"), 
            "semestre": request.form.get("semestre_maestro"),
            "calificacion": "", "reporte": "" # Campos vacíos para evitar errores
        })
    elif matricula.startswith("222"):
        datos.update({
            "rol": "alumno", 
            "semestre": request.form.get("semestre_alumno"),
            "calificacion": "0", "reporte": "Sin reporte"
        })
    
    usuarios_col.insert_one(datos)
    return "<h1>✅ Registro exitoso</h1><a href='/login'>Ir al Login</a>"

@app.route("/eliminar_cuenta/<matricula>")
def eliminar_cuenta(matricula):
    usuarios_col.delete_one({"matricula": matricula})
    return "<h1>🗑️ Cuenta eliminada</h1><a href='/'>Inicio</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
