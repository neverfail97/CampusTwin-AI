"""Server-side API for Smart Campus Management using Supabase PostgreSQL."""
from __future__ import annotations

import hashlib
import os
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from supabase import create_client

load_dotenv()
app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-this-before-deploying")

url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key) if url and key else None


def now(): return datetime.now(timezone.utc).isoformat()
def code_hash(value): return hashlib.sha256(value.strip().encode()).hexdigest()
def error(message, status=400): return jsonify({"error": message}), status
def client():
    if not supabase: raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to .env.")
    return supabase
def signed_in(role=None):
    profile = session.get("profile")
    if not profile: return None
    return profile if not role or profile["role"] == role else None
def require(role=None):
    profile = signed_in(role)
    return profile or None



CHAT_KNOWLEDGE = {
    "twin": {
        "name": "CampusTwin AI Guide",
        "scope": "CampusTwin AI overview page only.",
        "topics": "CampusConnect academic operations, EcoCampus sustainability operations, navigation between the two systems, and which system handles a task.",
    },
    "connect": {
        "name": "CampusConnect Assistant",
        "scope": "CampusConnect main page only. Explain Rooms & Resources, AI Resource Optimizer, Maintenance Desk, Timetable, Syllabus Progress, Dashboard, Room Map, AI Insights and Report Issue.",
        "topics": "Rooms can be added or edited through the room pop-up. Dashboard covers room availability, occupancy, issues and syllabus coverage. Room Map supports room selection and details. Maintenance follows issue reporting and repair/verification. Timetable checks clashes. Syllabus records coverage.",
    },
    "eco": {
        "name": "EcoCampus Advisor",
        "scope": "EcoCampus main page only. Explain dashboard, campus map, resources, AI insights, maintenance operations, impact, what-if simulator, building profiles, Eco Score and reporting.",
        "topics": "EcoCampus action loop is Measure -> Detect -> Explain -> Act -> Verify -> Save. Hostel A has a water anomaly example. The What-If Simulator produces projections, not measured savings. Building profiles show water, energy, waste, occupancy, alerts and recommendations.",
    },
}

