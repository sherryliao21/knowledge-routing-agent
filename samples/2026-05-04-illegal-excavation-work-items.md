# Work Meeting Minutes

**Project:** Illegal Excavation AI — Work Item Discussion
**Date:** 2026-05-04
**Attendees:** A-Bao, Ming-Xian, Sherry
**Minutes by:** Sherry

## Topics for This Session

- Confirming the functional scope of each Illegal-Excavation-AI work item
- Migration plan for the legacy MIS system
- AI interpretation task workflow and data flow explanation
- Map viewer features and image-comparison mode discussion
- Follow-up/reminder module planning

## Decisions

### [AI Interpretation Work Item]

- Each AI interpretation run creates one task, which runs in the background in the task list (similar to how the CC platform operates); a notification is sent when it completes
- Notification mechanism details are pending confirmation in the requirements interview
- Two image sources: a one-time large-scale nationwide batch of imagery obtained from Vendor A, or individual images uploaded by the user
- After interpretation completes, a list is generated; the user can confirm suspected points (yes/no) and decide whether to place them under watch/monitoring
- When placing a point under monitoring, the reason must be filled in and a polygon uploaded (large-area polygons are valid; overly small areas are automatically filtered out)
- Images must not be uploaded more than once (image files are large, so a duplicate-prevention mechanism is needed)

### [Image Comparison Feature Adjustment]

- Two-period image comparison will no longer pull from the image library — the user will annotate this manually instead
- A workstation will be set up on-site; images are sent to the client's AP, which then calls the workstation to run the model
- The base map will be provided by GIS Provider B via GeoServer

### [Map Viewer Features]

- The map viewer can load historically uploaded imagery, supports filtering the list by date and image-name keyword (type: satellite / aerial photo / drone), and displays points on the map
- Opening a point shows a "locate" button; the map automatically zooms to that location
- When the map is zoomed out past a certain scale, imagery automatically reverts to point display
- In comparison mode, the map view is locked and cannot be panned; a "release drag mode" button is provided to restore panning
- Users can adjust image transparency (an important feature for orthophoto analysis)
- The map viewer's design references the existing Forest Land Disaster Prevention System

### [Suspected Point Management]

- Projects are organized by year; suspected points can be created within a project
- Whether to split layers by county/city is pending confirmation in the requirements interview
- Suspected points require an uploaded polygon; no image upload is needed
- Each year forms one layer
- **Need to add a "New Survey Point Data" interface (including drawing number and key-monitoring-zone fields, refer to manual figure 2.13)**

  *[Screenshot: "New Survey Point Data" form, before/after clicking "Edit" — fields include survey serial number, drawing number, key monitoring zone, village, monitoring date, monitoring method (precise coordinates / aerial survey / rapid monitoring / unmanned equipment), volume (cubic meters), area (square meters), section, lot number, X/Y coordinates, longitude/latitude, approximate location]*

### [Legacy MIS System Migration]

- The original MS file management system will be migrated to the new system; the interface will be redesigned but functionality will remain unchanged
- The main reason for migration is information-security compliance requirements
- Migration details are pending confirmation in the requirements interview

### [Follow-up/Reminder Feature]

- The legacy system already has a follow-up/reminder feature, primarily via email notification
- Planning for the new system's follow-up feature:
  - Items to follow up on can be selected from suspected points and integrated into the follow-up module
  - Add a schedule-tracking interface (e.g. showing days remaining)
  - Follow-up dispatch interface (Shao-Chien already has a first draft)
  - After follow-up, this connects to survey-report management: including time, description, action taken, and uploaded images

### [Data Flow Documentation (requested by A-Bao)]

- A-Bao needs a data-flow document explaining how data moves after AI interpretation completes — where the data is pulled from, and where computation happens
- Data flow covers: image source → interpretation task execution (workstation) → result output → monitoring database

### [Project Timeline]

- The project is currently in the bidding process; if things go smoothly, it's expected to kick off in mid-May
- On the afternoon of the day the bid is awarded, a requirements interview and interface confirmation may need to happen immediately

## Action Items

| Owner | Task | Due |
|---|---|---|
| Sherry | Finish the "add suspected point" data interface (refer to figure 2.13) | Before 5/18 |
| Sherry | Organize existing interfaces (including the parts Shao-Chien owns) for use in the requirements interview | Before 5/20 |
| Sherry | Prepare the data-flow document (image source, compute node, data direction) for A-Bao to review | Before 5/18 |

## Next Meeting

**Time:** 2026-05-15
**Planned topic:** Discuss system architecture

## Requirements Interview

**Time:** 2026-05-20
**Planned topic:** First requirements interview
**Prep needed:** Consolidate existing interfaces, system architecture diagram, data flow diagram

**Open items to confirm:**
- Details of the AI interpretation task completion notification mechanism
- Whether the suspected-point layer should be split by county/city
- Interface design details for the MIS migration
- Who receives follow-up notifications and on what schedule
