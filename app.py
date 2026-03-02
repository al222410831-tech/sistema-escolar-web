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
            alumnos = list(usuarios_col.find({"rol": "alumno", "semestre": user.get("semestre")}))
            return render_template("menu_maestro.html", user=user, alumnos=alumnos)
        else:
            return render_template("menu_alumno.html", user=user)
    return "<h1>❌ Datos incorrectos</h1><a href='/login'>Volver</a>"

@app.route("/guardar_datos_alumno", methods=["POST"])
def guardar_datos_alumno():
    matricula = request.form.get("matricula")
    # Recibimos las 4 notas
    n1 = float(request.form.get("n1", 0))
    n2 = float(request.form.get("n2", 0))
    n3 = float(request.form.get("n3", 0))
    n4 = float(request.form.get("n4", 0))
    reporte = request.form.get("reporte", "")
    
    # Calculamos el promedio
    promedio = (n1 + n2 + n3 + n4) / 4
    
    usuarios_col.update_one(
        {"matricula": matricula},
        {"$set": {
            "n1": n1, "n2": n2, "n3": n3, "n4": n4, 
            "promedio": round(promedio, 2), 
            "reporte": reporte
        }}
    )
    return "<h1>✅ Datos actualizados</h1><a href='/'>Regresar al inicio</a>"

@app.route("/eliminar_cuenta/<matricula>")
def eliminar_cuenta(matricula):
    usuarios_col.delete_one({"matricula": matricula})
    return "<h1>🗑️ Cuenta eliminada</h1><a href='/'>Inicio</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
