# LLM Stability Lab Research Report

Generated at: 2026-11-06T20:25:01.374601+00:00

This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same task are not independent reasoning problems; results describe these prompts and this backend only.

## Task-level results

|   experiment_id | task_id         | experiment_name                  |   sample_count |   evaluated_count |   failure_count |   accuracy |   distinct_raw_outputs |   distinct_normalized_answers | most_frequent_answer   |   most_frequent_answer_count |   format_violation_rate |   raw_response_length_std |   latency_p50_seconds |   latency_p90_seconds |
|-----------------|-----------------|----------------------------------|----------------|-------------------|-----------------|------------|------------------------|-------------------------------|------------------------|------------------------------|-------------------------|---------------------------|-----------------------|-----------------------|
|              01 | task_01_math    | Determinism                      |            100 |               100 |               0 |   0        |                      1 |                             1 | 79                     |                          100 |                       0 |                         0 |             0.123431  |             0.126025  |
|              01 | task_02_logic   | Determinism                      |            100 |               100 |               0 |   1        |                      1 |                             1 | mixture                |                          100 |                       0 |                         0 |             0.0958564 |             0.0984773 |
|              01 | task_03_traffic | Determinism                      |            100 |               100 |               0 |   1        |                      1 |                             1 | green                  |                          100 |                       0 |                         0 |             0.0957742 |             0.098806  |
|              02 | task_01_math    | Position Sensitivity             |             10 |                10 |               0 |   0        |                      4 |                             4 | 59                     |                            3 |                       0 |                         0 |             0.195041  |             0.221855  |
|              02 | task_02_logic   | Position Sensitivity             |             10 |                10 |               0 |   1        |                      1 |                             1 | mixture                |                           10 |                       0 |                         0 |             0.204649  |             0.206139  |
|              02 | task_03_traffic | Position Sensitivity             |             10 |                10 |               0 |   1        |                      1 |                             1 | green                  |                           10 |                       0 |                         0 |             0.181262  |             0.192138  |
|              03 | task_01_math    | Reasoning Stability              |             11 |                11 |               0 |   0        |                      6 |                             6 | 73                     |                            4 |                       0 |                         0 |             0.172921  |             0.175404  |
|              03 | task_02_logic   | Reasoning Stability              |             11 |                11 |               0 |   0.818182 |                      2 |                             2 | mixture                |                            9 |                       0 |                         0 |             0.164684  |             0.185436  |
|              03 | task_03_traffic | Reasoning Stability              |             11 |                11 |               0 |   1        |                      1 |                             1 | green                  |                           11 |                       0 |                         0 |             0.151707  |             0.185579  |
|              04 | task_02_logic   | Answer Order Sensitivity         |             24 |                24 |               0 |   0.333333 |                      2 |                             3 | mixture                |                            8 |                       0 |                         0 |             0.163812  |             0.166964  |
|              04 | task_03_traffic | Answer Order Sensitivity         |             90 |                90 |               0 |   1        |                      9 |                             1 | green                  |                           90 |                       0 |                         0 |             0.145255  |             0.147824  |
|              05 | task_02_logic   | Noise x Answer Order Interaction |             72 |                72 |               0 |   0.638889 |                      2 |                             3 | mixture                |                           46 |                       0 |                         0 |             0.16483   |             0.205228  |
|              05 | task_03_traffic | Noise x Answer Order Interaction |             72 |                72 |               0 |   1        |                      9 |                             1 | green                  |                           72 |                       0 |                         0 |             0.150805  |             0.190944  |

## Paired perturbation results

|   experiment_id | task_id         | condition_type   | condition                    |   matched_count |   answer_flip_rate |   correct_to_wrong_rate |   accuracy_degradation |
|-----------------|-----------------|------------------|------------------------------|-----------------|--------------------|-------------------------|------------------------|
|              02 | task_01_math    | noise_position   | after_question               |               3 |           1        |                         |               0        |
|              02 | task_01_math    | noise_position   | before_task                  |               3 |           1        |                         |               0        |
|              02 | task_01_math    | noise_position   | between_description_question |               3 |           1        |                         |               0        |
|              02 | task_02_logic   | noise_position   | after_question               |               3 |           0        |                0        |               0        |
|              02 | task_02_logic   | noise_position   | before_task                  |               3 |           0        |                0        |               0        |
|              02 | task_02_logic   | noise_position   | between_description_question |               3 |           0        |                0        |               0        |
|              02 | task_03_traffic | noise_position   | after_question               |               3 |           0        |                0        |               0        |
|              02 | task_03_traffic | noise_position   | before_task                  |               3 |           0        |                0        |               0        |
|              02 | task_03_traffic | noise_position   | between_description_question |               3 |           0        |                0        |               0        |
|              03 | task_01_math    | noise_position   | after_question               |               9 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | quantity_16                  |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | quantity_4                   |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | quantity_8                   |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | sentence_1                   |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | sentence_2                   |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | sentence_3                   |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | wording_neutral              |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | words_1                      |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | words_2                      |               1 |           1        |                         |               0        |
|              03 | task_01_math    | perturbation_id  | words_3                      |               1 |           1        |                         |               0        |
|              03 | task_02_logic   | noise_position   | after_question               |               9 |           0.222222 |                0.222222 |               0.222222 |
|              03 | task_02_logic   | perturbation_id  | quantity_16                  |               1 |           1        |                1        |               1        |
|              03 | task_02_logic   | perturbation_id  | quantity_4                   |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | quantity_8                   |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | sentence_1                   |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | sentence_2                   |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | sentence_3                   |               1 |           1        |                1        |               1        |
|              03 | task_02_logic   | perturbation_id  | wording_neutral              |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | words_1                      |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | words_2                      |               1 |           0        |                0        |               0        |
|              03 | task_02_logic   | perturbation_id  | words_3                      |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | noise_position   | after_question               |               9 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | quantity_16                  |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | quantity_4                   |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | quantity_8                   |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | sentence_1                   |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | sentence_2                   |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | sentence_3                   |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | wording_neutral              |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | words_1                      |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | words_2                      |               1 |           0        |                0        |               0        |
|              03 | task_03_traffic | perturbation_id  | words_3                      |               1 |           0        |                0        |               0        |

## Noise and answer-order interaction

| task_id         |   matched_blocks |   accuracy_interaction |
|-----------------|------------------|------------------------|
| task_02_logic   |               18 |               0.111111 |
| task_03_traffic |               18 |               0        |

## Selected option by correct-answer position

| task_id         |   correct_numeric_answer |   selected_numeric_option |   selection_count |
|-----------------|--------------------------|---------------------------|-------------------|
| task_02_logic   |                        1 |                         3 |                 2 |
| task_02_logic   |                        1 |                         4 |                 4 |
| task_02_logic   |                        2 |                         3 |                 2 |
| task_02_logic   |                        2 |                         4 |                 4 |
| task_02_logic   |                        3 |                         3 |                 2 |
| task_02_logic   |                        3 |                         4 |                 4 |
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
