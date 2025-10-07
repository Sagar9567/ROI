# Invoice ROI Simulator 📊

A full-stack ROI calculator to help businesses visualize cost savings and payback periods when switching from manual to automated invoicing. This project was built as a 3-hour assignment.



## ✨ Features

- **Interactive Calculator:** A single-page web app for entering business metrics and seeing live ROI calculations.
- **Favorable Results:** The backend logic includes a bias factor to ensure results always demonstrate the advantages of automation.
- **Full CRUD for Scenarios:** Users can **Create (Save)**, **Read (Load)**, and **Delete** named scenarios.
- **Persistent Storage:** All saved scenarios are stored in a local SQLite database.
- **Email-Gated Reports:** Generates a simple HTML report after capturing a user's email for lead generation.
- **REST API:** A clean backend API built with Python and Flask to handle all business logic.

## ⚙️ Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **Database:** SQLite
- **Frontend:** HTML, CSS, vanilla JavaScript

## 🚀 How to Run

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/ROI-Calculator-App.git](https://github.com/your-username/ROI-Calculator-App.git)
    cd ROI-Calculator-App
    ```

2.  **Install Dependencies:**
    Make sure you have Python 3 installed. Then, install the required packages:
    ```bash
    pip install Flask Flask-Cors
    ```

3.  **Run the Backend Server:**
    Execute the following command in the project directory:
    ```bash
    python app.py
    ```
    The server will start on `http://127.0.0.1:5000`.

4.  **Use the Application:**
    Open the `index.html` file in your web browser.

## 🛠️ API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/simulate` | Run a simulation and return JSON results. |
| `POST` | `/scenarios` | Save a scenario to the database. |
| `GET` | `/scenarios` | List all saved scenarios. |
| `GET` | `/scenarios/:id` | Retrieve the details for a single scenario. |
| `DELETE` | `/scenarios/:id` | Delete a saved scenario. |
| `POST` | `/report/generate` | Generate an HTML report (email required). |

## 📝 Potential Improvements

- **PDF Report Generation:** The initial plan was to generate a PDF report. Due to complex dependencies with the `WeasyPrint` library on Windows (related to GTK3), the feature was scoped to generate a functional HTML snapshot to meet the deadline.
- **User Authentication:** Adding user accounts to keep scenarios private.
