from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/biblioteca"
db = SQLAlchemy(app)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100), nullable=False)

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
        
        resultados = Livro.query.filter(
            (Livro.nome == termo_nome) & 
            (Livro.autor == termo_autor) & 
            (Livro.editora == termo_editora)
        ).all()
    return render_template("search.html", resultados=resultados)


if __name__ == "__main__":
    app.run(debug=True)
