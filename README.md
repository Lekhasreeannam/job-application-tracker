# job-application-tracker
# Job Application Tracker

A web-based application built with Flask and MySQL to manage job applications, track application progress, and analyze skill gaps between a candidate's skills and job descriptions.

## Features

- **Application Management:** Add, edit, view, and delete job applications.
- **Application Dashboard:** View application statistics and monitor application statuses.
- **Search and Filtering:** Find applications by company or role and filter by status.
- **NLP-Based Skill Matching:** Compare candidate skills with job description requirements.
- **Skill Coverage Analysis:** Identify matched and missing skills and calculate skill coverage.
- **Text Similarity:** Use TF-IDF and cosine similarity to compare skills and job descriptions.
- **Personalized Learning Suggestions:** Get suggestions for skills that need improvement.
- **Analysis History:** Save skill-matching results and associate them with job applications.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, Jinja2 templates
- **Machine Learning / NLP:** Scikit-learn, TF-IDF, cosine similarity
- **Configuration:** Python Dotenv
- **Version Control:** Git and GitHub

## Project Structure

```text
job-application-tracker/
├── app.py
├── config.py
├── skill_matcher.py
├── requirements.txt
├── .env.example
├── .gitignore
└── templates/
    ├── applications.html
    ├── add_application.html
    ├── edit_application.html
    └── skill_matcher.html
```
###  Create the database

Open MySQL Workbench or a MySQL client and execute the SQL script in the project root:

```text
database.sql
```

Alternatively, run the script from a terminal:

```bash
mysql -u root -p < database.sql
```

Enter your local MySQL password when prompted. The script creates the `job_tracker` database and its required tables.

### Configure your environment

Create a local `.env` file based on `.env.example` and set your own MySQL connection details. Never commit your real `.env` file.

## Prerequisites

- Python 3
- MySQL Server