LOCAL_CHAT_RULES = {
    "twin": [
        (lambda q: any(x in q for x in ("campusconnect", "connect")), "CampusConnect is the academic-operations side: rooms and resources, AI Resource Optimizer, maintenance, clash-free timetable and syllabus progress."),
        (lambda q: any(x in q for x in ("ecocampus", "eco campus", "water", "energy", "waste", "sustainability")), "EcoCampus is the sustainability side: water, energy and waste monitoring, Eco Score, campus map, AI insights, maintenance actions, impact and issue reporting."),
        (lambda q: "navigate" in q or "where" in q or "how do i use" in q, "Use the main CampusTwin switcher to enter CampusConnect or EcoCampus. Each system keeps its own dashboard, operations and reporting workflows."),
    ],
    "connect": [
        (lambda q: "add" in q and "room" in q, "Open Operations → Rooms & resources → Add room. Fill the room pop-up, then press Add room. The browser prompt/alert is not used for room entry."),
        (lambda q: any(x in q for x in ("update room", "edit room", "change room")), "Open Operations → Rooms & resources, find the room, and use its Edit action. Update the fields in the same pop-up and save."),
        (lambda q: any(x in q for x in ("optimizer", "best room", "recommend room")), "Open AI Resource Optimizer. Enter student count, day/time and required equipment. It evaluates capacity, status, timetable conflicts, maintenance issues and equipment availability."),
        (lambda q: any(x in q for x in ("maintenance", "repair", "issue queue")), "Open Maintenance desk to review active issues. Issues move through reporting, assignment, In Progress/Resolved repair updates and faculty verification."),
        (lambda q: "report" in q and any(x in q for x in ("include", "content", "write", "what should")), "A strong report should include the room, exact problem/equipment, when it started, impact on teaching, priority and requested action. Example: CSE-103 projector not displaying input during class; observed at 10:15; teaching blocked; High priority; inspect projector and cable."),
        (lambda q: "report" in q or "complaint" in q, "Open Report issue. Enter faculty email, room, priority and a clear description, then submit."),
        (lambda q: any(x in q for x in ("timetable", "clash", "schedule")), "Open Clash-free timetable. Enter day, section, start/end time, room and subject. The system checks overlapping room bookings before saving."),
        (lambda q: any(x in q for x in ("syllabus", "coverage", "progress")), "Open Syllabus progress. Record subject code, week, coverage percentage, credits and topics covered, then save the weekly update."),
        (lambda q: any(x in q for x in ("dashboard", "occupancy")), "CampusConnect Dashboard summarizes rooms available, seat occupancy, open issues and syllabus coverage. Chart tabs switch between Occupancy, Issues and Coverage."),
        (lambda q: "room map" in q or ("map" in q and "room" in q), "Room Map lets you choose a room from the selector or click a map block. The detail panel shows capacity, occupancy, equipment, status and the recommended action."),
    ],
    "eco": [
        (lambda q: "hostel" in q and any(x in q for x in ("anomaly", "water", "investigate")), "Open AI Insights and choose the Hostel A water anomaly. Investigate it to see current usage, expected baseline, deviation, detected pattern, possible causes, confidence and the recommended action. Then create a maintenance ticket."),
        (lambda q: any(x in q for x in ("what-if", "what if", "simulator", "simulate improvement")), "The What-If Simulator lets you adjust projected reductions for water, energy and waste. It calculates projected monthly impact and clearly treats those values as projections, not measured savings."),
        (lambda q: any(x in q for x in ("maintenance", "active issue", "assign", "in progress", "resolved")), "EcoCampus Maintenance Command Center follows Detect → Assign → In progress → Resolved. After simulated repair, the system can show verification and estimated savings."),
        (lambda q: any(x in q for x in ("impact", "saving", "savings")), "Campus Impact summarizes this month's estimated water saved, energy saved, waste diverted, CO₂ reduction and cost avoided, with trend information."),
        (lambda q: "eco score" in q or "score" in q, "Eco Score is transparent: review water efficiency, energy efficiency, waste management and issue response rather than treating the score as an unexplained AI number."),
        (lambda q: any(x in q for x in ("building profile", "hostel a profile", "building")), "A building profile can show Eco Score, water, energy, waste, occupancy, active alerts and an AI recommendation. Select a building from the campus map to inspect it."),
        (lambda q: "forecast" in q or "prediction" in q or "predict" in q, "The AI Forecast card provides a forward-looking signal, such as projected energy demand peaks, plus a recommended preparation action."),
        (lambda q: "report" in q and any(x in q for x in ("include", "content", "what should", "write")), "For an EcoCampus report, choose a quick category such as Water leak, Energy waste, Waste problem, HVAC issue or Other, then provide the location, what you observed, a useful description and any available photo. The system returns a ticket and status."),
        (lambda q: "report" in q or "complaint" in q, "Open Report Issue, choose the category, location and description, attach a photo if available, and submit. The resulting ticket can enter the maintenance workflow."),
        (lambda q: any(x in q for x in ("dashboard", "water", "energy", "waste")), "EcoCampus Dashboard monitors water, energy and waste against baselines and shows Eco Score and resource signals. Use an anomaly's action control to move from detection into investigation and maintenance."),
    ],
}

def local_chat_answer(mode, question):
    q = " ".join(question.lower().strip().split())
    for matcher, answer in LOCAL_CHAT_RULES.get(mode, []):
        if matcher(q):
            return answer
    return None

def chat_context(mode, page):
    base = CHAT_KNOWLEDGE.get(mode, CHAT_KNOWLEDGE["twin"])
    return f"Assistant: {base['name']}\nScope: {base['scope']}\nCurrent page: {page or 'main page'}\nProduct knowledge: {base['topics']}"

