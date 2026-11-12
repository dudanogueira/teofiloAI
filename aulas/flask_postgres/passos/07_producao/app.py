"""Contador por usuário — passo 07: pronto para produção (gunicorn)."""
import os

# Documentação do Flask: https://flask.palletsprojects.com/en/stable/
# Guia rápido (rotas, templates, formulários): https://flask.palletsprojects.com/en/stable/quickstart/
from flask import Flask, flash, redirect, render_template, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from sqlalchemy import String, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, Regexp

app = Flask(__name__)

# Configuração do Flask: https://flask.palletsprojects.com/en/stable/config/
# A configuração vem de variáveis de ambiente, nunca escrita no código.
# Quem sobe pelo Compose recebe DATABASE_URL do docker-compose.yml.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
# SECRET_KEY: https://flask.palletsprojects.com/en/stable/config/#SECRET_KEY
# A SECRET_KEY assina o cookie de sessão: quem a conhece consegue se passar por
# qualquer usuário. Por isso ela é obrigatória e vem do .env.
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Flask-SQLAlchemy (integração Flask + banco): https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
db = SQLAlchemy(app)

# CSRF no Flask-WTF: https://flask-wtf.readthedocs.io/en/latest/csrf/
# Segurança em apps Flask (CSRF, cookies...): https://flask.palletsprojects.com/en/stable/web-security/
# Proteção CSRF em TODO POST do app: sem o token escondido no formulário, o Flask
# responde 400. Isso impede outro site de enviar formulários em nome de quem está
# logado aqui (inclusive o "Sair", que não é um FlaskForm).
CSRFProtect(app)

# Flask-Login (sessão de usuário logado): https://flask-login.readthedocs.io/en/latest/
login_manager = LoginManager(app)
login_manager.login_view = "login"  # para onde mandar quem não está logado
login_manager.login_message = "Faça login para continuar."


# Modelos e tabelas: https://flask-sqlalchemy.readthedocs.io/en/stable/models/
class Usuario(UserMixin, db.Model):
    """Uma linha da tabela `usuarios`. Cada usuário tem o seu próprio contador.

    O UserMixin dá ao modelo o que o Flask-Login precisa (is_authenticated, get_id...).
    """

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True)
    # Guardamos só o *hash* da senha: nem quem tem acesso ao banco descobre a senha.
    senha_hash: Mapped[str] = mapped_column(String(255))
    contador: Mapped[int] = mapped_column(default=0)

    # Hash de senha do Werkzeug (que vem junto com o Flask):
    # https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security
    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def confere_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


@login_manager.user_loader
def carregar_usuario(id_usuario: str):
    """O cookie de sessão guarda só o id; a cada requisição buscamos o usuário."""
    return db.session.get(Usuario, int(id_usuario))


# Formulários com Flask-WTF: https://flask-wtf.readthedocs.io/en/latest/form/
# Validadores do WTForms: https://wtforms.readthedocs.io/en/3.2.x/validators/
# Formulários do Flask-WTF: validam os campos e já incluem o token CSRF.
class FormCadastro(FlaskForm):
    nome = StringField(
        "Usuário",
        validators=[
            InputRequired(),
            Length(3, 50),
            Regexp(r"^[A-Za-z0-9_.-]+$", message="Use só letras, números, _ . ou -"),
        ],
    )
    senha = PasswordField("Senha", validators=[InputRequired(), Length(min=8)])
    confirmacao = PasswordField(
        "Repita a senha",
        validators=[InputRequired(), EqualTo("senha", message="As senhas não conferem")],
    )
    enviar = SubmitField("Criar conta")


class FormLogin(FlaskForm):
    nome = StringField("Usuário", validators=[InputRequired()])
    senha = PasswordField("Senha", validators=[InputRequired()])
    enviar = SubmitField("Entrar")


# create_all: https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/#create-the-tables
# Cria as tabelas que ainda não existem (as que já existem ficam como estão).
with app.app_context():
    db.create_all()
    # O gunicorn (com --preload) carrega este arquivo uma vez e depois cria cópias
    # do processo (workers). Fechamos as conexões abertas aqui para que cada worker
    # abra as suas: uma conexão de banco não pode ser dividida entre processos.
    db.engine.dispose()


# Rotas: https://flask.palletsprojects.com/en/stable/quickstart/#routing
@app.route("/")
@login_required
def inicio():
    return render_template("inicio.html")


# Métodos HTTP (GET/POST) nas rotas: https://flask.palletsprojects.com/en/stable/quickstart/#http-methods
# Mensagens flash: https://flask.palletsprojects.com/en/stable/patterns/flashing/
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = FormCadastro()
    if form.validate_on_submit():
        usuario = Usuario(nome=form.nome.data)
        usuario.definir_senha(form.senha.data)
        db.session.add(usuario)
        try:
            db.session.commit()
        except IntegrityError:  # a coluna `nome` é unique: o banco recusa repetidos
            db.session.rollback()
            form.nome.errors.append("Este nome de usuário já existe.")
        else:
            flash("Conta criada! Agora é só entrar.")
            return redirect(url_for("login"))
    return render_template("cadastro.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = FormLogin()
    if form.validate_on_submit():
        usuario = db.session.scalar(select(Usuario).where(Usuario.nome == form.nome.data))
        if usuario and usuario.confere_senha(form.senha.data):
            login_user(usuario)
            return redirect(url_for("inicio"))
        # Mensagem genérica de propósito: não contamos se o usuário existe.
        flash("Usuário ou senha incorretos.")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu.")
    return redirect(url_for("login"))


# UPDATE com SQLAlchemy: https://docs.sqlalchemy.org/en/20/tutorial/data_update.html
def somar_ao_contador(valor: int) -> None:
    """Soma `valor` ao contador de quem está logado, direto no banco.

    Fazemos `UPDATE usuarios SET contador = contador + 1 WHERE id = ...` em vez de
    ler o número no Python, somar e gravar: com dois cliques ao mesmo tempo (duas
    abas, por exemplo), o jeito "ler-somar-gravar" pode perder um dos cliques.
    O banco faz a conta de forma atômica.
    """
    db.session.execute(
        update(Usuario)
        .where(Usuario.id == current_user.id)
        .values(contador=Usuario.contador + valor)
    )
    db.session.commit()


# Só POST: um GET (link, robô de busca, pré-carregamento do navegador) nunca deve
# mudar dados. E o POST passa pela proteção CSRF.
@app.route("/incrementar", methods=["POST"])
@login_required
def incrementar():
    somar_ao_contador(+1)
    return redirect(url_for("inicio"))


@app.route("/decrementar", methods=["POST"])
@login_required
def decrementar():
    somar_ao_contador(-1)
    return redirect(url_for("inicio"))


@app.route("/saude")
def saude():
    # Pergunta a versão ao Postgres: se responder, a conexão está funcionando.
    versao = db.session.execute(text("SELECT version()")).scalar()
    usuarios = db.session.execute(text("SELECT count(*) FROM usuarios")).scalar()
    return {"banco": "ok", "versao": versao, "usuarios": usuarios}


# Servidor de desenvolvimento do Flask: https://flask.palletsprojects.com/en/stable/server/
if __name__ == "__main__":
    # Só para desenvolvimento. No contêiner quem roda o app é o gunicorn (veja o Dockerfile).
    # 0.0.0.0 = aceitar conexões de fora da máquina (vai importar no Docker).
    # Porta 8000, e não a 5000 padrão: no Mac a 5000 é do AirPlay Receiver.
    app.run(host="0.0.0.0", port=8000)
