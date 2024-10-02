from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, Session
from flask_migrate import Migrate
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, Length
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ContatoForm

app = Flask(__name__)
app.config.from_object('config')

# Configuração do SQLAlchemy
engine = create_engine('sqlite:///blog.db', echo=True)
Base = declarative_base()
# Modelos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_usuario = Column(String(80), nullable=False)
    nome = Column(String(80), nullable=False)
    senha = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    niver = Column(String(10))
    eh_administrador = Column(Boolean, default=False)  # Novo campo
    postagem = relationship("Postagem", back_populates="usuario")
    comentario = relationship("Comentario", back_populates="usuario")
class Postagem(Base):
    __tablename__ = "postagens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    review = Column(String, nullable=False)
    nota = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario_id'))
    usuario = relationship("Usuario", back_populates="postagem")
    comentario = relationship("Comentario", back_populates="postagem")
    
class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conteudo = Column(String, nullable=False)
    postagem_id = Column(Integer, ForeignKey('postagem_id'))
    usuario_id = Column(Integer, ForeignKey('usuario_id'))
    usuario = relationship("Usuario", back_populates="comentario")
    postagem = relationship("Postagem", back_populates="comentario")

def CriaUsuario(nome, nome_usuario, senha, email, niver):
    with Session(engine) as db_session:
         usuario = Usuario(nome_usuario = nome_usuario, nome = nome, senha = senha, email = email, niver = niver)
         db_session.add(usuario)
         db_session.commit()

def CriaPostagem(titulo, review, nota, usuario_id):
    with Session(engine) as db_session:
        postagem = Postagem(titulo = titulo, review = review, nota = nota, usuario_id = usuario_id)
        db_session.add(postagem)
        db_session.commit()
    
def CriaComentario(conteudo, postagem_id, usuario_id):
    with Session(engine) as db_session:
        comentario = Comentario(conteudo = conteudo, postagem_id = postagem_id, usuario_id = usuario_id)
        db_session.add(comentario)
        db_session.commit()
        
        
def DeletarPostagem(postagem_id):
    with Session(engine) as db_session:
        postagem = db_session.query(Postagem).filter_by(id = postagem_id).first()
        if postagem:
            db_session.delete(postagem)
            db_session.commit()
        

def Deletarcomentario(comentario_id):
    with Session(engine) as db_session:
        comentario = db_session.query(Comentario).filter_by(id = comentario_id).first()
        if comentario:
            db_session.delete(comentario)
            db_session.commit()


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = ContatoForm()

    if form.validate_on_submit():
        senha_hash = generate_password_hash(form.senha.data)
        
        novo_usuario = Usuario(
            nome_usuario=form.nome_usuario.data,
            nome=form.nome.data,
            senha=senha_hash,
            email=form.email.data,
            niver=form.niver.data
        )

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', formulario=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['nome_usuario'] = user.nome_usuario
            session['eh_administrador'] = user.eh_administrador
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        flash('Falha no login. Verifique seu email e senha.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    postagens = Postagem.query.all()
    return render_template('index.html', postagens=postagens)

@app.route('/criar_postagem', methods=['GET', 'POST'])
def criar_postagem():
    if request.method == 'POST':
        titulo = request.form['titulo']
        review = request.form['review']
        nota = request.form['nota']
        usuario_id = session.get('usuario_id')

        nova_postagem = Postagem(titulo=titulo, review=review, nota=nota, usuario_id=usuario_id)
        
        db.session.add(nova_postagem)  # Corrigido para db.session
        db.session.commit()

        flash('Postagem criada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('criar_postagem.html')

        flash('Postagem criada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('criar_postagem.html')

@app.route('/postagem/<int:postagem_id>', methods=['GET', 'POST'])
def detalhe_postagem(postagem_id):
    postagem = Postagem.query.get(postagem_id)
    comentarios = Comentario.query.filter_by(postagem_id=postagem_id).all()

    if request.method == 'POST':
        conteudo = request.form['conteudo']
        usuario_id = session.get('usuario_id')

        novo_comentario = Comentario(conteudo=conteudo, postagem_id=postagem_id, usuario_id=usuario_id)
        db.session.add(novo_comentario)
        db.session.commit()

        flash('Comentário adicionado com sucesso!', 'success')
        return redirect(url_for('detalhe_postagem', postagem_id=postagem_id))

    return render_template('detalhe_postagem.html', postagem=postagem, comentarios=comentarios)

@app.route('/excluir_postagem/<int:postagem_id>')
def excluir_postagem(postagem_id):
    usuario_id = session.get('usuario_id')
    postagem = Postagem.query.get(postagem_id)

    if postagem and (postagem.usuario_id == usuario_id or session.get('eh_administrador')):
        db.session.delete(postagem)
        db.session.commit()
        flash('Postagem excluída com sucesso!', 'success')
    else:
        flash('Você não tem permissão para excluir esta postagem.', 'danger')

    return redirect(url_for('index'))

@app.route('/excluir_comentario/<int:comentario_id>')
def excluir_comentario(comentario_id):
    usuario_id = session.get('usuario_id')
    comentario = Comentario.query.get(comentario_id)

    if comentario and (comentario.usuario_id == usuario_id or session.get('eh_administrador')):
        db.session.delete(comentario)
        db.session.commit()
        flash('Comentário excluído com sucesso!', 'success')
    else:
        flash('Você não tem permissão para excluir este comentário.', 'danger')

    return redirect(url_for('detalhe_postagem', postagem_id=comentario.postagem_id))

if __name__ == '__main__':
    app.run(debug=True)
