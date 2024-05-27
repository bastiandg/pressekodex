Write a prompt for evaluating the adherence of a news article to a pressekodex section.

Task: evaluate the adherence of the news article
Input: News article
Output: 1. <reasoning> block 2. <compliant> block containing only yes / no

Base the prompt on the pressekodex section and a capability self assessment of the LLM.

<pressekodex_section>
Ziffer 1 - Wahrhaftigkeit und Achtung der Menschenwürde

Die Achtung vor der Wahrheit, die Wahrung der Menschenwürde und die wahrhaftige Unterrichtung der Öffentlichkeit sind oberste Gebote der Presse.

Jede in der Presse tätige Person wahrt auf dieser Grundlage das Ansehen und die Glaubwürdigkeit der Medien.

Richtlinie 1.1 - Exklusivverträge
Die Unterrichtung der Öffentlichkeit über Vorgänge oder Ereignisse, die für die Meinungs- und Willensbildung wesentlich sind, darf nicht durch Exklusivverträge mit den Informanten oder durch deren Abschirmung eingeschränkt oder verhindert werden. Wer ein Informationsmonopol anstrebt, schließt die übrige Presse von der Beschaffung von Nachrichten dieser Bedeutung aus und behindert damit die Informationsfreiheit.

Richtlinie 1.2 – Wahlkampfberichterstattung
Zur wahrhaftigen Unterrichtung der Öffentlichkeit gehört, dass die Presse in der Wahlkampfberichterstattung auch über Auffassungen berichtet, die sie selbst nicht teilt.

Richtlinie 1.3 – Pressemitteilungen
Pressemitteilungen müssen als solche gekennzeichnet werden, wenn sie ohne Bearbeitung durch die Redaktion veröffentlicht werden.
</pressekodex_section>

<reasoning>
Given the text of a news article, the evaluation of compliance with the Pressekodex section "Ziffer 1 - Wahrhaftigkeit und Achtung der Menschenwürde" can be approached as follows:

- **Ziffer 1 - Wahrhaftigkeit und Achtung der Menschenwürde**: Evaluating whether a news article adheres to the principles of truthfulness, human dignity, and accurate public information can be partially done through careful reading of the article. The language used, the presentation of facts, and the portrayal of individuals can be assessed for their alignment with truth and respect for human dignity. However, full evaluation might require additional context about the circumstances and sources.

- **Richtlinie 1.1 - Exklusivverträge**: Determining if exclusive contracts are restricting public information involves knowing if other media outlets had access to the same information. This is not typically discernible from the article itself. Additional information about the agreements between the media and informants, as well as access granted to other media, is necessary.

- **Richtlinie 1.2 - Wahlkampfberichterstattung**: Analyzing election campaign reporting for fairness and balance in presenting all viewpoints can be done by examining the coverage within the article. However, understanding whether the article reflects a biased selection of viewpoints requires knowledge of the broader media landscape and editorial practices.

- **Richtlinie 1.3 - Pressemitteilungen**: Identifying press releases published without editorial modification can sometimes be inferred from the style and structure of the text, but confirming this would often need explicit labeling or information from the media outlet about their editorial processes.

Therefore, parts that involve the content and presentation within the article can be somewhat evaluated directly. In contrast, aspects that concern the broader context of media practices or specific editorial decisions require additional information beyond the article itself.

</reasoning>

<evaluation_summary>

<can_evaluate>
- Ziffer 1 - Wahrhaftigkeit und Achtung der Menschenwürde (to some extent, based on the language and presentation within the article).
- Richtlinie 1.2 – Wahlkampfberichterstattung (based on the representation of different viewpoints within the article).
</can_evaluate>

<cannot_evaluate>
- Richtlinie 1.1 – Exklusivverträge (requires information about media access and agreements).
- Richtlinie 1.3 – Pressemitteilungen (needs explicit identification of press releases and editorial processes).
</cannot_evaluate>

<additional_info_needed>
- Information about exclusive contracts or agreements between the media outlet and informants.
- Access details granted to other media outlets regarding the same information.
- Broader context of the media landscape to understand if the election campaign reporting is balanced.
- Details from the media outlet about their editorial practices and identification of unmodified press releases.
</additional_info_needed>

</evaluation_summary>


--------------------------------------------------------------------------------

Here is the relevant section of the Pressekodex journalistic code of ethics:

<pressekodex_section>
{pressekodex_section}
</pressekodex_section>

And here is the text of the news article to be evaluated for compliance with this section of the Pressekodex:

<article_text>
{article_text}
</article_text>

Please read both of these texts carefully. Then, in a <reasoning> block, write out your step-by-step reasoning for whether the article complies with the Pressekodex section. Address each relevant part of the Pressekodex, discussing what you can and cannot determine about the article's compliance based solely on the article text.

After you have written out your reasoning, please state your overall judgment in a <compliant> block containing only the word "yes" or "no" - does the article comply with this section of the Pressekodex, based on your analysis?
