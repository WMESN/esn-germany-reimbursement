from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import yagmail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# Folder to save uploaded PDFs
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

YOUR_EMAIL = os.getenv("YOUR_EMAIL")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Function to check if the uploaded file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render the form
@app.route('/')
def index():
    return render_template('form.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get form fields
    name = request.form['name']
    email = request.form['email']
    file = request.files['file']

    # Check if the file is allowed (i.e., a PDF)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Send the email with attachment
        try:
            yag = yagmail.SMTP(SMTP_USER, SMTP_PASSWORD)
            yag.send(
                to=YOUR_EMAIL,
                subject='New Form Submission',
                contents=f'Name: {name}\nEmail: {email}',
                attachments=[filepath]
            )
            flash('Form submitted successfully! Email sent.', 'success')
            os.remove(filepath)
        except Exception as e:
            print(f"Error: {e}")
            flash('Error sending email.', 'danger')
            os.remove(filepath)
        return redirect(url_for('index'))
    else:
        flash('Invalid file format. Please upload a PDF.', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(host='0.0.0.0', port=3000)