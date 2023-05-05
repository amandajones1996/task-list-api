from flask import Blueprint, jsonify, abort, make_response, request
from app import db
from app.models.task import Task
from datetime import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

def validate_task(task_id):
    try: 
        task_id = int(task_id)
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    
    task = Task.query.get(task_id)

    if not task: 
        abort(make_response({"details": f"Task id {task_id} not found"}, 404))
        
    return task 

@tasks_bp.route("", methods=['POST'])
def create_task():
    request_body = request.get_json()

    if not request_body.get("title") or not request_body.get("description"):
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"]
    )

    db.session.add(new_task)
    db.session.commit()

    return {
        "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": True if new_task.completed_at else False
        }
    }, 201

@tasks_bp.route("", methods=['GET'])
def read_all_tasks():
    task_response = []
    sort_query = request.args.get("sort")

    if sort_query == 'asc':
        tasks = Task.query.order_by(Task.title.asc()).all()
    elif sort_query == 'desc':
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()

    for task in tasks:
        task_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description, 
            "is_complete": True if task.completed_at else False
        })
    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=['GET'])
def read_task_by_id(task_id):
    task = validate_task(task_id)
    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description, 
            "is_complete": True if task.completed_at else False
        }
    }, 200

@tasks_bp.route("/<task_id>", methods=['PUT'])
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True if task.completed_at else False
        }
    }, 200

@tasks_bp.route("/<task_id>/mark_complete", methods=['PATCH'])
def mark_complete_task(task_id):
    task = validate_task(task_id)

    # if task.completed_at:
    #     return make_response({"details":f"Task with id {task_id} is already completed"})

    task.completed_at = datetime.utcnow()

    db.session.commit()
    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True 
        }
    }, 200
@tasks_bp.route("/<task_id>/mark_incomplete", methods=['PATCH'])
def mark_incomplete_task(task_id):
    task = validate_task(task_id)

    # if task.completed_at:
    #     return make_response({"details":f"Task with id {task_id} is already completed"})

    task.completed_at = None

    db.session.commit()
    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False 
        }
    }, 200

@tasks_bp.route("/<task_id>", methods=['DELETE'])
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()
    
    return make_response({'details': f'Task {task.task_id} "{task.title}" successfully deleted'}, 200)