import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="Personal Study Planner Agent", page_icon="📚", layout="wide")
DATA = Path("study_planner_data")
DATA.mkdir(exist_ok=True)
SUBJECTS_FILE = DATA / "subjects.csv"
CLASSES_FILE = DATA / "classes.csv"
SESSIONS_FILE = DATA / "sessions.csv"

DEFAULT_SUBJECTS = [
    ("ETI 2501X", "Project"),
    ("ETI 2502", "Data Communications"),
    ("ETI 2503", "Reliability Engineering"),
    ("ETI 2504", "Wireless Communication I"),
    ("ETI 2505", "Digital Signal Processing"),
    ("HBC 2112", "Business Law I"),
    ("ICS 2403", "Distributed Computing and Applications"),
    ("ETI 2506", "Telecommunication Systems"),
   
]
# Edit/verify these in the Class timetable tab.
DEFAULT_CLASSES = [
    ("Monday", "07:00", "09:00", "ETI 2506", ""),
    ("Monday", "09:00", "11:00", "ETI 2504", ""),
    ("Monday", "11:00", "13:00", "ICS 2403", ""),
    ("Tuesday", "07:00", "10:00", "ETI 2505", ""),
    ("Tuesday", "10:00", "12:00", "ETI 2502", ""),
    ("Tuesday", "12:00", "14:00", "ETI 2506", ""),
    ("Tuesday", "14:00", "19:00", "ETI 2501X", ""),
    ("Wednesday", "10:00", "12:00", "ETI 2503", ""),
    ("Wednesday", "14:00", "16:00", "ETI 2505", ""),
    ("Thursday", "10:00", "12:00", "ETI 2504", ""),
    ("Thursday", "12:00", "14:00", "ETI 2503", ""),
    ("Thursday", "15:00", "19:00", "ETI 2501X", ""),
    ("Friday", "07:00", "10:00", "ICS 2403", ""),
    ("Friday", "10:00", "13:00", "HBC 2112", ""),
    ("Friday", "14:00", "16:00", "ETI 2502", ""),
]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def init_file(path, rows, columns):
    if not path.exists():
        pd.DataFrame(rows, columns=columns).to_csv(path, index=False)

init_file(SUBJECTS_FILE, DEFAULT_SUBJECTS, ["code", "subject"])
init_file(CLASSES_FILE, DEFAULT_CLASSES, ["day", "start", "end", "code", "notes"])
init_file(SESSIONS_FILE, [], ["date", "code", "minutes", "status", "notes"])

def load(path, cols):
    try:
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns: df[c] = ""
        return df[cols].fillna("")
    except Exception:
        return pd.DataFrame(columns=cols)

subjects = load(SUBJECTS_FILE, ["code", "subject"])
classes = load(CLASSES_FILE, ["day", "start", "end", "code", "notes"])
sessions = load(SESSIONS_FILE, ["date", "code", "minutes", "status", "notes"])
subject_map = dict(zip(subjects["code"].astype(str), subjects["subject"].astype(str)))

st.title("📚 Personal Study Planner Agent")
st.caption("A small, transparent study-planning agent: it tracks time, selects the most under-studied subject, and suggests a session around classes.")
st.info("Please verify every class block in **Class timetable** before relying on recommendations.")

