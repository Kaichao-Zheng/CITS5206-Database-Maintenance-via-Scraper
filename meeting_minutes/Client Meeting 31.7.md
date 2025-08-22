# Client Meeting 31.7

Created: July 31, 2025 2:28 PM

**CITS5206 Client Meeting Summary**

**Date:** 31/07/2025

**Client Representatives:** Lisa Cluett, Melinda Mounsey, Bella Benjamin

**Student Team Members:** Zihan Wu, Kai Zheng, Mudit Mamgain

**Duration:** ~36 minutes

**Project Title:** Automating Contact Data Extraction and Cleaning for CRM

---

### **Purpose of the Meeting**

To clarify project requirements, understand client expectations, and discuss technical challenges around developing a tool to automate the process of extracting and cleaning contact data from public sources into a structured Excel format.

---

### **Key Discussion Points**

### 1. **Project Importance & Background**

- Lisa emphasized their team's strong engagement with interns and student projects.
- Current process is entirely **manual**—they search names across multiple sites to check for updates in roles, organizations, locations, etc.
- Maintaining updated records is essential as their CRM contains **7000+ entries**.

### 2. **Desired Output**

- A standardized Excel sheet with ~8–10 key fields per person:
    - First Name, Last Name
    - Job Title
    - Organization
    - Email
    - Location
    - Sector (e.g., Government, Education)
- Lisa uses these fields to filter and segment contact lists for outreach.

### 3. **Current Challenges**

- Data gets outdated quickly—people change jobs, move cities, or even pass away.
- Keeping the Excel database clean and consistent is time-consuming.
- Sometimes inconsistencies exist between sectors or companies (e.g., someone moves from government to private sector).

### 4. **Project Requirements**

- **Automate the process** of extracting data from online public sources (e.g., LinkedIn, company directories).
- The system should allow:
    - Uploading or reading existing records
    - Scraping the web for current info
    - Outputting a clean Excel file
- Should be **easy to use**, especially for non-technical users like Bella (the “test case” for usability).
- The **final upload to CRM is manual**, handled by Mel or Lisa, so the system does **not need direct CRM integration**.

### 5. **Nice-to-Have Features**

- Option to **run periodic checks** (e.g., every 1–2 weeks) to revalidate stored records.
- Sector tagging and classification (government, education, business) could be inferred if possible.
- Allow manual overrides or notes in the Excel file.

### **Client Expectations**

- **Accuracy over automation**: It’s okay if some work is still manual, as long as the tool saves significant time.
- Lisa is excited about the potential; she envisions pressing a button to get updated contact data.
- **Bella will test** the system for usability—make it intuitive and clean.

---

### **Questions & Answers from Client Discussion**

---

**Q1: What data fields should the tool collect for each person?**

**A:** The tool should gather consistent fields for every entry: full name, job title, organization, email address, and location. These are essential for sorting and filtering contacts in their CRM.

---

**Q2: Will the format or fields vary between entries?**

**A:** The goal is to have a uniform format, but the completeness of the data may vary depending on what's publicly available online.

---

**Q3: How is this data currently updated?**

**A:** The team manually looks up each person online, checks their job role and organization, and makes updates in the Excel file. This process is time-consuming and done as needed.

---

**Q4: Do we need to integrate the scraper with their internal database?**

**A:** No integration is necessary. Once the Excel file is cleaned and updated, it can be manually re-uploaded to the database by the internal team.

---

**Q5: Are there any classifications or categories we need to include?**

**A:** Yes, people are grouped into sectors such as government, education, business, etc. There are around 6–7 predefined sectors, and these are updated manually when needed.

---

**Q6: What happens if we find conflicting information for the same person?**

**A:** Conflicts are expected occasionally. The person's name will remain the same, but their job, sector, or organization may have changed. The tool should try to prioritize the most recent information, but manual review is acceptable.

---

**Q7: Should the tool check for data updates automatically on a schedule?**

**A:** This isn’t mandatory, but it would be a valuable feature. Currently, updates are done manually when time allows. If a periodic check (e.g., every two weeks) was possible, it could be very helpful.

---

**Q8: Who will use the tool, and how technical are they?**

**A:** Non-technical staff will be the primary users, so the tool should be simple, clear, and easy to operate—ideally with just a few clicks to upload, run, and download the results.

### **Next Steps**

- Melinda will share:
    - Sample Excel files (with the expected format and fields).
    - A list of sectors or tags used.
- Team to:
    - Confirm list of target data sources (e.g., LinkedIn, company websites).
    - Build a prototype to scrape one source and structure the data.
    - Share early UI mockups or interface sketches for feedback.

### **Meeting Closing**

- The team expressed understanding of the task.
- Client team was supportive, enthusiastic, and open to ideas.
- Lisa confirmed future communication, and testing will be coordinated through Mel.