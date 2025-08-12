from flask import Blueprint, request, jsonify
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS

from .. import app
from ..api.models import db, IdeaHistory
from ..utils.file_parser import parse_file
import os

from werkzeug.utils import secure_filename

api = Blueprint('api', __name__)
uploads = UploadSet('files', DOCUMENTS)


@api.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOADED_FILES_DEST'], filename))
        return jsonify({'message': '上传成功', 'filename': filename}), 200
    return jsonify({'error': 'Invalid file'}), 400


@api.route('/parse-file', methods=['POST'])
def parse_file_api():
    filename = request.json.get('file')
    text = parse_file(filename)
    return jsonify({'text': text}), 200


@api.route('/submit-idea', methods=['POST'])
def submit_idea():
    data = request.json
    idea = data['idea']
    params = data['params']
    # 存储到数据库
    new_idea = IdeaHistory(idea=idea, params=str(params), user_id=1)  # 假设用户ID
    db.session.add(new_idea)
    db.session.commit()
    # 触发prompt链（后续模块）
    return jsonify({'message': '提交成功', 'id': new_idea.id}), 200


@api.route('/history', methods=['GET'])
def get_history():
    ideas = IdeaHistory.query.filter_by(user_id=1).all()
    return jsonify([{'id': i.id, 'idea': i.idea} for i in ideas]), 200


@api.route('/templates', methods=['GET'])
def get_templates():
    # 硬编码或从DB加载
    templates = [{'name': 'Web App', 'content': '构建一个Web应用...'}]
    return jsonify(templates), 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}
