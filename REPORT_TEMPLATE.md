# CS 690 Assignment 1 Report: Replicating a Controlled Evaluation

## Part 1. Verification evidence

Command:

```text
python -m harness.verify
```

Paste the five `OK` lines here. Keep `results/verification.json` in your repository.
OK: loaded 20 frozen tasks
OK: dataset sha256 5d84176547cb679f4145676d1f4dfd5061bf3b9600904911da8e5700e82eee3b
OK: generated Python executed in Docker sandbox
OK: candidate network probe was blocked
OK: model/configuration metadata written to results/verification.json
## Part 2. Tests and code questions

Paste the final summary line of `pytest -q` here.

Answer each question in your own words, in about 75 to 150 words. Base every answer on the code in this repository, and name the files and functions you describe.

### Q1. The path of one attempt
One attempt is in the run() function in harness/runner.py. The runner loads the tasks with load_tasks() and creates the prompt with PROMPT_TEMPLATE. It then calls _generate_with_retry() which sends the prompt to the selected model through the provider’s generate() function. When the model responds, harness/grader.py's extract_python() pulls the Python code from the response. The runner saves both the raw response and extracted code, and then calls `grade_candidate()`, which runs the code against the task’s tests in the Docker sandbox. After grading, the runner writes information such as the model, task, token counts, pass/fail result and execution time to raw_results.jsonl.

### Q2. What is sent and what comes back
The request sent to the OpenAI API is generated in openAIProvider.generate() in harness/provider.py. The request contains the model name, the fixed task prompt, the maximum output-token limit and store=False. For this assignment, temperature is 1.0 and reasoning effort is " none " so those settings are included also . top_p and seed are not sent because they are null. The response is transformed into a Generation object. The harness stores the actual response text from the model, the model version returned by the API, the number of input tokens, the number of output tokens, the total number of tokens, and the reason the response ended. This allows the experiment to save more than just the pass/fail status of the answer.

### Q3. Same prompt, different answers
The generation of the model is not fully deterministic and the same prompt may lead to different answers. In harness/runner.py, the prompt for a task is the same for all three samples but _generate_with_retry() makes a separate call to provider.generate() for each attempt. The configuration has a temperature of 1.0 which allows for randomness in the framework's choice of tokens and the seed is null, meaning there is no fixed seed that would force the same output every time. And so one try can get the correct code, and another try at the same task can make a mistake. That’s why the experiment collects three samples per task, instead of judging each model based on only one generated response.

### Q4. pass@k by hand

Show your work for pass@1 and pass@2 with n = 3 and c = 1, the values `pass_at_k` returned, and the shortcut `1 - (1 - c/n) ** k` for k = 2.
For n = 3 attempts with c = 1 correct answer, pass_at_k() in harness/metrics.py calculates pass@1 as 1 - C(2,1) / C(3,1), which equals 1 - 2/3 = 1/3, or about 0.3333. For pass@2, it calculates 1 - C(2,2) / C(3,2), which equals 1 - 1/3 = 2/3, or about 0.6667. Therefore, pass_at_k(3, 1, 1) returns approximately 0.3333, while pass_at_k(3, 1, 2) returns approximately 0.6667. If I use the shortcut 1 - (1 - c/n)^k for k = 2, I get 1 - (2/3)^2 = 5/9, or about 0.5556. The shortcut gives a different answer because the harness uses combinations of the actual three tries, not treating each draw as independent.
### Q5. Why whole problems are redrawn
In harness/metrics.py, bootstrap_task_ci() resamples entire problems instead of individual attempts, because the three attempts for the same task are related. They all have the same prompt and are under the same task difficulty . To treat every attempt as completely independent would yield a misleading confidence interval . The function first computes the result for each task and then produces bootstrap samples by resampling the task-level results with replacement. This gathers all the information for a problem together. Resampling individual candidate attempts would give the illusion that there was more independent evidence in the experiment than there really was, and might lead to a confidence interval that is too narrow.

## Part 3. Replication

Part 3 has no written section. Its evidence is the committed `results/experiment/` and `prompts/` folders, and the dollars you spent, which go in the Part 4 table.

## Part 4. Results

Take every number from `results/experiment/summary_A.json` and `results/experiment/summary_B.json`, not from the console. Dollars spent come from the Usage page of your OpenAI account. If your account does not show them, write `not available`. If it shows only one total for the whole run, write the total in row A and `included in A` in row B.

| Condition | Requested model | Returned model version | Attempts per task | Total attempts | pass@1 | 95 percent CI for pass@1 | pass@2 | Input tokens | Output tokens | Dollars spent |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| A |gpt-5.6-luna |gpt-5.6-luna | 3 | 60 |0.95 |0.8667 to 1.0000 |0.9833 |7146 |3815 | 0.07|
| B | gpt-5.6-terra |gpt-5.6-terra | 3 | 60 |1.00 |1.0000 to 1.0000 |1.00 |7146 |4217 |included in A |

