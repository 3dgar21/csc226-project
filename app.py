from flask import Flask, render_template, request, redirect, session, url_for
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"

sample_songs = {
    "Pop": [
        ("Lady Gaga & Bruno Mars", "Die With A Smile", "2plbrEY59IikOBgBGLjaoe"),
        ("Billie Eilish", "BIRDS OF A FEATHER", "6dOtVTDdiauQNBQEDOtlAB"),
        ("Jimin", "Back to Friends", "0FTmksd2dxiE5e3rWyJXs6")
    ],
    "Rock": [
        ("Queen", "Bohemian Rhapsody", "7tFiyTwD0nx5a1eklYtX2J"),
        ("Led Zeppelin", "Stairway to Heaven", "5CQ30WqJwcep0pYcV4AMNc"),
        ("Nirvana", "Smells Like Teen Spirit", "5ghIJDpPoe3CfHMGu71E6T")
    ],
    "Hip-Hop": [
        ("Bone Thugs-N-Harmony", "Foe tha Love of $", "1muLq1kBLWIT3pmNC2xl0g"),
        ("Kendrick Lamar", "Not Like Us", "6AI3ezQ4o3HUoP6Dhudph3"),
        ("Biggie", "Big Poppa", "63BcfK6YAzJYeISaTPr6IO")
    ],
    "R&B": [
        ("PARTYNEXTDOOR", "Recognize", "1DMYEiuAgz1OKvANXiNFrN"),
        ("SZA", "Kill Bill", "3OHfY25tqY28d16oZczHc8"),
        ("The Weeknd", "Somebody Loves Me", "2kZoOj1n5vk9BuF0sih58M")
    ],
    "Latin music": [
        ("Los Dareyes de la Sierra", "Vita Fer", "5HZBdV5AwSvKdHFOYbXYD7"),
        ("Tito Double P", "Andamos Mejor", "3K56RPWS4q200IwHiIZcUD"),
        ("Peso Pluma", "Lady Gaga", "7mXuWTczZNxG5EDcjFEuJR")
    ],
    "Afro-Beat": [
        ("Burna Boy", "Last Last", "4WSbS21oUkwqdfjMhvnvkT"),
        ("Wizkid", "Essence", "5Aqf0OgNCH3QZtvznc0y6g"),
        ("Rema", "Calm Down", "4vUmTMuQqjdnvlZmAH61Qk"),
        ("Asake", "Peace Be Unto You (PBUY)", "06QUZaXSOtwRNH1ZB20JgX"),
        ("Burna Boy", "Sittin' On Top Of The World", "5aIVCx5tnk0ntmdiinnYvw"),
        ("Fireboy DML", "Peru", "3baPniPXS0iEII8rDUJdYP"),
        ("Ruger", "Asiwaju", "5Dz7hEiizJdHkUEPfnoBji"),
        ("Omah Lay", "soso", "5YbPxJwPfrj7uswNwoF1pJ"),
        ("Joeboy", "Sip (Alcohol)", "25Kyv5SeEenT0EETpP2hYn"),
        ("CKay", "Love Nwantiti", "4vb777iaycnlFxVkJMmtfd")
    ]
}

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT,
            artist TEXT,
            title TEXT,
            spotify_id TEXT,
            timestamp TEXT,
            user TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    selected = []
    if request.method == "POST":
        selected = request.form.getlist("genres")
        if not selected:
            return render_template("index.html", error="Please select at least one genre.", selected=selected)

        recs_by_genre = {}
        for genre in selected:
            if genre in sample_songs:
                songs = random.sample(sample_songs[genre], min(3, len(sample_songs[genre])))
                recs_by_genre[genre] = []
                for artist, title, spotify_id in songs:
                    save_history(genre, artist, title, spotify_id)
                    recs_by_genre[genre].append((artist, title, spotify_id))

        return render_template("result.html", recs_by_genre=recs_by_genre)

    return render_template("index.html", selected=selected)

def save_history(genre, artist, title, spotify_id):
    user = session.get("username")
    if user:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO history (genre, artist, title, spotify_id, timestamp, user)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (genre, artist, title, spotify_id, timestamp, user))
        conn.commit()
        conn.close()
    else:
        guest_history = session.get("guest_history", [])
        guest_history.append({
            "genre": genre,
            "artist": artist,
            "title": title,
            "spotify_id": spotify_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        session["guest_history"] = guest_history

@app.route("/history")
def history():
    user = session.get("username")
    if user:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT genre, artist, title, spotify_id, timestamp FROM history WHERE user = ? ORDER BY id DESC", (user,))
        history_data = cursor.fetchall()
        conn.close()
    else:
        guest_history = session.get("guest_history", [])
        history_data = [
            (entry["genre"], entry["artist"], entry["title"], entry["spotify_id"], entry["timestamp"])
            for entry in guest_history
        ]

    return render_template("history.html", history=history_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form.get("username", "Guest")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session["username"] = request.form.get("username", "Guest")
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("guest_history", None)
    return redirect(request.args.get("next", url_for("home")))

if __name__ == "__main__":
    app.run(debug=True)

