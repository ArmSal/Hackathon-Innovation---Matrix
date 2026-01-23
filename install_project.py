import os
import sys

# Definition of the Project Structure and File Contents - UPDATED 2026
project_structure = {
    "requirements.txt": """flask
flask-sqlalchemy
flask-login
werkzeug
psycopg2-binary
python-dotenv
""",

    "config.py": """import os

class Config:
    # Using SQLite as fallback database (no PostgreSQL server required)
    # To use PostgreSQL, change this to:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:YourPassword@localhost:5432/devops_db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///devops.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hackathon-secret-key-matrix-2026')
    SQLALCHEMY_ECHO = False
""",

    "run.py": """from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')
""",

    "app/__init__.py": """from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'core.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Import and Register Routes
    from app.routes.core import core_bp
    app.register_blueprint(core_bp)
    
    # Auto-create tables if they don't exist
    with app.app_context():
        from app.database.models import Project, Deployment, User
        db.create_all()
        
    return app
""",

    "app/database/__init__.py": "",

    "app/database/models.py": """from app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deployments = db.relationship('Deployment', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    stack = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='Running')
    last_deploy = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deployments = db.relationship('Deployment', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Deployment(db.Model):
    __tablename__ = 'deployments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    log_content = db.Column(db.Text, default='')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_by = db.Column(db.String(100), default='System')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Deployment {self.id} - {self.status}>'
""",

    "app/routes/__init__.py": "",

    "app/routes/core.py": """from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.database.models import Project, Deployment, User
from datetime import datetime
import random

core_bp = Blueprint('core', __name__)

# --- AUTHENTICATION ROUTES ---
@core_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('core.dashboard'))
        else:
            flash('Nom d\\'utilisateur ou mot de passe invalide', 'danger')
    
    return render_template('login.html')

@core_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if User.query.filter_by(username=username).first():
            flash('Le nom d\\'utilisateur existe déjà', 'danger')
            return redirect(url_for('core.register'))
        
        if User.query.filter_by(email=email).first():
            flash('L\\'email existe déjà', 'danger')
            return redirect(url_for('core.register'))
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('core.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Compte créé avec succès!', 'success')
        return redirect(url_for('core.dashboard'))
    
    return render_template('register.html')

@core_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('core.login'))

@core_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    return redirect(url_for('core.login'))

@core_bp.route('/dashboard')
@login_required
def dashboard():
    projects = Project.query.all()
    return render_template('home.html', projects=projects)

@core_bp.route('/project/<int:id>')
@login_required
def project_detail(id):
    project = Project.query.get_or_404(id)
    deployments = Deployment.query.filter_by(project_id=id).order_by(Deployment.timestamp.desc()).limit(10).all()
    return render_template('detail.html', project=project, deployments=deployments)

# --- DEPLOYMENT MANAGEMENT ---
@core_bp.route('/api/deploy/<int:id>', methods=['POST'])
@login_required
def trigger_deploy(id):
    project = Project.query.get_or_404(id)
    stack = request.json.get('stack', project.stack) if request.is_json else request.form.get('stack', project.stack)
    
    is_success = random.choice([True, True, True, True, False])
    status = 'Success' if is_success else 'Failed'
    
    log_text = f'''[INFO] Initializing CI/CD Pipeline for {project.name}...
[INFO] Stack: {stack}
[INFO] Fetching origin/master... OK
[INFO] Building Container... Done (0.4s)
[INFO] Running Unit Tests... 
       - test_api.py ... OK
       - test_db.py ... OK
[INFO] Pushing artifacts to production...'''

    if is_success:
        log_text += f'''
[INFO] Service restarted successfully.
[RESULT] DEPLOYMENT SUCCESSFUL.'''
        project.status = 'Running'
        project.last_deploy = datetime.utcnow()
    else:
        log_text += f'''
[ERROR] Timeout waiting for database connection.
[FATAL] Rollback initiated.
[RESULT] DEPLOYMENT FAILED.'''
        project.status = 'Error'

    new_deploy = Deployment(project_id=id, user_id=current_user.id, status=status, log_content=log_text, triggered_by=current_user.username, started_at=datetime.utcnow())
    db.session.add(new_deploy)
    db.session.commit()
    
    return jsonify({'status': status, 'logs': log_text, 'deployment_id': new_deploy.id})

@core_bp.route('/api/deploy/<int:deploy_id>/stop', methods=['POST'])
@login_required
def stop_deploy(deploy_id):
    deployment = Deployment.query.get_or_404(deploy_id)
    
    if deployment.status in ['Success', 'Failed', 'Stopped']:
        return jsonify({'error': f'Impossible d\\'arrêter un déploiement {deployment.status.lower()}'}), 400
    
    deployment.status = 'Stopped'
    deployment.ended_at = datetime.utcnow()
    deployment.log_content += f'\\n[WARN] Deployment stopped by {current_user.username} at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}'
    
    project = deployment.project
    project.status = 'Stopped'
    
    db.session.commit()
    
    return jsonify({'status': 'Stopped', 'message': 'Deployment stopped successfully'})

@core_bp.route('/api/deployment/<int:deploy_id>', methods=['DELETE'])
@login_required
def delete_deployment(deploy_id):
    deployment = Deployment.query.get_or_404(deploy_id)
    project_id = deployment.project_id
    
    db.session.delete(deployment)
    db.session.commit()
    
    return jsonify({'message': 'Deployment deleted successfully', 'project_id': project_id})

# --- MOCK PROJECT CREATION ---
@core_bp.route('/add-mock-project', methods=['GET', 'POST'])
@login_required
def add_mock_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        client_name = request.form.get('client_name')
        tech_stack_list = request.form.getlist('tech_stack')
        status = request.form.get('status', 'Running')
        
        if not all([project_name, client_name, tech_stack_list]):
            flash('Tous les champs sont requis', 'danger')
            return redirect(url_for('core.add_mock_project'))
        
        tech_stack = ' + '.join(tech_stack_list)
        
        new_project = Project(
            name=project_name,
            client_name=client_name,
            stack=tech_stack,
            status=status,
            last_deploy=datetime.utcnow()
        )
        db.session.add(new_project)
        db.session.commit()
        
        flash(f'Projet simulé « {project_name} » créé avec succès!', 'success')
        return redirect(url_for('core.project_detail', id=new_project.id))
    
    return render_template('add_project.html')
""",

    "app/frontend/__init__.py": "",

    "app/frontend/templates/base.html": """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Centre DevOps - Project DevOps</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-light">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="bi bi-hdd-network"></i> Centre DevOps
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <span class="nav-link">👤 {{ current_user.username }}</span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('core.logout') }}">Déconnexion</a>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('core.login') }}">Se connecter</a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
            <div class="container mb-3">
                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <!-- Footer -->
    <footer class="text-center py-4 text-muted mt-5">
        <small>&copy; 2026 Hackathon Innovation - Team Matrix</small>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Dynamic Script for Deploy Button -->
    <script>
        function triggerDeploy(projectId) {
            const btn = document.getElementById('deployBtn');
            const logBox = document.getElementById('consoleLogs');
            const badge = document.getElementById('statusBadge');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Pipeline En cours...';
            logBox.innerHTML = '> Connexion au runner Jenkins...\\n> Attente de l\\'agent...';
            logBox.className = 'console-logs';

            fetch(`/api/deploy/${projectId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                logBox.innerHTML = data.logs;
                btn.disabled = false;
                btn.innerHTML = '🚀 Déclencher Déploiement';
                
                if(data.status === 'Success') {
                    badge.className = 'badge bg-success fs-6';
                    badge.innerText = 'En cours';
                    logBox.style.border = "2px solid #198754";
                } else {
                    badge.className = 'badge bg-danger fs-6';
                    badge.innerText = 'Erreur';
                    logBox.style.border = "2px solid #dc3545";
                }
            })
            .catch(err => {
                console.error(err);
                logBox.innerHTML = "[ERREUR] Impossible de contacter l'API.";
                btn.disabled = false;
            });
        }
    </script>
</body>
</html>
""",

    "app/frontend/templates/login.html": """{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-5">
        <div class="card shadow-lg border-0">
            <div class="card-body p-5">
                <h2 class="text-center mb-4 fw-bold">🔐 Se connecter</h2>
                
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label fw-bold">Nom d'utilisateur</label>
                        <input type="text" class="form-control form-control-lg" id="username" name="username" required>
                    </div>
                    
                    <div class="mb-4">
                        <label for="password" class="form-label fw-bold">Mot de passe</label>
                        <input type="password" class="form-control form-control-lg" id="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold">Se connecter</button>
                </form>
                
                <hr class="my-4">
                
                <p class="text-center text-muted mb-0">
                    <a href="{{ url_for('core.register') }}" class="text-primary fw-bold">Créer un compte</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",

    "app/frontend/templates/register.html": """{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-6">
        <div class="card shadow-lg border-0">
            <div class="card-body p-5">
                <h2 class="text-center mb-2 fw-bold">Créer un Compte</h2>
                <p class="text-center text-muted mb-4">Rejoignez Notre Plateforme DevOps</p>
                
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label fw-bold">Nom d'utilisateur</label>
                        <input type="text" class="form-control form-control-lg" id="username" name="username" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label fw-bold">Email</label>
                        <input type="email" class="form-control form-control-lg" id="email" name="email" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label fw-bold">Mot de passe</label>
                        <input type="password" class="form-control form-control-lg" id="password" name="password" required>
                    </div>
                    
                    <div class="mb-4">
                        <label for="confirm_password" class="form-label fw-bold">Confirmer le mot de passe</label>
                        <input type="password" class="form-control form-control-lg" id="confirm_password" name="confirm_password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-success btn-lg w-100 fw-bold">Créer un Compte</button>
                </form>
                
                <hr class="my-4">
                
                <p class="text-center text-muted mb-0">
                    Vous avez déjà un compte? <a href="{{ url_for('core.login') }}" class="text-primary fw-bold">Se connecter</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",

    "app/frontend/templates/home.html": """{% extends "base.html" %}

{% block content %}
<!-- Top Stats Row -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary mb-3 shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">CPU du Cluster</h6>
                        <h2 class="my-2">68%</h2>
                    </div>
                    <i class="bi bi-cpu fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success mb-3 shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Total Projets</h6>
                        <h2 class="my-2">{{ projects|length }}</h2>
                    </div>
                    <i class="bi bi-folder2-open fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-dark bg-warning mb-3 shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Alertes</h6>
                        <h2 class="my-2">0</h2>
                    </div>
                    <i class="bi bi-bell fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info mb-3 shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Exécuteurs</h6>
                        <h2 class="my-2">4/5</h2>
                    </div>
                    <i class="bi bi-diagram-3 fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Projects Grid -->
<div class="d-flex justify-content-between align-items-center mb-3">
    <h3><i class="bi bi-grid-fill"></i> Projets Clients</h3>
    <a href="{{ url_for('core.add_mock_project') }}" class="btn btn-outline-primary btn-sm">+ Nouveau Projet</a>
</div>

<div class="row">
    {% for p in projects %}
    <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <h5 class="card-title fw-bold text-primary">{{ p.name }}</h5>
                    {% if p.status == 'Running' %}
                    <span class="badge bg-success">En cours</span>
                    {% elif p.status == 'Stopped' %}
                    <span class="badge bg-secondary">Arrêté</span>
                    {% else %}
                    <span class="badge bg-danger">Erreur</span>
                    {% endif %}
                </div>
                <h6 class="card-subtitle mb-3 text-muted">
                    <i class="bi bi-building"></i> {{ p.client_name }}
                </h6>
                <div class="mb-3">
                    <span class="badge bg-light text-dark border">{{ p.stack }}</span>
                    <span class="badge bg-light text-dark border">v1.0.{{ p.id }}</span>
                </div>
                <p class="card-text small text-muted">Dernier déploiement: {{ p.last_deploy.strftime('%Y-%m-%d %H:%M') }}</p>
                <a href="{{ url_for('core.project_detail', id=p.id) }}" class="btn btn-primary w-100">
                    <i class="bi bi-gear-wide-connected"></i> Gérer les Pipelines
                </a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12 text-center py-5">
        <p class="text-muted">Aucun projet trouvé. Veuillez exécuter scripts/seed.py</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
""",

    "app/frontend/templates/detail.html": """{% extends "base.html" %}

{% block content %}
<div class="mb-4">
    <a href="{{ url_for('core.dashboard') }}" class="text-decoration-none">
        <i class="bi bi-arrow-left"></i> Retour au Tableau de Bord
    </a>
</div>

<div class="row">
    <!-- Left Column: Info & Actions -->
    <div class="col-md-4">
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-white fw-bold py-3">
                Aperçu du Projet
            </div>
            <div class="card-body">
                <h2 class="mb-3">{{ project.name }}</h2>
                
                <div class="mb-3">
                    <label class="small text-muted fw-bold">CLIENT</label>
                    <div class="fs-5">{{ project.client_name }}</div>
                </div>
                
                <div class="mb-3">
                    <label class="small text-muted fw-bold">PILE TECHNOLOGIQUE</label>
                    <div><span class="badge bg-dark">{{ project.stack }}</span></div>
                </div>

                <div class="mb-4">
                    <label class="small text-muted fw-bold">STATUT ACTUEL</label>
                    <div>
                        <span id="statusBadge" class="badge fs-6 bg-{{ 'success' if project.status == 'Running' else 'danger' if project.status == 'Error' else 'secondary' }}">
                            {{ 'En cours' if project.status == 'Running' else 'Erreur' if project.status == 'Error' else 'Arrêté' }}
                        </span>
                    </div>
                </div>
                
                <hr>
                
                <div class="d-grid gap-2">
                    <button id="deployBtn" onclick="triggerDeploy({{ project.id }})" class="btn btn-primary py-2 fw-bold shadow-sm">
                        🚀 Déclencher Déploiement
                    </button>
                    <button class="btn btn-outline-secondary">
                        <i class="bi bi-file-earmark-text"></i> Voir Config
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Right Column: Console & History -->
    <div class="col-md-8">
        <!-- Live Console -->
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                <span><i class="bi bi-terminal-fill me-2"></i> Sortie de Compilation En Direct</span>
                <span class="badge bg-secondary">runner-01</span>
            </div>
            <div class="card-body bg-dark p-0">
                <pre id="consoleLogs" class="console-logs m-0">En attente du déclenchement du travail...</pre>
            </div>
        </div>

        <!-- History Table -->
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white fw-bold py-3">
                Historique des Déploiements
            </div>
            <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Statut</th>
                            <th>Date/Heure</th>
                            <th>Déclenché par</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for d in deployments %}
                        <tr>
                            <td>#{{ d.id }}</td>
                            <td>
                                {% if d.status == 'Success' %}
                                <span class="text-success"><i class="bi bi-check-circle-fill"></i> Succès</span>
                                {% else %}
                                <span class="text-danger"><i class="bi bi-x-circle-fill"></i> Échec</span>
                                {% endif %}
                            </td>
                            <td>{{ d.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                            <td><small class="text-muted">{{ d.triggered_by }}</small></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",

    "app/frontend/templates/add_project.html": """{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-6">
        <div class="card shadow-lg border-0">
            <div class="card-body p-5">
                <h2 class="text-center mb-4 fw-bold">🚀 Créer un Projet Simulé</h2>
                
                <form method="POST">
                    <div class="mb-3">
                        <label for="project_name" class="form-label fw-bold">Nom du Projet</label>
                        <input type="text" class="form-control form-control-lg" id="project_name" name="project_name" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="client_name" class="form-label fw-bold">Nom du Client</label>
                        <input type="text" class="form-control form-control-lg" id="client_name" name="client_name" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="tech_stack" class="form-label fw-bold">Pile Technologique</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="react" name="tech_stack" value="React/NextJS">
                            <label class="form-check-label" for="react">React/NextJS</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="springboot" name="tech_stack" value="Spring Boot">
                            <label class="form-check-label" for="springboot">Spring Boot</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="django" name="tech_stack" value="Django">
                            <label class="form-check-label" for="django">Django</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="laravel" name="tech_stack" value="Laravel">
                            <label class="form-check-label" for="laravel">Laravel</label>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <label for="status" class="form-label fw-bold">Statut Initial</label>
                        <select class="form-select form-select-lg" id="status" name="status">
                            <option value="Running">En cours</option>
                            <option value="Stopped">Arrêté</option>
                            <option value="Error">Erreur</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold">Créer le Projet</button>
                </form>
                
                <hr class="my-4">
                
                <p class="text-center text-muted mb-0">
                    <a href="{{ url_for('core.dashboard') }}" class="text-primary">Retour au Tableau de Bord</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",

    "app/static/css/style.css": r"""/* Custom DevOps Central Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.console-logs {
    background-color: #1e1e1e;
    color: #00ff00;
    font-family: 'Courier New', Courier, monospace;
    padding: 15px;
    border-radius: 5px;
    height: 300px;
    overflow-y: auto;
}

.card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn {
    transition: all 0.3s ease;
}

.btn:hover {
    transform: translateY(-1px);
}

.navbar {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.badge {
    padding: 0.35rem 0.65rem;
}
""",

    "app/static/js/pipeline.js": """console.log('Centre DevOps Pipeline Manager Chargé');

// Placeholder for pipeline management functions
function triggerDeploy(projectId) {
    console.log('Déclenchement du déploiement pour le projet:', projectId);
}

function stopDeployment(deploymentId) {
    console.log('Arrêt du déploiement:', deploymentId);
}
""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
""",

    "scripts/seed.py": """import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.database.models import Project, Deployment, User
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("🧹 Nettoyage de la base de données...")
    db.drop_all()
    db.create_all()

    print("👤 Création de l'utilisateur de test...")
    test_user = User(
        username='admin',
        email='admin@devops.local'
    )
    test_user.set_password('password123')
    db.session.add(test_user)
    db.session.commit()
    print("   ✅ Utilisateur 'admin' créé (mot de passe: password123)")

    print("🌱 Ensemencement des Projets...")
    projects_data = [
        {"name": "E-Commerce Frontend", "client": "Carrefour", "stack": "React/NextJS + PostgreSQL"},
        {"name": "HR Management API", "client": "Total Energies", "stack": "Spring Boot + MySQL"},
        {"name": "Data Analytics Platform", "client": "Orange Business", "stack": "Python/Django + MongoDB"},
        {"name": "Mobile Banking App", "client": "BNP Paribas", "stack": "Flutter/Dart + REST API"},
        {"name": "Legacy CRM System", "client": "Renault Group", "stack": "PHP/Laravel + PostgreSQL"},
    ]

    projects = []
    for p_data in projects_data:
        p = Project(
            name=p_data["name"],
            client_name=p_data["client"],
            stack=p_data["stack"],
            status=random.choice(['Running', 'Running', 'Running', 'Stopped', 'Error'])
        )
        db.session.add(p)
        projects.append(p)
    
    db.session.commit()

    print("🌱 Ensemencement de l'Historique des Déploiements...")
    for p in projects:
        # Create 3-5 fake history logs per project
        for i in range(random.randint(3, 5)):
            status = random.choice(['Success', 'Success', 'Success', 'Failed'])
            log = "[ARCHIVED] Build process completed successfully." if status == 'Success' else "[ARCHIVED] Build failed at test stage."
            
            d = Deployment(
                project_id=p.id,
                user_id=test_user.id,
                status=status,
                log_content=log,
                triggered_by='GitLab Hook',
                started_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            db.session.add(d)
    
    db.session.commit()
    
    print("\\n" + "="*60)
    print("✨ ENSEMENCEMENT TERMINÉ AVEC SUCCÈS! ✨")
    print("="*60)
    print("\\n📝 UTILISATEUR DE TEST:")
    print("   Nom d'utilisateur: admin")
    print("   Mot de passe: password123")
    print("   Email: admin@devops.local")
    print("\\n" + "="*60 + "\\n")
""",
}

def create_files():
    base_dir = os.getcwd()
    
    print("\\n" + "="*60)
    print("📂 Centre DevOps - Installation du Projet (Mise à jour 2026)")
    print("="*60)
    print(f"Répertoire cible: {base_dir}\\n")
    
    for filepath, content in project_structure.items():
        # Handle directory creation
        full_path = os.path.join(base_dir, filepath)
        directory = os.path.dirname(full_path)
        
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Répertoire créé: {directory}")
            
        # Write file content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fichier créé: {filepath}")

    print("\\n" + "="*60)
    print("✨ PROJET INSTALLÉ AVEC SUCCÈS! ✨")
    print("="*60)
    print("\\n📋 PROCHAINES ÉTAPES:\\n")
    print("1. Installer les dépendances:")
    print("   $ pip install -r requirements.txt\\n")
    print("2. Initialiser la base de données:")
    print("   $ python scripts/seed.py\\n")
    print("3. Exécuter l'application:")
    print("   $ python run.py\\n")
    print("4. Ouvrir dans le navigateur:")
    print("   http://localhost:5000\\n")
    print("5. Identifiants de connexion:")
    print("   Nom d'utilisateur: admin")
    print("   Mot de passe: password123\\n")
    print("="*60)
    print("✍️  FONCTIONNALITÉS DU PROJET:")
    print("="*60)
    print("✅ Support UI en Français")
    print("✅ Authentification des Utilisateurs (Connexion/Inscription)")
    print("✅ Système de Gestion des Projets")
    print("✅ Simulation de Déploiement CI/CD")
    print("✅ Journaux et Surveillance en Temps Réel")
    print("✅ Base de Données SQLite (ou PostgreSQL)")
    print("✅ Design Responsive Bootstrap 5")
    print("="*60)
    print("🎉 Bonne Gestion DevOps! Créé avec ❤️ par Team Matrix")
    print("="*60 + "\\n")

if __name__ == "__main__":
    try:
        create_files()
    except Exception as e:
        print(f"\\n❌ Erreur: {e}")
        sys.exit(1)
