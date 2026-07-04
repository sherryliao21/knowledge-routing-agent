# Engineering Meeting Minutes — V2 Prototype Feature Discussion

**Date:** 2026-03-27

## I. Core Features (V1 Implementation Scope)

- **Login / Registration**
  Users will log in exclusively via SSO through the external Portal. This system will not implement its own login or registration functionality.

- **Core Functionality**
  Two main features to prioritize:
  1. Photo upload
  2. Output modeling

- **Interface & Interaction**
  1. The sidebar needs to distinguish between two folder types — "Album" and "Project" — managing photos and modeling data separately
  2. The Album must support adding, deleting, and searching photos
  3. Modeling progress must be shown as a progress bar, displaying the status of each stage (AT computing, point cloud generation, model generation, etc.)
  4. When creating a project, users can select photos from the photo list to import into the project folder

## II. Advanced Features (Future Version Planning)

1. **Project sharing:** A project folder can designate other users to jointly view the modeling results; Albums are private to the owner only and do not support multi-user access
2. **Resumable uploads:** If an upload is interrupted, upload progress is preserved via a caching mechanism, supporting resume-from-breakpoint
3. **Storage quota management:** The user's personal page displays used and remaining storage; each user's photo-upload limit can be dynamically adjusted based on system settings and permissions
4. **AT error handling:** When AT computation fails, provide a mechanism to adjust parameters and re-run
5. **Expert mode:** After photo upload, distinguish between "Normal Mode" (default parameters) and "Expert Mode" (freely adjustable parameters); V1 will implement Normal Mode only
