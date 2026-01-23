from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
            flash('Nom d\'utilisateur ou mot de passe invalide', 'danger')
    
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
            flash('Le nom d\'utilisateur existe déjà', 'danger')
            return redirect(url_for('core.register'))
        
        if User.query.filter_by(email=email).first():
            flash('L\'email existe déjà', 'danger')
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
        return jsonify({'error': f'Impossible d\'arrêter un déploiement {deployment.status.lower()}'}), 400
    
    deployment.status = 'Stopped'
    deployment.ended_at = datetime.utcnow()
    deployment.log_content += f'\n[WARN] Deployment stopped by {current_user.username} at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}'
    
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
