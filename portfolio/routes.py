from flask import render_template, url_for, redirect
from portfolio import app, database, bcrypt
from portfolio.models import Usuario, Projeto
from flask_login import login_required, login_user, logout_user, current_user
from portfolio.forms import FormLogin, FormCriarConta, FormProjeto
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET","POST"])
def homepage():
    usuario = {current_user}
    fotos = Projeto.query.order_by(Projeto.titulo).all()
    return render_template("homepage.html", projeto=fotos, usuario=usuario)




@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))

    return render_template("adminlogin.html", form=form_login)

@app.route("/perfil/<id_usuario>",methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        form_foto = FormProjeto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   app.config["UPLOAD_FOLDER"],
                                   nome_seguro)
            arquivo.save(caminho)
            projeto = Projeto(imagem=nome_seguro, id_usuario=current_user.id, titulo=form_foto.titulo.data, descricao=form_foto.descricao.data, link=form_foto.link.data)
            database.session.add(projeto)
            database.session.commit()
            return redirect(url_for("perfil", id_usuario= current_user.id))
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data,
                          senha=senha,
                          email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criarconta)


@app.route("/feed")
@login_required
def feed():
    fotos = Projeto.query.order_by(Projeto.data_criacao.desc()).all()
    return render_template("homepage.html", fotos=fotos)

