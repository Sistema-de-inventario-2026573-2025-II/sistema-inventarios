# 🚀 Deployment Guide: Render + Supabase

This guide explains how to deploy the **Inventory Management System** for free using **Render** (for hosting) and **Supabase** (for the database).

## 1. Database Setup (Supabase)

1.  Go to [Supabase](https://supabase.com/) and sign up/log in.
2.  Click **"New Project"**.
3.  Enter a Name (e.g., `inventory-db`) and a **Strong Password** (Save this password!).
4.  Choose a Region close to you (or US East for Render compatibility).
5.  Click **"Create new project"**.
6.  Wait for the database to initialize.
7.  Go to **Project Settings (Cog icon)** -> **Database**.
8.  Under **Connection parameters**, note down these values:
    *   **Host** (`POSTGRES_SERVER`) 
    *   **User** (`POSTGRES_USER`) - Usually `postgres`. 
    *   **Database Name** (`POSTGRES_DB`) - Usually `postgres`. 
    *   **Password** (`POSTGRES_PASSWORD`) - The one you set in step 3.
    *   **Port** (`POSTGRES_PORT`)

## 2. Hosting Setup (Render)

1.  Push your latest code to **GitHub**.
2.  Go to [Render Dashboard](https://dashboard.render.com/).
3.  Click **"New +"** -> **"Blueprint Instance"**.
4.  Connect your GitHub repository.
5.  Render will detect the `render.yaml` file and show you a configuration screen.
6.  **Environment Variables:** You will be asked to fill in the values for the database. Use the values from Supabase:
    *   `POSTGRES_SERVER`: Copy from Supabase.
    *   `POSTGRES_PORT`: 5432 (or 6543 if using pooling).
    *   `POSTGRES_USER`: Copy from Supabase.
    *   `POSTGRES_PASSWORD`: Enter your password.
    *   `POSTGRES_DB`: Copy from Supabase.
7.  Click **"Apply"**.

Render will now:
1.  Build the Docker image (shared by both services).
2.  Start the **Backend**, run the DB initialization script (`init_db.py`), and start the API.
3.  Start the **Frontend**, inject the Backend's URL, and start the Dashboard.

## 3. Preventing "Sleep" (Cold Starts)

The free tier of Render spins down after 15 minutes of inactivity. To prevent this:

1.  Copy the URL of your **Frontend** application (e.g., `https://sistema-inventarios-frontend.onrender.com`).
2.  Use a free uptime monitor service:
    *   **[UptimeRobot](https://uptimerobot.com/)**: Create a new "HTTP(s)" monitor that checks your URL every 5 minutes.
    *   **[Cron-job.org](https://cron-job.org/)**: Create a cron job that visits your URL every 5-10 minutes.
3.  This simulated traffic will keep your services active 24/7.

## Troubleshooting

-   **Logs**: Check the "Logs" tab in the Render dashboard for either service if something fails.
-   **Database Connection**: If the backend fails to start, double-check your `POSTGRES_PASSWORD` and Host in the Environment Variables tab.
