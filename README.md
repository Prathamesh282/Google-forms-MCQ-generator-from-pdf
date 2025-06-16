MCQ Generator from PDF/Text with Google Form Integration

This web application allows users to upload `.pdf` or `.txt` files (or manually input text) to automatically generate Multiple Choice Questions (MCQs) using NLP via spaCy. The MCQs are then sent to a Google Apps Script backend to create a Google Form.

## 🚀 Features

- 📄 Accepts PDF and TXT file uploads
- ✍️ Manual text input supported
- 🤖 Uses spaCy to extract key nouns and generate MCQs
- 📑 Supports custom number of questions
- 🌐 Automatically creates a Google Form from the generated MCQs
- 🧠 Randomized distractors and shuffled answer choices

## 🧰 Requirements

Install the following Python libraries:

pip install flask flask-bootstrap spacy PyPDF2 requests
python -m spacy download en_core_web_sm


📝 How It Works
Upload a .pdf, .txt, or enter text manually.
Select the number of MCQs to generate.

The app:
Extracts sentences and nouns using spaCy
Forms a blanked sentence for the question stem
Adds distractors and shuffles choices
MCQs are sent to a Google Apps Script endpoint.
A Google Form link is returned and displayed.


🌐 Google Apps Script Setup
You must create and deploy a Google Apps Script web app to receive and process MCQ data into a Google Form.

Replace this placeholder URL in app.py:

script_url = "https://script.google.com/macros/s/your-script-id/exec"
Your script should accept POST requests with JSON data and return a Google Form link.

🔧 Running the App

python app.py
Then open http://127.0.0.1:5000 in your browser.

📃 License
MIT License

🙏 Acknowledgments
spaCy
Flask
PyPDF2
Bootstrap
Google Apps Script for Form automation
