"""
AnkiMD - Markdown & Mermaid support for Anki
Automatically creates note type and renders Markdown syntax.

Author: Lauren Wong
"""

from aqt import gui_hooks, mw
from anki.cards import Card
from anki.consts import MODEL_CLOZE

from .parser import render_markdown

# Note type names
NOTE_TYPE_NAME = "AnkiMD"
CLOZE_NOTE_TYPE_NAME = "AnkiMD Cloze"


def create_note_type() -> None:
    """Create the AnkiMD note type if it doesn't exist."""
    if not mw or not mw.col:
        return

    # Check if note type already exists
    if mw.col.models.by_name(NOTE_TYPE_NAME):
        return

    # Create new note type
    model = mw.col.models.new(NOTE_TYPE_NAME)

    # Add fields
    front_field = mw.col.models.new_field("Front")
    back_field = mw.col.models.new_field("Back")
    mw.col.models.add_field(model, front_field)
    mw.col.models.add_field(model, back_field)

    # Add template
    template = mw.col.models.new_template("Card 1")
    template["qfmt"] = '<h3 style="text-align:center;">{{Front}}</h3>'
    template["afmt"] = '{{FrontSide}}<hr id=answer>{{Back}}'
    mw.col.models.add_template(model, template)

    # Set CSS
    model["css"] = """.card {
  font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
  font-size: 16px;
  text-align: left;
  color: #d4d4d4;
  background-color: #1e1e1e;
  padding: 20px;
  line-height: 1.6;
}

.front {
  font-size: 1.4em;
  font-weight: 600;
  color: #569cd6;
}

hr#answer {
  border: none;
  border-top: 1px solid #444;
  margin: 16px 0;
}
"""

    # Add to collection
    mw.col.models.add(model)


def create_cloze_note_type() -> None:
    """Create the AnkiMD Cloze note type if it doesn't exist."""
    if not mw or not mw.col:
        return

    # Check if note type already exists
    if mw.col.models.by_name(CLOZE_NOTE_TYPE_NAME):
        return

    # Create new cloze note type
    model = mw.col.models.new(CLOZE_NOTE_TYPE_NAME)
    model['type'] = MODEL_CLOZE  # Set as Cloze type

    # Add fields (Text for cloze content, Extra for additional info)
    text_field = mw.col.models.new_field("Text")
    extra_field = mw.col.models.new_field("Extra")
    mw.col.models.add_field(model, text_field)
    mw.col.models.add_field(model, extra_field)

    # Add cloze template
    template = mw.col.models.new_template("Cloze")
    template["qfmt"] = '{{cloze:Text}}'
    template["afmt"] = '{{cloze:Text}}<hr id=answer>{{Extra}}'
    mw.col.models.add_template(model, template)

    # Set CSS (same dark theme as AnkiMD)
    model["css"] = """.card {
  font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
  font-size: 16px;
  text-align: left;
  color: #d4d4d4;
  background-color: #1e1e1e;
  padding: 20px;
  line-height: 1.6;
}

.cloze {
  font-weight: bold;
  color: #4ec9b0;
}

hr#answer {
  border: none;
  border-top: 1px solid #444;
  margin: 16px 0;
}
"""

    # Add to collection
    mw.col.models.add(model)


def on_card_will_show(text: str, card: Card, _kind: str) -> str:
    """Hook: process card content before display."""
    if not text:
        return text

    try:
        note = card.note()
        note_type = note.note_type()

        if not note_type:
            return text

        note_type_name = note_type.get("name")

        if note_type_name == NOTE_TYPE_NAME:
            return render_markdown(text)
        elif note_type_name == CLOZE_NOTE_TYPE_NAME:
            return render_markdown(text, is_cloze=True)

        return text

    except Exception:
        return text


def on_profile_loaded() -> None:
    """Called when profile is loaded - create note types if needed."""
    create_note_type()
    create_cloze_note_type()


# Register hooks
gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.profile_did_open.append(on_profile_loaded)
