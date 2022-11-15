from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadedogugu.models import Usuario
from flask_login import current_user


class CriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    instagram = StringField('Instagram: ', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_criar_conta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar')

    def validate_username(self, username):
        usuario2 = Usuario.query.filter_by(username=username.data).first()
        if usuario2:
            raise ValidationError('Nome já cadastrado.')


class Login(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_logar = SubmitField('Fazer Login')


class EditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    instagram = StringField('Instagram: ', validators=[DataRequired()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    interesse_jogos = BooleanField('Jogos')
    interesse_series_filmes = BooleanField('Séries/Filmes')
    interesse_livros = BooleanField('Livros')
    interesse_politica = BooleanField('Política')
    interesse_esportes = BooleanField('Esportes')
    interesse_corrida = BooleanField('Corrida')
    interesse_computador = BooleanField('Computador')
    interesse_escola = BooleanField('Escola')
    interesse_carros = BooleanField('Carros')
    interesse_comidas = BooleanField('Comidas')
    interesse_bebidas = BooleanField('Bebidas')
    botao_editar_perfil = SubmitField('Salvar Alterações')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com este e-mail. ')

    def validate_username(self, username):
        if current_user.username != username.data:
            usuario2 = Usuario.query.filter_by(username=username.data).first()
            if usuario2:
                raise ValidationError('Nome já cadastrado.')

class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')