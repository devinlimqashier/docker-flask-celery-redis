import celery.states as states
from flask import Flask, Response
from flask import url_for, jsonify, request
from worker import celery
import redis

dev_mode = True
app = Flask(__name__)
r = redis.Redis(host="redis")


@app.route('/add/<int:param1>/<int:param2>')
def add(param1: int, param2: int) -> str:
    task = celery.send_task('tasks.add', args=[param1, param2], kwargs={}, queue='')
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
    return response


@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)


@app.route('/health_check')
def health_check() -> Response:
    return jsonify("OK")

@app.route('/print', methods=['POST'])
def printer():
    body = request.json
    ip = body.get('ip')
    message = body.get('message')
    task = celery.send_task(f'tasks.printer', args=[ip, message], kwargs={}, queue=getQueue(ip))
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
    return response

# WIP.
# The below code is trying to get/set a queue pool from a redis (in memory database)  server
# The part i have not figured out here is the storage/retrieval of a list/array in Redis
def getQueue(ip: str):
    print(r)
    if not r.get("queue_pool"): r.json().set("queue_pool", [f"queue_{x}" for x in range(20)])
    print(r.get("queue_pool"))
    queue_pool = r.get("queue_pool")
    queue = queue_pool.pop()
    r.set("queue_pool", queue_pool)
    r.set(ip, queue)
    return queue

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
