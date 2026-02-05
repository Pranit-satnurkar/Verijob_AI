# Supply Chain Disruption Predictor 🚛📊

A real-time supply chain monitoring and disruption prediction system. This application provides a modern, interactive dashboard to track material risks, price trends, and inventory levels, helping supply chain managers make data-driven decisions.

![Dashboard Preview](screenshots/dashboard.png)

## 🚀 Features

-   **Real-time Dashboard**: Live monitoring of KPIs like Active Alerts, High Risk Items, and System Uptime.
-   **Risk Analytics**: Visual breakdown of risk distribution (Critical, High, Medium, Low) and historical price trends.
-   **Inventory Management**: Detailed view of materials including category, location, risk levels, and pricing.
-   **Live Alerts System**: Real-time notifications for critical shortages, price hikes, and delays.
-   **Interactive & Responsive**: Built with a clean, dark-themed UI using Tailwind CSS and Chart.js.
-   **Global Search**: Instantly filter materials and alerts across the platform.

## 📸 Functionality Previews

### Inventory Management
Track your stock levels, prices, and risk categories in a sortable, easy-to-read table.
![Inventory Preview](screenshots/inventory.png)

### Analytics & Trends
Visualize risk distribution and monitor price fluctuations over time with interactive charts.
![Analytics Preview](screenshots/analytics.png)

## 🛠️ Tech Stack

-   **Backend**: Python (Flask) with SQLite for data persistence.
-   **Frontend**: HTML5, JavaScript (Vanilla), Tailwind CSS.
-   **Charts**: Chart.js for data visualization.
-   **Design**: Google Stitch-inspired minimalist dark UI.

## 🔧 Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/supply-chain-predictor.git
    cd supply-chain-predictor
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    python app.py
    ```

5.  **Open in Browser**:
    Navigate to `http://localhost:5000` to view the dashboard.

## 📂 Project Structure

-   `app.py`: Main Flask application entry point.
-   `api/`: API route handlers.
-   `database/`: Database connection and query logic.
-   `static/`: Frontend assets (HTML, CSS, JS).
-   `alerts/`: Risk engine and alert generation logic.

---
*Built for the Advanced Agentic Coding Project.*
