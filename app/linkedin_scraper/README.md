# LinkedIn Scraper

# User Scraper

```python
person = Person("https://www.linkedin.com/in/joey-sham-aa2a50122", driver=driver, scrape=False, close_on_complete=False)
```

- `scrape=False`: it doesn't automatically scrape the profile, but Chrome will open the linkedin page anyways.

- when you run `person.scrape()`, it'll scrape and close the browser.
- `close_on_complete=False` keeps browser open to scrape next profile.

## LinkedIn URL

- The LinkedIn URL pattern should be `https://www.linkedin.com/in/joey-sham-aa2a50122` so I trim the strings after and include `?mini`
