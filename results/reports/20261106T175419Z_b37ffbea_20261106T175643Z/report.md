# LLM Stability Lab Research Report

Generated at: 2026-11-06T17:56:43.742262+00:00

This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same task are not independent reasoning problems; results describe these prompts and this backend only.

## Task-level results

|   experiment_id | task_id         | experiment_name             |   sample_count |   evaluated_count |   failure_count |   accuracy |   distinct_raw_outputs |   distinct_normalized_answers | most_frequent_answer   |   most_frequent_answer_count |   format_violation_rate |   raw_response_length_std |   latency_p50_seconds |   latency_p90_seconds |
|-----------------|-----------------|-----------------------------|----------------|-------------------|-----------------|------------|------------------------|-------------------------------|------------------------|------------------------------|-------------------------|---------------------------|-----------------------|-----------------------|
|              06 | task_02_logic   | Noise Length x Answer Order |             30 |                30 |               0 |   0.966667 |                      3 |                             2 | mixture                |                           29 |                       0 |                         0 |              3.28705  |               5.28324 |
|              06 | task_03_traffic | Noise Length x Answer Order |             30 |                30 |               0 |   1        |                      3 |                             1 | green                  |                           30 |                       0 |                         0 |              0.603335 |               1.76135 |

## Paired perturbation results

No matched perturbation comparisons are available.


## Noise and answer-order interaction

No complete matched factorial blocks are available.


## Selected option by correct-answer position

No valid multiple-choice selections are available.


## Noise length and errors

| task_id         |   noise_target_tokens |   noise_tokens | noise_position_planned       | answer_order   |   requests |   evaluated |   incorrect |   format_violations |   truncated |   failed_requests |   error_rate |
|-----------------|-----------------------|----------------|------------------------------|----------------|------------|-------------|-------------|---------------------|-------------|-------------------|--------------|
| task_02_logic   |                     0 |              0 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                     0 |              0 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                     0 |              0 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                     0 |              0 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                     0 |              0 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                     0 |              0 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                   256 |            256 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  1024 |           1024 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  4096 |           4096 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  8192 |           8192 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  8192 |           8192 | after_question               | shuffled       |          1 |           1 |           1 |                   0 |           0 |                 0 |            1 |
| task_02_logic   |                  8192 |           8192 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  8192 |           8192 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  8192 |           8192 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_02_logic   |                  8192 |           8192 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                     0 |              0 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                   256 |            256 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  1024 |           1024 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  4096 |           4096 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | after_question               | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | after_question               | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | before_task                  | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | before_task                  | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | between_description_question | original       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |
| task_03_traffic |                  8192 |           8192 | between_description_question | shuffled       |          1 |           1 |           0 |                   0 |           0 |                 0 |            0 |

## Uncertainty

Task-cluster bootstrap confidence intervals are omitted because this run does not contain at least ten independent task clusters. Repeated calls are not counted as independent tasks.

## Limitations

- This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same task are not independent reasoning problems; results describe these prompts and this backend only.
- An accepted request does not prove the backend applied every requested setting.
