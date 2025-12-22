# 📅 好時光女生運動樂園 Lesson to Calendar Scraper

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Success-blue?logo=githubactions)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

An automated calendar scraping tool that runs daily via GitHub Actions. It fetches event information from web sources and converts it into the standard `.ics` format, allowing you to subscribe via Google Calendar or iOS Calendar so you never miss an important event.

> **Note**: This scraper is specifically designed for **好時光女生運動樂園**(studio name). It automates the process of fetching your reserved classes and syncing them to your personal calendar.

## ✨ Features
- **Tailored for 好時光女生運動樂園**: Handles specific login flows and table structures of the booking site.
- **Automated Sync**: Runs via GitHub Actions.
- **Private & Free**: Host your own calendar link using GitHub Pages.

## 🏗️ Workflow

![image](https://github.com/Kay-Zhang1625/update_ics/blob/main/ics_flow_chart.png)

This project automates the entire process through a structured CI/CD pipeline as shown in the diagram above:

1. **Trigger**: A **Daily Cron Job** (GitHub Actions) initiates the workflow every 2 days.
2. **Runtime (Ubuntu)**: The environment is initialized on an Ubuntu runner to perform two core tasks:
   - **Step 1: Scrape Web Data**: Using Python and Chrome to log in and fetch reservation details.
   - **Step 2: Data Processing**: Converting the scraped JSON data into the standard ICS format.
3. **GitHub Repository**: The updated `events.json` and `mycalendar.ics` files are committed and pushed back to the repository.
4. **GitHub Pages**: The latest `.ics` file is deployed as a static site, generating a permanent link for subscription.
5. **Subscription**: The final output is synced to your **Google/iOS Calendar** via the provided URL.


## 🛠️ Tech Stack

### Core Technologies
- **Language**: Python (Selenium & BeautifulSoup)
- **CI/CD**: GitHub Actions (Ubuntu Runner)
- **Deployment**: GitHub Pages

## 🚀 Usage & Deployment

This project is a **personal calendar synchronizer**. To use it for your own classes, you need to host your own version by following these steps:

### Step 1: Fork & Setup
1. **Fork** this repository to your own GitHub account.
2. Go to your Forked repo -> **Settings** -> **Secrets and variables** -> **Actions**.
3. Add two New repository secrets:
   - `ICS_GOODTIME_USERNAME`: Your 好時光 account ID.
   - `ICS_GOODTIME_PASSWORD`: Your 好時光 password.

  *The script retrieves these values using `os.environ`, ensuring your credentials remain private even if your repository is public.*

4. Enable **GitHub Pages** in your repo settings (deploy from `main` branch).

### Step 2: Subscribe to Your Calendar
Once the GitHub Action runs successfully (manually trigger it or wait for the daily cron), your calendar will be available at:

`https://[YOUR_USERNAME].github.io/[REPO_NAME]/mycalendar.ics`

### Subscription Guides:
* **Google Calendar**: Go to the web version -> Click "+" next to "Other calendars" -> Select "From URL".
* **iOS Calendar**: Click "File" -> Select "New Calendar Subsription".

## 📄 License
This project is licensed under the [MIT License](LICENSE).
