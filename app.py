import os

from cs50 import SQL
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory,
)
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import *
from dateutil.relativedelta import relativedelta
import os
from os import listdir

from helpers import login_required

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

# Configure application
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pet.db")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show last and upcoming events"""
    pets = db.execute(
        "SELECT * FROM pets WHERE user_id = ?",
        session["user_id"],
    )
    # If no registered pets, welcome page is displayed
    if len(pets) < 1:
        info = "Welcome! Start from adding a pet!"
        return render_template("add.html", info=info)

    # Check possible deadline for treatments
    deadline = db.execute(
        "SELECT pets.type AS type, pets.name AS name, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until < (SELECT date('now')) ORDER BY valid_until",
        session["user_id"],
    )

    if len(deadline) > 0:
        # All procedures with expired date
        proc_dead = db.execute(
            "SELECT procedure FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until < (SELECT date('now')) AND pets.pet_id  = (SELECT pets.pet_id FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until < (SELECT date('now')))",
            session["user_id"],
            session["user_id"],
        )

        # All procedures that are not expired
        proc_n = db.execute(
            "SELECT procedure FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until > (SELECT date('now')) AND pets.pet_id  = (SELECT pets.pet_id FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until < (SELECT date('now')))",
            session["user_id"],
            session["user_id"],
        )

        # Check if expired procedures are in a list of non-expired procedures
        i = 0
        for proc in range(len(proc_dead)):
            for proc2 in range(len(proc_n)):
                if (proc_dead[proc]["procedure"]) == (proc_n[proc2]["procedure"]):
                    i = i + 1

        if i < len(deadline):
            flash(
                "Check vaccinations and treatments. You may have missed the deadline..."
            )

    # Check possible deadline for tests
    deadline_test = db.execute(
        "SELECT pets.type AS type, pets.name AS name, test, reason, url, date_of_test, tests.date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next < (SELECT date('now'))",
        session["user_id"],
    )

    if len(deadline_test) > 0:
        # All procedures with expired date
        test_dead = db.execute(
            "SELECT test FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next < (SELECT date('now')) AND pets.pet_id  = (SELECT pets.pet_id FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next < (SELECT date('now')))",
            session["user_id"],
            session["user_id"],
        )

        # All procedures that are not expired
        test_n = db.execute(
            "SELECT test FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next > (SELECT date('now')) AND pets.pet_id  = (SELECT pets.pet_id FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next < (SELECT date('now')))",
            session["user_id"],
            session["user_id"],
        )

        # Check if expired procedures are in a list of non-expired procedures
        j = 0
        for test in range(len(test_dead)):
            for test2 in range(len(test_n)):
                if (test_dead[test]["test"]) == (test_n[test2]["test"]):
                    j = j + 1

        if j < len(deadline_test):
            flash("Check medical tests. You may have missed the deadline...")

    # Show upcoming events
    # Show upcoming regular treatments"""
    treatments = db.execute(
        "SELECT pets.type AS type, pets.name AS name, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? AND treatments.valid_until > (SELECT date('now')) ORDER BY valid_until",
        session["user_id"],
    )

    # Show upcoming tests
    tests = db.execute(
        "SELECT pets.type AS type, pets.name AS name, test, reason, url, date_of_test, tests.date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? AND tests.date_next > (SELECT date('now')) ORDER BY tests.date_next",
        session["user_id"],
    )
    # Show upcoming visits
    visits = db.execute(
        "SELECT pets.type AS type, pets.name AS name, date_of_visit, reason, diagnosis, treatment, date_next FROM pets JOIN visits on visits.pet_id = pets.pet_id WHERE pets.user_id = ? AND date_next > (SELECT date('now')) ORDER BY date_next",
        session["user_id"],
    )

    # Show last events
    # Show 3 last regular treatments
    last_treatments = db.execute(
        "SELECT pets.type AS type, pets.name AS name, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments ON treatments.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY date_of_procedure DESC LIMIT 3",
        session["user_id"],
    )

    # Show 3 last tests
    last_tests = db.execute(
        "SELECT pets.type AS type, pets.name AS name, test, reason, url, date_of_test, tests.date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY tests.date_of_test DESC LIMIT 3",
        session["user_id"],
    )

    # Show 3 last visits
    last_visits = db.execute(
        "SELECT pets.type AS type, pets.name AS name, date_of_visit, reason, diagnosis, treatment, date_next FROM pets JOIN visits on visits.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY visits.date_of_visit DESC LIMIT 3",
        session["user_id"],
    )

    return render_template(
        "index.html",
        treatments=treatments,
        tests=tests,
        visits=visits,
        last_treatments=last_treatments,
        last_tests=last_tests,
        last_visits=last_visits,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add a pet"""
    if request.method == "POST":
        # Ensure type was submitted
        if not request.form.get("type"):
            if not request.form.get("type-other"):
                flash("Provide type of a pet!")
                return render_template("add.html")
        if request.form.get("type") != "other":
            type = request.form.get("type")
        else:
            type = request.form.get("type-other").lower()

        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Provide name of a pet!")
            return render_template("add.html")
        name = request.form.get("name").capitalize()

        # Ensure date of birth was submitted
        if not request.form.get("dob"):
            flash("Provide date of birth of a pet!")
            return render_template("add.html")
        date = request.form.get("dob")

        # Update database
        db.execute(
            "INSERT INTO pets (user_id, type, name, date_of_birth) VALUES(?, ?, ?, ?)",
            session["user_id"],
            type,
            name,
            date,
        )

        flash("Added!")
        return redirect("/")
    return render_template("add.html")


@app.route("/pets")
@login_required
def pets():
    """Show info about added pets"""
    pets = db.execute(
        "SELECT * FROM pets WHERE user_id = ?",
        session["user_id"],
    )
    # If no registered pets, welcome page is displayed
    if len(pets) < 1:
        info = "You have no pets yet! Start from adding a pet!"
        return render_template("add.html", info=info)

    return render_template("pets.html", pets=pets)


@app.route("/add_treat", methods=["GET", "POST"])
@login_required
def add_treat():
    """Add info about treatments"""
    pets = db.execute(
        "SELECT * FROM pets WHERE user_id = ?",
        session["user_id"],
    )
    if request.method == "POST":
        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Provide name of a pet!")
            return redirect("/")
        name = request.form.get("name")

        # Calculate pet_id
        pet_id = db.execute(
            "SELECT pet_id FROM pets WHERE user_id = ? and name =?",
            session["user_id"],
            request.form.get("name"),
        )
        pet_id = list(pet_id[0].values())
        pet_id = pet_id[0]

        # Ensure procedure was submitted
        if not request.form.get("procedure"):
            if not request.form.get("procedure-other"):
                flash("Provide type of a procedure!")
                return redirect("/")
        if request.form.get("procedure") != "other":
            procedure = request.form.get("procedure")
        else:
            procedure = request.form.get("procedure-other").lower()

        # Name of drug / vaccine
        if request.form.get("drug"):
            drug = request.form.get("drug").capitalize()
        else:
            drug = ""

        # Ensure date of procedure was submitted
        if not request.form.get("date_of"):
            flash("Provide date of a procedure!")
            return redirect("/")
        date = request.form.get("date_of")

        date_format = "%Y-%m-%d"
        date_obj = datetime.strptime(date, date_format)

        # Valid until
        if request.form.get("valid_until"):
            valid_until = request.form.get("valid_until")
        else:
            if procedure == "vaccination":
                valid_until = date_obj + relativedelta(years=1)
            if procedure == "deworming":
                valid_until = date_obj + relativedelta(days=90)
            if procedure == "flee and tick treatment":
                valid_until = date_obj + relativedelta(days=30)
        valid_until = valid_until.date()

        # Update database
        db.execute(
            "INSERT INTO treatments (user_id, pet_id, procedure, drug, date_of_procedure, valid_until) VALUES(?, ?, ?, ?, ?, ?)",
            session["user_id"],
            pet_id,
            procedure,
            drug,
            date,
            valid_until,
        )

        flash("Added!")
        return render_template("add_treat.html", pets=pets)
    return render_template("add_treat.html", pets=pets)


@app.route("/treat", methods=["GET", "POST"])
@login_required
def treat():
    """Show info about treatments"""
    treatments = db.execute(
        "SELECT * FROM treatments WHERE user_id = ?",
        session["user_id"],
    )
    # If no treatments, add treatments page is displayed
    if len(treatments) < 1:
        info = "No treatments yet! Start from adding a treatment!"
        return render_template("add_treat.html", info=info)

    pets = db.execute(
        "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, treatments.id AS treatment_id, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments on treatments.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY pets.pet_id ASC, date_of_procedure DESC",
        session["user_id"],
    )
    if request.method == "POST":
        return render_template("treat.html", pets=pets)

    return render_template("treat.html", pets=pets)


@app.route("/add_tests", methods=["GET", "POST"])
@login_required
def add_tests():
    """Add info about tests and examinations"""
    pets = db.execute(
        "SELECT * FROM pets WHERE user_id = ?",
        session["user_id"],
    )
    if request.method == "POST":
        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Provide name of a pet!")
            return redirect("/")
        name = request.form.get("name")

        # Calculate pet_id
        pet_id = db.execute(
            "SELECT pet_id FROM pets WHERE user_id = ? and name =?",
            session["user_id"],
            request.form.get("name"),
        )
        pet_id = list(pet_id[0].values())
        pet_id = pet_id[0]

        # Ensure test was submitted
        if not request.form.get("test"):
            if not request.form.get("test-other"):
                flash("Provide test or examination!")
                return redirect("/")
        if request.form.get("test") != "other":
            test = request.form.get("test")
        else:
            test = request.form.get("test-other").lower()

        # Why was test conducted
        if request.form.get("reason"):
            reason = request.form.get("reason")
        else:
            reason = ""

        # Upload files
        if request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = str(len(listdir(UPLOAD_FOLDER))) + filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                file_url = url_for("download_file", name=filename)
            else:
                file_url = ""

        # User comments
        if request.form.get("comments"):
            comments = request.form.get("comments")
        else:
            comments = ""

        # Ensure date of test was submitted
        if not request.form.get("date_of"):
            flash("Provide date of a test/examination!")
            return redirect("/")
        date = request.form.get("date_of")

        date_format = "%Y-%m-%d"
        date_obj = datetime.strptime(date, date_format)

        # Date of re-test / re-examination
        if request.form.get("date_next"):
            date_next = request.form.get("date_next")
        else:
            date_next = date_obj + relativedelta(years=1)
        date_next = date_next.date()

        # Update database
        db.execute(
            "INSERT INTO tests (user_id, pet_id, test, reason, url, comments, date_of_test, date_next) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            session["user_id"],
            pet_id,
            test,
            reason,
            file_url,
            comments,
            date,
            date_next,
        )

        flash("Added!")
        return render_template("add_tests.html", pets=pets)
    return render_template("add_tests.html", pets=pets)


@app.route("/tests", methods=["GET", "POST"])
@login_required
def tests():
    """Show info about tests and examinations"""
    tests = db.execute(
        "SELECT * FROM tests WHERE user_id = ?",
        session["user_id"],
    )
    # If no tests, add tests page is displayed
    if len(tests) < 1:
        info = "No tests yet! Start from adding a test!"
        return render_template("add_tests.html", info=info)

    pets = db.execute(
        "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, tests.id AS test_id, test, reason, url, comments, date_of_test, date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY pets.pet_id ASC, date_of_test DESC",
        session["user_id"],
    )
    if request.method == "POST":
        return render_template("tests.html", pets=pets)

    return render_template("tests.html", pets=pets)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show medical history"""
    visits = db.execute(
        "SELECT * FROM visits WHERE user_id = ?",
        session["user_id"],
    )
    # If no visits yet, add visits page is displayed
    if len(visits) < 1:
        info = "No visits yet! Start from adding a visit!"
        return render_template("add_history.html", info=info)

    pets = db.execute(
        "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, visits.id AS visit_id, date_of_visit, clinic, veterinarian, reason, diagnosis, treatment, comments, date_next FROM pets JOIN visits on visits.pet_id = pets.pet_id WHERE pets.user_id = ? ORDER BY pets.pet_id ASC, date_of_visit DESC",
        session["user_id"],
    )
    if request.method == "POST":
        return render_template("history.html", pets=pets)

    return render_template("history.html", pets=pets)


@app.route("/add_history", methods=["GET", "POST"])
@login_required
def add_history():
    """Add medical history"""
    pets = db.execute(
        "SELECT * FROM pets WHERE user_id = ?",
        session["user_id"],
    )
    if request.method == "POST":
        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Provide name of a pet!")
            return redirect("/")
        name = request.form.get("name")

        # Calculate pet_id
        pet_id = db.execute(
            "SELECT pet_id FROM pets WHERE user_id = ? and name =?",
            session["user_id"],
            request.form.get("name"),
        )
        pet_id = list(pet_id[0].values())
        pet_id = pet_id[0]

        # Ensure date of visit was submitted
        if not request.form.get("date_of"):
            flash("Provide date of a visit!")
            return redirect("/")
        date = request.form.get("date_of")

        # Name of clinic
        if request.form.get("clinic"):
            clinic = request.form.get("clinic").capitalize()
        else:
            clinic = ""

        # Name of veterinarian
        if request.form.get("veterinarian"):
            veterinarian = request.form.get("veterinarian").capitalize()
        else:
            veterinarian = ""

        # Ensure reason was submitted
        if not request.form.get("reason"):
            flash("Provide reason for a visit!")
            return redirect("/")
        reason = request.form.get("reason").lower()

        # Ensure diagnosis was submitted
        if not request.form.get("diagnosis"):
            flash("Provide diagnosis!")
            return redirect("/")
        diagnosis = request.form.get("diagnosis").lower()

        # Ensure treatment was submitted
        if not request.form.get("treatment"):
            flash("Provide treatment!")
            return redirect("/")
        treatment = request.form.get("treatment").lower()

        # User comments
        if request.form.get("comments"):
            comments = request.form.get("comments")
        else:
            comments = ""

        # Date of next visit
        if request.form.get("date_next"):
            date_next = request.form.get("date_next")
        else:
            date_next = ""

        # Update database
        db.execute(
            "INSERT INTO visits (user_id, pet_id, date_of_visit, clinic, veterinarian, reason, diagnosis, treatment, comments, date_next) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            session["user_id"],
            pet_id,
            date,
            clinic,
            veterinarian,
            reason,
            diagnosis,
            treatment,
            comments,
            date_next,
        )

        flash("Added!")
        return render_template("add_history.html", pets=pets)

    return render_template("add_history.html", pets=pets)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Provide username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Provide password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password!")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Provide username!")
            return render_template("register.html")

        # Ensure username does not already exists
        users = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(users) == 1:
            flash("Username already exists!")
            return render_template("register.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Provide password!")
            return render_template("register.html")

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            flash("Provide confirmation!")
            return render_template("register.html")

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match!")
            return render_template("register.html")

        username = request.form.get("username")
        password = request.form.get("password")

        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            username,
            generate_password_hash(password),
        )

        return render_template("login.html")
    return render_template("register.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Remove a pet"""
    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        pet_id = int(pet_id)
        db.execute(
            "DELETE FROM treatments WHERE treatments.pet_id = ? and user_id = ?",
            pet_id,
            session["user_id"],
        )
        db.execute(
            "DELETE FROM pets WHERE pets.pet_id = ? and user_id = ?",
            pet_id,
            session["user_id"],
        )
    return redirect("/")


@app.route("/remove_treat", methods=["GET", "POST"])
@login_required
def remove_treat():
    """Remove vaccination/treatment"""
    if request.method == "POST":
        treatment_id = request.form.get("treatment_id")
        treatment_id = int(treatment_id)
        db.execute(
            "DELETE FROM treatments WHERE treatments.id = ? and user_id = ?",
            treatment_id,
            session["user_id"],
        )
    return redirect("/")


@app.route("/remove_tests", methods=["GET", "POST"])
@login_required
def remove_tests():
    """Remove vaccination/treatment"""
    if request.method == "POST":
        test_id = request.form.get("test_id")
        test_id = int(test_id)
        db.execute(
            "DELETE FROM tests WHERE tests.id = ? and user_id = ?",
            test_id,
            session["user_id"],
        )
    return redirect("/")


@app.route("/remove_history", methods=["GET", "POST"])
@login_required
def remove_history():
    """Remove a visit to a vet"""
    if request.method == "POST":
        visit_id = request.form.get("visit_id")
        visit_id = int(visit_id)
        db.execute(
            "DELETE FROM visits WHERE visits.id = ? and user_id = ?",
            visit_id,
            session["user_id"],
        )
    return redirect("/")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit a pet"""
    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        pet_id = int(pet_id)
        pet = db.execute(
            "SELECT * FROM pets WHERE pet_id = ? AND user_id = ?",
            pet_id,
            session["user_id"],
        )
        return render_template("edit.html", pet=pet)
    return redirect("/")


@app.route("/edit_treat", methods=["GET", "POST"])
@login_required
def edit_treat():
    """Edit treatment"""
    if request.method == "POST":
        treatment_id = request.form.get("treatment_id")
        treatment_id = int(treatment_id)
        treatment = db.execute(
            "SELECT pets.type AS type, pets.name AS name, treatments.id AS treatment_id, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments on treatments.pet_id = pets.pet_id WHERE treatments.id = ? AND pets.user_id = ?",
            treatment_id,
            session["user_id"],
        )
        return render_template("edit_treat.html", treatment=treatment)
    return redirect("/")


@app.route("/edit_tests", methods=["GET", "POST"])
@login_required
def edit_tests():
    """Edit tests"""
    if request.method == "POST":
        test_id = request.form.get("test_id")
        test_id = int(test_id)
        test = db.execute(
            "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, tests.id AS test_id, test, reason, url, comments, date_of_test, date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE tests.id = ? AND pets.user_id = ?",
            test_id,
            session["user_id"],
        )
        return render_template("edit_tests.html", test=test)
    return redirect("/")


@app.route("/edit_history", methods=["GET", "POST"])
@login_required
def edit_history():
    """Edit tests"""
    if request.method == "POST":
        visit_id = request.form.get("visit_id")
        visit_id = int(visit_id)
        visit = db.execute(
            "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, visits.id AS visit_id, date_of_visit, clinic, veterinarian, reason, diagnosis, treatment, comments, date_next FROM pets JOIN visits on visits.pet_id = pets.pet_id WHERE visits.id = ? AND pets.user_id = ?",
            visit_id,
            session["user_id"],
        )
        return render_template("edit_history.html", visit=visit)
    return redirect("/")


@app.route("/edit2", methods=["GET", "POST"])
@login_required
def edit2():
    """Edit a pet, 2"""
    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        pet_id = int(pet_id)
        pet = db.execute(
            "SELECT * FROM pets WHERE pet_id = ? AND user_id = ?",
            pet_id,
            session["user_id"],
        )

        if request.form.get("type"):
            if request.form.get("type-other"):
                new_type = request.form.get("type-other").lower()
            else:
                new_type = request.form.get("type")
        else:
            new_type = pet[0]["type"]

        if request.form.get("name"):
            new_name = request.form.get("name").capitalize()
        else:
            new_name = pet[0]["name"]

        if request.form.get("dob"):
            new_date = request.form.get("dob")
        else:
            new_date = pet[0]["date_of_birth"]

        # Update database
        db.execute(
            "UPDATE pets SET type = ?, name = ?, date_of_birth = ? WHERE pet_id = ? AND user_id = ?",
            new_type,
            new_name,
            new_date,
            pet_id,
            session["user_id"],
        )

        flash("Updated!")
        return redirect("/")
    return render_template("pets.html")


@app.route("/edit_treat2", methods=["GET", "POST"])
@login_required
def edit_treat2():
    """Edit treatment, 2"""
    if request.method == "POST":
        treatment_id = request.form.get("treatment_id")
        treatment_id = int(treatment_id)
        treatment = db.execute(
            "SELECT pets.type AS type, pets.name AS name, treatments.id AS treatment_id, procedure, drug, date_of_procedure, valid_until FROM pets JOIN treatments on treatments.pet_id = pets.pet_id WHERE treatments.id = ? AND pets.user_id = ?",
            treatment_id,
            session["user_id"],
        )

        if request.form.get("procedure"):
            if request.form.get("procedure-other"):
                new_procedure = request.form.get("procedure-other").lower()
            else:
                new_procedure = request.form.get("procedure")
        else:
            new_procedure = treatment[0]["procedure"]

        if request.form.get("drug"):
            new_drug = request.form.get("drug")
        else:
            new_drug = treatment[0]["drug"]

        if request.form.get("date_of"):
            new_date = request.form.get("date_of")
        else:
            new_date = treatment[0]["date_of_procedure"]
        date_format = "%Y-%m-%d"
        date_obj = datetime.strptime(new_date, date_format)

        if request.form.get("valid_until"):
            new_valid_until = request.form.get("valid_until")
        else:
            if new_procedure == "vaccination":
                new_valid_until = date_obj + relativedelta(years=1)
            if new_procedure == "deworming":
                new_valid_until = date_obj + relativedelta(days=90)
            if new_procedure == "flee and tick treatment":
                new_valid_until = date_obj + relativedelta(days=30)
            new_valid_until = new_valid_until.date()

        # Update database
        db.execute(
            "UPDATE treatments SET procedure = ?, drug = ?, date_of_procedure = ?, valid_until = ? WHERE treatments.id = ? AND user_id = ?",
            new_procedure,
            new_drug,
            new_date,
            new_valid_until,
            treatment_id,
            session["user_id"],
        )

        flash("Updated!")
        return redirect("/")
    return render_template("treat.html")


@app.route("/edit_tests2", methods=["GET", "POST"])
@login_required
def edit_tests2():
    """Edit tests, 2"""
    if request.method == "POST":
        test_id = request.form.get("test_id")
        test_id = int(test_id)
        test = db.execute(
            "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, tests.id AS test_id, test, reason, url, comments, date_of_test, date_next FROM pets JOIN tests on tests.pet_id = pets.pet_id WHERE tests.id = ? AND pets.user_id = ?",
            test_id,
            session["user_id"],
        )

        if request.form.get("test"):
            if request.form.get("test-other"):
                new_test = request.form.get("test-other").lower()
            else:
                new_test = request.form.get("test")
        else:
            new_test = test[0]["test"]

        if request.form.get("reason"):
            new_reason = request.form.get("reason")
        else:
            new_reason = test[0]["reason"]

        if request.form.get("comments"):
            new_comments = request.form.get("comments")
        else:
            new_comments = test[0]["comments"]

        if request.form.get("date_of"):
            new_date = request.form.get("date_of")
        else:
            new_date = test[0]["date_of_test"]
        date_format = "%Y-%m-%d"
        date_obj = datetime.strptime(new_date, date_format)

        if request.form.get("date_next"):
            new_date_next = request.form.get("date_next")
        else:
            new_date_next = date_obj + relativedelta(years=1)
            new_date_next = new_date_next.date()

        # Update database
        db.execute(
            "UPDATE tests SET test = ?, reason = ?, comments = ?, date_of_test = ?, date_next = ? WHERE tests.id = ? AND user_id = ?",
            new_test,
            new_reason,
            new_comments,
            new_date,
            new_date_next,
            test_id,
            session["user_id"],
        )

        flash("Updated!")
        return redirect("/")
    return render_template("tests.html")


@app.route("/edit_history2", methods=["GET", "POST"])
@login_required
def edit_history2():
    """Edit history, 2"""
    if request.method == "POST":
        visit_id = request.form.get("visit_id")
        visit_id = int(visit_id)
        visit = db.execute(
            "SELECT pets.user_id AS user_id, pets.pet_id AS pet_id, pets.type AS type, pets.name AS name, visits.id AS visit_id, date_of_visit, clinic, veterinarian, reason, diagnosis, treatment, comments, date_next FROM pets JOIN visits on visits.pet_id = pets.pet_id WHERE visits.id = ? AND pets.user_id = ?",
            visit_id,
            session["user_id"],
        )

        if request.form.get("date_of"):
            new_date = request.form.get("date_of")
        else:
            new_date = visit[0]["date_of_visit"]

        if request.form.get("clinic"):
            new_clinic = request.form.get("clinic").capitalize()
        else:
            new_clinic = visit[0]["clinic"]

        if request.form.get("veterinarian"):
            new_veterinarian = request.form.get("veterinarian").capitalize()
        else:
            new_veterinarian = visit[0]["veterinarian"]

        if request.form.get("reason"):
            new_reason = request.form.get("reason")
        else:
            new_reason = visit[0]["reason"]

        if request.form.get("diagnosis"):
            new_diagnosis = request.form.get("diagnosis")
        else:
            new_diagnosis = visit[0]["diagnosis"]

        if request.form.get("treatment"):
            new_treatment = request.form.get("treatment")
        else:
            new_treatment = visit[0]["treatment"]

        if request.form.get("comments"):
            new_comments = request.form.get("comments")
        else:
            new_comments = visit[0]["comments"]

        if request.form.get("date_next"):
            new_date_next = request.form.get("date_next")
        else:
            new_date_next = visit[0]["date_next"]

        # Update database
        db.execute(
            "UPDATE visits SET date_of_visit = ?, clinic = ?, veterinarian = ?,  reason = ?, diagnosis = ?, treatment = ?, comments = ?, date_next = ? WHERE visits.id = ? AND user_id = ?",
            new_date,
            new_clinic,
            new_veterinarian,
            new_reason,
            new_diagnosis,
            new_treatment,
            new_comments,
            new_date_next,
            visit_id,
            session["user_id"],
        )

        flash("Updated!")
        return redirect("/")
    return render_template("history.html")
