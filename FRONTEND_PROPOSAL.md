# Frontend Design Proposal: Election Campaign Helping App

## 1. Vision & Goals
The **Election Campaign Helping App** is a strategic platform designed to empower political candidates and their campaign teams. It transforms raw electoral data into actionable intelligence, enabling targeted voter outreach, efficient field operations, and real-time campaign monitoring.

**Primary Goals:**
- **Voter Empowerment:** Provide workers with instant access to voter information and history.
- **Strategic Fieldwork:** Optimize door-to-door visits with digital tracking and household mapping.
- **Data-Driven Decisions:** Use heatmaps and analytics to identify campaign strongholds and swing areas.
- **High-Speed Data Ingestion:** Leverage a robust OCR pipeline to digitize new voter lists rapidly.

---

## 2. User Personas
| Persona | Key Responsibility | Primary Need |
| :--- | :--- | :--- |
| **Candidate** | Overall Strategy & Public Image | High-level analytics, campaign progress reports, and constituent sentiment. |
| **Campaign Manager** | Operations & Logistics | Resource allocation, field worker tracking, and data integrity oversight. |
| **Field Worker** | Ground-level Outreach | Easy voter search, mobile-friendly visit logging, and route navigation. |

---

## 3. Core Modules & Features

### A. Candidate Landing & Login
*   **Branded Experience:** A professional, candidate-centric landing page highlighting the campaign's vision.
*   **Secure Access:** Multi-role authentication (Candidate, Manager, Worker) with restricted data access.

### B. Constituency Voter Search (Elasticsearch Powered)
*   **Fuzzy Search:** Lightning-fast search across names, EPIC IDs, and addresses, handling common misspellings.
*   **Advanced Filtering:** Filter by Booth No, AC (Assembly Constituency), Age, Gender, and interaction status.
*   **Voter Profiles:** Detailed view of voter information, including household members and past interactions.

### C. Field Visit Tracker (Mobile-Web Sync)
*   **Real-time Logging:** Record household visits, voter sentiment (Supportive/Neutral/Opposed), and specific issues.
*   **Offline Support:** Seamless data entry in low-connectivity areas with background synchronization.
*   **Household Mapping:** Group voters by residence to streamline door-to-door campaigns.

### D. Admin Data Entry (The OCR Review Module)
*   **OCR Ingestion:** Upload and process electoral rolls using the **docTR** engine.
*   **Human-in-the-Loop Review:** High-fidelity side-by-side verification interface with spatial highlighting of OCR results.
*   **Template Management:** Configure and test extraction templates (YAML) for various electoral roll formats.

### E. Campaign Intelligence & Heatmaps
*   **Geospatial Visualization:** Interactive maps showing voter density, visit coverage, and support levels.
*   **Progress Analytics:** Dashboards tracking daily visit targets and campaign reach.

---

## 4. Tech Stack & Architecture

### Frontend Framework
- **React (v18+)**: Utilizing Functional Components and Hooks.
- **State Management**: **Zustand** for lightweight, performant global state (essential for managing large voter datasets).
- **Styling**: **Vanilla CSS** (keeping it clean, standard-compliant, and high-performance).

### Specialized Libraries
- **react-pdf-viewer**: For document rendering in the OCR review module.
- **Lucide React**: For a consistent, lightweight icon set.
- **TanStack Query (React Query)**: For efficient API caching and synchronization with the FastAPI backend.
- **Leaflet / React-Leaflet**: For rendering campaign heatmaps and field maps.

### Architecture
- **Service Layer**: Decoupled API client using Axios, mapped to Backend's `ExtractionJob` and `Voter` schemas.
- **Responsive Design**: Mobile-first approach for Field Worker modules, Desktop-optimized for Admin/Manager dashboards.

---

## 5. UI/UX Design Strategy

### Theme
- **Primary Color:** Campaign-specific branding (e.g., Deep Blue or Saffron).
- **Secondary Color:** High-contrast accents for action items.
- **Surface:** Clean, high-contrast layouts to ensure readability in field conditions (outdoors).

### Interaction Patterns
- **Optimized Search:** Quick-action buttons for common search queries.
- **One-Tap Logging:** Minimal input required for field workers to log a visit.
- **Skeleton Loading:** Ensure the app feels fast even when loading large lists.

---

## 6. Implementation Roadmap

### Phase 1: Foundation & Search (MVP)
- [x] Candidate branding and landing page.
- [x] Elasticsearch integration for voter search.
- [ ] Basic OCR pipeline for data ingestion.

### Phase 2: Field Operations & Outreach
- [ ] Mobile-responsive Field Visit Tracker.
- [ ] Sentiment tagging and household grouping.
- [ ] SMS/WhatsApp integration for direct voter communication.

### Phase 3: Intelligence & Analytics
- [ ] Geographic heatmaps of visited households.
- [ ] Advanced campaign progress dashboards.
- [ ] Predictive analytics for voter turnout.

---

## 7. Success Criteria
1.  **Data Accuracy:** High precision in OCR-digitized voter records.
2.  **Field Efficiency:** Significant reduction in time taken to log and track voter visits.
3.  **Strategic Insight:** Actionable heatmaps that influence campaign resource allocation.
