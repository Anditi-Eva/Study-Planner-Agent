# Personal Study Planner Agent (MVP)

A beginner-friendly Streamlit app that recommends which subject to study next, tracks study time, and suggests a time slot around entered classes.

## 1. Requirements
- Python 3.10 or newer
- Internet access for the initial package installation
- VS Code (recommended)

## 2. Setup
Open this folder in VS Code. In the terminal, run:

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```bat
.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and start the app:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually http://localhost:8501. Open it in your browser.

## 3. First things to do
1. Open **Class timetable** and verify every prefilled class. These are rough estimates read from the screenshot, not guaranteed accurate. Fix group-specific blocks and add missing sessions.
2. Open **Subjects & targets** and confirm the nine subjects. Change the weekly target in the sidebar.
3. In **Today's recommendation**, review the suggested subject and time slot.
4. After studying, use **Log study time** to record completed minutes.
5. If you miss a session, log it as **Missed**. It does not count as completed time, so the subject remains behind its target.
6. Check **Progress** to see how time is distributed.

## 4. How the decision logic works
- Every subject gets the same weekly target by default.
- The app totals completed minutes for the current Monday–Sunday week.
- It selects the subject with the largest remaining time to target.
- It searches for a gap in the entered class timetable between 07:00 and 21:00.
- It respects the maximum daily study duration and preferred session length.

This is a transparent rule-based agent, not a trained machine-learning model. That is a good starting point: its decisions are understandable and easy to test.

## 5. Important limitations in this MVP
- The timetable screenshot is not parsed automatically; the class blocks are prefilled estimates and must be checked manually.
- It does not yet import Google Calendar, infer difficulty, or send reminders.
- The class-time search uses entered classes only; add work, commute, meals, and other commitments if you want those blocked out.
- Local CSV files store data on the machine running the app. Back them up if needed.
- The recommendation is a suggestion, not a replacement for your own judgment.

## 6. Suggested next improvements
1. Add image OCR for timetable extraction, with a review step before saving.
2. Add exam dates and assignment deadlines.
3. Add a weekly calendar view.
4. Add notifications or calendar export.
5. Add a simple natural-language chat interface after the core planner is reliable.
