# 🚀 DevOps Central - Plateforme Multi-tenant (3PRJ1)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Hackathon-orange)
![OS](https://img.shields.io/badge/OS-Windows%2011-blue)

**Projet de Fin d'Unité - Hackathon Innovation**  
École IT - Bachelor 3 - Année 2025-2026

Ce dépôt contient le code source du **Projet D : DevOps Central**, une plateforme unifiée de gestion de projets et d'automatisation pour ESN.

🔗 **URL du Dépôt :** [https://github.com/ArmSal/Hackathon-Innovation---Matrix.git](https://github.com/ArmSal/Hackathon-Innovation---Matrix.git)

---

## 👥 L'Équipe Matrix

Projet réalisé en mode **Agile** sur une durée intensive de **3 jours**.

| Membre | Rôle | Responsabilités Principales |
| :--- | :--- | :--- |
| **Serge Anglesy N'GUESSAN** | 👑 **Lead Dev / Architecte** | Architecture globale, choix technologiques, coordination, Core Django. |
| **Fedi KHALDI** | 🗄️ **Backend / BDD** | Modèles de données, logique métier, APIs, gestion PostgreSQL. |
| **Babikir IBRAHIM AL KHALIL** | 🎨 **Frontend / UI / UX** | Design des interfaces, expérience utilisateur, intégration HTML/CSS/JS. |
| **Armend SALIHU** | ⚙️ **DevOps / Automation** | Scripts d'automatisation, pipelines CI/CD simulés, déploiement. |

---

## 🎯 Contexte du Projet (Scénario)

**Client :** TechConsulting Group (ESN de 200 développeurs).

**Problématique :** Dispersion des outils, coûts de configuration élevés à chaque nouveau projet, manque de standardisation des environnements de développement.

**Solution :** Une plateforme SaaS multi-tenant permettant de :
1. Centraliser la création de projets (Self-service).
2. Standardiser les stacks techniques via des templates.
3. Automatiser les pipelines CI/CD et le monitoring.
4. Isoler les données par client (Multi-tenancy).

---

## 🛠️ Stack Technique

*   **Langage :** Python 3.10+
*   **Framework Web :** Django
*   **Base de Données :** PostgreSQL (Prod) / SQLite (Dev)
*   **Frontend :** HTML5, CSS3, JavaScript, Bootstrap 5
*   **Automatisation :** Scripts Python & Batch/PowerShell
*   **OS de Développement :** Windows 11

---

## ✨ Fonctionnalités Clés

### 1. Module Projets (Self-Service)
*   Création de projets à la demande.
*   Sélection de templates préconfigurés (Web Django, API Flask, Mobile, etc.).
*   Isolation complète des environnements par client.

### 2. Module CI/CD & Automation
*   Simulation de pipelines de déploiement.
*   Scripts d'initialisation de repository Git.
*   Automatisation des tâches récurrentes.

### 3. Module Monitoring
*   Tableaux de bord (Dashboards) par projet.
*   Remontée d'alertes et logs centralisés.
*   Vue globale administrateur.

### 4. Administration & Sécurité
*   Gestion des utilisateurs et des rôles (RBAC).
*   Audit trails (traçabilité des actions).
*   Conformité RGPD.

---

## 💻 Installation & Démarrage (Windows 11)

Suivez ces instructions pour lancer le projet localement.

### Prérequis
*   Python installé (vérifiez avec `python --version`).
*   Git installé.

### 1. Cloner le projet
```powershell
git clone https://github.com/ArmSal/Hackathon-Innovation---Matrix.git
cd Hackathon-Innovation---Matrix
