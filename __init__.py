"""
AnkiMD - Markdown & Mermaid support for Anki
Automatically creates note type and renders Markdown syntax.

Author: Lauren Wong
"""

from aqt import gui_hooks, mw
from anki.cards import Card

from .parser import render_markdown

# Note type name
NOTE_TYPE_NAME = "AnkiMD"


def create_note_type() -> None:
    """Create the AnkiMD note type if it doesn't exist."""
    if not mw or not mw.col:
        return

    # Check if note type already exists
    if mw.col.models.by_name(NOTE_TYPE_NAME):
        print(f"[AnkiMD] Note type '{NOTE_TYPE_NAME}' already exists")
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
    print(f"[AnkiMD] Created note type '{NOTE_TYPE_NAME}'")


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    """Hook: process card content before display."""
    if not text:
        return text

    try:
        note = card.note()
        note_type = note.note_type()

        if note_type and note_type.get("name") == NOTE_TYPE_NAME:
            return render_markdown(text)

        return text

    except Exception as e:
        print(f"[AnkiMD] Error: {e}")
        return text


def on_profile_loaded() -> None:
    """Called when profile is loaded - create note type if needed."""
    create_note_type()


# Register hooks
gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.profile_did_open.append(on_profile_loaded)

print("[AnkiMD] Plugin loaded")
