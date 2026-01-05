# EGOEJO – UN & Foundations Institutional Pack

**Version** : 1.0  
**Date** : 2025-01-05  
**Status** : Official Document  
**Target Audience** : International Organizations (UN, UNESCO), Foundations, Public Institutions  
**Language** : English  
**Pages** : 15-20  
**Style** : Technocratic, SDG-oriented, no New Age or spiritual vocabulary

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution Architecture](#3-solution-architecture)
4. [Governance Framework](#4-governance-framework)
5. [Legal Trajectory](#5-legal-trajectory)
6. [Alignment with SDGs](#6-alignment-with-sustainable-development-goals)
7. [Annexes](#7-annexes)

---

## 1. Executive Summary

**EGOEJO** is a digital subsistence infrastructure designed to support local regenerative programs while preserving community autonomy from financial markets.

### Institutional Positioning

EGOEJO operates as a **digital subsistence infrastructure** enabling:

- **Discovery and participation** in local regenerative programs (shelters, food gardens, knowledge-sharing workshops, research-action residencies)
- **Transparent fund collection** with full traceability (100% of net donations after platform fees allocated to programs)
- **Recognition of citizen engagement** via an internal non-financial and non-monetary system
- **Protection against capture** through enforceable technical mechanisms encoded in source code

### Contribution to Sustainable Development Goals (SDGs)

EGOEJO directly contributes to the following SDGs:

- **SDG 11** (Sustainable Cities and Communities): Facilitation of local regenerative projects
- **SDG 15** (Life on Land): Support for regeneration of living systems
- **SDG 17** (Partnerships for the Goals): Infrastructure for commons governance
- **SDG 2** (Zero Hunger): Support for food gardens and local food systems

### Measurable Impact

- **Short term (12 months)**: 50-100 local programs referenced, 500-1000 active users, €50,000-100,000 collected (net after platform fees)
- **Medium term (3 years)**: Network of 200-500 programs, 5,000-10,000 users, €500,000-1,000,000 collected (net after platform fees)
- **Long term (5-10 years)**: Replicable model, adoption by third-party projects, measurable impact on regeneration of living systems

---

## 2. Problem Statement

### Value Extraction and Dependence on Financial Markets

Local regenerative programs face three structural obstacles:

#### 2.1. Value Extraction by Platforms

Existing digital platforms apply high commissions (15-30%) that reduce the real impact of donations. This value extraction limits programs' capacity to operate autonomously.

#### 2.2. Dependence on Financial Markets

Traditional funding mechanisms (grants, investments) create structural dependence on economic cycles and political priorities, compromising program sustainability.

#### 2.3. Absence of Recognition for Relational Engagement

Citizen engagement (volunteer participation, knowledge transmission, care for living systems) is not recognized or valued by existing measurement systems, reducing participation incentives.

### Observed Consequences

- **Fragmentation**: Isolated projects, coordination difficulties
- **Financial instability**: Dependence on ad-hoc grants
- **Devaluation of care**: Relational engagement unrecognized
- **Institutional capture**: Dependence on funders

---

## 3. Solution Architecture

### 3.1. Protected Dual Structure

EGOEJO operates according to a **strictly separated dual structure**:

#### Instrumental Structure (EUR)

- **Function**: Funding of infrastructure and operations
- **Unit**: Euro (real currency)
- **Usage**: Donations, fund collection, payments
- **Management**: Stripe (secure payment, PCI-DSS compliance)
- **Allocation**: 100% of net donations (after platform fees) allocated to programs

#### Relational Structure (SAKA)

- **Function**: Recognition of relational engagement and care
- **Unit**: SAKA (internal engagement unit, non-financial, non-monetary)
- **Usage**: Project participation, voting, governance, symbolic support
- **Characteristics**:
  - Non-convertible to EUR (enforceable technical separation)
  - Mandatory cycle: seeding → usage → composting → redistribution
  - Anti-accumulation: automatic composting mechanism

### 3.2. Enforceable Technical Separation

The separation between structures is **encoded in source code** and **automatically tested continuously**:

- **Blocking tests**: Test suite verifying absence of SAKA ↔ EUR conversion
- **Protective CI/CD**: Any violation automatically blocks deployments
- **Public verification**: Endpoint `/api/public/egoejo-constitution.json` exposing real-time compliance status

### 3.3. Financial Transparency

- **100% of net donations** (after platform fees) allocated to programs
- **Transparent fees**: Platform fees explicitly mentioned (Stripe: ~3%, management fees: to be defined)
- **Full traceability**: Every euro is traceable from user to program

---

## 4. Governance Framework

### 4.1. Enforceable Constitution

EGOEJO governance is encoded in an **enforceable technical Constitution**:

#### Constitutional Principles

1. **SAKA/EUR Separation**: No conversion possible, blocking automatic tests
2. **Anti-Accumulation**: Mandatory composting of inactive SAKA
3. **Transparency**: 100% of net donations allocated to programs
4. **Non-Capture**: Technical mechanisms preventing capture by private interests

#### Enforceability Mechanism

- **Encoding in source code**: Constitutional principles translated into technical rules
- **Blocking automatic tests**: Continuous verification of compliance
- **Protective CI/CD**: Deployment blocked in case of violation
- **Public compliance badge**: Compliance status publicly exposed (`/api/public/egoejo-constitution.json`)

### 4.2. Non-Derogation Mechanism

The non-derogation system guarantees automatic detection and notification of any violation of constitutional principles:

- **Automatic triggers**: Real-time detection of violations (bypass, massive modification, inconsistency)
- **Multi-channel notification**: Email + Webhook (optional) for critical alerts
- **Traceability**: Automatic recording in `CriticalAlertEvent` for audit
- **Auditability**: Monthly export of alerts via management command `alerts_report`

### 4.3. Organizational Governance

- **Board of directors**: Strategic decisions, validation of critical modifications
- **Mission committee**: Monitoring compliance with constitutional principles
- **Mandatory review**: Any critical modification requires validation
- **Continuous training**: Team trained in constitutional principles

---

## 5. Legal Trajectory

### 5.1. Prospective Legal Trajectory

EGOEJO follows a progressive legal trajectory enabling adapted institutional evolution:

#### Phase 1: Association (Current)

- **Status**: Association loi 1901 (or equivalent depending on jurisdiction)
- **Advantages**: Administrative simplicity, operational flexibility
- **Limitations**: Limited funding capacity, dependence on grants

#### Phase 2: Endowment Fund (Medium term)

- **Status**: Fonds de dotation (France) or equivalent (non-public utility foundation)
- **Advantages**: Capacity to receive donations, patrimonial management, sustainability
- **Conditions**: Initial capital, structured governance, regulatory compliance

#### Phase 3: Hosted Foundation (Long term)

- **Status**: Hosted foundation under the aegis of a recognized public utility foundation
- **Advantages**: Maximum funding capacity, institutional credibility, tax benefits
- **Conditions**: Partnership with recognized foundation, compliance with aegis requirements

### 5.2. Legal Qualification of SAKA

**SAKA** (internal engagement unit) is subject to explicit legal qualification:

- **Internal non-monetary accounting unit**: Exclusively intended for measuring relational engagement
- **Non-financial fungibility**: Neither electronic money, nor digital asset (PSAN), nor financial instrument
- **Non-transferability**: Non-transferable between third parties outside protocol mechanisms (donation, vote, redistribution)

**Objective**: Avoid any erroneous interpretation as crypto-asset, financial token, or financial instrument by regulators.

### 5.3. Regulatory Compliance

- **Financial compliance**: SAKA/EUR separation, financial transparency, PCI-DSS compliance (Stripe)
- **Data compliance (GDPR)**: Explicit consent, right to erasure, data export, data security
- **Advertising compliance**: No financial promises, fee transparency, editorial compliance

---

## 6. Alignment with Sustainable Development Goals

### Direct Contribution to SDGs

#### SDG 11: Sustainable Cities and Communities

- **Target 11.3**: Inclusive and sustainable urbanization
- **EGOEJO Contribution**: Facilitation of local regenerative projects (shelters, food gardens, knowledge-sharing workshops)

#### SDG 15: Life on Land

- **Target 15.1**: Conservation and restoration of ecosystems
- **EGOEJO Contribution**: Support for regeneration of living systems via local projects

#### SDG 17: Partnerships for the Goals

- **Target 17.16**: Strengthening the Global Partnership for Sustainable Development
- **EGOEJO Contribution**: Infrastructure for commons governance, replicable model

#### SDG 2: Zero Hunger

- **Target 2.4**: Sustainable food production systems
- **EGOEJO Contribution**: Support for food gardens and local food systems

### Contribution Indicators

- **Number of referenced regenerative programs**: Target 50-100 (12 months), 200-500 (3 years)
- **Collected amounts (net)**: Target €50,000-100,000 (12 months), €500,000-1,000,000 (3 years)
- **Active users**: Target 500-1000 (12 months), 5,000-10,000 (3 years)

---

## 7. Annexes

### Annex A: Proof of Governance (Public Compliance Badge)

#### Public Verification Endpoint

**URL**: `https://egoejo.org/api/public/egoejo-constitution.json`

**Response Format**:
```json
{
  "status": "compliant",
  "version": "1.0.0",
  "last_check": "2025-01-03T10:00:00Z",
  "checks": {
    "saka_separation": true,
    "anti_accumulation": true,
    "no_monetary_symbols": true,
    "editorial_compliance": true
  },
  "proof_hash": "a1b2c3d4e5f6g7h8"
}
```

#### Dynamic SVG Badge

**URL**: `https://egoejo.org/api/public/egoejo-constitution.svg`

**Visual States**:
- **Green**: Compliant
- **Red**: Non-compliant
- **Orange**: Unknown status

**Security**: The badge never returns "compliant" if:
- The compliance report is missing
- The HMAC-SHA256 signature is invalid
- The report is older than 24 hours

#### Automatic Generation

The compliance report is automatically generated by CI/CD after all tests pass:
- **Workflow**: `.github/workflows/audit-global.yml`
- **Script**: `scripts/generate_compliance_report.py`
- **Signature**: HMAC-SHA256 with secret key (`COMPLIANCE_SIGNATURE_SECRET`)

### Annex B: Anti-Capture Clause

#### Anti-Capture Principles

The EGOEJO Constitution includes technical mechanisms preventing capture by private interests:

1. **SAKA/EUR Separation**: No conversion possible, preventing SAKA monetization
2. **Anti-Accumulation**: Mandatory composting, preventing passive accumulation
3. **Blocking tests**: Any violation automatically blocks deployments
4. **Transparency**: 100% of net donations allocated to programs, transparent fees

#### Technical Mechanisms

- **Open source code**: Verification possible by third parties
- **Automatic tests**: Continuous verification of compliance
- **Public badge**: Compliance status publicly exposed
- **Audit logs**: Full traceability of critical actions

#### Protection Against Capture

- **No SAKA ↔ EUR conversion**: Prevents SAKA speculation
- **Mandatory composting**: Prevents passive accumulation
- **Financial transparency**: Prevents hidden value extraction
- **Enforceable governance**: Prevents unilateral modification of principles

### Annex C: Technical References

#### Public Endpoints

- `/api/public/egoejo-constitution.json`: Constitutional compliance status
- `/api/public/egoejo-constitution.svg`: SVG compliance badge
- `/api/compliance/integrity/saka/`: SAKA integrity verification (admin)

#### Management Commands

- `python manage.py alerts_report --month YYYY-MM`: Monthly report of critical alerts

#### Documentation

- `docs/security/ALERTING_EMAIL.md`: Email alerting system
- `docs/security/ALERTING_WEBHOOK.md`: Webhook alerting system
- `docs/observability/ALERTS_METRICS.md`: Metrics and observability
- `docs/institutionnel/PROCEDURES_AUDIT_EXTERNE.md`: External audit procedures

---

**Document generated on**: 2025-01-05  
**Version**: 1.0  
**Status**: Official Document  
**Contact**: [To be completed]  
**Structure**: Ghisi Institutional (Executive Summary, Problem, Solution, Governance, Legal Trajectory, Annexes)

