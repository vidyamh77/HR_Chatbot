# Evaluation Report & Benchmark Specifications

This report details the evaluation framework, custom evaluation metrics, and test datasets designed for the HR Agentic Solution (MVP 1).

---

## 1. Evaluation Methodology

The HR Agentic Solution uses a **Quality Flywheel** methodology to verify functional compliance, safety guardrails, and conversation quality. The evaluation suite is designed to run in-process using the official `agents-cli eval` command line.

### LLM-as-a-Judge Pattern
To evaluate conversational responses that do not have exact textual matches, the framework leverages an LLM-as-a-judge model (specified in `tests/eval/response_quality.py`). The judge evaluates responses on:
1.  **Factuality & Policy Grounding**: Ensuring answers are derived exclusively from the retrieved context.
2.  **Citation Completeness**: Ensuring every policy answer includes a source link (e.g., `[Title - Section](Link)`).
3.  **Governance Compliance**: Confirming that prohibited spending is blocked, and transaction rules are strictly respected.

### Scope and Assumptions
To establish a clear testing context, the evaluation framework operates under the following explicit boundary assumptions:
*   **Target Workforce**: 5,000 FTE employees.
*   **Geographic Context**: Singapore (APAC HQ) with Singapore-specific leave laws (e.g. MOM-mandated outpatient sick leave MC deadlines, vacation accruals).
*   **System Boundaries & Integrations**: Direct tool integrations are limited to `WorkWeek` (HCM) and `ServiceImmediately` (ITSM) mock SaaS backend servers.
*   **Workforce Taxonomies**: Users are classified into three distinct roles with isolated access rights: standard `FTE` (Full-Time Employee), `Contractor` (TVC), and `Manager`.

---

## 2. Evaluation Datasets

The test cases are split into two targeted datasets in the `tests/eval/datasets/` directory:

### A. Single-Turn Benchmark (`eval-data.json`)
Consists of 16 single-turn test cases covering five critical functional domains:
*   **Policy Q&A (UC-1.1)**: Validates bereavement/medical/bonding policy retrieval, source citations, and off-topic filtering.
*   **HR Transactions (UC-1.2)**: Validates leave balance checking, phone/address contact updates, and leave request submission constraints.
*   **Role-Based Access Control (RBAC)**: Asserts that employees can only access their own profiles, while managers can fetch direct reports' records.
*   **IT Service Tickets (UC-1.3)**: Tests ticket creation, status checks, and Priority 1 critical incident validation.
*   **Spend Restrictions**: Tests the "Gotcha" categories (asserting that gift cards and adult entertainment are blocked, even if below expense SGD limits).

### B. Multi-Turn Benchmark (`eval-multi-turn.json`)
Consists of conversational turn sequences simulating multi-step employee workflows:
*   **Relocation Sequence**: Simulates an employee checking their relocation allowance caps, updating their address in WorkWeek, and opening an ITSM badging request ticket in sequence.

---

## 3. Configuration & Evaluation Metrics

The evaluation run is controlled via `tests/eval/eval_config.yaml`:

```yaml
metrics_to_run:
  - custom_response_quality

custom_metrics:
  - name: custom_response_quality
    custom_function_file: response_quality.py
  - name: agent_turn_count
    custom_function: |
      def evaluate(instance):
          turns = (instance.get("agent_data") or {}).get("turns", [])
          return {'score': len(turns)}
```

### Metrics Definitions
1.  **`custom_response_quality`**: Evaluates semantic accuracy, policy grounding, and rule compliance (returning a quality score from `0` to `1`).
2.  **`agent_turn_count`**: Evaluates the efficiency of the orchestrator by counting the number of message turns taken to resolve a request.

---

## 4. How to Run Evaluations Locally

To run the evaluations using the `agents-cli` tool:

1.  **Establish Environment Variables**:
    ```bash
    export GEMINI_API_KEY="<your-api-key>"
    ```
2.  **Run Single-Turn Benchmark**:
    ```bash
    agents-cli eval run \
      --config tests/eval/eval_config.yaml \
      --dataset tests/eval/datasets/eval-data.json
    ```
3.  **Run Multi-Turn Benchmark**:
    ```bash
    agents-cli eval run \
      --config tests/eval/eval_config.yaml \
      --dataset tests/eval/datasets/eval-multi-turn.json
    ```

---

## 5. Evaluation Cost & Execution Time Analysis

This section outlines the cost budget, concurrency controls, and backoff throttle policy for running the evaluation suite:

| Parameter | Target / Limit | Details & Configuration |
| :--- | :--- | :--- |
| **Evaluation Cost Target** | `< $5.00 per 100 runs` | Projected actual cost is **~$0.20 per 100 runs** based on Gemini 2.5/3.6 Flash pricing ($0.075/1M input, $0.30/1M output tokens). |
| **Execution Concurrency** | `5 threads max` | To avoid model quota exhaustion, append `--concurrency 5` to the `agents-cli eval run` commands. |
| **Model Timeout & Backoff** | `Exponential backoff` | The SDK client handles HTTP 429 and 503 rate limits with a minimum wait of 2s doubling up to 60s per retry. |
| **Synthetic Data Gen Limit** | `150,000 tokens` | Max token ceiling for synthetic dataset generation and test-case creation. |
| **LLM Judge Cost Cap** | `$0.05 per case` | Budget cap per evaluated test case. Automated safety pre-checks bypass LLM grading and cost $0. |
| **Latency Target** | `< 10.0s average` | Target end-to-end processing response latency for standard execution pipelines. |

### Quota & Throttle Policies (HTTP 429 Mitigation)
To run evaluations without triggering transient API quota errors, configure the following runtime settings:
1.  **Set Concurrency Limit**: Always run the evaluations with the thread-count capped at 5:
    ```bash
    agents-cli eval run --concurrency 5 --config tests/eval/eval_config.yaml --dataset tests/eval/datasets/eval-data.json
    ```
2.  **SDK Backoff & Retries**: Ensure the underlying Python environment uses GenAI client retries by setting the environment variables:
    ```bash
    export GOOGLE_GENAI_MAX_RETRIES=5
    ```

