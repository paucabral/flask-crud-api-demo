from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class NoteSchema(ma.Schema):
    class Meta:
        fields = ("id","title", "content")

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

# Create a new note
@app.route('/notes', methods=['POST'])
def create_note():
    try:
        data = {
            "title": request.json["title"],
            "content": request.json["content"]
        }
        print(data)
        note = Note(title=data["title"], content=data["content"])
        db.session.add(note)
        db.session.commit()
        
        response = {
            "note_id": note.id,
            "message": "Note created."
        }
        return jsonify(response), 200
    except (KeyError, TypeError):
        response = {
            "error": "Invalid data"
        }
        return jsonify(response), 400

@app.route('/notes', methods=['GET'])
def get_notes():
    all_notes = Note.query.all()
    response = notes_schema.dump(all_notes)
    return jsonify(response)

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    try:
        note = Note.query.get(note_id)
        if note:
            response = note_schema.dump(note)
            return note_schema.jsonify(note), 200
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except (ValueError, TypeError):
        response = {
            "error": "Invalid note ID"
        }
        return jsonify(response), 400
    
@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note = Note.query.get(note_id)
        if note:
            data = request.get_json()
            note.title = data['title']
            note.content = data['content']
            db.session.commit()

            response = note_schema.dump(note)
            return jsonify(response)
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except (KeyError, TypeError):
        response = {
            "error": "Invalid data"
        }
        return jsonify(response), 400

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        note = Note.query.get(note_id)
        if note:
            db.session.delete(note)
            db.session.commit()
            response = {
                "message": "Note deleted"
            }
            return jsonify(response)
        else:
            response = {
                "error": "Note not found"
            }
            return jsonify(response), 404
    except ValueError:
        response = {
            "error": "Invalid note ID"
        }
        return jsonify(), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)