# Can LLMs evaluate Journalism Ethics in News Articles?

[🔗 LinkedIn Post](https://www.linkedin.com/posts/bastiandegroot_pressekodex-activity-7202425438202118146-ujHY)

My previous side projects were mainly about creating stuff with #genAi. This project is about testing how well Large Language Models (LLMs) can be used to evaluate content.

The ["Deutscher Presserat"](https://www.presserat.de/) provides a code of ethics (the "Pressecodex") for German media. The [Pressecodex](https://www.presserat.de/pressekodex.html) is a lengthy text description on what constitutes good journalism and what doesn't. Ideal for LLMs.

My goal with this project is to have an automated process, for evaluating news articles against the Pressecodex.

## Implementation

I implemented this process with #python, #goose3, #beautifulsoup and #langchain. The process has 3 parts.

1. **Download & Parse**: the script downloads a news article and parses it with goose3. Modern news sites obfuscate the content of their website a lot, to make the usage of adblockers or scripts harder. That's why goose3 is a blessing. For most pages it can bypass all the nonesense.
2. **LLM Evaluation**: The LLM is called. Each Pressecodex is evaluated separately. Sections which cannot be evaluated purely by reading the article text are skipped. Prompt: https://raw.githubusercontent.com/bastiandg/pressekodex/main/prompts/compliance.md
3. **Results Display**: Results are put in a table and displayed in a browser (see screenshot).

## Results

The results are impressive. Depending on which #LLM (#gpt4 and #claude3 tested) is used, it can spot sensationalism, discrimination, violations of human dignity and predjudice. My favorite bit of judgement comes from claude3 opus:

> *The characterization of [Name Redacted] as an "Israel-Hasserin" in the headline, […] are arguably an inappropriate attack on her honor that violates Ziffer 9. […] On balance, I judge it as likely non-compliant with Ziffer 9, but I acknowledge it is a close call based just on the text of that clause.*

It seems to have an awareness for the nuances of the language and finds a good way to express its uncertainty appropriately.

**Important Note**: This is a proof of concept. It has flaws and sometimes the evaluation goes wrong, especially when using weaker models like claude3 haiku.

