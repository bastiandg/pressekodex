Prompt for preprocessing the German "Pressekodex".
The Pressekodex is a ruleset of 16 sections.
Task: Describe whether an LLM is able to evaluate a section on a news article, given only the text of the news article.
Input: Pressekodex Section
Output: The Output contains three parts: 0. internal reasoning block 1. What parts of the section it can evaluate 2. Which parts it can't evaluate 3. What additional information would the LLM need to evaluate everything of the Pressekodex section.

--------------------------------------------------------------------------------

Here is the text of a section from the German Pressekodex journalistic code of ethics:

<pressekodex_section>
{{PRESSEKODEX_SECTION}}
</pressekodex_section>

Please read this section carefully and make sure you fully understand what it is saying.

Then, think step-by-step about whether you, as a language model, could evaluate whether a news article adheres to the standards laid out in this Pressekodex section if you were only given the text of the news article itself. Write out your reasoning inside <reasoning> tags.

Based on your reasoning, do you believe you could evaluate a news article's adherence to this Pressekodex section with only the article text, yes or no? Answer inside <llm_can_evaluate> tags.

If you answered "No", please list the additional information beyond the article text itself that you would need in order to evaluate adherence to this Pressekodex section. Provide your answer inside <additional_info_needed> tags. If you answered "Yes", you may leave this blank.

Reply in English.

Please do not actually attempt to evaluate any news articles. The goal is only to assess your own capability to perform this task.

--------------------------------------------------------------------------------

Here is the text of a section from the German Pressekodex journalistic code of ethics:

<pressekodex_section>
{{PRESSEKODEX_SECTION}}
</pressekodex_section>

Please carefully read and analyze this section of the Pressekodex. Then, think step-by-step, in a <reasoning> block through the following:

- What parts of this section do you believe you would be able to evaluate, given only the text of a news article?
- What parts of the section would you be unable to evaluate without having additional information beyond just the text of the news article?
- For the parts you cannot evaluate, what specific additional information would you need in order to be able to evaluate the news article's compliance with those parts of the section?

Write out your full reasoning and analysis in the <reasoning> block.

Then, summarize your conclusions in an <evaluation_summary> block, with the following sections:

<can_evaluate>
List here the parts of the Pressekodex section that you believe you could evaluate given only a news article text.
</can_evaluate>

<cannot_evaluate>
List here the parts of the section you do not believe you could evaluate without additional information.
</cannot_evaluate>

<additional_info_needed>
List here the specific pieces of additional information you would need in order to fully evaluate a news article's compliance with all parts of this Pressekodex section.
</additional_info_needed>

Please note, do not actually perform any evaluation. Your task is only to analyze the Pressekodex section and assess your ability to evaluate it, not to apply it to any specific text.
