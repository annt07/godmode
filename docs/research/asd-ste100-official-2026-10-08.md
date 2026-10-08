# Research: What ASD-STE100 (Issue 9, Jan 2025) officially specifies that matters for STE in agent instruction documents and agent-written outputs

**Date:** 2026-10-08
**Version investigated:** ASD-STE100 Issue 9, released 15 January 2025. Public pages fetched 2026-10-08. I could not get the standard PDF: it is sent only after you fill in a request form.

## Method and access notes

- I fetched these pages: `about_STE.html`, `STE_downloads.html`, `STE_faq.html` (the current FAQ), `faq.html` (an old FAQ from the Issue 8 era, still online), `STEsoftware.html`, `STE_training.html`, `STEMG_ToR.html`, `index.html`. I also fetched the STEMG AI White Paper PDF (`assets/files/WhitePaper-ASD-STE100_and_AI.pdf`) and the ASD Europe STE page.
- **Fetch failures:** `https://www.asd-ste100.org/` (the root URL) closed the connection with no response. `index.html` did load. `news.html` returned 404, and I found no news page.
- **No public page gives the rule text or rule numbers.** The rule numbers (1.x–9.x) and the numeric limits (20/25 words, 3-word noun clusters, 6 sentences) are not on any official page I could reach. Facts that I could confirm only from Wikipedia or TechScribe are marked **SECONDARY**.

## Findings

### 1. Structure: 53 rules in 9 sections, plus a dictionary
The standard has two parts. Part 1 is the writing rules: "53 writing rules in 9 sections that focus on word choice, grammar, sentence structure, and style". Part 2 is a dictionary of about 900 approved words, "each with one meaning and one part of speech", plus about 1,200 words that are not approved, each with alternatives. Source: https://www.asd-ste100.org/about_STE.html, "How does STE work? / Rules / Dictionary". Also https://www.asd-ste100.org/STE_faq.html, "What is ASD-STE100…".

**The official pages do not name the 9 sections.** SECONDARY (Wikipedia, "Writing rules"): Section 1 is "Words", which covers technical nouns and technical verbs. From memory of the Issue 8 table of contents (UNVERIFIED), the sections are: 1 Words, 2 Noun clusters, 3 Verbs, 4 Sentences, 5 Procedural writing, 6 Descriptive writing, 7 Safety instructions, 8 Punctuation, 9 Writing practices. Check this against the PDF.

### 2. Rules that the official site describes publicly
- **Word choice:** STE picks one synonym and leaves out the others ("start", not begin/commence/initiate/originate). Meanings and spelling follow American English and Merriam-Webster. Source: STE_faq.html, "What is ASD-STE100".
- **One part of speech per word:** "check" is approved only as a noun ("do a check"), not as a verb. "about" is approved only with the meaning "concerned with". Source: STE_faq.html, "How were the words … selected?".
- **-ing forms:** "usually not permitted". They are allowed only as technical nouns or as parts of technical nouns. The dictionary has some -ing words, but they are nouns, adjectives, pronouns or prepositions (opening, remaining, something, during). Source: STE_faq.html, "Why does STE not allow '-ing' forms?". The old FAQ adds a reason: -ing verb tenses "imply a duration that is not always clearly expressed". Source: faq.html.
- **Conditions first:** if readers must know a condition before they do a work step, put the condition at the start of the sentence ("If hot oil touches your skin, injuries can occur."). Source: STE_faq.html, "Do conditional clauses always need to precede the main clause?".
- **Voice:**
  - In procedures, use the imperative ("Install the component."). "Procedures must not be narrative and must not use passive sentences."
  - In descriptive text, also use active voice. Use passive voice "only if the agent … is unknown".
  - Source: STE_faq.html, "Why can't I use passive sentences?".
  - The old FAQ was looser. It allowed passive voice "when absolutely necessary", for example when an item receives an action (faq.html). Issue 9 narrows this to "agent unknown" only.
- **Safety instructions (WARNING/CAUTION):** STE handles them "without difficulty". Company legal departments may control the wording, and "individual company policies will determine the extent to which STE is used in safety instructions". Source: STE_faq.html, safety-instructions question. The public pages do not describe the format (for example, a command first, then the reason).
- **Principles that carry over to other writing:** "short sentences, one topic per sentence, and the use of the active voice". Source: STE_faq.html, "Who needs to write in STE?". The ASD Europe page also lists "active voice, short sentences, logical structure". Source: https://www.asd-europe.org/standards-specifications/simplified-technical-english/.
- **SECONDARY only (Wikipedia, "Writing rules"; TechScribe):**
  - Sentences: at most 20 words in procedures and 25 in descriptive text (TechScribe also gives 25 for descriptive).
  - Do not leave out the verb, subject or article to make the text shorter.
  - Use vertical lists for complex text.
  - One instruction per sentence.
  - One topic per paragraph, and at most 6 sentences in a paragraph.
  - Start safety instructions with a clear command or condition.
  - Simple tenses only (no present perfect).
