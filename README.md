# Lifeguard Rotation Scheduler

A scheduling tool that automates the creation of lifeguard rotation schedules for pool operations.

This project began as a personal solution to a recurring problem while working as a lifeguard at **Teaneck Recreation**. Rotation schedules were created manually, requiring constant attention to timing, staffing levels, station assignments, and breaks.

Although originally created in high school, this project represents one of my earliest experiences designing software to solve a real operational problem. Although it could be script, it is designed for those with no programming background to use.

---

## Features

- Automatically generates lifeguard rotation schedules
- Assigns guards to stations throughout the day
- Rotates guards at fixed time intervals
- Handles lunch and break scheduling
- Produces schedules to post on shared staff board
- Eliminates repetitive manual scheduling

---

## Motivation

Creating daily rotations by hand was time-consuming and error-prone, especially when accounting for staffing changes, break requirements, and station coverage.

The goal of this project was to:

- Reduce the time required to generate schedules
- Automate a task that was previously performed manually

---

## Technical Highlights

Some of the concepts explored in this project include:

- Scheduling algorithms
- XLSX File generation
- Modular Python design
- Simple Flask backend and Bootstrap frontend

---

## Project Structure

```
.
├── backend     # algorithms handling scheduling and file saving
├── debug       # basic logger to debug live application
├── instance    # database instance
├── src         # flask backend
└── templates   # html/css frontend
```

---

## Running the Project

The project runs on **3.11.4**. Create a Python venv and install the project dependencies
```
python -m venv
pip install -r requirements.txt
```

Create a .env file, and fill in a **EXAMPLE_USERNAME** and **EXAMPLE_PASSWORD** field in it. Afterwards, use the Makefile command to run the program

```
make run
```

The application should start running! Sit back and enjoy your application!

---

### Author's Note

This project represents a solution that provides automation to a repetetive task. While live [here](https://ben451.pythonanywhere.com/) on a PythonAnywhere server, it is not a
permanent location, and is not open to public consumption due to lack of load testing.
