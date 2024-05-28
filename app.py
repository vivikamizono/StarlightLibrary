from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from cryptography.fernet import Fernet

app = Flask(__name__)

# Gera uma chave para criptografar os dados da seção
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Configuração Flask-Session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_DIR"] = "/tmp/flask_session"
app.config["SECRET_KEY"] = key  # Usar a chave gerada como secret key

# Inicia a sessão
Session(app)

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/biblioteca"
db = SQLAlchemy(app)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100), nullable=False)

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@app.before_request
def before_request():
    if 'session_data' in session:
        encrypted_data = session['session_data']
        try:
            # Descriptografa os dados da sessão antes de cada requisição
            decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
            session['decrypted_data'] = decrypted_data.decode()
        except Exception as e:
            session.pop('session_data', None)
            session.pop('decrypted_data', None)

@app.after_request
def after_request(response):
    if 'decrypted_data' in session:
        decrypted_data = session['decrypted_data']
        # Criptografa os dados da sessão antes de salvá-los
        encrypted_data = cipher_suite.encrypt(decrypted_data.encode())
        session['session_data'] = encrypted_data.decode()
        session.pop('decrypted_data', None)
    return response

@app.route("/")
def index():
    livros = Livro.query.all()
    return render_template("index.html", livros=livros)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        livro = Livro(
            nome=request.form["nome"],
            autor=request.form["autor"],
            editora=request.form["editora"]
        )
        db.session.add(livro)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    livro = Livro.query.get(id)
    if request.method == "POST":
        livro.nome = request.form["nome"]
        livro.autor = request.form["autor"]
        livro.editora = request.form["editora"]
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("update.html", livro=livro)

@app.route("/delete/<int:id>")
def delete(id):
    livro = Livro.query.get(id)
    db.session.delete(livro)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/search", methods=["GET", "POST"])
def search():
    resultados = None
    if request.method == "POST":
        termo_nome = request.form["nome"]
        termo_autor = request.form["autor"]
        termo_editora = request.form["editora"]
        
        query = Livro.query
        
        if termo_nome:
            query = query.filter(Livro.nome.ilike(f"%{termo_nome}%"))
        if termo_autor:
            query = query.filter(Livro.autor.ilike(f"%{termo_autor}%"))
        if termo_editora:
            query = query.filter(Livro.editora.ilike(f"%{termo_editora}%"))
        
        resultados = query.all()
        
    return render_template("search.html", resultados=resultados)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = Login(
            nome=request.form["nome"],
            senha=request.form["senha"],
            email=request.form["email"]
        )
        db.session.add(login)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