- **Not confirmed from any source I fetched:**
  - The noun-cluster limit of 3 words. STEsoftware.html mentions only that checkers flag "overlong multi-word nouns".
  - The semicolon ban and its rule number 8.1.
  - The phrasal-verb rule 9.3 and the verb-not-noun rule 3.7.
  - The list of allowed verb forms.

### 3. Procedural and descriptive writing are two separate text types
The FAQ says writers "use it in procedural and descriptive texts". The voice rules differ between the two (see section 2). The tools page says: "Can the checker distinguish between procedural and descriptive text? Some rules differ between these two text types." Source: STE_faq.html and STEsoftware.html, "Functionality". The 20/25-word limits also differ by text type (SECONDARY).

### 4. Technical nouns and technical verbs (Issue 9 renamed them)
- Issue 9 uses the terms **"technical nouns"** and **"technical verbs"**. These terms follow ISO 1087-1:2019. Earlier issues said "technical names". Source: about_STE.html, "What's new in Issue 9". Compare faq.html, which still says "technical names".
- Company, industry or project terms that are not in the dictionary are allowed. The rules define them by subject-field category, not by listing them. Source: about_STE.html, "Terminology"; STE_faq.html.
- A word that is not approved is acceptable when it is part of a technical noun or verb, if the term comes from official documentation, engineering drawings, company glossaries or terminology databases. "This is the only way to use words that are not approved", and you should "limit this use as much as possible". Source: STE_faq.html, "Can technical nouns and technical verbs contain terms that are not approved…".
- Checkers need a company glossary of these terms. Source: STEsoftware.html, "Word and rule checkers".

### 5. Licensing and redistribution
- "The standard is available to everyone free of charge. The only file format for distribution is PDF." You must request it through the downloads form. Source: STE_faq.html, "Where can I get a copy".
- "ASD-STE100 is fully owned by ASD, Brussels." Source: about_STE.html.
- "Simplified Technical English, ASD-STE100, is a Copyright and a Trademark of ASD … All rights reserved. European Union Trade Mark No. 017966390." Source: faq.html, footer.
- Tool vendors may not use the ASD logo, copyright or trademark. Source: STE_faq.html; STEsoftware.html.
- The reproduction clause on page 2 of the PDF (eight categories that get free reproduction rights) is not on any public page. I could not verify it without the PDF.

### 6. Scope: software, use outside aerospace, and machine or AI readers
- STE is used "well beyond its original purpose … outside the aerospace and defense domains". Source: about_STE.html, "Today".
- ASD Europe lists "defence, rail, automotive, oil & gas, IT, medical devices". Source: ASD Europe page.
- FAQ: "Can STE be applied to all technical documentation? Yes." Also: "Anyone can use the principles of STE in general documents." STE is "not intended for general-purpose writing, such as international correspondence". STE is not for oral communication.
- STE helps translation "by translators, neural machine translation engines, or Large Language Models (LLMs)". Source: STE_faq.html, translation question. This is the only official mention of a machine reader. Nothing on the site addresses AI agents as readers of instructions.
- **STEMG White Paper "ASD-STE100 and AI" (dated June 2026)** says:
  - AI output "can appear … consistent with STE, even when it does not correctly apply the rules". "Plausibility must not be confused with verified compliance."
  - AI should assist authors, not replace them.
  - Mark AI-assisted content with disclaimers.
  - Responsibility stays with the human author.
  - "the standard takes priority".
  - STEMG endorses no AI tool.
  - Sources: STE_downloads.html (White Paper section); WhitePaper-ASD-STE100_and_AI.pdf, pp. 1–3.

### 7. Quoted non-STE text, code and user input
I found no official public guidance on how to quote non-STE text, code, or user input. The closest point is on the tools page: checkers should process formatting such as "XML tags" to decide "which text should be checked". This implies that marked-up non-prose is excluded from checks. Source: STEsoftware.html, "Technical and functional considerations".

### 8. Current issue and tooling
- Current issue: Issue 9, January 2025 (released 15 January 2025). Issue 10 is scheduled for January 2028. Issues now come about every three years.
- In Issue 9, STE changed from a "specification" to a "standard" (subtitle: "Standard for Technical Documentation"). More than half of the 53 rules were refined, and 555 dictionary entries were updated. STE is no longer part of the S-Series.
- Sources: about_STE.html, "What's new in Issue 9"; STE_faq.html, maintenance questions.
- Checkers are optional. "No tool can replace the standard." Tools "cannot convert non-STE text into STE".
- Some things a checker can check: sentence length, overlong multi-word nouns, passive voice. Some things it cannot check: for example, whether the first sentence of a paragraph is the topic sentence. Source: STEsoftware.html, "Disclaimer", "Functionality".
- The FAQ recommends that writers have C1 English. Source: STE_faq.html, "Is STE simple to write?".

