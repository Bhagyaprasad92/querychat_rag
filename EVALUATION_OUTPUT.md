# QueryChat RAG - Complete Execution Output & Verification Log

**Generated On:** October 29, 2026  
**Document Ingested:** `sample_document.pdf` (Project Nova: Autonomous Aerial Logistics System)  
**Model In Use:** `llama3.2` via local Ollama  

---

## 1. Document Ingestion & Chunking
- **Filename:** `sample_document.pdf`
- **Total Pages:** 1
- **Total Searchable Chunks:** 3
- **Ingestion Duration:** 0.04 seconds

### Chunk Details
- **Chunk 1 (Page 1):**
  > *"Project Nova: Autonomous Aerial Logistics System Author: Advanced Systems Engineering Group | Published: November 15, 2026. 1. Executive Summary: Project Nova is a next-generation autonomous drone network designed for rapid, energy-efficient medical supply delivery across remote regions..."*
- **Chunk 2 (Page 1):**
  > *"2. Key Milestones and Important Dates: January 10, 2026: Project inception... May 4, 2026: First indoor simulation... September 18, 2026: Phase 1 outdoor autonomous test... December 1, 2026: Commercial pilot deployment... March 30, 2027: International compliance certification. 3. Core Technical Advantages..."*
- **Chunk 3 (Page 1):**
  > *"4. Operational Budget and Resource Allocation: The total approved capital budget for Project Nova is $14.8 million USD spanning FY2026 through FY2028. Of this budget, $6.2 million is allocated directly to hardware prototyping, $4.5 million to software, $2.1 million to regulatory safety, and $2.0 million contingency reserve..."*

---

## 2. Test Queries & Model Output

### Query 1: Key Milestones and Dates
**Prompt:** *"What are the key milestones and important dates mentioned?"*  
**Retrieved Context Chunks:** 2 chunks (Page 1, TF-IDF Scores: 0.1777 and 0.0178)  
**Model Output:**
```text
The key milestones and important dates mentioned in the document are:

1. January 10, 2026: Project inception and preliminary architectural sign-off.
2. May 4, 2026: First successful indoor tethered flight simulation in Munich.
3. September 18, 2026: Phase 1 outdoor autonomous navigation test over 50 km.
4. December 1, 2026: Scheduled commercial pilot deployment in the Bavarian Alps.
5. March 30, 2027: Target completion date for international regulatory compliance certification.

These milestones and dates are mentioned on page 1 of the document.
```

---

### Query 2: Core Technical Advantages
**Prompt:** *"List the core technical advantages of Project Nova."*  
**Retrieved Context Chunks:** 3 chunks (Page 1, Top TF-IDF Score: 0.2697)  
**Model Output:**
```text
According to the document, the core technical advantages of Project Nova are:

1. Hybrid Solar-Hydrogen Propulsion: Delivers up to 6 hours of continuous flight with zero carbon emissions.
2. Fault-Tolerant Edge AI: On-board neural navigation enables obstacle avoidance in GPS-denied environments without remote pilot latency.
3. Hermetic Climate-Controlled Cargo Pod: Maintains vaccines and sensitive medical biologics between 2°C and 8°C throughout transit.
```

---

### Query 3: Budget & Financial Allocation
**Prompt:** *"What is the approved budget and how is it allocated?"*  
**Retrieved Context Chunks:** 2 chunks (Page 1, Top TF-IDF Score: 0.1982)  
**Model Output:**
```text
According to the document, the total approved capital budget for Project Nova is $14.8 million USD spanning FY2026 through FY2028.

The budget is allocated as follows:
- Hardware prototyping: $6.2 million
- Software and autonomous navigation algorithms: $4.5 million
- Regulatory safety certifications: $2.1 million
- Contingency reserve: $2.0 million
```

---

### Query 4: Negative Constraint / Grounding Test
**Prompt:** *"Does the document mention any quantum computing hardware? If not, clearly state that it does not."*  
**Model Output:**
```text
The document does not mention any quantum computing hardware.
```

---

### Query 5: Comparison Mode (RAG vs Baseline Without Retrieval)
**Prompt:** *"Summarize what Project Nova is, its primary goal, and its advantages."*  

```text
================================================================================
RAG ANSWER (retrieval + context)
================================================================================
Based on the provided context, here is a summary of Project Nova:

Project Nova is a next-generation autonomous drone network designed for rapid,
energy-efficient medical supply delivery across remote regions.

The primary goal of Project Nova is to reduce critical supply transit times by up to
75% compared to ground transportation, especially in mountainous or flood-prone terrain.

The project introduces three key advantages over conventional unmanned aerial vehicles:
1. Hybrid Solar-Hydrogen Propulsion: Delivers up to 6 hours of continuous flight with zero carbon emissions.
2. Fault-Tolerant Edge AI: On-board neural navigation enables obstacle avoidance in GPS-denied environments without remote pilot latency.
3. Hermetic Climate-Controlled Cargo Pod: Maintains vaccines and sensitive medical biologics between 2°C and 8°C throughout transit.

================================================================================
BASELINE ANSWER (without retrieval)
================================================================================
Project Nova is a proposed NASA mission to return humans to the Moon by 2025 and
establish a sustainable presence on the lunar surface. The primary goal of Project
Nova is to send the first woman and the next man to the Moon's south pole, with the
aim of conducting scientific research, testing technologies for future human missions
to Mars, and demonstrating the capability to sustain human life on the lunar surface...
```

