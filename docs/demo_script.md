# ForgeMinds — Demo Scenarios Guide

> **Prepared for:** ETAI Hackathon 2026 Judges  
> **Version:** 1.0.0

---

## Demo 1: Document Intelligence Pipeline

**Goal:** Show the full journey from raw industrial document to AI-powered insights.

### Steps

1. **Login** → Navigate to the login page → Use demo credentials  
   - Email: `demo@forgeminds.ai` / Password: `ForgeMinds2026!`

2. **Upload Document** → Click "Documents" → Click "Upload"  
   - Upload sample file: `data/sample_documents/inspection_reports/INS-2024-0001.txt`
   - Observe: Upload progress, processing status changes (queued → processing → completed)

3. **View Extracted Entities** → Click on the uploaded document  
   - See: Equipment tags (P-101, V-200), regulations (ASME B31.3), dates, personnel
   - See: Document metadata, chunk count, processing time

4. **Explore Knowledge Graph** → Navigate to "Knowledge Graph"  
   - Filter by entity type: Equipment
   - Click on node "P-101" → See connected nodes (documents, regulations, personnel)
   - Expand subgraph (depth=2) → Observe relationship network

5. **Ask AI** → Navigate to "Chat"  
   - Query: *"What maintenance recommendations exist for Pump P-101 based on the latest inspection?"*
   - Observe: Agent indicator shows "Maintenance Agent"
   - See: Response with citations [1], [2], confidence score (87%)
   - Click citations to view source documents

---

## Demo 2: Predictive Maintenance & RCA

**Goal:** Demonstrate AI-powered equipment failure prediction and root cause analysis.

### Steps

1. **Dashboard Overview** → Navigate to "Dashboard"  
   - See: Total documents processed, active equipment count, compliance score
   - See: System health indicators (green = all services healthy)

2. **Maintenance Dashboard** → Navigate to "Maintenance"  
   - See: Three alert levels (Critical, Warning, Info)
   - Critical: "Pump P-101 bearing failure predicted in 14 days (92% confidence)"
   - Observe: Equipment health cards with color-coded status

3. **Run Root Cause Analysis** → Click on P-101 alert → Click "Run RCA"  
   - See: Root cause tree diagram
   - See: Correlated past incidents from similar equipment
   - See: AI-generated recommendations with action items

4. **Ask AI about RCA** → Navigate to "Chat"  
   - Query: *"What caused the bearing failure on Pump P-101 and what similar incidents have occurred?"*
   - See: RCA Agent response with historical correlations and prevention recommendations

---

## Demo 3: Compliance Intelligence

**Goal:** Show automated compliance assessment with gap detection and evidence packaging.

### Steps

1. **Compliance Dashboard** → Navigate to "Compliance"  
   - See: Overall compliance score (94.2%) in circular gauge
   - See: Per-regulation scores: ASME B31.3 (98%), API 510 (95%), OSHA 29 CFR (89%)

2. **Gap Detection** → Click "View Gaps"  
   - See: Compliance gap heatmap (color-coded grid)
   - Identify: Red cells indicating critical gaps in OSHA 29 CFR

3. **Evidence Package** → Click on a regulation → Click "Generate Evidence"  
   - See: Collected evidence documents linked to specific clauses
   - See: Gap descriptions with recommended actions

4. **Ask AI about Compliance** → Navigate to "Chat"  
   - Query: *"Are we fully compliant with ASME B31.3? Show me any gaps and the evidence."*
   - See: Compliance Agent response with specific clause references and evidence links

---

## Demo 4: Knowledge Graph Deep Dive

**Goal:** Showcase the power of connected industrial knowledge.

### Steps

1. **Full Graph View** → Navigate to "Knowledge Graph"  
   - See: Force-directed graph with color-coded nodes
   - See: Statistics bar: "X Nodes | Y Relationships | 6 Entity Types"

2. **Filter & Explore** → Use filter toggles  
   - Toggle: Show only Equipment + Regulation nodes
   - See: Which regulations apply to which equipment

3. **Node Deep Dive** → Click on any equipment node  
   - See: Node detail panel with all attributes
   - See: Connected entities listed by relationship type
   - See: Related documents, maintenance history, compliance status

4. **Subgraph Query** → Select a node → Set depth to 3  
   - See: Expanded network showing indirect relationships
   - Discover: Hidden connections between seemingly unrelated equipment

---

## Demo 5: Hybrid Search & Analytics

**Goal:** Demonstrate multi-modal search and real-time analytics.

### Steps

1. **Search** → Navigate to "Search"  
   - Query: *"bearing failures in pumps last 6 months"*
   - See: Hybrid results combining vector similarity, graph connections, and keyword matches
   - See: Relevance scores and result highlighting

2. **Refine Search** → Apply filters  
   - Filter by: Document type (Inspection Reports)
   - Filter by: Date range (Last 6 months)
   - See: Refined results with higher precision

3. **Analytics Dashboard** → Navigate to "Analytics"  
   - See: Document processing trends (line chart)
   - See: Entity distribution (bar chart)
   - See: Query volume metrics, response times

4. **Ask AI** → Navigate to "Chat"  
   - Query: *"Summarize all bearing-related failures across our pump fleet and identify any patterns"*
   - See: Lessons Learned Agent response with pattern analysis across multiple documents

---

## Demo Credentials

| Field | Value |
|-------|-------|
| **Email** | `demo@forgeminds.ai` |
| **Password** | `ForgeMinds2026!` |

## Sample Data Included

| Category | Count | Examples |
|----------|-------|---------|
| Inspection Reports | 10 | INS-2024-0001 through INS-2024-0010 |
| Maintenance Records | 15 | WO-2024-0001 through WO-2024-0015 |
| Equipment Types | 5+ | Pumps, Compressors, Heat Exchangers, Vessels, Valves |
| Regulations | 4+ | ASME B31.3, API 510, OSHA 29 CFR, ISO 14001 |
