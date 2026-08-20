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
