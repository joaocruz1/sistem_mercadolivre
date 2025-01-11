from flask import Flask, request, redirect, render_template, url_for, session, jsonify
from data.users_data import UserServices
from dataclasses import dataclass
from services import Services

@dataclass
class FlaskRoute:
    app: Flask
    user_login: UserServices
    services_api: Services
    user_infoml: str = None
    user_info: str = None
    date_login: str = None
    user_adm: bool = None

    def __post_init__(self):
        # Registra as rotas
        self.register_routes()

    def register_routes(self):
        # Função que será chamada antes de cada requisição (before request)
        @self.app.before_request
        def check_login():
            # Verifica se a chave 'userinfo' existe na sessão
            if 'userinfo' not in session:
                # Se não estiver logado e a requisição não for para login ou erro, redireciona
                if request.endpoint not in ['login', 'autherror']:
                    return render_template('login.html')
                
        @self.app.route('/')
        def index():
            return redirect(url_for('login'))

        # Rota inicial de login
        @self.app.route('/login')
        def home():
            return render_template('login.html')

        # Rota de login (POST)
        @self.app.route('/login', methods=['POST'])
        def login():
            try:
                # Pega os dados do formulário de login
                email = request.form['email']
                password = request.form['password']
                shop = request.form['shop']

                # Armazena os dados em uma variável
                data = {"email": email, "password": password, "shop": shop}

                # Verifica se o login foi bem-sucedido
                login_success, self.user_info = self.user_login.login(data)

                if login_success:
                    session['userinfo'] = self.user_info  # Armazena os dados do usuário na sessão
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('autherror'))

            except ValueError as e:
                # Tratamento para erros conhecidos
                print(f"Erro no login: {e}")
                return jsonify({"error": str(e)}), 400

            except Exception as e:
                # Tratamento para erros inesperados
                print(f"Erro inesperado no login: {e}")
                return jsonify({"error": "Erro no servidor"}), 500

        # Dashboard do usuário
        @self.app.route('/dashboard')
        def dashboard():

            # Obtém as informações do usuário (simulando uma consulta externa)
            self.user_info_ml = session.get('userinfo_ml')
            session['userinfo_ml'] = self.services_api.infouser()
            
            quantity_products = self.services_api.search_products()
            quantity_sales = self.services_api.import_sales()

            return render_template('dashboard.html', userinfo=self.user_info_ml, quantity_products=quantity_products, quantity_sales=quantity_sales)
        
        


        # Rota de informações do usuário
        @self.app.route('/userinfo')
        def userinfo():
            return render_template('userinfo.html', userinfo_ml=session.get('userinfo_ml'),userinfo=session.get('userinfo') )
        
        @self.app.route('/users')
        def users():
            usersinfo = self.user_login.consult_users()
            return render_template('users.html', usersinfo=usersinfo)
        
        @self.app.route('/check-session')
        def check_session():
            if session:
                return {key: session[key] for key in session}, 200  # Retorna as informações da sessão como JSON
            else:
                return "No session data available", 200
        
        @self.app.route('/clear-session')
        def clear_session():
            session.clear()  # Limpa todos os dados armazenados na sessão
            return redirect(url_for('home'))  # Redireciona para a página inicial (ou outra página desejada)

