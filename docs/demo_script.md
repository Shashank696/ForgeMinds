# ForgeMinds — Demo Video Resources & Script

Use this resource kit to record your hackathon demo video. It contains copy-pasteable sample documents, exact search queries, AI chat prompts, and a step-by-step video script.

---

## 📄 Part 1: Sample Documents to Upload

Create these files on your computer (save them as `.txt` files) so you can upload them during the demo video.

### File 1: `INS-2024-0012_Pump_P101.txt`
*(Save this as a text file. It represents a real inspection report with equipment tags, regulations, dates, and failure details).*

```text
==================================================
INDUSTRIAL INSPECTION REPORT: INS-2024-0012
==================================================
Facility: Houston Refining Plant A, Unit 3
Date: October 15, 2024
Inspector: Eng. Richard Martinez
Subject: Centrifugal Pump P-101 Vibration Inspection

EQUIPMENT DETAILS:
- Equipment Tag: P-101
- Type: Centrifugal Water Pump
- Criticality: HIGH

FINDINGS:
During routine vibration analysis on Pump P-101, abnormal radial acceleration was detected on the outboard bearing housing (DE bearing). 
Vibration levels reached 8.2 mm/s RMS, exceeding the permissible threshold of 4.5 mm/s RMS specified under ASME B31.3 piping and machine standards. 

INSPECTION SUMMARY:
The bearing is showing signs of severe fatigue and lubrication degradation. Temperature readings indicated a peak of 85°C (thermal alarm limit is 70°C). 

RECOMMENDATIONS:
1. Schedule bearing replacement for P-101 within 14 days to prevent catastrophic lockup.
2. Flush and replace lubrication oil immediately.
3. Re-align the shaft coupling to ASME standards during the next scheduled maintenance window.
==================================================
```

### File 2: `REG-ASME-B31-3_Extract.txt`
*(Save this text file. It represents a regulatory standard).*

```text
==================================================
REGULATORY STANDARD EXTRACT: ASME B31.3 - SECTION 3
==================================================
Regulation Code: ASME B31.3
Title: Process Piping Standards for Rotating Machinery
Effective Date: January 1, 2022
Compliance Authority: Industrial Safety Board

REGULATION SUMMARY:
Section 3.1.2: Vibration Thresholds for High-Criticality Pumps
All active process pumps with high criticality must maintain vibration levels below 4.5 mm/s RMS. Any machine operating above 6.0 mm/s RMS must be placed on a 14-day mandatory repair window.

Section 3.4.1: Thermal Operating Limits
The maximum allowable surface operating temperature for rotating shafts and bearing housings in hazardous environments is 70°C. Operations exceeding 80°C require an immediate safety shutdown audit.
==================================================
```

---

## 🎬 Part 2: Video Recording Script (3-Minute Walkthrough)

Here is a step-by-step timeline of what to show on your screen and what to say.

### Scene 1: The Landing Page & Dashboard (0:00 - 0:30)
*   **On Screen:** Show the Landing Page, click "Sign In", type credentials (`demo@forgeminds.ai` / `ForgeMinds2026!`), and load the Dashboard. Hover over the stat cards and system health.
*   **What to Say (Voiceover):**
    > *"Welcome to ForgeMinds, an Industrial Intelligence Platform. Today, we are showcasing how we transform unstructured documentation into connected knowledge and predictive maintenance insights. We start on our premium dark-themed dashboard, which gives operators a real-time overview of processed documents, active equipment health, compliance scores, and overall system health."*

### Scene 2: Document Upload & Ingestion (0:30 - 1:10)
*   **On Screen:** Click "Documents" in the sidebar. Click "Upload", choose your saved file `INS-2024-0012_Pump_P101.txt` and click upload. Show the processing animation, then click on the finished document to show the extracted entities (P-101, ASME B31.3, Richard Martinez, etc.) highlighted in the sidebar.
*   **What to Say (Voiceover):**
    > *"Let's upload a raw inspection report for Pump P-101. As we upload, the ForgeMinds ingestion pipeline automatically runs OCR, cleans the text, and performs Named Entity Recognition. In seconds, the platform extracts crucial metadata, identifying the equipment tag P-101, standard regulations like ASME B31.3, key inspection dates, and the inspector."*

### Scene 3: The Knowledge Graph Explorer (1:10 - 1:40)
*   **On Screen:** Click "Knowledge Graph" in the sidebar. Show the glowing network graph. Use the filters on top. Click on the node `P-101`, expand the connections, and show the panel details.
*   **What to Say (Voiceover):**
    > *"All these extracted entities are mapped into our Neo4j Knowledge Graph. Here, operators can explore the relationships between documents, machinery, failures, and regulations. If we filter by Equipment and click on P-101, we instantly see all documents referencing it, the regulations governing it, and the failure modes associated with its history."*

### Scene 4: Predictive Maintenance & RCA (1:40 - 2:20)
*   **On Screen:** Click "Maintenance" in the sidebar. Show the critical predictive alert for P-101. Click "Run RCA" to show the root cause analysis breakdown and historical similarities.
*   **What to Say (Voiceover):**
    > *"Our platform goes beyond search. Under the Maintenance Intelligence module, the system predicts failures. Here, we see a critical alert: Pump P-101 bearing failure is predicted within 14 days with 92% confidence. By clicking Run Root Cause Analysis, our AI correlates this with historical documents and outlines the exact failure path, offering actionable repair steps."*

### Scene 5: Hybrid AI Copilot & Wrap-Up (2:20 - 3:00)
*   **On Screen:** Click "Chat" in the sidebar. Type the query (from Part 3 below), hit send, watch the response stream in, show the "Maintenance Agent" badge, hover over the citations, and click one.
*   **What to Say (Voiceover):**
    > *"Finally, we can talk to our data using our Multi-Agent RAG Copilot. We ask the system for maintenance recommendations for P-101. The orchestrator routes this to the Maintenance Agent. The agent queries our vector store and graph databases to generate a highly structured response, complete with direct document citations and a confidence score. This is ForgeMinds—bridging the gap between raw data and industrial safety. Thank you."*

---

## 💬 Part 3: Search Queries & Chat Prompts to Show

Copy and paste these exact inputs during your recording:

### Global Search Bar
*   **Search Query:** `bearing failure P-101`
*   **Result:** Shows the uploaded inspection report and related maintenance records with high relevance.

### AI Copilot Chat Window
*   **User Question:** `What are the maintenance recommendations for Pump P-101 based on our recent inspections, and are there any ASME B31.3 violations?`
*   **Expected AI Response:** 
    - Routes to the **Maintenance/Compliance Agent**.
    - Mentions replacing the Outboard Bearing housing (DE bearing) within 14 days due to vibration of 8.2 mm/s.
    - Notes a violation of ASME B31.3 section 3.1.2 because vibration exceeded 4.5 mm/s (operating at 8.2 mm/s) and temperature reached 85°C (exceeding the 70°C limit).
    - Cites `INS-2024-0012` and `REG-ASME-B31-3`.
