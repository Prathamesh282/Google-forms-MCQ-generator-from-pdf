import os
from flask import Flask, render_template, request, abort, json
from flask_bootstrap import Bootstrap
import spacy
import random
import requests
from PyPDF2 import PdfReader
from typing import List, Tuple
import google.generativeai as genai

app = Flask(__name__)
Bootstrap(app)

# --- MODEL AND API CONFIGURATION ---

# 1. Load the spaCy model for NLP tasks (this runs locally)
try:
    print("Loading spaCy model...")
    SPACY_MODEL = spacy.load("en_core_web_md")
    print("spaCy model loaded successfully! ✅")
except Exception as e:
    raise RuntimeError(f"Error loading spaCy model: {e}. Please run 'python -m spacy download en_core_web_md'")

# 2. Configure the Gemini API with your key
# IMPORTANT: Paste your secret API key here
API_KEY = ''
try:
    genai.configure(api_key=API_KEY)
    print("Gemini API configured successfully! ✅")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
# ----------------------------------------------------------------

# This is the NEW DEBUGGING version of your MCQ function
# This is the FINAL, UPGRADED version of your MCQ function
def get_mcqs(text: str, num_questions: int = 5) -> list:
    """
    Generates MCQs using a refined HYBRID approach:
    1. spaCy for identifying key concepts.
    2. A highly-tuned Gemini prompt for generating the full, natural-language MCQ.
    """
    print("\n--- Starting MCQ Generation ---")
    
    # === Step 1: Text Cleaning ===
    all_paragraphs = text.split('\n')
    good_paragraphs = [p.strip() for p in all_paragraphs if len(p.strip()) > 10] # Lowered threshold slightly
    print(f"Found {len(good_paragraphs)} good paragraphs.")
    if not good_paragraphs:
        return []
    clean_text = " ".join(good_paragraphs)

    # === Step 2: Key Concept Extraction (Your NLP work) ===
    doc = SPACY_MODEL(clean_text)
    potential_answers = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "DATE"]]
    unique_answers = list(set(potential_answers))
    random.shuffle(unique_answers)
    answers_to_use = unique_answers[:num_questions]
    print(f"Found {len(answers_to_use)} unique answers to generate questions for.")
    if not answers_to_use:
        return []

    # === Step 3: Creative Generation (LLM's work with a better prompt) ===
    formatted_mcqs = []
    model = genai.GenerativeModel('gemini-2.5-flash')

    for answer in answers_to_use:
        # Find the sentence where the answer appeared to provide context for the LLM
        context = ""
        for sent in doc.sents:
            if answer in sent.text:
                context = sent.text
                break
        if not context:
            continue

        # --- THE NEW, MORE POWERFUL PROMPT ---
        prompt = f"""
        You are an expert educator creating a quiz. Based on the following context, create a single multiple-choice question.

        **Rules:**
        1. The correct answer must be **exactly** "{answer}". If this answer seems incomplete, rephrase it into a natural, complete phrase based on the context.
        2. The question must be a direct and clear query. **Do not** start the question with phrases like "According to the context," or "Based on the provided text.".
        3. Generate three plausible but incorrect options (distractors) that are conceptually related to the correct answer.

        **Context:** "{context}"

        **Output Format:** Return ONLY a single, valid JSON object with this exact structure:
        {{"question": "Your generated question here?", "options": ["Option A", "Option B", "Option C", "Correct Answer"], "answer": "The polished correct answer here"}}
        ""
        
        try:
            response = model.generate_content(prompt)
            json_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            mcq = json.loads(json_response_text)

            question = mcq.get("question")
            options = mcq.get("options", [])
            correct_answer = mcq.get("answer") # Use the polished answer from the model
            
            if not all([question, options, correct_answer]) or correct_answer not in options:
                continue

            random.shuffle(options)
            correct_answer_index = options.index(correct_answer)
            correct_answer_letter = chr(65 + correct_answer_index)
            
            formatted_mcqs.append((question, options, correct_answer_letter))

        except Exception as e:
            print(f"Skipping an answer due to an error for '{answer}': {e}")
            continue
            
    print(f"\n--- Finished. Generated {len(formatted_mcqs)} MCQs successfully. ---")
    return formatted_mcqs


# --- YOUR ORIGINAL FLASK ROUTES AND FUNCTIONS (UNCHANGED) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = ""

        if 'files[]' in request.files and request.files.getlist('files[]')[0].filename:
            files = request.files.getlist('files[]')
            for file in files:
                if file.filename.endswith('.pdf'):
                    text += process_pdf(file)
                elif file.filename.endswith('.txt'):
                    text += file.read().decode('utf-8', errors='ignore')
        else:
            text = request.form['text']

        num_questions = int(request.form.get('num_questions', 5))
        
        # This now calls your new hybrid function!
        mcqs = get_mcqs(text, num_questions=num_questions)

        mcq_data = [(mcq[0], mcq[1]) for mcq in mcqs]
        # Make sure to use YOUR OWN Google Apps Script URL
        script_url = ""

        try:
            response = requests.post(script_url, data=json.dumps(mcq_data), headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                form_url = response.text
                return render_template('form_created.html', form_url=form_url)
            else:
                return f"Error creating form: {response.text}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template('index.html')

def process_pdf(file) -> str:
    text = ""
    try:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        abort(400, description=f"Failed to process PDF: {e}")
    return text

if __name__ == '__main__':
    app.run(debug=True)
