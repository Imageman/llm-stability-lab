# LLM Stability Lab Research Report

Generated at: 2026-11-07T10:52:49.562193+00:00

This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same task are not independent reasoning problems; results describe these prompts and this backend only.

## Task-level results

|   experiment_id | task_id         | experiment_name                  |   sample_count |   evaluated_count |   failure_count |   accuracy |   distinct_raw_outputs |   distinct_normalized_answers | most_frequent_answer   |   most_frequent_answer_count |   format_violation_rate |   raw_response_length_std |   latency_p50_seconds |   latency_p90_seconds |
|-----------------|-----------------|----------------------------------|----------------|-------------------|-----------------|------------|------------------------|-------------------------------|------------------------|------------------------------|-------------------------|---------------------------|-----------------------|-----------------------|
|              01 | task_01_math    | Determinism                      |            100 |               100 |               0 |          1 |                      1 |                             1 | 66                     |                          100 |                       0 |                         0 |               5.32873 |               5.47266 |
|              01 | task_02_logic   | Determinism                      |            100 |               100 |               0 |          1 |                      1 |                             1 | mixture                |                          100 |                       0 |                         0 |              16.499   |              17.2799  |
|              01 | task_03_traffic | Determinism                      |            100 |               100 |               0 |          1 |                      1 |                             1 | green                  |                          100 |                       0 |                         0 |               4.27985 |               4.39516 |
|              02 | task_01_math    | Position Sensitivity             |             10 |                 9 |               1 |          1 |                      1 |                             1 | 66                     |                            9 |                       0 |                         0 |               5.58589 |               5.97527 |
|              02 | task_02_logic   | Position Sensitivity             |             10 |                10 |               0 |          1 |                      1 |                             1 | mixture                |                           10 |                       0 |                         0 |              16.3411  |              17.9635  |
|              02 | task_03_traffic | Position Sensitivity             |             10 |                10 |               0 |          1 |                      1 |                             1 | green                  |                           10 |                       0 |                         0 |               5.31487 |               7.32254 |
|              03 | task_01_math    | Reasoning Stability              |             11 |                10 |               1 |          1 |                      1 |                             1 | 66                     |                           10 |                       0 |                         0 |               5.63361 |               5.99854 |
|              03 | task_02_logic   | Reasoning Stability              |             11 |                11 |               0 |          1 |                      1 |                             1 | mixture                |                           11 |                       0 |                         0 |              16.4916  |              19.1692  |
|              03 | task_03_traffic | Reasoning Stability              |             11 |                11 |               0 |          1 |                      1 |                             1 | green                  |                           11 |                       0 |                         0 |               5.08889 |               6.01144 |
|              04 | task_02_logic   | Answer Order Sensitivity         |             24 |                24 |               0 |          1 |                      4 |                             1 | mixture                |                           24 |                       0 |                         0 |              15.4125  |              19.6806  |
|              04 | task_03_traffic | Answer Order Sensitivity         |             90 |                90 |               0 |          1 |                      9 |                             1 | green                  |                           90 |                       0 |                         0 |               4.49355 |               6.6337  |
|              05 | task_02_logic   | Noise x Answer Order Interaction |             72 |                72 |               0 |          1 |                      4 |                             1 | mixture                |                           72 |                       0 |                         0 |              14.3632  |              19.0515  |
|              05 | task_03_traffic | Noise x Answer Order Interaction |             72 |                72 |               0 |          1 |                      9 |                             1 | green                  |                           72 |                       0 |                         0 |               4.43058 |               6.3553  |

## Paired perturbation results

|   experiment_id | task_id         | condition_type   | condition                    |   matched_count |   answer_flip_rate |   correct_to_wrong_rate |   accuracy_degradation |
|-----------------|-----------------|------------------|------------------------------|-----------------|--------------------|-------------------------|------------------------|
|              02 | task_01_math    | noise_position   | after_question               |               2 |                  0 |                       0 |                      0 |
|              02 | task_01_math    | noise_position   | before_task                  |               3 |                  0 |                       0 |                      0 |
|              02 | task_01_math    | noise_position   | between_description_question |               3 |                  0 |                       0 |                      0 |
|              02 | task_02_logic   | noise_position   | after_question               |               3 |                  0 |                       0 |                      0 |
|              02 | task_02_logic   | noise_position   | before_task                  |               3 |                  0 |                       0 |                      0 |
|              02 | task_02_logic   | noise_position   | between_description_question |               3 |                  0 |                       0 |                      0 |
|              02 | task_03_traffic | noise_position   | after_question               |               3 |                  0 |                       0 |                      0 |
|              02 | task_03_traffic | noise_position   | before_task                  |               3 |                  0 |                       0 |                      0 |
|              02 | task_03_traffic | noise_position   | between_description_question |               3 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | noise_position   | after_question               |               8 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | quantity_16                  |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | quantity_4                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | quantity_8                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | sentence_1                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | sentence_2                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | sentence_3                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | wording_neutral              |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | words_1                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_01_math    | perturbation_id  | words_2                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | noise_position   | after_question               |               9 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | quantity_16                  |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | quantity_4                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | quantity_8                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | sentence_1                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | sentence_2                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | sentence_3                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | wording_neutral              |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | words_1                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | words_2                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_02_logic   | perturbation_id  | words_3                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | noise_position   | after_question               |               9 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | quantity_16                  |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | quantity_4                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | quantity_8                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | sentence_1                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | sentence_2                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | sentence_3                   |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | wording_neutral              |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | words_1                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | words_2                      |               1 |                  0 |                       0 |                      0 |
|              03 | task_03_traffic | perturbation_id  | words_3                      |               1 |                  0 |                       0 |                      0 |

## Noise and answer-order interaction

| task_id         |   matched_blocks |   accuracy_interaction |
|-----------------|------------------|------------------------|
| task_02_logic   |               18 |                      0 |
| task_03_traffic |               18 |                      0 |

## Selected option by correct-answer position

| task_id         |   correct_numeric_answer |   selected_numeric_option |   selection_count |
|-----------------|--------------------------|---------------------------|-------------------|
| task_02_logic   |                        1 |                         1 |                 6 |
| task_02_logic   |                        2 |                         2 |                 6 |
| task_02_logic   |                        3 |                         3 |                 6 |
| task_02_logic   |                        4 |                         4 |                 6 |
| task_03_traffic |                        1 |                         1 |                10 |
| task_03_traffic |                        2 |                         2 |                10 |
| task_03_traffic |                        3 |                         3 |                10 |
| task_03_traffic |                        4 |                         4 |                10 |
| task_03_traffic |                        5 |                         5 |                10 |
| task_03_traffic |                        6 |                         6 |                10 |
| task_03_traffic |                        7 |                         7 |                10 |
| task_03_traffic |                        8 |                         8 |                10 |
| task_03_traffic |                        9 |                         9 |                10 |

## Uncertainty

Task-cluster bootstrap confidence intervals are omitted because this run does not contain at least ten independent task clusters. Repeated calls are not counted as independent tasks.

## Limitations

- This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same task are not independent reasoning problems; results describe these prompts and this backend only.
- An accepted request does not prove the backend applied every requested setting.
