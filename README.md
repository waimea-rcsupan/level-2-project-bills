# ... Project

by Raven Supan

## Project Description

This is an app that You can manage your bills in to.

The app has the following key features:
- Notes The bills
- Shows how much the bill costs
- you can add when it is due
- ...

## Live Site

https://level-2-project-bills.onrender.com




## Supporting Documents

Task Instructions:
- [Instruction documents](docs/instructions/)

Project Evidence
- [Sprint 0: Project Requirements](docs/evidence/sprint-0-requirements.md)
- [Sprint 1: Prototype Development](docs/evidence/sprint-1-prototype.md)
- [Sprint 2: MVP Development](docs/evidence/sprint-2-mvp.md)
- [Sprint 3: Final System Development](docs/evidence/sprint-3-final.md)
- [Review: Project Final Review](docs/evidence/system-review.md)





## Technologies Used

- [Flask](https://flask.palletsprojects.com/) as the web framework
- [Python](https://www.python.org/) as the programming language used
- [SQLite](https://sqlite.org/) for the database
- [Jinja2](https://jinja.palletsprojects.com/templates/) for page templating



*For easier reading, the docs are hosted as a [GH Pages site](https://waimea-rcsupan.github.io/level-2-project-bills/)*


## Project Structure

```
├── README.md            # Project README
│
├── requirements.txt     # Python modules required
│
├── app/                 # Flask application
│   │
│   ├── __init__.py      # Routes and app logic
│   │
│   ├── .env             # Environment values
│   │
│   ├── templates/       # Jinja2 templates
│   │   ├── pages/       # Full page templates
│   │   └── partials/    # Reusable template parts
│   │
│   ├── static/          # Files to be served directly
│   │   ├── css/         # CSS stylesheets
│   │   ├── images/      # Images
│   │   └── js/          # Javascript files
│   │
│   ├── db/              # Database files
│   │   ├── config.py    # Database schema & seed data
│   │   └── data.sqlite  # SQLite database
│   │
│   └── helpers/         # Helper files (don't modify)
│
└── docs/                # Project documentation
    ├── guides/          # Helpful guides
    ├── instructions/    # Task instructions
    └── evidence/        # Project evidence
```
