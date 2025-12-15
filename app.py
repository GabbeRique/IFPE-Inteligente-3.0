from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from firebase_config import auth, db
import requests
from google.cloud import firestore

app = Flask(__name__)
app.secret_key = "chave-super-secreta-do-gabriel"

API_KEY = "AIzaSyA23RqXJ2Z92E-B19hajBi5uumh6XbGvpw"


# ========== FUNÇÃO LOGIN FIREBASE ==========
def login_firebase(email, senha):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": senha,
        "returnSecureToken": True
    }

    r = requests.post(url, json=payload, timeout=10)
    return r.json()


# ========== TELA INICIAL ==========
@app.route("/")
def index():
    return render_template("telainicial.html")


# ========== CRIAR CONTA ==========
@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    if request.method == "POST":
        try:
            user = auth.create_user(
                email=request.form["email"],
                password=request.form["senha"],
                display_name=request.form["nome"]
            )

            db.collection("usuarios").document(user.uid).set({
                "nome": request.form["nome"],
                "email": request.form["email"],
                "curso": request.form["curso"],
                "turma": request.form["serie"],
                "pontos": 0,
                "locais_visitados": []
            })

            return redirect("/login")

        except Exception as e:
            print("ERRO CRIAR CONTA:", e)
            return "Erro ao criar conta"

    return render_template("criarconta.html")


# ========== LOGIN ==========
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        resultado = login_firebase(
            request.form["email"],
            request.form["senha"]
        )

        if "localId" in resultado:
            session.clear()
            session["user"] = resultado["localId"]
            session.permanent = True
            return redirect("/home")

        print("ERRO LOGIN:", resultado)
        return "Email ou senha incorretos."

    return render_template("telalogin.html")


# ============ HOME ============
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]
    doc = db.collection("usuarios").document(user_id).get()

    usuario = doc.to_dict() if doc.exists else {
        "nome": "Não encontrado",
        "curso": "Não informado",
        "turma": "Não informado",
        "pontos": 0
    }

    return render_template("home.html", usuario=usuario)


# ============ PERFIL ============
@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect("/login")

    doc = db.collection("usuarios").document(session["user"]).get()
    usuario = doc.to_dict() if doc.exists else {}

    return render_template("perfil.html", usuario=usuario)


# ============ OUTRAS ROTAS ============
@app.route("/config")
def configuracoes():
    if "user" not in session:
        return redirect("/login")
    return render_template("configuracoes.html")


@app.route("/ifpeflow")
def ifpeflow():
    if "user" not in session:
        return redirect("/login")
    return render_template("ifpeflow.html")


@app.route("/ecoscan")
def ecoscan():
    if "user" not in session:
        return redirect("/login")
    return render_template("ecoscan.html")


@app.route("/helpme")
def helpme():
    if "user" not in session:
        return redirect("/login")

    doc = db.collection("usuarios").document(session["user"]).get()
    usuario = doc.to_dict() if doc.exists else {}

    return render_template("helpme.html", usuario=usuario)


# ============ REGISTRAR LIXO ============
@app.route("/registrar_lixo", methods=["POST"])
def registrar_lixo():
    if "user" not in session:
        return jsonify({"erro": "não logado"}), 403

    dados = request.get_json()
    quantidade = int(dados.get("quantidade", 0))

    pontos = quantidade  # 1 lixo = 1 ponto

    ref = db.collection("usuarios").document(session["user"])
    user_data = ref.get().to_dict() or {}

    novo_total = user_data.get("pontos", 0) + pontos
    ref.update({"pontos": novo_total})

    return jsonify({
        "status": "ok",
        "pontos_adicionados": pontos,
        "novo_total": novo_total
    })


# ============ RANKING ============
@app.route("/ranking")
def ranking():
    user_id = session.get("user")

    usuarios = (
        db.collection("usuarios")
        .order_by("pontos", direction=firestore.Query.DESCENDING)
        .limit(5)
        .stream()
    )

    ranking = []
    for doc in usuarios:
        data = doc.to_dict()
        ranking.append({
            "id": doc.id,
            "nome": data.get("nome", "Sem nome"),
            "pontos": data.get("pontos", 0),
            "is_me": doc.id == user_id
        })

    return jsonify({"ranking": ranking})


# ============ EDITAR PERFIL ============
@app.route("/editarperfil")
def editarperfil():
    if "user" not in session:
        return redirect("/login")
    return render_template("editarperfil.html")


# ============ LOGOUT ============
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ============ RUN ============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