with st.sidebar:
    st.header("Planning settings")
    daily_limit = st.number_input("Maximum study time per day (hours)", min_value=0.5, max_value=8.0, value=2.0, step=0.5)
    session_minutes = st.select_slider("Preferred session length", options=[25, 30, 45, 60, 90, 120], value=60)
    weekly_hours = st.number_input("Weekly study target per subject (hours)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    st.caption("Equal allocation means the same target per subject. The agent prioritizes the subject furthest behind that target.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Today's recommendation", "Subjects & targets", "Class timetable", "Log study time", "Progress"])

with tab2:
    st.subheader("Your subjects")
    edited_subjects = st.data_editor(subjects, num_rows="dynamic", use_container_width=True, key="subjects_editor",
        column_config={"code": st.column_config.TextColumn("Subject code", required=True),
                       "subject": st.column_config.TextColumn("Subject name", required=True)})
    if st.button("Save subjects", key="save_subjects"):
        edited_subjects = edited_subjects.dropna(subset=["code"])
        edited_subjects.to_csv(SUBJECTS_FILE, index=False)
        st.success("Subjects saved.")
        st.rerun()
    st.caption("Add or remove subjects depending on whether you need to study it weekly.")

with tab3:
    st.subheader("Class timetable")
    st.write("Time format is 24-hour (for example, 13:00).")
    edited_classes = st.data_editor(classes, num_rows="dynamic", use_container_width=True, key="classes_editor",
        column_config={
            "day": st.column_config.SelectboxColumn("Day", options=DAYS, required=True),
            "start": st.column_config.TextColumn("Start (HH:MM)", required=True),
            "end": st.column_config.TextColumn("End (HH:MM)", required=True),
            "code": st.column_config.SelectboxColumn("Subject code", options=subjects["code"].astype(str).tolist(), required=True),
            "notes": st.column_config.TextColumn("Notes / group")
        })
    if st.button("Save class timetable"):
        edited_classes.to_csv(CLASSES_FILE, index=False)
        st.success("Class timetable saved.")
        st.rerun()
    st.warning("Do not assume a blank cell means a free period until you have checked the original timetable and your group allocation.")

with tab4:
    st.subheader("Log a study session")
    if subjects.empty:
        st.warning("Add subjects first.")
    else:
        with st.form("log_form"):
            log_date = st.date_input("Study date", value=date.today())
            log_code = st.selectbox("Subject", subjects["code"].astype(str).tolist(),
                                    format_func=lambda c: f"{c} — {subject_map.get(c, '')}")
            log_minutes = st.number_input("Minutes studied", min_value=5, max_value=300, value=60, step=5)
            log_status = st.selectbox("Status", ["Completed", "Missed"])
            log_notes = st.text_input("Notes (optional)")
            submitted = st.form_submit_button("Save session")
        if submitted:
            new = pd.DataFrame([{"date": str(log_date), "code": log_code, "minutes": int(log_minutes),
                                 "status": log_status, "notes": log_notes}])
            pd.concat([sessions, new], ignore_index=True).to_csv(SESSIONS_FILE, index=False)
            st.success("Session logged.")
            st.rerun()
    st.caption("Log completed sessions to update balance. A missed session is recorded as missed; its time remains outstanding and can be suggested again.")

def safe_time(s):
    try: return datetime.strptime(str(s).strip(), "%H:%M").time()
    except Exception: return None

def free_windows(day_name, class_df):
    events=[]
    for _, r in class_df[class_df["day"].astype(str)==day_name].iterrows():
        a,b=safe_time(r["start"]),safe_time(r["end"])
        if a and b and a < b: events.append((a,b))
    events.sort()
    windows=[]
    cursor=time(7,0); finish=time(21,0)
    for a,b in events:
        if b <= cursor or a >= finish: continue
        a=max(a,cursor); b=min(b,finish)
        if a>cursor: windows.append((cursor,a))
        cursor=max(cursor,b)
    if cursor<finish: windows.append((cursor,finish))
    return [(a,b) for a,b in windows if (datetime.combine(date.today(),b)-datetime.combine(date.today(),a)).total_seconds()>=session_minutes*60]

def get_completed():
    if sessions.empty: return pd.Series(dtype=float)
    done=sessions[sessions["status"].astype(str).str.lower()=="completed"].copy()
    if done.empty: return pd.Series(dtype=float)
    done["minutes"]=pd.to_numeric(done["minutes"], errors="coerce").fillna(0)
    return done.groupby(done["code"].astype(str))["minutes"].sum()

with tab1:
    st.subheader("What should I study next?")
    today = date.today()
    today_name = today.strftime("%A")
    completed = get_completed()
    week_start = today - timedelta(days=today.weekday())
    if not sessions.empty:
        ss=sessions.copy()
        ss["parsed_date"]=pd.to_datetime(ss["date"], errors="coerce")
        week_done=ss[(ss["parsed_date"]>=pd.Timestamp(week_start)) &
                     (ss["parsed_date"]<pd.Timestamp(week_start+timedelta(days=7))) &
                     (ss["status"].astype(str).str.lower()=="completed")].copy()
        week_done["minutes"]=pd.to_numeric(week_done["minutes"], errors="coerce").fillna(0)
        week_by_code=week_done.groupby(week_done["code"].astype(str))["minutes"].sum()
    else:
        week_by_code=pd.Series(dtype=float)
    if subjects.empty:
        st.warning("Add at least one subject in Subjects & targets.")
    else:
        overview=[]
        for _, r in subjects.iterrows():
            code=str(r["code"])
            done_min=float(week_by_code.get(code,0))
            target=weekly_hours*60
            overview.append({"Code":code,"Subject":str(r["subject"]),"Studied this week (min)":int(done_min),
                             "Target (min)":int(target),"Remaining (min)":max(0,int(target-done_min))})
        progress=pd.DataFrame(overview)
        st.dataframe(progress, use_container_width=True, hide_index=True)
        behind=progress.sort_values(["Remaining (min)","Studied this week (min)"], ascending=[False,True])
        choice=behind.iloc[0]
        st.markdown("### Agent recommendation")
        st.success(f"Study **{choice['Subject']} ({choice['Code']})** next for up to **{min(session_minutes, int(daily_limit*60))} minutes**.")
        st.write(f"It has **{choice['Remaining (min)']} minutes** remaining toward this week's equal target of {int(weekly_hours*60)} minutes per subject.")
        day_classes=classes[classes["day"].astype(str)==today_name]
        if not day_classes.empty:
            st.write("**Classes listed for today:**")
            st.dataframe(day_classes[["start","end","code","notes"]], use_container_width=True, hide_index=True)
        windows=free_windows(today_name, classes)
        slot=None
        for a,b in windows:
            available=int((datetime.combine(today,b)-datetime.combine(today,a)).total_seconds()/60)
            if available>=min(session_minutes,int(daily_limit*60)):
                slot=(a,b); break
        if slot:
            st.info(f"Suggested slot: **{slot[0].strftime('%H:%M')}–{(datetime.combine(today,slot[0])+timedelta(minutes=min(session_minutes,int(daily_limit*60)))).time().strftime('%H:%M')}** (based on class blocks entered; confirm travel, meals and personal commitments).")
        else:
            st.warning("No suitable slot found between 07:00 and 21:00 using the class timetable. Try a shorter session or check the class entries.")
        st.caption("This first version chooses the subject with the largest remaining weekly target. It does not yet read image text automatically or sync with Google Calendar.")

with tab5:
    st.subheader("Study progress")
    if subjects.empty:
        st.info("Add subjects to see progress.")
    else:
        rows=[]
        for _,r in subjects.iterrows():
            code=str(r["code"])
            mins=float(completed.get(code,0))
            rows.append({"Subject":str(r["subject"]),"Code":code,"All-time completed (hours)":round(mins/60,2),
                         "This week's completed (hours)":round(float(week_by_code.get(code,0))/60,2),
                         "Weekly target (hours)":weekly_hours})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if not sessions.empty:
            st.markdown("#### Session history")
            st.dataframe(sessions.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
            if st.button("Export session history CSV"):
                st.download_button("Download CSV", sessions.to_csv(index=False).encode("utf-8"), "study_sessions.csv", "text/csv")
        st.caption("Data is saved locally in the study_planner_data folder on the computer running Streamlit.")