### Memo, no more than 500 words, not counting the table

Address all five items:

1. State the observed ranking by pass@1 point estimate.
2. State whether the uncertainty evidence supports ranking the two conditions.
3. If it does not, include the exact sentence: `The evidence does not support a ranking.`
4. State one external-validity limitation specific to `CS690-Eval20`.
5. State one likely source of variance specific to this experiment, and explain why a rerun, or a classmate's run, gives somewhat different numbers.

Overlapping intervals are not a formal significance test, and you are not asked to run one.
Point estimates of the pass@1 indicated that condition B had the higher observed outcome. Condition B with gpt-5.6-terra had a pass@1 of 1.00, and Condition A with gpt-5.6-luna had a pass@1 of 0.95.

However, the uncertainty evidence is not strong enough to rank the two conditions with confidence. 95 percent confidence interval for Condition A: 0.8667 to 1.0. 95 percent confidence interval for Condition B: 1.0 to 1.0. The confidence intervals overlap at 1.0, and comparison of overlapping confidence intervals is not a formal test of significance. There is no evidence for ranking.

A limitation in external validity is that CS690-Eval20 contains only 20 relatively small, self-contained Python programming problems. But these tasks don't touch many parts of a real software project, like working across multiple files, understanding an existing architecture, debugging a large codebase, changing requirements, or integrating outside systems.

One potential source of variance is the sampling process of the model. We only attempted each problem three times and the model can produce different code on different generations even when the prompt is the same. This means that if you rerun or if another student runs it, you might get slightly different solutions and thus slightly different pass@1 and pass@2 numbers.

## Part 5. Reading a published score, 300 to 400 words

Benchmark chosen (HumanEval, MBPP, LiveCodeBench, or SWE-bench):

Use the benchmark's primary paper or its official documentation for the task definition. Cite evidence for any contamination, saturation, or current-status claim, and date any current-status source.

### 1. What does it measure?

### 2. What does it not measure that a software project may depend on?

### 3. How can a reported score rise without the underlying model becoming better?

### 4. Could the model have seen the answers already?

End with at least one sentence explaining why the published score is not interchangeable with your `CS690-Eval20` result.
HumanEval . First presented by Chen, HumanEval is a benchmark for measuring functional correctness of code generated from natural language specifications. It includes 164 hand-written Python programming problems, for which the model is provided with a function signature and docstring, and the generated code is tested using unit tests. The benchmark commonly reports pass@k, which measures whether at least one of the k generated solutions passes all of the tests. Thus, HumanEval mainly measures whether a model can generate correct, self-contained Python functions from short specifications (Chen et al., 2021). But HumanEval doesn't test many skills that real software projects depend on. The tasks are small individual functions, changes to larger codebases, so it doesn't directly test working across multiple files, understanding an existing architecture, debugging large applications, integrating databases or APIs, handling changing requirements, or maintaining software over time. A reported HumanEval score may increase even without an improvement in the underlying model. For example, a higher k gives the model more chances to generate at least one correct answer, thus pass@k can be improved by generating more samples. The original HumanEval paper showed that repeated sampling improves the percentage of problems solved (Chen et al 2021). The quality of the test can also affect the score.EvalPlus extended HumanEval with additional test cases that stronger testing reduced the reported pass@k results for some models, indicating that weaker tests can accept solutions that are not truly fully correct (Liu et al., 2023). It is also possible that newer models have been exposed to HumanEval problems or similar solutions during training, as the benchmark has been publicly available since 2021. In 2023, a contamination study detected HumanEval overlap in large public training datasets, which does not demonstrate that a particular model memorized the answers, but does demonstrate that benchmark exposure is possible (Yang et al., 2023). For these reasons, my CS690-Eval20 score is not interchangeable with a published HumanEval score because the two evaluations have different tasks, prompts, tests, sample counts, and experimental settings.
## References
Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. O., Kaplan, J., et al. (2021). Evaluating Large Language Models Trained on Code. arXiv:2107.03374.
Liu, J., Xia, C. S., Wang, Y., & Zhang, L. (2023). Is Your Code Generated by ChatGPT Really Correct? Rigorous Evaluation of Large Language Models for Code Generation. arXiv:2305.01210.
Yang, S., Chiang, W.-L., Zheng, L., Gonzalez, J. E., & Stoica, I. (2023). Rethinking Benchmark and Contamination for Language Models with Rephrased Samples. arXiv:2311.04850.