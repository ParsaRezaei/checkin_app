from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import csv
import os
import asyncio
import threading
from queue import Queue

app = Flask(__name__)

# Path to the CSV file
CSV_FILE = 'check_ins_9.13.24.csv'

# Queue to hold incoming form data
form_queue = Queue()

# Write the header to the CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Email', 'Browser', 'Device', 'Check-in Time'])

# Asynchronous function to process the queue and write data to the CSV file
async def process_queue():
    while True:
        if not form_queue.empty():
            form_data = form_queue.get()
            with open(CSV_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(form_data)
                print("CSV updated")
            form_queue.task_done()  # Mark the task as done
        await asyncio.sleep(1)  # Pause for 1 second between writes

# Start the asyncio loop in a background thread
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkin', methods=['POST'])
def checkin():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    browser = request.form['browser']
    device = request.form['device']
    check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Add form data to the queue
    form_queue.put([name, email, browser, device, check_in_time])

    return redirect(url_for('thank_you'))

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

# Route to display all check-ins
@app.route('/checkins')
def show_checkins():
    check_ins = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse the check-in time from the CSV
            check_in_time_str = row['Check-in Time']
            check_in_time = datetime.strptime(check_in_time_str, '%Y-%m-%d %H:%M:%S')
            
            # Calculate how long ago the check-in occurred
            now = datetime.now()
            time_diff = now - check_in_time
            row['Time Ago'] = format_time_ago(time_diff)
            
            check_ins.append(row)
    
    return render_template('checkins.html', check_ins=check_ins)

# Helper function to format the time difference
def format_time_ago(time_diff):
    if time_diff.days > 0:
        return f"{time_diff.days} day"
    elif time_diff.seconds >= 3600:
        hours = time_diff.seconds // 3600
        return f"{hours} hr"
    elif time_diff.seconds >= 60:
        minutes = time_diff.seconds // 60
        return f"{minutes} min"
    else:
        return f"{time_diff.seconds} sec"

if __name__ == '__main__':
    # Initialize the asyncio loop
    loop = asyncio.new_event_loop()
    
    # Start the background thread with the asyncio loop
    threading.Thread(target=start_async_loop, args=(loop,), daemon=True).start()
    
    # Schedule the queue processing task to run
    asyncio.run_coroutine_threadsafe(process_queue(), loop)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)