def call_ai_chat(mode, page, question, history):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-6-luna").strip()
    endpoint = os.environ.get("OPENAI_RESPONSES_URL", "https://api.openai.com/v1/responses").strip()
    instructions = (
        "You are a helpful in-product assistant for CampusTwin AI. Answer only about the application's documented features. "
        "Do not invent buttons, data, APIs, permissions or capabilities. If the user asks how to perform an action, give short numbered steps. "
        "Distinguish measured values from projected/simulated values. Never reveal or request secret API keys. "
        + chat_context(mode, page)
    )
    recent = []
    for item in (history or [])[-8:]:
        role = item.get("role") if isinstance(item, dict) else None
        content = item.get("content") if isinstance(item, dict) else None
        if role in ("user", "assistant") and isinstance(content, str):
            recent.append({"role": role, "content": content[:2000]})
    recent.append({"role": "user", "content": question[:4000]})
    payload = {"model": model, "instructions": instructions, "input": recent, "max_output_tokens": 500}
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))
        if isinstance(data.get("output_text"), str) and data["output_text"].strip():
            return data["output_text"].strip()
        texts = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    texts.append(content["text"])
        return "\n".join(texts).strip() or None
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

@app.post("/api/chat")
def chat():
    data = request.get_json() or {}
    mode = data.get("mode", "twin") if data.get("mode") in CHAT_KNOWLEDGE else "twin"
    page = str(data.get("page", "main"))[:100]
    question = str(data.get("question", "")).strip()
    if not question:
        return error("Enter a question.")
    local = local_chat_answer(mode, question)
    if local:
        return jsonify({"answer": local, "source": "local"})
    ai = call_ai_chat(mode, page, question, data.get("history", []))
    if ai:
        return jsonify({"answer": ai, "source": "ai"})
    fallback = {
        "twin": "I can explain CampusConnect, EcoCampus, navigation and what each system is used for. Ask me about one of those features.",
        "connect": "I can help with Rooms & Resources, the Optimizer, Maintenance, Timetable, Syllabus Progress, Dashboard, Room Map, AI Insights and reporting. Ask me how to use a specific feature.",
        "eco": "I can help with the EcoCampus dashboard, anomalies, maintenance workflow, What-If Simulator, building profiles, Eco Score, Campus Impact and issue reporting.",
    }[mode]
    return jsonify({"answer": fallback, "source": "local-fallback"})

@app.errorhandler(RuntimeError)
def config_error(exc): return error(str(exc), 503)

@app.get("/")
def home(): return send_from_directory("templates", "index.html")

@app.get("/api/session")
def get_session(): return jsonify({"profile": session.get("profile")})

@app.post("/api/session")
def sign_in():
    """Stores a faculty/maintenance identity in Supabase; access code remains hashed."""
    data = request.get_json() or {}
    name, email, access_code = (data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("access_code", "").strip())
    role = data.get("role", "faculty")
    if not name or not email or not access_code or "@" not in email or role not in ("faculty", "worker"):
        return error("Enter a name, valid email, access code and role.")
    db = client(); existing = db.table("profiles").select("*").eq("email", email).execute().data
    if existing:
        profile = existing[0]
        if profile["name"].casefold() != name.casefold() or profile["access_code_hash"] != code_hash(access_code) or profile["role"] != role:
            return error("The supplied name, role or access code does not match this email.", 403)
    else:
        profile = db.table("profiles").insert({"name": name, "email": email, "role": role, "access_code_hash": code_hash(access_code)}).execute().data[0]
    session["profile"] = {"id": profile["id"], "name": profile["name"], "email": profile["email"], "role": profile["role"]}
    return jsonify({"profile": session["profile"]})

@app.delete("/api/session")
def sign_out(): session.clear(); return jsonify({"message": "Signed out."})

@app.get("/api/dashboard")
def dashboard():
    db = client(); rooms = db.table("rooms").select("capacity, benches, occupied_seats, status").execute().data
    issues = db.table("issues").select("id").neq("status", "Verified").execute().data
    return jsonify({"rooms": len(rooms), "available": sum(x["status"] == "Available" for x in rooms), "attention": sum(x["status"] == "Attention" for x in rooms), "empty": sum(x["status"] == "Empty" for x in rooms), "unavailable": sum(x["status"] == "Unavailable" for x in rooms), "benches": sum(x["benches"] for x in rooms), "seats": sum(x["capacity"] for x in rooms), "occupied": sum(x["occupied_seats"] for x in rooms), "open_issues": len(issues)})

