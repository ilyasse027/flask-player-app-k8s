from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Utilisation des variables d'environnement
db_user = os.getenv('POSTGRES_USER', 'postgres')
db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
db_name = os.getenv('POSTGRES_DB', 'playersdb')
db_host = os.getenv('DB_HOST', 'db')  # 'db' est le nom du service dans docker-compose
db_port = os.getenv('DB_PORT', '5432')

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'age': self.age
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/players', methods=['GET'])
def get_players():
    try:
        players = Player.query.all()
        return jsonify([player.to_dict() for player in players])
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des joueurs: {str(e)}")
        return jsonify({"error": "Une erreur s'est produite lors de la récupération des joueurs"}), 500

@app.route('/api/players', methods=['POST'])
def create_player():
    try:
        data = request.json
        new_player = Player(name=data['name'], position=data['position'], age=data['age'])
        db.session.add(new_player)
        db.session.commit()
        return jsonify(new_player.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la création du joueur: {str(e)}")
        return jsonify({"error": "Une erreur s'est produite lors de la création du joueur"}), 500

@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        return jsonify(player.to_dict())
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération du joueur {player_id}: {str(e)}")
        return jsonify({"error": "Une erreur s'est produite lors de la récupération du joueur"}), 500

@app.route('/api/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        data = request.json
        player.name = data.get('name', player.name)
        player.position = data.get('position', player.position)
        player.age = data.get('age', player.age)
        db.session.commit()
        return jsonify(player.to_dict())
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la mise à jour du joueur {player_id}: {str(e)}")
        return jsonify({"error": "Une erreur s'est produite lors de la mise à jour du joueur"}), 500

@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        db.session.delete(player)
        db.session.commit()
        return jsonify({"message": "Joueur supprimé avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la suppression du joueur {player_id}: {str(e)}")
        return jsonify({"error": "Une erreur s'est produite lors de la suppression du joueur"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)