# Empirical Benchmark Results

**Evaluation Date**: 2026-11-10  
**Hardware Environment**: Local NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM), PyTorch 2.5.1 + CUDA 12.1  
**Cloud API**: NVIDIA NIM API (`nvidia/nemotron-3.5-lightning-30b-a3b`)

---

## 1. Executive Summary

This report documents the live empirical evaluation of the QueryMind Text-to-SQL platform across all three core generation pathways:
1. **NVIDIA Nemotron 3.5 Lightning (30B parameter MoE)** via NVIDIA NIM Cloud API (`temperature: 0.0`, thinking disabled).
2. **Qwen2.5-Coder-3B-Instruct (Few-Shot Prompting)** running locally on CUDA with 3 in-context Spider demonstrations.
3. **Qwen2.5-Coder-3B-Instruct (Supervised LoRA Adapter)** running locally on CUDA with a rank-8 Spider fine-tuned adapter.

The benchmark evaluated 20 hand-verified queries spanning 4 SQLite database schemas scaling from 3 to 12 tables.

---

## 2. Benchmark Scorecard

| Model Architecture | Deployment | SQL Validity | Execution Success | Right Answers (Accuracy) | Average Latency |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **NVIDIA Nemotron 3.5 Lightning** | Cloud API (NIM) | **100.0%** | **95.0%** | **85.0%** (17/20) | **1,173.95 ms** |
| **Qwen2.5-Coder-3B (Few-Shot)** | Local RTX 4060 GPU | **100.0%** | **90.0%** | **85.0%** (17/20) | **3,132.06 ms** |
| **Qwen2.5-Coder-3B (LoRA Adapter)** | Local RTX 4060 GPU | **100.0%** | **90.0%** | **85.0%** (17/20) | **3,690.99 ms** |

---

## 3. Database Complexity Spectrum

| Database File | Tables | Domain & Key Entities |
| :--- | :---: | :--- |
| `veterinary_clinic.db` | 3 | Clinics, veterinarians, pet visits |
| `film_production.db` | 9 | Studios, directors, films, cast, genres, box office, awards |
| `research_grants.db` | 10 | Campuses, professors, grants, publications, allocations, students |
| `maritime_shipping.db` | 12 | Lines, vessels, voyages, containers, crew members, assignments, invoices |

---

## 4. Accuracy by Schema Scale

| Database | Tables | Nemotron | Qwen Few-Shot | Qwen LoRA |
| :--- | :---: | :---: | :---: | :---: |
| `veterinary_clinic.db` | 3 | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) |
| `film_production.db` | 9 | 6/7 (85.7%) | 6/7 (85.7%) | 6/7 (85.7%) |
| `research_grants.db` | 10 | 4/5 (80.0%) | 4/5 (80.0%) | 4/5 (80.0%) |
| `maritime_shipping.db` | 12 | 3/4 (75.0%) | 3/4 (75.0%) | 3/4 (75.0%) |

---

## 5. Detailed Breakdown of Edge Cases & Misses

### Case 1: `film_01` (Database: `film_production`, 9 tables)
* **Question**: *"For each film released after 2018 that won at least one award, list the film title, director last name, studio name, and total worldwide gross."*
* **Ground Truth SQL**:
  ```sql
  SELECT f.title, d.last_name, s.studio_name, 
         (SELECT SUM(b.gross_usd) FROM box_office b WHERE b.film_id = f.film_id) 
  FROM films f 
  JOIN directors d ON f.director_id = d.director_id 
  JOIN studios s ON d.studio_id = s.studio_id 
  WHERE f.release_year > 2018 AND f.film_id IN (SELECT film_id FROM awards WHERE won = 1);
  ```
* **Model Behaviors**:
  * **Nemotron**: Generated a multi-table `JOIN awards a ON f.film_id = a.film_id` with `HAVING COUNT(a.award_id) >= 1` and `SUM(b.gross_usd)`. Because awards joined across multiple rows, the Cartesian product multiplied the box office gross sum.
  * **Qwen (Few-Shot & LoRA)**: Omitted the award filter check entirely (`WHERE release_year > 2018 AND gross_usd > 0`).

---

### Case 2: `grant_02` (Database: `research_grants`, 10 tables)
* **Question**: *"List professors who are the principal investigator on active grants totaling more than 500000 and who also authored a publication with more than 100 citations. Include each professor's total active grant amount."*
* **Ground Truth SQL**:
  ```sql
  SELECT p.first_name, p.last_name, SUM(g.amount) 
  FROM professors p 
  JOIN grants g ON p.prof_id = g.pi_prof_id 
  WHERE g.status = 'Active' 
    AND p.prof_id IN (
      SELECT pa.prof_id FROM publication_authors pa 
      JOIN publications pub ON pa.pub_id = pub.pub_id 
      WHERE pub.citation_count > 100
    ) 
  GROUP BY p.prof_id, p.first_name, p.last_name 
  HAVING SUM(g.amount) > 500000;
  ```
* **Model Behaviors**:
  * **Nemotron**: Included `p.prof_id` in the `SELECT` list (`SELECT p.prof_id, p.first_name, p.last_name, SUM(g.amount)`), causing a column count / header mismatch against the gold result.
  * **Qwen (Few-Shot & LoRA)**: Joined on `T3` incorrectly without qualifying the grant amount relation, throwing `no such column: T3.amount`.

---

### Case 3: `ship_05` & `ship_03` (Database: `maritime_shipping`, 12 tables)
* **Question (`ship_05` - Nemotron Miss)**: *"What is the total container weight in kilograms for bookings made by Acme Retail?"*
  * **Nemotron**: Formulated a subquery with `WHERE customer_id = (SELECT customer_id FROM customers WHERE company_name LIKE '%Acme Retail%')` and joined `containers` with `SUM(gross_weight_kg)`. The schema column is named `weight_kg`, causing `no such column: c.gross_weight_kg`.
  * **Qwen (Few-Shot & LoRA)**: Correctly referenced `weight_kg` and passed with accurate result rows.
* **Question (`ship_03` - Qwen Miss)**: *"Which crew members assigned only through vessels with capacity above 10000 TEU worked more total contract days than the average contract length of all crew assignments, and what is each member's total contract days?"*
  * **Nemotron**: Successfully bridged `crew_members` -> `crew_assignments` -> `voyages` -> `vessels` and correctly matched the gold answer.
  * **Qwen (Few-Shot & LoRA)**: Attempted to join `crew_assignments` directly onto `vessels` (`ON T2.voyage_id = T4.voyage_id`), throwing `no such column: T4.voyage_id` because `vessels` does not contain `voyage_id` (requires intermediate `voyages` table).

---

## 6. How to Reproduce

Run the full automated benchmark from PowerShell:

```powershell
.venv\Scripts\python.exe scripts/run_scale_complexity_benchmark.py --models nemotron,qwen_few_shot,qwen_lora --suite scored
```

Outputs are written to:
- Primary report: [`outputs/evaluation/scale_complexity_latest.json`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/outputs/evaluation/scale_complexity_latest.json)
- Dashboard cache: [`outputs/evaluation/latest_evaluation_summary.json`](file:///c:/Users/pavan/OneDrive/Desktop/llm_new/outputs/evaluation/latest_evaluation_summary.json)
