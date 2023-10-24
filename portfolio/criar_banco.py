from portfolio import database, app
from portfolio.models import Usuario, Projeto

with app.app_context():
    database.create_all()