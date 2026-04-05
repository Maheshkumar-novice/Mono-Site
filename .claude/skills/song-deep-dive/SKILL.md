---
name: song-deep-dive
description: >
  Use this skill whenever the user wants to explore, understand, or analyze an English song.
  Triggers include: any mention of a song title or artist with intent to understand it, requests
  like "break down this song", "what does this song mean", "explain the lyrics of", "deep dive into",
  "analyze this song", "tell me about [song] by [artist]", or "I want to learn from this song".
  Also trigger when a user shares lyrics and asks for help understanding them, or wants to build
  a blog post or markdown file about a song. Always use this skill — even for casual song questions —
  because the output is a rich structured markdown file the user can render in their blog.
---

# Song Deep-Dive Skill

Produce a rich, structured **Markdown file** analyzing an English song for a non-native English
speaker who wants to understand the lyrics deeply, learn vocabulary, and explore the artist and
cultural context. The output should be blog-ready.

---

## Input

The user will provide one of:
- Song title + artist name
- A snippet of lyrics
- Just an artist name and rough description ("that sad Adele song about someone coming back")

If the song is ambiguous, clarify before proceeding.

---

## Research Step (Always do this first)

Use **web search** to gather:
1. Song background — release year, album, chart performance
2. Artist bio — 2–3 sentences covering who they are, origin, and significance
3. Verified lyric excerpts — key lines that are most meaningful or interesting
4. Any known interviews or statements by the artist about the song's meaning
5. Cultural/historical context relevant to the song
6. Streaming links — search for the song on Spotify, Apple Music, YouTube (official music video), and YouTube Music. Use only verified URLs from search results.

Do NOT reproduce full lyrics. Use key lines/excerpts only (under 15 words per quote, max one direct quote per source). Paraphrase the rest.

---

## Output Format

Produce a single Markdown file with this exact structure:

```markdown
# 🎵 [Song Title] — [Artist Name]

> *[One evocative sentence summarizing the song's emotional core]*

---

## 📀 About the Song

- **Released:** [year]
- **Album:** [album name or "Single"]
- **Genre:** [genre(s)]
- **In one line:** [plain-English summary of what the song is about]

---

## 🎭 Themes & Emotions

[3–5 paragraphs exploring the emotional and thematic landscape of the song.
What feelings does it evoke? What big ideas does it explore — love, loss, identity,
resilience, nostalgia, etc.? Write warmly and accessibly for a non-native English speaker.]

---

## 📖 Lyrics: Key Lines & What They Mean

For each key excerpt, use this format:

### "[Key line or short excerpt]"

**What it means:** [Plain explanation of the literal and figurative meaning]

**Why it matters:** [What this line reveals about the song's deeper message]

---
[Repeat for 4–6 key lines/moments in the song]

---

## 🌍 Cultural & Historical Context

[2–3 paragraphs. What was happening in the world, in the artist's life, or in pop culture
when this song was made? Why did it resonate? Are there references to specific places,
events, or movements a listener might miss?]

---

## 📚 Vocabulary Builder

Pick the **3 most important** words/phrases from the song — prioritize idioms, emotionally loaded words, or phrases that are key to understanding the song's meaning. For each:

| Word / Phrase | Meaning | Example Sentence |
|---|---|---|
| [word] | [clear definition] | [natural example sentence] |

Focus on: idioms, phrasal verbs, emotionally loaded words, slang, or words with
nuanced meanings that don't translate directly.

---

## 🎯 Fun Facts

- [Interesting fact about the song's creation, reception, or legacy]
- [Another fun fact — chart position, cover versions, movie appearances, etc.]
- [A third fact — something surprising or little-known]

---

## 🧑‍🎤 About the Artist

[2–3 sentences: who they are, where they're from, why they matter musically]

---

## 🎬 Resonating Movies

List 2–3 films that share the same emotional themes as the song — not necessarily movies the song appears in, but films a fan of this song would likely connect with. For each, give the title, year, and one sentence on why it resonates thematically.

---

## 💬 Why This Song Is Worth Your Time

[2–3 sentences: a warm, personal-feeling closing note on why this song is special
and what a non-native English speaker can take away from it — linguistically,
emotionally, or culturally.]

```

---

## Quality Guidelines

- **Tone:** Warm, curious, educational — like a knowledgeable friend explaining a song
- **Language:** Clear and accessible; briefly explain any English idioms you use in explanations
- **Length:** Aim for a thorough but not exhausting read — roughly 800–1200 words total
- **Copyright:** Never reproduce more than a short excerpt (under 15 words). Always paraphrase lyrics; do not quote full verses or choruses.
- **Accuracy:** Ground claims in web search results. If the artist's intent is unknown, say so honestly ("this line is often interpreted as...")
- **Blog-ready:** The markdown should render cleanly with standard renderers (GitHub, blog platforms, Obsidian, etc.)

---

## Example Trigger Phrases

- "Deep dive into 'Someone Like You' by Adele"
- "I want to understand 'Lose Yourself' by Eminem"
- "Can you analyze 'Bohemian Rhapsody'?"
- "Make a blog post about 'Shape of You' by Ed Sheeran"
- "What does this song mean?" [followed by lyrics]
