# This branch is for testing purpose and not allowed to merge into main

## Get Started

### If you are using virtual environment, Python version is `Python 3.10.18`

### Create a New Virtual Environment:

1. With venv:

   ```bash
   # create environment
   python3.10 -m venv venv		# or other name you like

   # activate environment
   source venv/bin/activate    # macOS/Linux
   .\venv\Scripts\activate     # Windows Powershell
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

### Configure User Authentication

Create a `.env` file in the root directory:

```env
LINKEDIN_EMAIL=some-email@email.address
LINKEDIN_PASSWORD=your_password
```

### Start the program

```bash
python3 scraper.py
```

## User Scraping

```python
person = Person("https://www.linkedin.com/in/joey-sham-aa2a50122", driver=driver, scrape=False, close_on_complete=False)
```

- `scrape=False`: it doesn't automatically scrape the profile, but Chrome will open the linkedin page anyways.

- when you run `person.scrape()`, it'll scrape and close the browser.
- `close_on_complete=False` keeps browser open to scrape next profile.

## URL

- The URL pattern should be `https://www.linkedin.com/in/joey-sham-aa2a50122` so I trim the strings after and include `?mini`
