# Раунд 2

Основная метрика: максимум ошибок из 12; при равенстве меньше длина.
Условия: 2 задачи, 3 позиции, 2 порядка, длины 300/1024/4096, seed 1731.
Гипотеза: новые последовательности существующих типов изменят число ошибок.
Лимит шума 8192 токена, контекст 18000, резерв генерации 2048.
instruction.md missing; default policy used.

Уточнение: 15 вариантов на модель: 3 вида шума × seed 1731–1735.
По максимуму ошибок выбирается один вариант; предыдущие шумы сохраняются для финала.

- search_oss_random_words_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T190922Z_75933d88', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T190922Z_75933d88', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T190922Z_75933d88', 'actual_tokens': 4096}]; данные results/raw/20261106T190922Z_75933d88.jsonl.

- search_oss_sentences_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T190956Z_f37d4931', 'actual_tokens': 299}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T190956Z_f37d4931', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T190956Z_f37d4931', 'actual_tokens': 4096}]; данные results/raw/20261106T190956Z_f37d4931.jsonl.

- search_oss_catalog_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191032Z_6b691f1b', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191032Z_6b691f1b', 'actual_tokens': 1023}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191032Z_6b691f1b', 'actual_tokens': 4096}]; данные results/raw/20261106T191032Z_6b691f1b.jsonl.

- search_oss_random_words_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191105Z_30e1d9d6', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191105Z_30e1d9d6', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191105Z_30e1d9d6', 'actual_tokens': 4096}]; данные results/raw/20261106T191105Z_30e1d9d6.jsonl.

- search_oss_sentences_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191138Z_a15f7cf9', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191138Z_a15f7cf9', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T191138Z_a15f7cf9', 'actual_tokens': 4096}]; данные results/raw/20261106T191138Z_a15f7cf9.jsonl.

- search_oss_catalog_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191210Z_ea4acd2a', 'actual_tokens': 298}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191210Z_ea4acd2a', 'actual_tokens': 1021}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191210Z_ea4acd2a', 'actual_tokens': 4096}]; данные results/raw/20261106T191210Z_ea4acd2a.jsonl.

- search_oss_random_words_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191242Z_a73b9410', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191242Z_a73b9410', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191242Z_a73b9410', 'actual_tokens': 4096}]; данные results/raw/20261106T191242Z_a73b9410.jsonl.

- search_oss_sentences_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191316Z_03c0ded8', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191316Z_03c0ded8', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191316Z_03c0ded8', 'actual_tokens': 4095}]; данные results/raw/20261106T191316Z_03c0ded8.jsonl.

- search_oss_catalog_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191346Z_a6b9a053', 'actual_tokens': 299}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191346Z_a6b9a053', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191346Z_a6b9a053', 'actual_tokens': 4094}]; данные results/raw/20261106T191346Z_a6b9a053.jsonl.

- search_oss_random_words_1734: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191419Z_3fe69df4', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191419Z_3fe69df4', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191419Z_3fe69df4', 'actual_tokens': 4096}]; данные results/raw/20261106T191419Z_3fe69df4.jsonl.

- search_oss_sentences_1734: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191457Z_0933e802', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191457Z_0933e802', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191457Z_0933e802', 'actual_tokens': 4096}]; данные results/raw/20261106T191457Z_0933e802.jsonl.

- search_oss_catalog_1734: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191538Z_f9fd0c6a', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191538Z_f9fd0c6a', 'actual_tokens': 1023}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191538Z_f9fd0c6a', 'actual_tokens': 4094}]; данные results/raw/20261106T191538Z_f9fd0c6a.jsonl.

- search_oss_random_words_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191615Z_6f3d4d89', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191615Z_6f3d4d89', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191615Z_6f3d4d89', 'actual_tokens': 4096}]; данные results/raw/20261106T191615Z_6f3d4d89.jsonl.

