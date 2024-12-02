from flask import Flask, request, redirect, Response
import csv
import os
import ngrok
from threading import Lock

app = Flask(__name__)

# Path to the CSV file
CSV_FILE = 'email_list.csv'

# Lock for file access
file_lock = Lock()

# Ensure the CSV file exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Email', 'Status'])  # Add headers: Email, Status


# Route to track clicks
@app.route('/track-click', methods=['GET'])
def track_click():
    email = request.args.get('email')

    if email:
        update_csv(email, 'Seen the email and Opened it')
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

    if email:
        update_csv(email, 'Seen the email and Not Opened it')
        # Return a 1x1 transparent GIF
        gif_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B'
        return Response(gif_data, content_type='image/gif')
    return "Invalid Request: Missing email parameter", 400


def update_csv(email, status):
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
                        row['Status'] = status  # Update status
                        updated = True
                    rows.append(row)

        # If the email wasn't found, append a new row
        if not updated:
            rows.append({'Email': email, 'Status': status})

        # Write back all rows to the CSV
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Email', 'Status'])
            writer.writeheader()
            writer.writerows(rows)


if __name__ == '__main__':
    app.run(debug=True)
