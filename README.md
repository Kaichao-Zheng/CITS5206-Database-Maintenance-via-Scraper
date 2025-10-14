# Group 6 – Database Maintenance via Scraper

## 🤝Collaborators

| UWA ID   | Student Name         | GitHub User Name                                  |
| -------- | -------------------- | ------------------------------------------------- |
| 24070858 | Jiazheng Guo         | [Jiazheng GUO](https://github.com/GJZ99123)       |
| 23931717 | Mudit Mamgain        | [Mudit Mamgain](https://github.com/mudit2322)     |
| 22496593 | Jordan Daniel Rigden | [jordanrigden](https://github.com/jordanrigden)   |
| 24071068 | Erica Kong           | [ErikaKK](https://github.com/ErikaKK)             |
| 24372276 | Zihan Wu             | [warrenwu123](https://github.com/warrenwu123)     |
| 24141207 | Kaichao Zheng        | [Kai Zheng](https://github.com/Kaichao-Zheng)     |
| 24056458 | Xin Li               | [lilyjelleycat](https://github.com/lilyjelleycat) |

## 🛠️Collaboration Tools

- Check tasks in [Jira](https://group-6.atlassian.net/jira/software/projects/KAN/boards/1).
- Edit **Meeting Minutes** in [Notion](https://www.notion.so/CITS5206-Project-Meeting-Minutes-238e5d3a9f71803f9ba4fed7f91a0950?source=copy_link), then export and upload them to GitHub repo.
- Edit **Weekly Accountability Documents** in [OneDrive Shared Folder](https://uniwa-my.sharepoint.com/:f:/g/personal/24141207_student_uwa_edu_au/EnXSuU20PElDhmz5yLTyoW0B7K_1jvGaCH-0zw2MWpEwlg?e=kOH95R) and uploaded them to [Teams Group Channel](https://teams.microsoft.com/l/channel/19%3A19052e6b5a1b4d39b279248917efd1de%40thread.tacv2/Group%206?groupId=e524efef-b404-40f0-a05e-8dd542306098&tenantId=05894af0-cb28-46d8-8716-74cdb46e2226&ngc=true).
- Check Frontend design in [Figma](https://www.figma.com/design/S9aRCTd4FYe4vIpNMJm8X0/CITS5206-project?node-id=2002-3&t=x1OeMjkGU0oQr35F-1).

## 📚Core Dependencies

| Library                                                      | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Tailwind](https://tailwindcss.com/docs/installation/using-vite) | The frontend CSS framework                                   |
| [Flask](https://flask.palletsprojects.com/en/stable/)        | Render, route, interact with pages <br />Configure database migration |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | Parse HTML and filter HTTP data                              |
| [Selenium](https://www.selenium.dev/)                        | Automate browsing operations                                 |
| [LinkedIn_Scraper](https://github.com/joeyism/linkedin_scraper) | Automated LinkedIn sign-in                                   |
| [Undetected_ChromeDriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) | Bypass LinkedIn scraper detection                            |
| [Requests](https://requests.readthedocs.io/en/latest/)       | Fetch [free IP proxies](https://free-proxy-list.net/en/) for bypassing |
| [Pandas](https://pandas.pydata.org/)                         | Cleanse invalid data                                         |

## 📂Core Files

```bash
.
├── app/                      # Main Flask application
├── .env                      # Environment config
├── run.py                    # Flask application runner
├── README.md                 # Project instruction
├── sample_gov.csv            # Sample gov officer profiles to be scraped
├── sample_linkedin.csv       # Sample LinkedIn profiles to be scraped
└── sample_senator.csv        # Sample senator profiles to be scraped
```

## 🚀Get Started

```bash
git clone https://github.com/Kaichao-Zheng/CITS5206-Database-Maintenance-via-Scraper.git
```

### Create a New Virtual Environment

#### Virtual environment Python version is `Python 3.10.18`

1. With venv:

   ```bash
   # create environment
   python3.10 -m venv .venv     # or other name you like

   # activate environment
   source .venv/bin/activate    # macOS/Linux
   .\.venv\Scripts\activate     # Windows Powershell
   ```

2. Or with conda:

   ```bash
   # create environment
   conda create -n yourEnvName python=3.10.18
   
   # activate environment
   conda activate yourEnvName
   ```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables and User Authentication

Copy the file `.env.example` and rename the file to `.env` in the root directory.
Or create a `.env` file that has the following content:

```env
# LinkedIn Account Login
LINKEDIN_EMAIL=some-email@email.address
LINKEDIN_PASSWORD=your-linkedin-password

# System Default User Info
ADMIN_PASSWORD=app-login-password
ADMIN_EMAIL=   # Optional, default is blank

FLASK_APP=run.py
FLASK_CONFIG=config.DevelopmentConfig

# leave blank for production env
FLASK_ENV=

# CSRF protection; leave blank for default dev key
SECRET_KEY=
```

### Create Database

```bash
flask db upgrade
```

### Add Administrator

```bash
python add_default_user.py	# add default admin user when you start the program for the first time
```

### Run the Web Application

```bash
flask run # Or
python run.py
```

### Open your usual browser and visit

http://127.0.0.1:5000 or http://localhost:5000

### Login application using the password you configured in `.env`

```env
# System Default User Info
ADMIN_PASSWORD=
```

## 🐞Scraping

### Scrape LinkedIn profiles

1. Navigate to sidebar tag "Workspace"

2. Upload provided `sample_linkedin.csv`

3. Check parsed information

4. Click the "Update" button at the bottom right

5. Select "LinkedIn" as data source

6. Watch the automated scraping work (1.5 min per profile)

7. Export the scraped profiles

### Scrape government officer profiles or parliament senator profiles

1. Navigate to sidebar tag "Settings"
2. Click "Update Local Database" button (4-7 min)
   This will scrape **all profiles** from both [Directory.gov](https://www.directory.gov.au/commonwealth-entities-and-companies) and [Parliament Senators](https://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results).
3. Navigate to sidebar tag "Workspace"
4. Upload provided `sample_gov.csv` 
   Or upload provided `sample_senator.csv`
5. Select corresponding "Directory.gov" as data source
   Or select "Australian Parliament" to scrape senators
6. Export the scraped profiles
