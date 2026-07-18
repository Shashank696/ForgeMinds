/**
 * ForgeMinds — Mock Data (fallback when backend returns 501)
 * Data shapes match shared/interfaces.py exactly.
 */

const now = new Date().toISOString();
const yesterday = new Date(Date.now() - 86400000).toISOString();
const lastWeek = new Date(Date.now() - 604800000).toISOString();
const lastMonth = new Date(Date.now() - 2592000000).toISOString();

// ─── Documents ────────────────────────────────────────────
export const mockDocuments = {
  items: [
    { id: 'doc-001', filename: 'pump_maintenance_SOP.pdf', original_filename: 'pump_maintenance_SOP.pdf', file_type: 'application/pdf', document_category: 'operating_procedure', file_size_bytes: 2450000, page_count: 24, upload_status: 'completed', processing_stage: 'graph_linked', entity_count: 18, created_at: yesterday },
    { id: 'doc-002', filename: 'valve_inspection_2024.pdf', original_filename: 'valve_inspection_2024.pdf', file_type: 'application/pdf', document_category: 'inspection_report', file_size_bytes: 1800000, page_count: 12, upload_status: 'completed', processing_stage: 'graph_linked', entity_count: 14, created_at: lastWeek },
    { id: 'doc-003', filename: 'P&ID_unit_7.png', original_filename: 'P&ID_unit_7.png', file_type: 'image/png', document_category: 'engineering_drawing', file_size_bytes: 5200000, page_count: 1, upload_status: 'completed', processing_stage: 'entities_extracted', entity_count: 42, created_at: lastWeek },
    { id: 'doc-004', filename: 'compressor_failure_report.pdf', original_filename: 'compressor_failure_report.pdf', file_type: 'application/pdf', document_category: 'incident_report', file_size_bytes: 890000, page_count: 8, upload_status: 'completed', processing_stage: 'graph_linked', entity_count: 11, created_at: lastMonth },
    { id: 'doc-005', filename: 'OISD_guidelines_154.pdf', original_filename: 'OISD_guidelines_154.pdf', file_type: 'application/pdf', document_category: 'regulatory', file_size_bytes: 3400000, page_count: 56, upload_status: 'completed', processing_stage: 'graph_linked', entity_count: 35, created_at: lastMonth },
    { id: 'doc-006', filename: 'motor_vibration_data.xlsx', original_filename: 'motor_vibration_data.xlsx', file_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', document_category: 'maintenance_record', file_size_bytes: 450000, page_count: null, upload_status: 'processing', processing_stage: 'ocr_complete', entity_count: 0, created_at: now },
    { id: 'doc-007', filename: 'safety_shutdown_procedure.docx', original_filename: 'safety_shutdown_procedure.docx', file_type: 'application/docx', document_category: 'safety_procedure', file_size_bytes: 720000, page_count: 16, upload_status: 'completed', processing_stage: 'graph_linked', entity_count: 22, created_at: lastWeek },
    { id: 'doc-008', filename: 'heat_exchanger_OEM_manual.pdf', original_filename: 'heat_exchanger_OEM_manual.pdf', file_type: 'application/pdf', document_category: 'oem_manual', file_size_bytes: 8900000, page_count: 145, upload_status: 'completed', processing_stage: 'embedded', entity_count: 67, created_at: lastMonth },
  ],
  total: 8,
  page: 1,
  limit: 20,
};

export const mockDocumentDetail = {
  id: 'doc-001',
  filename: 'pump_maintenance_SOP.pdf',
  original_filename: 'pump_maintenance_SOP.pdf',
  file_type: 'application/pdf',
  document_category: 'operating_procedure',
  file_size_bytes: 2450000,
  page_count: 24,
  upload_status: 'completed',
  processing_stage: 'graph_linked',
  entity_count: 18,
  created_at: yesterday,
  extracted_text: 'Standard Operating Procedure for Centrifugal Pump Maintenance\n\n1. SCOPE\nThis SOP covers preventive and corrective maintenance procedures for all centrifugal pumps (P-101 through P-108) in Unit 7 of the refinery complex.\n\n2. SAFETY PRECAUTIONS\n- Ensure LOTO (Lock Out Tag Out) procedures are followed\n- Wear appropriate PPE including safety goggles, gloves, and steel-toed boots\n- Verify zero energy state before commencing work\n\n3. PREVENTIVE MAINTENANCE SCHEDULE\n- Daily: Visual inspection, vibration monitoring\n- Weekly: Bearing temperature check, seal inspection\n- Monthly: Oil analysis, alignment verification\n- Quarterly: Complete overhaul per OEM guidelines\n\n4. TROUBLESHOOTING GUIDE\n4.1 Excessive Vibration: Check alignment, bearing condition, impeller balance\n4.2 Low Discharge Pressure: Verify suction conditions, inspect impeller wear\n4.3 Seal Leakage: Replace mechanical seal per manufacturer specifications',
  metadata: { author: 'Rajesh Kumar', department: 'Mechanical Maintenance', revision: '3.2', last_reviewed: '2024-11-15' },
  entities: [
    { id: 'ent-001', entity_type: 'equipment', name: 'P-101', properties: { type: 'pump' } },
    { id: 'ent-002', entity_type: 'equipment', name: 'P-108', properties: { type: 'pump' } },
    { id: 'ent-003', entity_type: 'procedure', name: 'LOTO Procedure', properties: {} },
    { id: 'ent-004', entity_type: 'person', name: 'Rajesh Kumar', properties: { role: 'Author' } },
    { id: 'ent-005', entity_type: 'location', name: 'Unit 7', properties: {} },
    { id: 'ent-006', entity_type: 'parameter', name: 'Vibration Level', properties: { unit: 'mm/s' } },
    { id: 'ent-007', entity_type: 'part', name: 'Mechanical Seal', properties: {} },
    { id: 'ent-008', entity_type: 'maintenance_action', name: 'Oil Analysis', properties: { frequency: 'Monthly' } },
  ],
  linked_equipment: [
    { id: 'eq-001', tag: 'P-101', name: 'Centrifugal Pump Unit 7A', equipment_type: 'pump', criticality: 'critical' },
    { id: 'eq-002', tag: 'P-108', name: 'Centrifugal Pump Unit 7H', equipment_type: 'pump', criticality: 'high' },
  ],
  chunk_count: 12,
};

// ─── Equipment ────────────────────────────────────────────
export const mockEquipment = {
  items: [
    { id: 'eq-001', tag: 'P-101', name: 'Centrifugal Pump 7A', equipment_type: 'pump', description: 'Primary feed pump for Unit 7', location: 'Unit 7, Bay 3', plant: 'Refinery Complex A', unit: 'Unit 7', criticality: 'critical', status: 'operational', manufacturer: 'Sulzer' },
    { id: 'eq-002', tag: 'V-201', name: 'Gate Valve 2A', equipment_type: 'valve', description: 'Main isolation valve', location: 'Unit 2, Section A', plant: 'Refinery Complex A', unit: 'Unit 2', criticality: 'high', status: 'operational', manufacturer: 'Emerson' },
    { id: 'eq-003', tag: 'C-301', name: 'Reciprocating Compressor', equipment_type: 'compressor', description: 'Gas boost compressor', location: 'Unit 3', plant: 'Gas Processing', unit: 'Unit 3', criticality: 'critical', status: 'under_maintenance', manufacturer: 'Atlas Copco' },
    { id: 'eq-004', tag: 'HX-401', name: 'Shell & Tube Exchanger', equipment_type: 'heat_exchanger', description: 'Pre-heater for crude distillation', location: 'Unit 4, Bay 1', plant: 'Refinery Complex A', unit: 'Unit 4', criticality: 'high', status: 'operational', manufacturer: 'Alfa Laval' },
    { id: 'eq-005', tag: 'M-501', name: 'Induction Motor 5A', equipment_type: 'motor', description: 'Drive motor for blower', location: 'Unit 5', plant: 'Utility Block', unit: 'Unit 5', criticality: 'medium', status: 'operational', manufacturer: 'ABB' },
    { id: 'eq-006', tag: 'T-601', name: 'Storage Tank 6A', equipment_type: 'tank', description: 'Raw material storage', location: 'Tank Farm', plant: 'Storage Area', unit: 'Tank Farm', criticality: 'medium', status: 'operational', manufacturer: 'Tata Projects' },
  ],
  total: 6,
  page: 1,
  limit: 20,
};

export const mockEquipmentDetail = {
  ...mockEquipment.items[0],
  model: 'MSD-D 50/200',
  serial_number: 'SLZ-2019-78432',
  installation_date: '2019-06-15',
  specifications: { flow_rate: '450 m³/h', head: '85 m', power: '200 kW', speed: '2980 RPM', material: 'SS 316L' },
  related_documents: mockDocuments.items.slice(0, 3),
  maintenance_records: [
    { id: 'mr-001', date: '2024-10-15', type: 'preventive', description: 'Quarterly overhaul — bearings replaced', status: 'completed', technician: 'Suresh Patel' },
    { id: 'mr-002', date: '2024-07-20', type: 'corrective', description: 'Mechanical seal replacement due to leakage', status: 'completed', technician: 'Amit Shah' },
    { id: 'mr-003', date: '2024-04-10', type: 'predictive', description: 'Vibration analysis — within limits', status: 'completed', technician: 'Rajesh Kumar' },
  ],
  failure_events: [
    { id: 'fe-001', date: '2024-07-18', description: 'Mechanical seal failure causing process fluid leakage', severity: 'high', root_cause: 'Dry running due to suction strainer blockage', downtime_hours: 8 },
    { id: 'fe-002', date: '2023-11-05', description: 'Bearing failure with elevated vibration detected', severity: 'medium', root_cause: 'Lubrication degradation', downtime_hours: 4 },
  ],
  compliance_records: [
    { regulation: 'OISD-154', status: 'compliant', last_assessed: '2024-09-01' },
    { regulation: 'Factory Act Schedule IV', status: 'compliant', last_assessed: '2024-08-15' },
  ],
};

// ─── Knowledge Graph ──────────────────────────────────────
export const mockGraphNodes = [
  { id: 'n-001', entity_type: 'equipment', name: 'P-101', properties: { type: 'pump', unit: 'Unit 7' }, connection_count: 8 },
  { id: 'n-002', entity_type: 'equipment', name: 'V-201', properties: { type: 'valve', unit: 'Unit 2' }, connection_count: 5 },
  { id: 'n-003', entity_type: 'equipment', name: 'C-301', properties: { type: 'compressor', unit: 'Unit 3' }, connection_count: 7 },
  { id: 'n-004', entity_type: 'document', name: 'Pump Maintenance SOP', properties: { category: 'operating_procedure' }, connection_count: 12 },
  { id: 'n-005', entity_type: 'person', name: 'Rajesh Kumar', properties: { role: 'Senior Engineer' }, connection_count: 6 },
  { id: 'n-006', entity_type: 'procedure', name: 'LOTO Procedure', properties: {}, connection_count: 9 },
  { id: 'n-007', entity_type: 'regulation', name: 'OISD-154', properties: { body: 'OISD' }, connection_count: 11 },
  { id: 'n-008', entity_type: 'failure_event', name: 'Seal Failure — P-101', properties: { date: '2024-07-18' }, connection_count: 4 },
  { id: 'n-009', entity_type: 'maintenance_action', name: 'Bearing Replacement', properties: { frequency: 'Quarterly' }, connection_count: 3 },
  { id: 'n-010', entity_type: 'location', name: 'Unit 7', properties: { plant: 'Refinery Complex A' }, connection_count: 15 },
  { id: 'n-011', entity_type: 'parameter', name: 'Vibration Level', properties: { unit: 'mm/s', threshold: 4.5 }, connection_count: 5 },
  { id: 'n-012', entity_type: 'part', name: 'Mechanical Seal', properties: { material: 'SiC/SiC' }, connection_count: 4 },
  { id: 'n-013', entity_type: 'equipment', name: 'HX-401', properties: { type: 'heat_exchanger', unit: 'Unit 4' }, connection_count: 6 },
  { id: 'n-014', entity_type: 'document', name: 'OISD Guidelines 154', properties: { category: 'regulatory' }, connection_count: 8 },
  { id: 'n-015', entity_type: 'equipment', name: 'M-501', properties: { type: 'motor', unit: 'Unit 5' }, connection_count: 4 },
];

export const mockGraphEdges = [
  { id: 'e-001', source_id: 'n-004', target_id: 'n-001', relationship_type: 'REFERENCES', properties: {}, confidence: 0.95 },
  { id: 'e-002', source_id: 'n-005', target_id: 'n-004', relationship_type: 'AUTHORED', properties: {}, confidence: 1.0 },
  { id: 'e-003', source_id: 'n-001', target_id: 'n-006', relationship_type: 'REQUIRES_PROCEDURE', properties: {}, confidence: 0.88 },
  { id: 'e-004', source_id: 'n-001', target_id: 'n-010', relationship_type: 'LOCATED_IN', properties: {}, confidence: 1.0 },
  { id: 'e-005', source_id: 'n-008', target_id: 'n-001', relationship_type: 'AFFECTS', properties: {}, confidence: 0.92 },
  { id: 'e-006', source_id: 'n-009', target_id: 'n-001', relationship_type: 'PERFORMED_ON', properties: {}, confidence: 0.9 },
  { id: 'e-007', source_id: 'n-012', target_id: 'n-001', relationship_type: 'COMPONENT_OF', properties: {}, confidence: 1.0 },
  { id: 'e-008', source_id: 'n-007', target_id: 'n-001', relationship_type: 'REGULATES', properties: {}, confidence: 0.85 },
  { id: 'e-009', source_id: 'n-011', target_id: 'n-001', relationship_type: 'MEASURED_ON', properties: {}, confidence: 0.93 },
  { id: 'e-010', source_id: 'n-014', target_id: 'n-007', relationship_type: 'DEFINES', properties: {}, confidence: 1.0 },
  { id: 'e-011', source_id: 'n-002', target_id: 'n-010', relationship_type: 'LOCATED_IN', properties: {}, confidence: 0.7 },
  { id: 'e-012', source_id: 'n-003', target_id: 'n-010', relationship_type: 'LOCATED_IN', properties: {}, confidence: 0.7 },
  { id: 'e-013', source_id: 'n-013', target_id: 'n-010', relationship_type: 'LOCATED_IN', properties: {}, confidence: 0.7 },
  { id: 'e-014', source_id: 'n-015', target_id: 'n-010', relationship_type: 'LOCATED_IN', properties: {}, confidence: 0.7 },
];

export const mockGraphStats = {
  total_nodes: 247,
  total_edges: 523,
  nodes_by_type: { equipment: 48, document: 65, person: 22, procedure: 31, regulation: 18, failure_event: 15, maintenance_action: 19, location: 12, parameter: 9, part: 8 },
  edges_by_type: { REFERENCES: 124, AUTHORED: 42, REQUIRES_PROCEDURE: 38, LOCATED_IN: 67, AFFECTS: 32, PERFORMED_ON: 55, COMPONENT_OF: 45, REGULATES: 52, MEASURED_ON: 28, DEFINES: 40 },
};

// ─── Chat ─────────────────────────────────────────────────
export const mockChatSessions = [
  { session_id: 'sess-001', title: 'Pump P-101 maintenance query', message_count: 6, last_message_at: now, agent_type: 'maintenance' },
  { session_id: 'sess-002', title: 'OISD-154 compliance check', message_count: 4, last_message_at: yesterday, agent_type: 'compliance' },
  { session_id: 'sess-003', title: 'Compressor failure root cause', message_count: 8, last_message_at: lastWeek, agent_type: 'rca' },
];

export const mockChatResponse = {
  session_id: 'sess-001',
  response: 'Based on the maintenance records and OEM manual for **P-101 (Centrifugal Pump Unit 7A)**, the recommended maintenance schedule includes:\n\n1. **Daily**: Visual inspection, check for leaks, vibration monitoring\n2. **Weekly**: Bearing temperature measurement, mechanical seal inspection\n3. **Monthly**: Oil analysis, alignment verification using laser alignment tool\n4. **Quarterly**: Complete overhaul per Sulzer MSD-D maintenance guide\n\nThe most recent failure event was a **mechanical seal failure** on July 18, 2024, caused by dry running due to suction strainer blockage. After corrective action, the pump has been operating within normal parameters.\n\n> **Recommendation**: Schedule the next quarterly overhaul within 2 weeks, with special attention to the suction strainer condition.',
  agent_type: 'maintenance',
  confidence_score: 0.92,
  citations: [
    { document_id: 'doc-001', document_title: 'Pump Maintenance SOP', chunk_text: 'Quarterly: Complete overhaul per OEM guidelines including bearing replacement, seal inspection, and impeller clearance check.', page_number: 8, relevance_score: 0.95 },
    { document_id: 'doc-008', document_title: 'Heat Exchanger OEM Manual', chunk_text: 'Centrifugal pump MSD-D series requires scheduled maintenance at intervals not exceeding 2000 operating hours.', page_number: 34, relevance_score: 0.82 },
  ],
  related_entities: [
    { id: 'ent-001', entity_type: 'equipment', name: 'P-101', properties: {} },
    { id: 'ent-007', entity_type: 'part', name: 'Mechanical Seal', properties: {} },
  ],
  suggested_followups: [
    'What was the root cause of the last seal failure?',
    'Show me the vibration trend for P-101',
    'Which spare parts should be ordered for the overhaul?',
  ],
  metadata: {},
};

// ─── Search ───────────────────────────────────────────────
export const mockSearchResults = {
  results: [
    { document_id: 'doc-001', chunk_text: 'Standard Operating Procedure for Centrifugal Pump Maintenance covering preventive and corrective maintenance procedures for all centrifugal pumps (P-101 through P-108) in Unit 7.', relevance_score: 0.95, document_title: 'Pump Maintenance SOP', document_category: 'operating_procedure', page_number: 1, highlights: ['centrifugal pump', 'maintenance', 'P-101'], entities: [{ id: 'ent-001', entity_type: 'equipment', name: 'P-101', properties: {} }] },
    { document_id: 'doc-004', chunk_text: 'Compressor C-301 experienced catastrophic bearing failure on November 5, 2023. Root cause analysis identified lubrication degradation as primary contributor.', relevance_score: 0.87, document_title: 'Compressor Failure Report', document_category: 'incident_report', page_number: 3, highlights: ['bearing failure', 'root cause'], entities: [{ id: 'ent-003', entity_type: 'equipment', name: 'C-301', properties: {} }] },
    { document_id: 'doc-005', chunk_text: 'OISD Standard 154 covers requirements for the safe operation of reciprocating gas compressors, centrifugal pumps, and associated instrumentation in petroleum installations.', relevance_score: 0.78, document_title: 'OISD Guidelines 154', document_category: 'regulatory', page_number: 12, highlights: ['centrifugal pumps', 'petroleum installations'], entities: [] },
  ],
  total_results: 3,
  search_time_ms: 142,
};

// ─── Maintenance ──────────────────────────────────────────
export const mockPredictions = [
  { equipment_id: 'eq-001', equipment_tag: 'P-101', prediction_type: 'Bearing Degradation', risk_level: 'high', predicted_failure_mode: 'Bearing wear leading to increased vibration and eventual seizure', confidence: 0.85, reasoning: 'Vibration trend analysis shows 15% increase over last 3 months. Oil analysis indicates metallic particle contamination above threshold.', recommended_action: 'Schedule bearing replacement during next planned shutdown within 30 days', supporting_evidence: [{ document_id: 'doc-001', document_title: 'Pump Maintenance SOP', chunk_text: 'Monthly oil analysis results indicate bearing wear patterns', page_number: 14, relevance_score: 0.88 }], estimated_date: '2025-02-15' },
  { equipment_id: 'eq-003', equipment_tag: 'C-301', prediction_type: 'Valve Wear', risk_level: 'critical', predicted_failure_mode: 'Suction valve plate cracking due to fatigue cycling', confidence: 0.91, reasoning: 'Operating hours since last valve replacement exceed OEM recommended interval by 20%. Historical data shows 3 similar failures across fleet.', recommended_action: 'Immediate valve inspection recommended. Plan replacement within 14 days.', supporting_evidence: [], estimated_date: '2025-01-20' },
  { equipment_id: 'eq-004', equipment_tag: 'HX-401', prediction_type: 'Fouling', risk_level: 'medium', predicted_failure_mode: 'Tube-side fouling reducing heat transfer efficiency', confidence: 0.72, reasoning: 'Pressure drop across tube side has increased 12% over 6 months. Outlet temperature differential narrowing.', recommended_action: 'Schedule chemical cleaning during next turnaround', supporting_evidence: [], estimated_date: '2025-04-01' },
  { equipment_id: 'eq-005', equipment_tag: 'M-501', prediction_type: 'Insulation Degradation', risk_level: 'low', predicted_failure_mode: 'Winding insulation resistance declining', confidence: 0.65, reasoning: 'Megger test values trending down but still above minimum threshold.', recommended_action: 'Monitor during next quarterly test cycle', supporting_evidence: [], estimated_date: '2025-06-01' },
];

export const mockAlerts = [
  { id: 'alert-001', alert_type: 'failure_pattern', severity: 'critical', title: 'Recurring Seal Failure Pattern Detected', description: 'Similar seal failure conditions detected on P-101 that match the July 2024 incident. Suction strainer differential pressure rising.', equipment: { id: 'eq-001', tag: 'P-101', name: 'Centrifugal Pump 7A', equipment_type: 'pump', criticality: 'critical' }, evidence: [], created_at: now },
  { id: 'alert-002', alert_type: 'maintenance_overdue', severity: 'high', title: 'Quarterly Overhaul Overdue — C-301', description: 'Compressor C-301 has exceeded its scheduled quarterly overhaul date by 12 days.', equipment: { id: 'eq-003', tag: 'C-301', name: 'Reciprocating Compressor', equipment_type: 'compressor', criticality: 'critical' }, evidence: [], created_at: yesterday },
  { id: 'alert-003', alert_type: 'compliance_due', severity: 'medium', title: 'PESO Certification Renewal Due', description: 'Pressure vessel certification for V-201 expires in 45 days. Initiate renewal process.', equipment: { id: 'eq-002', tag: 'V-201', name: 'Gate Valve 2A', equipment_type: 'valve', criticality: 'high' }, evidence: [], created_at: lastWeek },
];

// ─── RCA ──────────────────────────────────────────────────
export const mockRCAResponse = {
  root_causes: [
    { cause: 'Suction strainer blockage causing dry running condition', confidence: 0.88, evidence: [{ document_id: 'doc-001', document_title: 'Pump Maintenance SOP', chunk_text: 'Dry running protection must be verified during each startup sequence', page_number: 6, relevance_score: 0.91 }], similar_incidents: [{ id: 'inc-001', description: 'Similar seal failure on P-103 in 2022 due to strainer blockage', date: '2022-03-15', equipment_tag: 'P-103', severity: 'high' }] },
    { cause: 'Improper seal installation during last maintenance', confidence: 0.62, evidence: [], similar_incidents: [] },
    { cause: 'Seal material incompatibility with process fluid at elevated temperature', confidence: 0.45, evidence: [], similar_incidents: [] },
  ],
  recommended_actions: [
    'Install differential pressure indicator on suction strainer with alarm setpoint',
    'Add dry-run protection interlock to pump control logic',
    'Update SOP to include pre-startup strainer check as mandatory step',
    'Review seal material compatibility for current operating conditions',
  ],
  related_equipment_at_risk: [
    { id: 'eq-002', tag: 'P-102', name: 'Centrifugal Pump 7B', equipment_type: 'pump', criticality: 'critical' },
    { id: 'eq-003', tag: 'P-103', name: 'Centrifugal Pump 7C', equipment_type: 'pump', criticality: 'high' },
  ],
};

// ─── Compliance ───────────────────────────────────────────
export const mockComplianceOverview = {
  overall_compliance_score: 0.82,
  by_regulation: [
    { regulation_code: 'OISD-154', regulation_name: 'Fire & Explosion Safety', compliance_score: 0.90, total_requirements: 45, compliant: 41, non_compliant: 2, partial: 2 },
    { regulation_code: 'PESO-2004', regulation_name: 'Pressure Equipment Safety', compliance_score: 0.85, total_requirements: 32, compliant: 27, non_compliant: 1, partial: 4 },
    { regulation_code: 'FACTORY-ACT', regulation_name: 'Factories Act Schedule IV', compliance_score: 0.78, total_requirements: 28, compliant: 22, non_compliant: 3, partial: 3 },
    { regulation_code: 'ENV-NORMS', regulation_name: 'Environmental Compliance', compliance_score: 0.72, total_requirements: 38, compliant: 27, non_compliant: 5, partial: 6 },
  ],
};

export const mockComplianceGaps = [
  { id: 'gap-001', regulation_code: 'OISD-154', regulation_name: 'Fire & Explosion Safety', requirement_text: 'All pressure relief valves shall be tested and certified at intervals not exceeding 24 months', compliance_status: 'non_compliant', gap_description: 'PRV on vessel V-401 has not been tested in 28 months', remediation_action: 'Schedule PRV testing and certification immediately', affected_equipment: [{ id: 'eq-002', tag: 'V-201', name: 'Gate Valve 2A', equipment_type: 'valve', criticality: 'high' }], due_date: '2025-01-31' },
  { id: 'gap-002', regulation_code: 'FACTORY-ACT', regulation_name: 'Factories Act Schedule IV', requirement_text: 'Rotating equipment guards shall be inspected quarterly', compliance_status: 'partially_compliant', gap_description: 'Guard inspection records missing for 2 pumps in Unit 7', remediation_action: 'Complete guard inspection and update records for P-105 and P-107', affected_equipment: [], due_date: '2025-02-15' },
  { id: 'gap-003', regulation_code: 'ENV-NORMS', regulation_name: 'Environmental Compliance', requirement_text: 'Continuous emission monitoring data shall be archived for minimum 5 years', compliance_status: 'non_compliant', gap_description: 'Emission data from 2019 Q1-Q2 not available in digital archive', remediation_action: 'Locate physical records and digitize. Update data retention policy.', affected_equipment: [], due_date: '2025-03-01' },
];

// ─── Analytics ────────────────────────────────────────────
export const mockAnalyticsOverview = {
  total_documents: 847,
  total_entities: 2453,
  total_equipment: 186,
  total_queries: 1289,
  avg_response_time_ms: 340,
  documents_by_category: { maintenance_record: 245, operating_procedure: 132, inspection_report: 178, engineering_drawing: 89, safety_procedure: 67, regulatory: 45, oem_manual: 38, incident_report: 32, work_order: 15, other: 6 },
  entities_by_type: { equipment: 412, document: 847, person: 189, procedure: 234, regulation: 127, failure_event: 156, maintenance_action: 198, location: 98, parameter: 112, part: 80 },
  recent_activity: [
    { type: 'upload', description: 'motor_vibration_data.xlsx uploaded', timestamp: now },
    { type: 'query', description: 'AI query: P-101 maintenance schedule', timestamp: yesterday },
    { type: 'alert', description: 'Critical alert: Seal failure pattern detected', timestamp: yesterday },
    { type: 'compliance', description: 'Compliance assessment completed for OISD-154', timestamp: lastWeek },
    { type: 'upload', description: 'safety_shutdown_procedure.docx uploaded', timestamp: lastWeek },
  ],
};

export const mockTrendData = [
  { date: '2024-07', documents: 45, queries: 120, entities: 180 },
  { date: '2024-08', documents: 62, queries: 145, entities: 240 },
  { date: '2024-09', documents: 78, queries: 167, entities: 310 },
  { date: '2024-10', documents: 95, queries: 198, entities: 385 },
  { date: '2024-11', documents: 112, queries: 234, entities: 460 },
  { date: '2024-12', documents: 128, queries: 278, entities: 520 },
  { date: '2025-01', documents: 147, queries: 310, entities: 590 },
];