- search_oss_sentences_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191652Z_3c476a89', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T191652Z_3c476a89', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T191652Z_3c476a89', 'actual_tokens': 4096}]; данные results/raw/20261106T191652Z_3c476a89.jsonl.

- search_oss_catalog_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T191726Z_6a40e521', 'actual_tokens': 298}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T191726Z_6a40e521', 'actual_tokens': 1022}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T191726Z_6a40e521', 'actual_tokens': 4095}]; данные results/raw/20261106T191726Z_6a40e521.jsonl.

- verify_oss_oss: [{'level': 300, 'errors': 1, 'count': 12, 'run_id': '20261106T191759Z_07cd8630', 'actual_tokens': 300}]; данные results/raw/20261106T191759Z_07cd8630.jsonl.

- search_qwen_random_words_1731: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191858Z_a37dfbaa', 'actual_tokens': 299}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T191858Z_a37dfbaa', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T191858Z_a37dfbaa', 'actual_tokens': 4096}]; данные results/raw/20261106T191858Z_a37dfbaa.jsonl.

- search_qwen_sentences_1731: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191909Z_a6fc4078', 'actual_tokens': 299}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T191909Z_a6fc4078', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T191909Z_a6fc4078', 'actual_tokens': 4096}]; данные results/raw/20261106T191909Z_a6fc4078.jsonl.

- search_qwen_catalog_1731: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191920Z_a49a5b7f', 'actual_tokens': 299}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T191920Z_a49a5b7f', 'actual_tokens': 1023}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T191920Z_a49a5b7f', 'actual_tokens': 4095}]; данные results/raw/20261106T191920Z_a49a5b7f.jsonl.

- search_qwen_random_words_1732: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191931Z_a52d54c5', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T191931Z_a52d54c5', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T191931Z_a52d54c5', 'actual_tokens': 4096}]; данные results/raw/20261106T191931Z_a52d54c5.jsonl.

- search_qwen_sentences_1732: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191943Z_e70ec511', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T191943Z_e70ec511', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T191943Z_e70ec511', 'actual_tokens': 4096}]; данные results/raw/20261106T191943Z_e70ec511.jsonl.

- search_qwen_catalog_1732: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T191954Z_f8cabee5', 'actual_tokens': 298}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T191954Z_f8cabee5', 'actual_tokens': 1021}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T191954Z_f8cabee5', 'actual_tokens': 4096}]; данные results/raw/20261106T191954Z_f8cabee5.jsonl.

- search_qwen_random_words_1733: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192006Z_32dcb3ea', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192006Z_32dcb3ea', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192006Z_32dcb3ea', 'actual_tokens': 4096}]; данные results/raw/20261106T192006Z_32dcb3ea.jsonl.

- search_qwen_sentences_1733: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192017Z_52ad2372', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192017Z_52ad2372', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T192017Z_52ad2372', 'actual_tokens': 4095}]; данные results/raw/20261106T192017Z_52ad2372.jsonl.

- search_qwen_catalog_1733: [{'level': 300, 'errors': 2, 'count': 4, 'run_id': '20261106T192029Z_05fdf0b8', 'actual_tokens': 296}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192029Z_05fdf0b8', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192029Z_05fdf0b8', 'actual_tokens': 4091}]; данные results/raw/20261106T192029Z_05fdf0b8.jsonl.

- search_qwen_random_words_1734: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192040Z_66aa8ac2', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192040Z_66aa8ac2', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192040Z_66aa8ac2', 'actual_tokens': 4096}]; данные results/raw/20261106T192040Z_66aa8ac2.jsonl.

- search_qwen_sentences_1734: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192051Z_4eb5962f', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192051Z_4eb5962f', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T192051Z_4eb5962f', 'actual_tokens': 4096}]; данные results/raw/20261106T192051Z_4eb5962f.jsonl.

