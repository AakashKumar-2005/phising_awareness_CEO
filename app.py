from flask import Flask, request, redirect, Response, render_template, send_file
import csv
import os
from threading import Lock

app = Flask(__name__)

# Path to the CSV file
CSV_FILE = 'email_list.csv'

# Lock for file access
file_lock = Lock()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'secure1'


# Ensure the CSV file exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Email', 'Name', 'Status'])  # Add headers: Email, Name, Status


# Route to track clicks
@app.route('/track-click', methods=['GET'])
def track_click():
    email = request.args.get('email')
    name = request.args.get('name')

    if email:
        update_csv(email, 'Seen the email and Opened it', name)
        # Redirect to phishing awareness page
        response = redirect('https://aakashkumar-2005.github.io/phising_awareness_CEO/')
        response.headers['ngrok-skip-browser-warning'] = 'true'  # Skip ngrok browser warning
        response.headers['User-Agent'] = 'CustomUserAgent/1.0'   # Custom User-Agent
        response.headers['Cache-Control'] = 'no-store'          # Prevent caching
        return response
    return "Invalid Request: Missing email parameter", 400


# Route to track "Seen but Not Opened" (using tracking pixel)
@app.route('/track-view', methods=['GET'])
def track_view():
    email = request.args.get('email')
    name = request.args.get('name')

    if email:
        update_csv(email, 'Seen the email and Not Opened it', name)
        # Return a 1x1 transparent GIF
        gif_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B'

        return Response(gif_data, content_type='image/gif')
    return "Invalid Request: Missing email parameter", 400


def update_csv(email, status, name=None):
    """
    Safely update the CSV file with the email status.
    """
    with file_lock:  # Ensure thread-safe access
        updated = False
        rows = []

        # Read existing rows
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Email'] == email:
                        # Update status and keep the existing name if no new name is provided
                        row['Status'] = status
                        if name:
                            row['Name'] = name
                        updated = True
                    rows.append(row)

        # If the email wasn't found, append a new row
        if not updated:
            rows.append({'Email': email, 'Name': name or '', 'Status': status})

        # Write back all rows to the CSV
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Email', 'Name', 'Status'])
            writer.writeheader()
            writer.writerows(rows)

@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    # Read the data from CSV and count statuses
    data = []
    unseen_count = 0
    seen_count = 0
    opened_count = 0

    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
            if row['Status'] == 'unseen':
                unseen_count += 1
            elif row['Status'] == 'Seen the email':
                seen_count += 1
            elif row['Status'] == 'Seen the email and Opened it':
                opened_count += 1

    # Send the counts to frontend as pie data
    pie_data = {
        'labels': ['Unseen', 'Seen', 'Opened'],
        'data': [unseen_count, seen_count, opened_count]
    }

    return render_template('dashboard.html', data=data, pie_data=pie_data)


@app.route('/download-csv', methods=['GET'])
def download_csv():
    # Check for admin authentication
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return Response(
            'Access Denied: Invalid credentials',
            401,
            {'WWW-Authenticate': 'Basic realm="Admin Dashboard"'}
        )

    # Serve the CSV file
    return send_file(
        CSV_FILE,
        mimetype='text/csv',
        as_attachment=True,
        download_name='email_list.csv'
    )
@app.route('/filter', methods=['GET'])
def filter_data():
    status = request.args.get('status')  # Get the status from the URL (Unseen, Seen, Opened)
    filtered_data = []

    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Status'] == status:  # Filter employees by status
                filtered_data.append(row)

    return render_template('dashboard.html', data=filtered_data, pie_data={})


if __name__ == '__main__':
    app.run(debug=True)
