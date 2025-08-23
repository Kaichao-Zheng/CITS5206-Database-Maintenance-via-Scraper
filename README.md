# Group 6 – Database Maintenance

## Collaboration Tools

- Check tasks in [Jira](https://group-6.atlassian.net/jira/software/projects/KAN/boards/1).
- Edit **Meeting Minutes** in [Notion](https://www.notion.so/CITS5206-Project-Meeting-Minutes-238e5d3a9f71803f9ba4fed7f91a0950?source=copy_link), then export and upload them to GitHub repo.
- Edit **Weekly Accountability Documents** in [OneDrive Shared Folder](https://uniwa-my.sharepoint.com/:f:/g/personal/24141207_student_uwa_edu_au/EnXSuU20PElDhmz5yLTyoW0B7K_1jvGaCH-0zw2MWpEwlg?e=kOH95R) and uploaded them to [Teams Group Channel](https://teams.microsoft.com/l/channel/19%3A19052e6b5a1b4d39b279248917efd1de%40thread.tacv2/Group%206?groupId=e524efef-b404-40f0-a05e-8dd542306098&tenantId=05894af0-cb28-46d8-8716-74cdb46e2226&ngc=true).
- Check Frontend design in [Figma](https://www.figma.com/design/S9aRCTd4FYe4vIpNMJm8X0/CITS5206-project?node-id=2002-3&t=x1OeMjkGU0oQr35F-1).

## Collaborators

| UWA ID   | Student Name         | GitHub User Name                                  |
| -------- | -------------------- | ------------------------------------------------- |
| 24070858 | Jiazheng Guo         | [Jiazheng GUO](https://github.com/GJZ99123)       |
| 23931717 | Mudit Mamgain        | [Mudit Mamgain](https://github.com/mudit2322)     |
| 22496593 | Jordan Daniel Rigden | [jordanrigden](https://github.com/jordanrigden)   |
| 24071068 | Xiaoyun Kong         | [Erica](https://github.com/ErikaKK)               |
| 24372276 | Zihan Wu             | [warrenwu123](https://github.com/warrenwu123)     |
| 24141207 | Kaichao Zheng        | [Kai Zheng](https://github.com/Kaichao-Zheng)     |
| 24056458 | Xin Li               | [lilyjelleycat](https://github.com/lilyjelleycat) |

## Tech Used

- [Flask](https://flask.palletsprojects.com/en/stable/)
- [Tailwind](https://tailwindcss.com/docs/installation/using-vite)
- [Linkedin_scraper](https://github.com/joeyism/linkedin_scraper)

## Get Started

### Virtual environment Python version is `Python 3.10.18`

### Create a New Virtual Environment:

1. With venv:

   ```bash
   # create environment
   python3.10 -m venv .venv  #or other name you like

   # activate environment
   source .venv/bin/activate    # macOS/Linux
   .\.venv\Scripts\activate     # Windows
   ```

2. Or with conda:

   ```bash
   # create environment
   conda create -n yourEnvName python=3.9.18

   # activate environment
   conda activate yourEnvName
   ```

### Manage Dependencies:

- Install dependency:
  ```bash
  pip install -r requirements.txt
  ```
- Add new dependency:

  ```bash
  pip install <package-name>

  # commit in requirements.txt
  pip freeze > requirements.txt
  ```

### Start the program

```bash
python add_default_user.py # add default admin user when you start the program for the first time
flask run # Or
python run.py
```

### Database

```bash
flask db init
flask db migrate
flask db upgrade
```