## Differences from the local asd-ste100 skill

Files compared: `asd-ste100-skill/SKILL.md` and `references/writing-rules.md`.

1. **Terminology:** the skill says "Domain terms" and "project-specific glossary". Issue 9 calls them **technical nouns** and **technical verbs**. Also, the skill says "define them once if not common English". The official condition is that the terms come from official docs, drawings, glossaries or terminology databases, and that you limit their use. Defining a term is not the condition. (SKILL.md, lexical table "Domain terms"; writing-rules.md, "Structure".)
2. **Passive voice:**
   - The skill (SKILL.md, structural table) allows passive "unless the actor is genuinely unknown **or irrelevant**".
   - writing-rules.md, "Voice", also adds "or irrelevant".
   - Issue 9 FAQ says **unknown only**, and it requires active voice in descriptive text as well.
   - The skill also does not say that procedures must use the imperative and "must not be narrative".
3. **Conditions first:** the official FAQ rule (put a condition at the start of the sentence) is missing from SKILL.md. writing-rules.md covers it only for safety instructions.
4. **-ing forms:** writing-rules.md covers them, but the SKILL.md rules and checklist do not. The official text says "usually not permitted", except in technical nouns.
5. **Procedural vs descriptive:** the skill has only a "Strict / STE-flavored" mode split. It does not tell the agent to classify text as procedural or descriptive, although the standard does. Only the 20/25 word limits reflect the split.
6. **Unverified rule numbers and limits:** the skill presents Rule 8.1 (semicolon), Rule 9.3 (phrasal verbs), Rule 3.7 (verb, not noun), the 3-word noun cluster, the ≤6-sentence paragraph and the 20/25 word limits as official. None of these is on an official public page. Wikipedia confirms only the 20/25 and 6-sentence limits. The quote "You can use all standard English punctuation marks but not the semicolon" has no public source I could find.
7. **Licensing quote:** SKILL.md, "Source and Scope", quotes page 2 of the PDF (eight categories). I could not verify this publicly. The public facts are: free to everyone, PDF only, ASD copyright and EU trademark.
8. **"Free to download since Issue 6 (2013)":** only Wikipedia states this (SECONDARY). The official pages say only "free of charge".
9. **AI White Paper:** the skill does not mention it. The skill's disclaimer ("not a certified STE authoring tool") agrees with it. The White Paper also asks for disclaimers on AI-assisted content, and the skill does not do that.
10. **Linter claims:** the official tools page says tools "cannot convert non-STE text into STE" and that their feedback "can be inaccurate". The skill's `ste-lint.py` and rewrite process should state this limit.
11. **Spelling basis:** the skill does not say that STE spelling and meanings are American English (Merriam-Webster).
12. **Present perfect exception:** the skill keeps compound tenses when they add meaning. The skill admits this departs from the standard, and the official sources give no allowance for it.
13. **Safety instructions:** the skill says nothing about WARNING/CAUTION structure or about company or legal control of their wording.
14. **Name and status:** the skill does not say that STE is now a "standard", not a "specification". writing-rules.md says "STE…Maintenance Group…free to download since Issue 6", which is fine. The White Paper is dated June 2026, which is newer than anything the skill cites.

## Contradictions or Gaps

- The old FAQ (`faq.html`, Issue 8 era) is still online, and it contradicts the current FAQ on two points: passive voice ("when absolutely necessary" versus "only if the agent is unknown") and terminology ("technical names" versus "technical nouns"). It also gives the cadence as "two to four years" and names Issue 8 as current. Use STE_faq.html.
- The White Paper is dated "June 2026". It is newer than Issue 9 and is not part of the standard.
- No official public source gives the exact rule text, the rule numbers, or the names of the 9 sections. You need the PDF (request form at STE_downloads.html) to verify the numeric limits and the rule numbers.
- No official guidance exists on quoting code or user input, or on readers that are AI agents.

## Conclusion

The official public sources confirm these rules:
- one meaning and one part of speech per word
- one synonym chosen
- no -ing verb forms
- conditions first
- imperative in procedures, with no passive voice
- active voice in descriptive text, with passive voice only when the agent is unknown
- technical nouns and technical verbs, which allow company or project terms from authoritative glossaries
- a split between procedural and descriptive text, with different rules for each

They also say STE principles apply to any technical documentation, that tools and AI cannot make text compliant, and that humans stay accountable.

The local skill gets the main points right. It is wrong on the passive-voice exception ("or irrelevant"). It is out of date on terminology ("technical names" and domain terms). It leaves out the conditions-first rule and the procedural/descriptive classification. It states rule numbers and limits that are not publicly verifiable, so mark them as "per standard; verify against PDF", or check them against the requested PDF.
