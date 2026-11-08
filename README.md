# StudyMate Excel Version 1

A beginner-friendly Excel tutor prototype built with Python and Streamlit.

## Run locally
1. Install Python 3.10 or newer.
2. Extract the ZIP and open a terminal in `StudyMate_Excel_V1`.
3. (Recommended) Create a virtual environment: `py -m venv .venv`
4. Activate it on Windows: `.venv\\Scripts\\activate` (macOS/Linux: `source .venv/bin/activate`).
5. Install dependencies: `pip install -r requirements.txt`
6. Run: `streamlit run app.py`
7. Open the local URL shown in the terminal, usually http://localhost:8501.

## Included
Dashboard, five learning modules, lesson explanations, worked examples, guided/hint/independent practice, answer feedback, sales project, Excel dataset download and session-based progress.

## Prototype limitations
Progress is stored only in the current Streamlit session and is not permanently saved. The answer checker compares responses with predefined answers; it does not execute arbitrary Excel formulas. The sales project uses pandas to calculate results and displays equivalent Excel formulas for learners to practise in Excel.
