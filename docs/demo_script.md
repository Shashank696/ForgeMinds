# ForgeMinds — Demo Script

## Preparation Checklist

- [ ] All services running (`docker compose ps`)
- [ ] Database seeded with sample data
- [ ] Sample documents uploaded
- [ ] Pre-cached LLM responses for demo queries
- [ ] Browser open to http://localhost:5173
- [ ] Mobile view ready (DevTools responsive mode)

## Demo Flow (8 minutes)

### Act 1: The Problem (1 min)
*"Indian industrial plants operate across 7–12 disconnected document systems. Engineers spend 35% of their time just searching for information. And 25% of experienced engineers are retiring — taking decades of undocumented knowledge with them."*

### Act 2: Dashboard Overview (1 min)
- Show the ForgeMinds dashboard
- Highlight: X documents ingested, Y entities extracted, Z equipment tracked
- Show system health and recent activity

### Act 3: Document Ingestion (1.5 min)
- Upload a maintenance record PDF
- Show processing animation
- Show extracted entities (equipment tags, dates, failure modes)
- Show knowledge graph update in real-time

### Act 4: Knowledge Copilot (2 min)
- Ask: "What are the common failure modes for pump P-101A?"
- Show AI response with citations, confidence score, and source links
- Click a citation to see the original document
- Ask a follow-up: "What maintenance is recommended?"
- Show the Maintenance Agent handling this query

### Act 5: Knowledge Graph (1 min)
- Navigate to Knowledge Graph Explorer
- Show equipment P-101A and its connections
- Demonstrate interactive exploration
- Show how clicking a regulation node leads to compliance context

### Act 6: Intelligence Features (1.5 min)
- **Maintenance Intelligence**: Show predictive alerts and RCA
- **Compliance Dashboard**: Show gap heatmap and compliance scores
- **Proactive Alert**: "Similar failure pattern detected on P-101B"

### Act 7: Mobile & Conclusion (0.5 min)
- Resize to mobile view
- Show the copilot working on mobile
- *"ForgeMinds: reducing search time by 85%, audit prep by 95%, and preventing the next unplanned shutdown."*

## Demo Queries (Pre-cached)

1. "What are the common failure modes for pump P-101A?"
2. "When was the last inspection of atmospheric distillation column V-2001?"
3. "Are we compliant with OISD-STD-137 for all pressure vessels?"
4. "What maintenance is recommended for the hydrogen recycle compressor?"
5. "Show me all incidents related to seal failures in the past 2 years"
6. "What spare parts should we order for next quarter?"
