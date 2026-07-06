# Requirements Interview Minutes

## General Information
* **Project Name:** Chiayi Livestock Big Data Query Platform
* **Interview Date:** April 20, 2025
* **Client / Interviewees:** Deputy Director, Director, Section Chief, Case Officer, On-site Staff
* **Attendees (Our Team):** Account Manager, Senior Analyst, Lead Analyst
* **Recorder:** Lead Analyst

---

## Interview Objectives
* Collect feedback from executives following the report to confirm the platform's development direction and functional scope.
* Confirm development priorities and schedule planning leading up to the mid-term milestone.
* Gather executive feedback and suggestions on proposals for next year's work items.
* Validate feedback regarding the prototype operation.

---

## Future Scope Expansion (Functions / Specifications)
* **Penalties & Violations:** Confirm whether inspections of illegal chicken farms will be covered.
* **Petition Data:** Incorporate data from the "Livestock Disease Control Center (LDCC), Agriculture Department" (responsible for epidemic prevention and technical operations, which is distinct from the livestock administration unit). Follow-up discussions will be held with the LDCC regarding the data they can provide.
* **Epidemic Geographical Query:** In the event of an outbreak, the system should allow queries within a 3–5 km radius, displaying epidemic prevention details such as the livestock types and quantities of each farm.
* **Subsequent Maintenance and Management:** On-site staff will be responsible for data entry for two years. Afterwards, the system will be handed over to the business unit for self-maintenance.
* **Data Cross-Referencing:** Enable cross-referencing capabilities among the geographic distribution of petition numbers, locations of non-open type livestock sheds, river basin distributions, and pig/chicken livestock farm data.
* **LDCC Integration:** Requirements from the LDCC (including violations, disinfection, and drug administration management) can be integrated into this platform.
* **Permissions & Feedback:** Open read-only access to township office personnel and provide an appeal channel for reporting data errors.

---

## Prototype Feedback
* **User Operations Log:** Add a feature to download log records.
* **Penalty Records:** When multiple penalty records exist, the detailed view must paginate them by date.
* **Homepage Content:** The Case Officer will provide the layout design. The content must fit within a single page without requiring the user to scroll.

---

## Action Items

| Owner | Task Description | Deadline |
| :--- | :--- | :--- |
| Lead Analyst, UX Designer | Begin UI design (Provide 2 to 3 drafts for the client's confirmation; frontend development will commence only after approval). | TBD |
| Lead Analyst, Engineer | Begin API development ahead of schedule. | TBD |
| Lead Analyst, Account Manager | Discuss requirements integration (violations, disinfection, drug administration management) with the LDCC. | TBD |
| Case Officer | Provide the homepage layout and content planning. | TBD |
| Account Manager | Supplement and complete the "Contract Veterinarian Data" (as referenced on page 9 of the briefing). | TBD |

---

## Next Meeting / Milestones
* Submit UI design drafts for client confirmation once completed (Date TBD).
* Convene the project kickoff meeting once the engineer roster is finalized (Anticipated after April 22).
* Complete the **Data Editing, Maintenance, and Read-Only** functions before the Mid-term Report (July 7).
