from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, Length

class ContatoForm(FlaskForm):

    nome_usuario = StringField(
        'Nome do Usuario', 
        validators=[
            DataRequired(message="O campo de nome do usuario é obrigatório."),
  
        ]
    )

    nome = StringField(
        'Nome',
        validators=[
            DataRequired(message="O campo nome é obrigatorio"),
            Length(min=2, max=50, message="O nome deve ter entre 2 e 50 caracteres.")
        ]
    )
    senha = StringField(
        "Senha",
        validators=[
            DataRequired(message="O campo de senha é obrigatorio"),
            Length(min=1)
        ]
    )
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message="O campo de email é obrigatório."),
            Email(message="Digite um endereço de email válido.")
        ]
    )
    niver = DateField(
        'Niver', 
        format='%Y-%m-%d',
        validators=[
            DataRequired(message="O campo de idade é obrigatório.")
        ]
    )
        
    enviar = SubmitField('Enviar')
    
class PostagemForm(FlaskForm):
    titulo = StringField(
        "Título",
        validators=[DataRequired(message="O campo título é obrigatório")]
    )
    review = StringField(
        "Review",
        validators=[
            DataRequired(message="O campo review é obrigatório"),
            Length(min=15, message="O review deve ter pelo menos 15 caracteres.")
        ]
    )
    nota = IntegerField(
        "Nota",
        validators=[DataRequired(message="O campo nota é obrigatório"),
                    NumberRange(min=0, max=5, message="A nota deve ser entre 0 e 5.")]
    )