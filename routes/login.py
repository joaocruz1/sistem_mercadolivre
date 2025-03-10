from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import login_user, logout_user
from dataclasses import dataclass
from services import Services
from database import User, Shop
from peewee import DoesNotExist

@dataclass
class LoginRoute:
    blueprint_name: str = "login"
    import_name: str = __name__
    services_api: Services = None

    
    def __post_init__(self):
        self.blueprint = Blueprint(self.blueprint_name, self.import_name)
        self.register_routes()

    def register_routes(self):
        @self.blueprint.route('/')
        def home():
            return render_template('login.html')

        @self.blueprint.route('/logout')
        def logout():
            logout_user()
            session.clear()
            return redirect(url_for('login.login'))


        @self.blueprint.route('/', methods=['POST'])
        def login():
            try:
                shop_name = request.form.get('shop')
                email = request.form.get('email')
                password = request.form.get('password')

                # Valida se os campos foram enviados
                if not shop_name or not email or not password:

                    flash('Por favor, preencha todos os campos.', 'error')
                    return redirect(url_for('login.login'))

                # Busca a loja pelo nome
                shop = Shop.get(Shop.name == shop_name)

                # Busca o usuário pelo e-mail e senha dentro da loja encontrada
                user = User.get(User.email == email, User.password == password, User.shop == shop)

                # Faz login do usuário
                login_user(user)

                # Armazena as informações do usuário na sessão
                session['userinfo'] = {
                    'user_name': user.name,
                    'user_email': user.email,
                    'user_adm': user.adm,
                    'user_shop': shop.name,
                    'shop_id': shop.id
                }
                return redirect(url_for('dashboard.dashboard'))

            except DoesNotExist:
                flash('Credenciais inválidas. Por favor, verifique seu e-mail e senha.', 'error')
                return redirect(url_for('login.login'))

            except Exception as e:
                flash('Erro ao fazer login. Por favor, tente novamente mais tarde.', 'error')
                return redirect(url_for('login.login'))