- search_qwen_catalog_1734: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192103Z_fca6aaae', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192103Z_fca6aaae', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192103Z_fca6aaae', 'actual_tokens': 4096}]; данные results/raw/20261106T192103Z_fca6aaae.jsonl.

- search_qwen_random_words_1735: [{'level': 300, 'errors': 2, 'count': 4, 'run_id': '20261106T192114Z_69c866e1', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192114Z_69c866e1', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192114Z_69c866e1', 'actual_tokens': 4096}]; данные results/raw/20261106T192114Z_69c866e1.jsonl.

- search_qwen_sentences_1735: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192125Z_c82b3041', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192125Z_c82b3041', 'actual_tokens': 1024}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T192125Z_c82b3041', 'actual_tokens': 4096}]; данные results/raw/20261106T192125Z_c82b3041.jsonl.

- search_qwen_catalog_1735: [{'level': 300, 'errors': 1, 'count': 4, 'run_id': '20261106T192136Z_a50af3af', 'actual_tokens': 298}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192136Z_a50af3af', 'actual_tokens': 1023}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192136Z_a50af3af', 'actual_tokens': 4095}]; данные results/raw/20261106T192136Z_a50af3af.jsonl.

- verify_qwen_oss: [{'level': 300, 'errors': 4, 'count': 12, 'run_id': '20261106T192147Z_3f84a189', 'actual_tokens': 399}]; данные results/raw/20261106T192147Z_3f84a189.jsonl.

- verify_qwen_qwen: [{'level': 300, 'errors': 4, 'count': 12, 'run_id': '20261106T192157Z_7631a586', 'actual_tokens': 296}]; данные results/raw/20261106T192157Z_7631a586.jsonl.

- search_gemma_random_words_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T192252Z_9a7df9e6', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192252Z_9a7df9e6', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T192252Z_9a7df9e6', 'actual_tokens': 4096}]; данные results/raw/20261106T192252Z_9a7df9e6.jsonl.

- search_gemma_sentences_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T192606Z_66f75409', 'actual_tokens': 299}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T192606Z_66f75409', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T192606Z_66f75409', 'actual_tokens': 4096}]; данные results/raw/20261106T192606Z_66f75409.jsonl.

- search_gemma_catalog_1731: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T192901Z_a5831a6a', 'actual_tokens': 297}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T192901Z_a5831a6a', 'actual_tokens': 1020}, {'level': 4096, 'errors': 1, 'count': 4, 'run_id': '20261106T192901Z_a5831a6a', 'actual_tokens': 4095}]; данные results/raw/20261106T192901Z_a5831a6a.jsonl.

- search_gemma_random_words_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T193153Z_3b487f62', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T193153Z_3b487f62', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T193153Z_3b487f62', 'actual_tokens': 4096}]; данные results/raw/20261106T193153Z_3b487f62.jsonl.

- search_gemma_sentences_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T193351Z_aec4c0f3', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T193351Z_aec4c0f3', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T193351Z_aec4c0f3', 'actual_tokens': 4096}]; данные results/raw/20261106T193351Z_aec4c0f3.jsonl.

- search_gemma_catalog_1732: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T193729Z_1d52617f', 'actual_tokens': 298}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T193729Z_1d52617f', 'actual_tokens': 1021}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T193729Z_1d52617f', 'actual_tokens': 4092}]; данные results/raw/20261106T193729Z_1d52617f.jsonl.

- search_gemma_random_words_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T193928Z_1f0df27b', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T193928Z_1f0df27b', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T193928Z_1f0df27b', 'actual_tokens': 4096}]; данные results/raw/20261106T193928Z_1f0df27b.jsonl.

- search_gemma_sentences_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T194137Z_ca22ce7f', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T194137Z_ca22ce7f', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T194137Z_ca22ce7f', 'actual_tokens': 4095}]; данные results/raw/20261106T194137Z_ca22ce7f.jsonl.

