
from flask import Flask, render_template, request, redirect, url_for
from config import get_db_connection
from skill_matcher import match_skills, generate_suggestions

app = Flask(__name__)

ALLOWED_STATUSES = {
    "Applied",
    "Assessment",
    "Interview",
    "Offer",
    "Rejected",
    "Withdrawn"
}



@app.route("/")
def home():
    connection = None
    cursor = None

    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    if status_filter not in ALLOWED_STATUSES:
        status_filter = ""

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Dashboard statistics (counts all applications)
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(status = 'Applied'), 0) AS applied,
                COALESCE(SUM(status = 'Assessment'), 0) AS assessment,
                COALESCE(SUM(status = 'Interview'), 0) AS interviews,
                COALESCE(SUM(status = 'Offer'), 0) AS offers,
                COALESCE(SUM(status = 'Rejected'), 0) AS rejected
            FROM applications
        """)
        stats = cursor.fetchone()

        # 2. Build search and status filters
        query = """
            SELECT id, company_name, job_role,
                   application_date, status
            FROM applications
            WHERE 1 = 1
        """
        values = []

        if search_query:
            query += """
                AND (company_name LIKE %s OR job_role LIKE %s)
            """
            search_value = f"%{search_query}%"
            values.extend([search_value, search_value])

        if status_filter:
            query += " AND status = %s"
            values.append(status_filter)

        query += " ORDER BY id DESC"

        # 3. Fetch matching applications
        cursor.execute(query, values)
        applications = cursor.fetchall()

        return render_template(
            "applications.html",
            applications=applications,
            stats=stats,
            search_query=search_query,
            status_filter=status_filter,
            added=request.args.get("added") == "1",
            updated=request.args.get("updated") == "1",
            deleted=request.args.get("deleted") == "1"
        )

    except Exception:
        app.logger.exception("Failed to load dashboard")
        return "Unable to load dashboard. Check the server log.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "GET":
        return render_template("add_application.html")

    company_name = request.form.get("company_name", "").strip()
    job_role = request.form.get("job_role", "").strip()
    job_link = request.form.get("job_link", "").strip() or None
    application_date = request.form.get("application_date", "")
    status = request.form.get("status", "Applied")
    deadline = request.form.get("deadline", "") or None
    notes = request.form.get("notes", "").strip() or None

    if not company_name or not job_role or not application_date:
        return "Company, role, and application date are required.", 400

    if len(company_name) > 100 or len(job_role) > 100:
        return "Company name or job role is too long.", 400

    if job_link and len(job_link) > 500:
        return "Job link is too long.", 400

    if status not in ALLOWED_STATUSES:
        return "Invalid application status.", 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO applications
                (company_name, job_role, job_link,
                 application_date, status, deadline, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            company_name,
            job_role,
            job_link,
            application_date,
            status,
            deadline,
            notes
        )

        cursor.execute(query, values)
        connection.commit()

        return redirect(url_for("home", added="1"))

    except Exception:
        if connection is not None and connection.is_connected():
            connection.rollback()

        app.logger.exception("Failed to save application")
        return "Unable to save application. Check the server log.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


from datetime import date

# Use the ALLOWED_STATUSES set already defined in app.py.


@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == "POST":
            company_name = request.form.get("company_name", "").strip()
            job_role = request.form.get("job_role", "").strip()
            job_link = request.form.get("job_link", "").strip() or None
            application_date = request.form.get("application_date", "")
            status = request.form.get("status", "")
            deadline = request.form.get("deadline", "") or None
            notes = request.form.get("notes", "").strip() or None

            if (
                not company_name
                or not job_role
                or not application_date
                or len(company_name) > 100
                or len(job_role) > 100
                or (job_link and len(job_link) > 500)
                or status not in ALLOWED_STATUSES
            ):
                return "Invalid input. Check the required fields and status.", 400

            # Validate dates before sending them to MySQL.
            try:
                date.fromisoformat(application_date)
                if deadline:
                    date.fromisoformat(deadline)
            except ValueError:
                return "Invalid date format.", 400

            cursor.execute("""
                UPDATE applications
                SET company_name = %s,
                    job_role = %s,
                    job_link = %s,
                    application_date = %s,
                    status = %s,
                    deadline = %s,
                    notes = %s
                WHERE id = %s
            """, (
                company_name, job_role, job_link,
                application_date, status, deadline, notes,
                application_id
            ))

            if cursor.rowcount == 0:
                # Distinguish an unchanged record from a missing ID.
                cursor.execute(
                    "SELECT id FROM applications WHERE id = %s",
                    (application_id,)
                )
                if cursor.fetchone() is None:
                    return "Application not found.", 404

            connection.commit()
            return redirect(url_for("home", updated="1"))

        cursor.execute(
            "SELECT * FROM applications WHERE id = %s",
            (application_id,)
        )
        job = cursor.fetchone()

        if job is None:
            return "Application not found.", 404

        return render_template(
            "edit_application.html",
            job=job,
            statuses=sorted(ALLOWED_STATUSES)
        )

    except Exception:
        if connection is not None and connection.is_connected():
            connection.rollback()

        app.logger.exception("Failed to edit application")
        return "Unable to edit application. Check the server log.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM applications WHERE id = %s",
            (application_id,)
        )

        if cursor.rowcount == 0:
            return "Application not found.", 404

        connection.commit()
        return redirect(url_for("home", deleted="1"))

    except Exception:
        if connection is not None and connection.is_connected():
            connection.rollback()

        app.logger.exception("Failed to delete application")
        return "Unable to delete application. Check the server log.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()




@app.route("/skill-matcher", methods=["GET", "POST"])
def skill_matcher_page():
    result = None
    suggestions = []
    user_skills_text = ""
    job_description = ""
    error = None
    history = []
    applications = []
    selected_application_id = ""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Load applications for the dropdown.
        cursor.execute("""
            SELECT id, company_name, job_role
            FROM applications
            ORDER BY company_name, job_role
        """)
        applications = cursor.fetchall()

        if request.method == "POST":
            user_skills_text = request.form.get(
                "skills", ""
            ).strip()

            job_description = request.form.get(
                "job_description", ""
            ).strip()

            selected_application_id = request.form.get(
                "application_id", ""
            ).strip()

            user_skills = [
                skill.strip()
                for skill in user_skills_text.split(",")
                if skill.strip()
            ]

            # Remove duplicate skills, ignoring capitalization.
            unique_skills = []
            seen = set()

            for skill in user_skills:
                key = skill.casefold()
                if key not in seen:
                    unique_skills.append(skill)
                    seen.add(key)

            linked_application_id = None

            if selected_application_id:
                try:
                    linked_application_id = int(
                        selected_application_id
                    )
                except ValueError:
                    error = "Please select a valid application."

                if not error:
                    cursor.execute("""
                        SELECT id
                        FROM applications
                        WHERE id = %s
                    """, (linked_application_id,))

                    if cursor.fetchone() is None:
                        error = "The selected application does not exist."

            if not error and not unique_skills:
                error = "Please enter at least one skill."

            if not error and not job_description:
                error = "Please enter a job description."

            if not error:
                result = match_skills(
                    unique_skills,
                    job_description
                )

                suggestions = generate_suggestions(
    result["missing_skills"]
)

                cursor.execute("""
                    INSERT INTO skill_match_results (
                        application_id,
                        skills_input,
                        job_description,
                        matched_skills,
                        missing_skills,
                        skill_coverage,
                        text_similarity
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    linked_application_id,
                    ", ".join(unique_skills),
                    job_description,
                    ", ".join(result["matched_skills"]),
                    ", ".join(result["missing_skills"]),
                    result["skill_coverage"],
                    result["text_similarity"]
                ))

                connection.commit()

        # Load recent analyses with their linked job, if any.
        cursor.execute("""
            SELECT
                smr.id,
                smr.skills_input,
                smr.skill_coverage,
                smr.text_similarity,
                smr.created_at,
                a.company_name,
                a.job_role
            FROM skill_match_results AS smr
            LEFT JOIN applications AS a
                ON smr.application_id = a.id
            ORDER BY smr.id DESC
            LIMIT 10
        """)
        history = cursor.fetchall()

    except Exception:
        if connection is not None and connection.is_connected():
            connection.rollback()

        app.logger.exception(
            "Failed to process skill-match analysis"
        )
        error = (
            "Unable to process or load skill-match history. "
            "Check the Flask terminal for details."
        )

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

    return render_template(
        "skill_matcher.html",
        result=result,
        suggestions=suggestions,
        skills=user_skills_text,
        job_description=job_description,
        error=error,
        history=history,
        applications=applications,
        selected_application_id=selected_application_id
    )



if __name__ == "__main__":
    app.run(debug=True)
