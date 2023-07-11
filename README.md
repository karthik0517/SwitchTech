# Switching Tech System

Switching Tech System is a web application designed to assist employees who are interested in transitioning from their current technology to a new one. The application provides a comprehensive platform for employees to evaluate their knowledge through interactive quizzes and receive personalized course recommendations based on their quiz scores. Employees can attempt quizzes on their chosen new technology and, based on their performance, the application suggests relevant Udemy and YouTube courses across Beginner, Intermediate, and Advanced levels. The dashboard features a dedicated learning module where employees can conveniently access and begin learning from the recommended YouTube courses. Additionally, employees can conveniently review their previous quiz attempts and track their overall progress on the dashboard, enabling them to monitor their completion percentage for the YouTube course they are currently undertaking.



## Prerequisites

- Python version >3.6
- Make sure to have a virtual environment set up. Install the project dependencies by running `pip install -r requirements.txt` while the virtual environment is activated.

## Technologies Used

- Frontend: HTML, CSS, JavaScript, Vue.js
- Backend: Python (Django Framework)
- Database: SQLite3


## Features

Quiz Module: Employees can attempt quizzes related to the new technology they wish to switch to. The application calculates their scores.

Course Suggestions: Based on the quiz scores, the application suggests the Beginner, Intermediate and Advanced courses for Udemy courses and YouTube courses that align with the employee's learning needs

Learning Module: The dashboard page includes a learning module where employees can access and start learning from the suggested YouTube courses.

History Page: Employees can view their previous quiz attempts and track their progress on the dashboard page.

Progress Tracking: The dashboard features an overall progress that visually represents the employee's completion percentage for the YouTube course.


## Getting Started

To get started with the project, follow these steps:

1. Clone the repository.
2. Set up a virtual environment.
3. Install the project dependencies by running `pip install -r requirements.txt` within the virtual environment.
4. Configure the database settings in the project's settings file.
5. Run the development server using the command `python manage.py runserver`.