@app.get("/api/rooms")
def rooms():
    term, category = request.args.get("q", ""), request.args.get("category", "")
    query = client().table("rooms").select("*").order("room_number")
    if category: query = query.eq("category", category)
    data = query.execute().data
    if term: data = [r for r in data if term.casefold() in f"{r['room_number']} {r['room_name']}".casefold()]
    return jsonify(data)

@app.post("/api/optimizer")
def optimize_room():
    """Constraint-based campus resource recommendation with explainable scoring."""
    profile = require("faculty")
    if not profile:
        return error("Sign in as faculty to use the AI Resource Optimizer.", 401)
    data = request.get_json() or {}
    try:
        students = int(data.get("students", 0))
    except (TypeError, ValueError):
        return error("Student count must be a positive number.")
    day, start_time, end_time = data.get("day"), data.get("start_time"), data.get("end_time")
    if students < 1 or not day or not start_time or not end_time or start_time >= end_time:
        return error("Enter a day, valid time range, and student count.")

    db = client()
    rooms_data = db.table("rooms").select("*").execute().data
    entries = db.table("timetable").select("room_id,start_time,end_time,section,faculty_id").eq("day", day).execute().data
    issues_data = [issue for issue in db.table("issues").select("room_id,title,status,priority").execute().data if issue["status"] != "Verified"]
    active_issues = {}
    for issue in issues_data:
        active_issues.setdefault(issue["room_id"], []).append(issue)
    recommendations, rejected = [], []

    for room in rooms_data:
        reasons = []
        conflicts = [entry for entry in entries if entry["room_id"] == room["id"] and entry["start_time"] < end_time and entry["end_time"] > start_time]
        if room["status"] != "Available": reasons.append(f"room status is {room['status'].lower()}")
        if room["capacity"] < students: reasons.append(f"capacity is {room['capacity']}, below the required {students}")
        if data.get("projector") and room["projector"] != "Available": reasons.append("projector is unavailable")
        if data.get("network") and room["internet"] != "Available": reasons.append("network is unavailable")
        if data.get("board") and room["board"] not in ("Available", "Whiteboard", "Smart Board"): reasons.append("board is unavailable")
        if conflicts: reasons.append("has a timetable conflict")
        if active_issues.get(room["id"]): reasons.append("has an unresolved maintenance issue")
        if reasons:
            rejected.append({"room_number": room["room_number"], "room_name": room["room_name"], "reasons": reasons})
            continue
        spare = room["capacity"] - students
        score = 100 - min(spare, 60) * 0.45 - min(room["occupied_seats"], 80) * 0.05
        if room["category"] == "Classroom":
            score += 15  # Prefer teaching-ready classroom space over a laboratory when both fit.
        suitability = [f"{room['capacity']} seats for {students} students", "Available status", "no timetable conflict"]
        if data.get("projector"): suitability.append("projector available")
        if data.get("network"): suitability.append("network available")
        if data.get("board"): suitability.append("board available")
        if room["category"] == "Classroom": suitability.append("teaching-ready classroom setting")
        recommendations.append({"room_id":room["id"], "room_number":room["room_number"], "room_name":room["room_name"], "category":room["category"], "capacity":room["capacity"], "occupied_seats":room["occupied_seats"], "score":round(max(score, 0), 1), "reasons":suitability})
    recommendations.sort(key=lambda room: room["score"], reverse=True)
    return jsonify({"recommendations": recommendations[:3], "rejected": rejected[:5], "analysis": f"Evaluated {len(rooms_data)} campus spaces against capacity, equipment, status, maintenance and timetable constraints."})

@app.get("/api/issues")
def issues():
    return jsonify(client().table("issues").select("*, rooms(room_number,room_name)").order("priority_rank", desc=True).order("created_at", desc=True).execute().data)

@app.post("/api/issues")
def report_issue():
    profile = require("faculty")
    if not profile: return error("Sign in as faculty to report an issue.", 401)
    data = request.get_json() or {}
    required = ("room_id", "title", "category", "priority", "description")
    if not all(data.get(field) for field in required): return error("Complete all issue fields.")
    rank = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(data["priority"], 1)
    result = client().table("issues").insert({**{k:data[k] for k in required}, "priority_rank":rank, "reported_by":profile["id"], "created_at":now()}).execute().data
    return jsonify(result[0]), 201

