import psutil
import time
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Store previous CPU times globally
prev_times = {}

def get_process_data():
    global prev_times
    processes = []
    current_times = {}
    total_cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_times', 'memory_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            status = proc.info['status']
            memory_percent = proc.info['memory_percent']
            cpu_times = proc.info['cpu_times']

            # Calculate CPU usage based on time difference
            if pid in prev_times:
                prev = prev_times[pid]
                delta_user = cpu_times.user - prev['user']
                delta_system = cpu_times.system - prev['system']
                delta_time = time.time() - prev['timestamp']
                cpu_percent = (delta_user + delta_system) / delta_time * 100 if delta_time > 0 else 0.0
            else:
                cpu_percent = 0.0  # First call for this process

            current_times[pid] = {'user': cpu_times.user, 'system': cpu_times.system, 'timestamp': time.time()}
            processes.append({
                'pid': pid,
                'name': name,
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    prev_times = current_times
    processes.sort(key=lambda p: p['cpu_percent'], reverse=True)  # Sort by CPU usage
    return {'processes': processes, 'cpu_usage': total_cpu, 'memory_usage': memory}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def data():
    return jsonify(get_process_data())

if __name__ == '__main__':
    app.run(debug=True)