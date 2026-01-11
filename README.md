# AnkiMD

Markdown & Mermaid support for Anki flashcards.

![AnkiMD Screenshot](AnkiMD.png)

## Features

- Full Markdown syntax (headers, bold, italic, strikethrough, lists, tables, blockquotes, links, images)
- Code blocks with syntax highlighting (VSCode Dark+ theme)
- Mermaid diagrams (offline, no internet required)
- Cloze deletion support in Mermaid diagrams
- Automatic note type creation (AnkiMD and AnkiMD Cloze)

## Installation

1. Copy the `ankimd` folder to your Anki addons directory:
   - macOS: `~/Library/Application Support/Anki2/addons21/`
   - Windows: `%APPDATA%\Anki2\addons21\`
   - Linux: `~/.local/share/Anki2/addons21/`

2. Restart Anki

## Usage

### Basic (AnkiMD)

1. Create a new card using the "AnkiMD" note type
2. Write Markdown in the Back field
3. Content renders when reviewing cards

### Cloze Deletion (AnkiMD Cloze)

![AnkiMD Cloze Screenshot](AnkiMD%20-%20Cloze.png)

1. Create a new card using the "AnkiMD Cloze" note type
2. Write Markdown with cloze syntax in the Text field: `{{c1::answer}}`
3. Cloze deletions work inside Mermaid diagrams too

Example with Mermaid cloze:

~~~
```mermaid
graph LR
    A[Glucose] --> B[{{c1::Pyruvate}}]
    B --> C[{{c2::Acetyl-CoA}}]
```
~~~

## License

MIT
