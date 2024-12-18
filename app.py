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


# Route to track both views and clicks
@app.route('/track', methods=['GET'])
def track():
    email = request.args.get('email')
    name = request.args.get('name')
    action = request.args.get('action')

    if email and action:
        if action == 'open':  # User clicked and opened the email
            update_csv(email, 'Seen the email and Opened it', name)
            # Redirect to phishing awareness page
            response = redirect('https://aakashkumar-2005.github.io/phising_awareness_CEO/')
            response.headers['ngrok-skip-browser-warning'] = 'true'  # Skip ngrok browser warning
            response.headers['User-Agent'] = 'CustomUserAgent/1.0'   # Custom User-Agent
            response.headers['Cache-Control'] = 'no-store'          # Prevent caching
            return response
        elif action == 'view':  # User only viewed the email
            update_csv(email, 'Seen the email', name)
            return Response(status=204)  # No content response as it is just a view
        else:
            return "Invalid action", 400
    return "Invalid Request: Missing email or action parameter", 400


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

@app.route('/filter', methods=['GET'])
def filter_data():
    status = request.args.get('status')  # Get the status from the URL (Unseen, Seen, Opened)
    filtered_data = []
    unseen_count = 0
    seen_count = 0
    opened_count = 0

    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Status'] == status:  # Filter employees by status
                filtered_data.append(row)
                if row['Status'] == 'unseen':
                    unseen_count += 1
                elif row['Status'] == 'Seen the email':
                    seen_count += 1
                elif row['Status'] == 'Seen the email and Opened it':
                    opened_count += 1

    # Send the filtered data and updated pie data to frontend
    pie_data = {
        'labels': ['Unseen', 'Seen', 'Opened'],
        'data': [unseen_count, seen_count, opened_count]
    }

    return render_template('dashboard.html', data=filtered_data, pie_data=pie_data)


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


if __name__ == '__main__':
    app.run(debug=True)
