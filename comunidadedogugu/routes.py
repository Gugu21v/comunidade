from flask import render_template, redirect, url_for, request, flash, abort
from comunidadedogugu import app, database, bcrypt
from comunidadedogugu.forms import Login, CriarConta, EditarPerfil, FormCriarPost
from comunidadedogugu.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from datetime import datetime

@app.route('/')
#serve pra criar os caminhos do site ('/Gustavo/posts')
def home():
    posts = Post.query.order_by(Post.id.desc())
    usuarios = Usuario.query.all()
    return render_template("index.html", posts=posts, usuarios=usuarios, datetime=datetime)

@app.route('/inicio')
def inicio():
    return render_template("inicio.html")

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios=lista_usuarios)

@app.route('/login', methods=["GET", "POST"])
def login():
    form_login = Login()
    form_criar_conta = CriarConta()

    if form_login.validate_on_submit() and 'botao_logar' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash('Login feito com sucesso no email: {}'.format(form_login.email.data), 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('inicio'))
        else:
            flash('Falha no login. E-mail ou senha incorretos.', 'alert-danger')
    if form_criar_conta.validate_on_submit() and 'botao_criar_conta' in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(username=form_criar_conta.username.data, email=form_criar_conta.email.data, senha=senha_crypt, cidade=form_criar_conta.cidade.data, instagram=form_criar_conta.instagram.data)
        database.session.add(usuario)
        database.session.commit()
        flash('Conta criada com sucesso no email: {}'.format(form_criar_conta.email.data), 'alert-success')
        return redirect(url_for('inicio'))
    return render_template("login.html", form_login=form_login, form_criar_conta=form_criar_conta)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout realizado com sucesso', 'alert-success')
    return redirect(url_for('inicio'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template("perfil.html", foto_perfil=foto_perfil)

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form_criar_post = FormCriarPost()
    if form_criar_post.validate_on_submit():
        post = Post(titulo=form_criar_post.titulo.data, corpo=form_criar_post.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso! ', 'alert-success')
        return redirect(url_for('home'))
    return render_template("criar_post.html", form_criar_post=form_criar_post)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_interesses(form):
    lista_interesses = []
    for campo in form:
        if 'interesse_' in campo.name:
            if campo.data:
                lista_interesses.append(campo.label.text)
    return ';'.join(lista_interesses)

@app.route('/perfil/editar', methods=["GET", "POST"])
@login_required
def editar_perfil():
    form_editar_perfil = EditarPerfil()
    if form_editar_perfil.validate_on_submit():
        current_user.email = form_editar_perfil.email.data
        current_user.username = form_editar_perfil.username.data
        current_user.cidade = form_editar_perfil.cidade.data
        current_user.instagram = form_editar_perfil.instagram.data
        if form_editar_perfil.foto_perfil.data:
            nome_imagem = salvar_imagem(form_editar_perfil.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.interesses = atualizar_interesses(form_editar_perfil)
        database.session.commit()
        flash('Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form_editar_perfil.email.data = current_user.email
        form_editar_perfil.username.data = current_user.username
        form_editar_perfil.cidade.data = current_user.cidade
        form_editar_perfil.instagram.data = current_user.instagram
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template("editarperfil.html", foto_perfil=foto_perfil, form_editar_perfil=form_editar_perfil)

@app.route('/post/<post_id>', methods=["GET", "POST"])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso!', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, datetime=datetime, form=form)


@app.route('/post/<post_id>/excluir', methods=["GET", "POST"])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
