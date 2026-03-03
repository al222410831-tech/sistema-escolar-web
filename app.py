from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# CONEXIÓN MONGODB
MONGO_URI = "mongodb+srv://al222410831_db_user:Daniel123@cluster0.iuigysp.mongodb.net/proyecto2?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["proyecto2"]

# DEFINICIÓN DE COLECCIONES
usuarios_col = db["usuarios"]
calif_col = db["calificaciones"]
reportes_col = db["reportes"]
horarios_col = db["horarios"]

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
            # Usamos .get() con un valor por defecto para evitar Error 500 si falta el semestre
            semestre_m = user.get("semestre", "N/A")
            alumnos = list(usuarios_col.find({"rol": "alumno", "semestre": semestre_m}))
            return render_template("menu_maestro.html", user=user, alumnos=alumnos)
        else:
            notas = list(calif_col.find({"matricula": matricula}))
            reps = list(reportes_col.find({"matricula": matricula}))
            # Pasamos la colección horarios_col para que el HTML del alumno funcione
            return render_template("menu_alumno.html", user=user, notas=notas, reportes=reps, horarios_col=horarios_col)
    
    return "<h1>❌ Credenciales incorrectas</h1><a href='/login'>Volver</a>"

@app.route("/guardar_materia", methods=["POST"])
def guardar_materia():
    matri = request.form.get("matricula")
    materia = request.form.get("materia_nombre")
    try:
        n1 = float(request.form.get("n1", 0))
        n2 = float(request.form.get("n2", 0))
        n3 = float(request.form.get("n3", 0))
        n4 = float(request.form.get("n4", 0))
        promedio = round((n1 + n2 + n3 + n4) / 4, 2)
        
        calif_col.update_one(
            {"matricula": matri, "materia": materia},
            {"$set": {"n1": n1, "n2": n2, "n3": n3, "n4": n4, "promedio": promedio}},
            upsert=True
        )
        
        rep_txt = request.form.get("reporte")
        if rep_txt:
            reportes_col.update_one(
                {"matricula": matri, "materia": materia},
                {"$set": {"texto": rep_txt}},
                upsert=True
            )
        return render_template("exito.html", mensaje="Datos guardados", destino="panel")
    except:
        return "<h1>❌ Error en los datos</h1><a href='/'>Volver</a>"

@app.route("/guardar_horario", methods=["POST"])
def guardar_horario():
    cuatri = request.form.get("cuatrimestre")
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
    
    for dia in dias:
        bloques = {}
        for i in range(1, 18):
            # Recogemos los inputs del formulario dinámico
            valor = request.form.get(f"{dia}_bloque_{i}")
            if valor:
                bloques[f"bloque_{i}"] = valor
        
        if bloques:
            # Actualizamos bloques específicos sin borrar otros maestros
            update_fields = {f"bloques.{k}": v for k, v in bloques.items()}
            horarios_col.update_one(
                {"cuatrimestre": cuatri, "dia": dia},
                {"$set": update_fields},
                upsert=True
            )
            
    return render_template("exito.html", mensaje="Horario actualizado", destino="panel")

@app.route("/guardar_usuario", methods=["POST"])
def guardar_usuario():
    matricula = request.form.get("matricula")
    datos = {
        "matricula": matricula, 
        "nombre": request.form.get("nombre"), 
        "password": request.form.get("password")
    }
    
    if matricula.startswith("111"):
        datos.update({
            "rol": "maestro", 
            "materia1": request.form.get("materia1"), 
            "materia2": request.form.get("materia2"), 
            "semestre": request.form.get("semestre_maestro")
        })
    else:
        datos.update({
            "rol": "alumno", 
            "semestre": request.form.get("semestre_alumno")
        })
        
    usuarios_col.insert_one(datos)
    return render_template("exito.html", mensaje="Registro exitoso", destino="inicio")

if __name__ == "__main__":
    # Configuración para Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