- search_gemma_catalog_1733: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T194528Z_28941de0', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T194528Z_28941de0', 'actual_tokens': 1022}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T194528Z_28941de0', 'actual_tokens': 4093}]; данные results/raw/20261106T194528Z_28941de0.jsonl.

- search_gemma_random_words_1734: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T194744Z_06ccc4fd', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T194744Z_06ccc4fd', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T194744Z_06ccc4fd', 'actual_tokens': 4096}]; данные results/raw/20261106T194744Z_06ccc4fd.jsonl.

- search_gemma_sentences_1734: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T194941Z_0789aa64', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T194941Z_0789aa64', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T194941Z_0789aa64', 'actual_tokens': 4096}]; данные results/raw/20261106T194941Z_0789aa64.jsonl.

- search_gemma_catalog_1734: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T195258Z_6e4198f6', 'actual_tokens': 298}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T195258Z_6e4198f6', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T195258Z_6e4198f6', 'actual_tokens': 4091}]; данные results/raw/20261106T195258Z_6e4198f6.jsonl.

- search_gemma_random_words_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T195452Z_1613bf7b', 'actual_tokens': 300}, {'level': 1024, 'errors': 1, 'count': 4, 'run_id': '20261106T195452Z_1613bf7b', 'actual_tokens': 1024}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T195452Z_1613bf7b', 'actual_tokens': 4096}]; данные results/raw/20261106T195452Z_1613bf7b.jsonl.

- search_gemma_sentences_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T195627Z_29612428', 'actual_tokens': 300}, {'level': 1024, 'errors': 0, 'count': 4, 'run_id': '20261106T195627Z_29612428', 'actual_tokens': 1024}, {'level': 4096, 'errors': 0, 'count': 4, 'run_id': '20261106T195627Z_29612428', 'actual_tokens': 4096}]; данные results/raw/20261106T195627Z_29612428.jsonl.

- search_gemma_catalog_1735: [{'level': 300, 'errors': 0, 'count': 4, 'run_id': '20261106T195907Z_a2da2523', 'actual_tokens': 300}, {'level': 1024, 'errors': 2, 'count': 4, 'run_id': '20261106T195907Z_a2da2523', 'actual_tokens': 1023}, {'level': 4096, 'errors': 2, 'count': 4, 'run_id': '20261106T195907Z_a2da2523', 'actual_tokens': 4096}]; данные results/raw/20261106T195907Z_a2da2523.jsonl.

- verify_gemma_oss: [{'level': 300, 'errors': 0, 'count': 12, 'run_id': '20261106T200030Z_d556a3b3', 'actual_tokens': 395}]; данные results/raw/20261106T200030Z_d556a3b3.jsonl.

- verify_gemma_qwen: [{'level': 300, 'errors': 0, 'count': 12, 'run_id': '20261106T200438Z_f4a3b69b', 'actual_tokens': 294}]; данные results/raw/20261106T200438Z_f4a3b69b.jsonl.

- verify_gemma_gemma: [{'level': 1024, 'errors': 4, 'count': 12, 'run_id': '20261106T200819Z_76a0f467', 'actual_tokens': 1020}]; данные results/raw/20261106T200819Z_76a0f467.jsonl.

- verify_oss_qwen: [{'level': 300, 'errors': 0, 'count': 12, 'run_id': '20261106T201104Z_693f0d85', 'actual_tokens': 223}]; данные results/raw/20261106T201104Z_693f0d85.jsonl.

- verify_oss_gemma: [{'level': 1024, 'errors': 0, 'count': 12, 'run_id': '20261106T201140Z_18543354', 'actual_tokens': 771}]; данные results/raw/20261106T201140Z_18543354.jsonl.

- verify_qwen_gemma: [{'level': 1024, 'errors': 4, 'count': 12, 'run_id': '20261106T201226Z_a3ef31d5', 'actual_tokens': 1030}]; данные results/raw/20261106T201226Z_a3ef31d5.jsonl.
