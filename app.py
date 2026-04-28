from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import sqlite3
import uuid

from search_engine.indexer import build_inverted_index
from search_engine.search import search_documents
from search_engine.ranking import rank_results
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file


app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
INDEX_FILE = "inverted_index.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===============================
# LOAD INDEX
# ===============================
def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

inverted_index = load_index()


# ===============================
# USER / GUEST FOLDER
# ===============================
def get_user_folder():
    if session.get("mode") == "guest":
        return f"uploads/guest_{session.get('guest_id')}"
    elif session.get("mode") == "user":
        return f"uploads/user_{session.get('user_id')}"
    return "uploads/common"


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ===============================
# UPLOAD
# ===============================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    global inverted_index

    if "mode" not in session:
        return redirect(url_for("login"))

    folder = get_user_folder()
    os.makedirs(folder, exist_ok=True)

    if request.method == "POST":
        files = request.files.getlist("files")

        for file in files:
            if file.filename.lower().endswith((".txt", ".pdf")):

                if session.get("current_folder"):
                    save_folder = os.path.join(folder, session["current_folder"])
                else:
                    save_folder = folder

                os.makedirs(save_folder, exist_ok=True)

                filepath = os.path.join(save_folder, file.filename)
                file.save(filepath)

            else:
                return "Only .txt and .pdf files are allowed."

        inverted_index = build_inverted_index(folder)

        if session.get("current_folder"):
            return redirect(url_for("open_folder", foldername=session["current_folder"]))

        return redirect(url_for("upload"))

    session_current = session.get("current_folder")

    if session_current:
        selected_folder = os.path.join(folder, session_current)

        files = []
        if os.path.exists(selected_folder):
            files = os.listdir(selected_folder)

    else:
        files = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]

    folders = [
        f for f in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, f))
    ]

    return render_template(
        "upload.html",
        files=files,
        folders=folders,
        current_folder=session_current
    )


# ===============================
# CREATE FOLDER
# ===============================
@app.route("/create_folder/<foldername>")
def create_folder(foldername):

    folder = get_user_folder()
    folder_path = os.path.join(folder, foldername)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return redirect(url_for("upload"))


# ===============================
# OPEN FOLDER
# ===============================
@app.route("/folder/<foldername>")
def open_folder(foldername):

    folder = get_user_folder()
    selected_folder = os.path.join(folder, foldername)

    session["current_folder"] = foldername

    files = []

    if os.path.exists(selected_folder):
        files = os.listdir(selected_folder)

    folders = [
        f for f in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, f))
    ]

    return render_template(
        "upload.html",
        files=files,
        folders=folders,
        current_folder=foldername
    )


# ===============================
# RESET FOLDER
# ===============================
@app.route("/reset_folder")
def reset_folder():

    session.pop("current_folder", None)

    return redirect(url_for("upload"))


# ===============================
# DELETE FILE
# ===============================
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):

    folder = get_user_folder()

    if session.get("current_folder"):
        filepath = os.path.join(folder, session["current_folder"], filename)
    else:
        filepath = os.path.join(folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)

    if session.get("current_folder"):
        return redirect(url_for("open_folder", foldername=session["current_folder"]))

    return redirect(url_for("upload"))


# ===============================
# VIEW FILE
# ===============================
@app.route("/view/<filename>")
def view_file(filename):

    folder = get_user_folder()

    if session.get("current_folder"):
        filepath = os.path.join(folder, session["current_folder"], filename)
    else:
        filepath = os.path.join(folder, filename)

    source = request.args.get("source", "upload")

    if os.path.exists(filepath):

        if filename.lower().endswith(".pdf"):
            return send_file(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return render_template(
            "view.html",
            file=filename,
            content=content,
            source=source
        )

    return "File not found"


# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session.clear()

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["email"] = user[2]
            session["mode"] = "user"

            return redirect(url_for("upload"))

        return "Invalid credentials."

    return render_template("login.html")


# ===============================
# SIGNUP
# ===============================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()

        except:
            return "Email already exists."

        finally:
            conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ===============================
# GUEST MODE
# ===============================
@app.route("/guest")
def guest():

    session.clear()

    guest_id = str(uuid.uuid4())[:8]

    session["guest_id"] = guest_id
    session["username"] = f"Guest_{guest_id}"
    session["mode"] = "guest"

    return redirect(url_for("upload"))


@app.route("/search_page")
def search_page():
    return render_template("search.html")


# ===============================
# SEARCH
# ===============================

@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"]

    folder = get_user_folder()

    if session.get("current_folder"):
        search_folder = os.path.join(folder, session["current_folder"])
    else:
        search_folder = folder

    if not os.path.exists(search_folder):
        return render_template("results.html", results=[])

    current_index = build_inverted_index(search_folder)

    results = search_documents(query, current_index, search_folder)

    documents = {}

    for file in results:

        filepath = os.path.join(search_folder, file)

        if file.lower().endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as f:
                documents[file] = f.read()

        elif file.lower().endswith(".pdf"):

            import PyPDF2

            text = ""

            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                for page in reader.pages:
                    extracted = page.extract_text()

                    if extracted:
                        text += extracted

            documents[file] = text

    ranked = rank_results(query, documents)

    session["last_results"] = ranked

    return render_template("results.html", results=ranked)
@app.route("/export_pdf")
def export_pdf():

    folder = "static"
    filepath = os.path.join(folder, "search_results.pdf")

    c = canvas.Canvas(filepath, pagesize=letter)

    c.drawString(100, 750, "Findr Search Results")

    y = 700

    results = session.get("last_results", [])

    for file, score in results:
        c.drawString(100, y, f"{file}   Score: {round(score, 4)}")
        y -= 25

    c.save()

    return redirect("/static/search_results.pdf")


# ===============================
# PROFILE
# ===============================
@app.route("/profile")
def profile():

    folder = get_user_folder()

    folders = []

    if os.path.exists(folder):
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)

            if os.path.isdir(item_path):
                folders.append(item)

    return render_template(
        "profile.html",
        user=session.get("username"),
        email=session.get("email"),
        folders=folders
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)