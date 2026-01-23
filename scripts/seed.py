import sys
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
    
    print("\n" + "="*60)
    print("✨ ENSEMENCEMENT TERMINÉ AVEC SUCCÈS! ✨")
    print("="*60)
    print("\n📝 UTILISATEUR DE TEST:")
    print("   Nom d'utilisateur: admin")
    print("   Mot de passe: password123")
    print("   Email: admin@devops.local")
    print("\n" + "="*60 + "\n")
