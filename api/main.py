from flask import Flask, jsonify
from flask_cors import CORS
from routes.inheritance import inheritance_bp

app = Flask(__name__)
CORS(app)

# # --- Database Configuration ---
# # Get the absolute path for the project directory
# project_dir = os.path.abspath(os.path.dirname(__name__))
# # Define the database file path
# database_file = f"sqlite:///{os.path.join(project_dir, 'database', 'app.db')}"

# app.config['SQLALCHEMY_DATABASE_URI'] = database_file
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # --- Initialize Extensions ---
# db.init_app(app)
# migrate = Migrate(app, db)

# with app.app_context():
#     db.create_all()

# --- Blueprints Registration ---
app.register_blueprint(inheritance_bp, url_prefix='/api')
# app.register_blueprint(user_bp, url_prefix='/api/users')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
