
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Common skills and alternative names used in job descriptions.
SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "SQL": ["sql", "structured query language"],
    "MySQL": ["mysql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Flask": ["flask"],
    "Django": ["django"],
    "React": ["react", "react.js"],
    "Node.js": ["node.js", "nodejs"],
    "Git": ["git"],
    "GitHub": ["github"],
    "REST API": ["rest api", "restful api"],
    "Excel": ["excel", "microsoft excel"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": ["data visualization"],
    "Statistics": ["statistics", "statistical analysis"],
    "AWS": ["aws", "amazon web services"],
    "Docker": ["docker"],
    "Linux": ["linux"],
    "Spring Boot": ["spring boot"],
    "Hibernate": ["hibernate"],
}


def normalize_text(text):
    """Convert text to lowercase and normalize whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def phrase_exists(phrase, text):
    """Check whether a complete phrase appears in the text."""
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def canonicalize_skill(skill):
    """Convert known skill aliases to their standard names."""
    normalized = normalize_text(skill)

    for canonical, aliases in SKILL_ALIASES.items():
        if normalized == normalize_text(canonical):
            return canonical

        if normalized in [normalize_text(alias) for alias in aliases]:
            return canonical

    # Keep unrecognized skills instead of discarding them.
    return skill.strip()


def match_skills(user_skills, job_description):
    """
    Compare the user's skills with skills detected in the job description.
    """

    # Clean and standardize the user's skills.
    cleaned_skills = []
    seen = set()

    for skill in user_skills:
        if skill.strip():
            canonical = canonicalize_skill(skill)
            key = canonical.casefold()

            if key not in seen:
                cleaned_skills.append(canonical)
                seen.add(key)

    description = normalize_text(job_description)

    # Find known skills mentioned in the job description.
    required_skills = []

    for canonical, aliases in SKILL_ALIASES.items():
        all_names = [canonical] + aliases

        if any(phrase_exists(name, description) for name in all_names):
            required_skills.append(canonical)

    # Compare the user's skills against detected job skills.
    user_skill_names = {
        skill.casefold() for skill in cleaned_skills
    }

    matched_skills = [
        skill for skill in required_skills
        if skill.casefold() in user_skill_names
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.casefold() not in user_skill_names
    ]

    # Calculate coverage of the detected job skills.
    if required_skills:
        skill_coverage = round(
            len(matched_skills) / len(required_skills) * 100,
            2
        )
    else:
        skill_coverage = 0.0

    # Calculate TF-IDF text similarity.
    skills_text = " ".join(cleaned_skills)

    if skills_text and description:
        try:
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform(
                [skills_text, description]
            )

            similarity = cosine_similarity(
                matrix[0:1], matrix[1:2]
            )[0][0]

            text_similarity = round(float(similarity) * 100, 2)

        except ValueError:
            text_similarity = 0.0
    else:
        text_similarity = 0.0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": required_skills,
        "skill_coverage": skill_coverage,
        "text_similarity": text_similarity
    }


def generate_suggestions(missing_skills):
    """Generate learning suggestions for missing job skills."""

    learning_resources = {
        "Python": "Practise Python basics, functions, collections, and problem-solving.",
        "Java": "Learn Java syntax, OOP concepts, collections, and exception handling.",
        "SQL": "Practise SELECT queries, joins, grouping, subqueries, and indexes.",
        "MySQL": "Practise database design, joins, constraints, and CRUD operations.",
        "Git": "Learn Git status, add, commit, branches, merge, and push.",
        "GitHub": "Practise creating repositories, pushing code, and writing README files.",
        "HTML": "Learn semantic HTML, forms, tables, and page structure.",
        "CSS": "Practise selectors, Flexbox, Grid, responsive design, and layouts.",
        "JavaScript": "Learn variables, functions, arrays, objects, and DOM manipulation.",
        "Flask": "Practise Flask routes, templates, forms, and database integration.",
        "Django": "Learn Django models, views, templates, and URL routing.",
        "React": "Learn components, props, state, hooks, and event handling.",
        "REST API": "Learn HTTP methods, status codes, JSON, and API testing.",
        "Excel": "Practise formulas, lookup functions, PivotTables, and data cleaning.",
        "Power BI": "Learn Power Query, data modelling, DAX, and dashboards.",
        "Tableau": "Practise connecting datasets, creating charts, and building dashboards.",
        "Pandas": "Practise DataFrames, filtering, groupby, merging, and missing values.",
        "NumPy": "Practise arrays, indexing, vectorized operations, and matrix operations.",
        "Scikit-learn": "Practise preprocessing, model training, evaluation, and pipelines.",
        "Machine Learning": "Study supervised learning, model evaluation, and feature engineering.",
        "Deep Learning": "Learn neural networks, backpropagation, and model training.",
        "NLP": "Learn text preprocessing, tokenization, TF-IDF, and text classification.",
        "Data Analysis": "Practise data cleaning, exploratory analysis, and communicating findings.",
        "Data Visualization": "Learn to select suitable charts and explain trends clearly.",
        "Statistics": "Revise probability, distributions, hypothesis testing, and correlation.",
        "AWS": "Learn cloud fundamentals, IAM, storage, and compute services.",
        "Docker": "Learn images, containers, Dockerfiles, and basic container workflows.",
        "Linux": "Practise file navigation, permissions, pipes, and common shell commands.",
        "Spring Boot": "Learn dependency injection, REST controllers, and database integration.",
        "Hibernate": "Learn ORM concepts, entity mapping, and database persistence.",
        "Node.js": "Learn modules, asynchronous JavaScript, and server-side APIs.",
        "TensorFlow": "Practise building, training, and evaluating neural network models."
    }

    suggestions = []

    for skill in missing_skills:
        suggestion = learning_resources.get(
            skill,
            f"Study the fundamentals of {skill} and build a small practical project."
        )
        suggestions.append({
            "skill": skill,
            "suggestion": suggestion
        })

    return suggestions


if __name__ == "__main__":
    my_skills = [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "Flask"
    ]

    job_description = """
    We are looking for a candidate with Python, SQL,
    Pandas, and Machine Learning knowledge.
    Experience with Java, Git, and Flask is preferred.
    """

    result = match_skills(my_skills, job_description)

    print("\n--- JOB SKILL MATCHER ---")
    print("Job skills detected:", result["required_skills"])
    print("Matched skills:", result["matched_skills"])
    print("Missing job skills:", result["missing_skills"])
    print("Job skill coverage:", result["skill_coverage"], "%")
    print("TF-IDF text similarity:", result["text_similarity"], "%")