@app.patch("/api/issues/<issue_id>/repair")
def repair(issue_id):
    profile = require("worker")
    if not profile: return error("Sign in as maintenance staff to update this issue.", 401)
    data = request.get_json() or {}; status = data.get("status")
    if status not in ("In Progress", "Resolved"): return error("Choose In Progress or Resolved.")
    client().table("issues").update({"status":status,"worker_note":data.get("worker_note", ""),"updated_at":now(),"assigned_to":profile["id"]}).eq("id", issue_id).execute()
    return jsonify({"message":"Maintenance update saved."})

@app.patch("/api/issues/<issue_id>/verify")
def verify(issue_id):
    profile = require("faculty")
    if not profile: return error("Sign in as faculty to verify this issue.", 401)
    data = request.get_json() or {}; verdict = data.get("verdict")
    issue = client().table("issues").select("reported_by").eq("id", issue_id).execute().data
    if not issue: return error("Issue not found.", 404)
    if issue[0]["reported_by"] != profile["id"]: return error("Only the reporting faculty member may verify or reopen this issue.", 403)
    if verdict not in ("Verified", "Reopened"): return error("Choose Verified or Reopened.")
    client().table("issues").update({"status":"Verified" if verdict == "Verified" else "Open", "faculty_verification":verdict, "updated_at":now()}).eq("id", issue_id).execute()
    return jsonify({"message":f"Issue {verdict.lower()}."})

@app.get("/api/subjects")
def subjects(): return jsonify(client().table("subjects").select("*, profiles(name)").order("semester").order("code").execute().data)

@app.get("/api/timetable")
def timetable(): return jsonify(client().table("timetable").select("*, rooms(room_number), subjects(code,name,credits), profiles(name)").order("day_order").order("start_time").execute().data)

@app.post("/api/timetable")
def add_timetable():
    profile = require("faculty")
    if not profile: return error("Sign in as faculty to create a timetable entry.", 401)
    data = request.get_json() or {}; fields=("day","day_order","start_time","end_time","room_id","section","subject_id")
    if not all(str(data.get(x,"")) for x in fields): return error("Complete all timetable fields.")
    subject = client().table("subjects").select("faculty_id").eq("id",data["subject_id"]).execute().data
    if not subject or subject[0]["faculty_id"] != profile["id"]: return error("Only the assigned lecturer can schedule this subject.",403)
    entries = client().table("timetable").select("*").eq("day",data["day"]).execute().data
    conflict = any(e["start_time"] < data["end_time"] and e["end_time"] > data["start_time"] and (e["room_id"] == data["room_id"] or e["section"] == data["section"] or e["faculty_id"] == profile["id"]) for e in entries)
    if conflict: return error("Clash found for this room, lecturer or section.", 409)
    output=client().table("timetable").insert({k:data[k] for k in fields}|{"faculty_id":profile["id"]}).execute().data[0]
    return jsonify(output),201

@app.get("/api/progress")
def progress(): return jsonify(client().table("syllabus_progress").select("*, subjects(code,name,credits,semester), profiles(name)").order("updated_at",desc=True).execute().data)

@app.post("/api/progress")
def add_progress():
    profile=require("faculty")
    if not profile:return error("Sign in as faculty to update syllabus coverage.",401)
    data=request.get_json() or {}; subject=client().table("subjects").select("faculty_id").eq("id",data.get("subject_id")).execute().data
    if not subject or subject[0]["faculty_id"] != profile["id"]:return error("Only the assigned lecturer can update this subject.",403)
    try: coverage=float(data["coverage_percent"])
    except (KeyError,ValueError,TypeError):return error("Coverage must be from 0 to 100.")
    if not 0<=coverage<=100 or not data.get("topics_covered") or not data.get("week_number"):return error("Complete week, coverage and topics.")
    record={"subject_id":data["subject_id"],"week_number":data["week_number"],"coverage_percent":coverage,"topics_covered":data["topics_covered"],"updated_by":profile["id"],"updated_at":now()}
    output=client().table("syllabus_progress").upsert(record,on_conflict="subject_id,week_number").execute().data[0]
    return jsonify(output),201

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")), debug=True)
