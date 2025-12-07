# Character Card Support

BrainDancev2 now supports importing and exporting character cards compatible with [Tavern/SillyTavern Character Card Spec v2](https://github.com/malfoyslastname/character-card-spec-v2).

## What are Character Cards?

Character cards are PNG images that contain embedded character data (personality, description, greeting messages, etc.) in their metadata. This allows you to easily share and import AI characters between different applications like:

- Text Generation WebUI (oobabooga)
- SillyTavern
- Tavern AI
- And now BrainDancev2!

## How to Use

### Importing a Character Card

1. Open the BrainDancev2 web interface
2. In the sidebar, scroll to the **Persona** section
3. Under "Character Cards", click the **Import Card** button
4. Select a PNG file containing a character card
5. The character's name, personality, and profile picture will be automatically loaded
6. If the card includes a greeting message, it will appear in the chat

**Supported Format:** PNG images with embedded character metadata (Tavern/SillyTavern format)

### Exporting a Character Card

1. Set up your character's name and persona description in the sidebar
2. Optionally upload a profile picture
3. Under "Character Cards", click the **Export Card** button
4. A PNG file will be downloaded containing your character's data
5. This file can be shared and imported into other compatible applications

## Technical Details

### Character Card Format

Character cards follow the Tavern/SillyTavern specification:

- **Format**: PNG image with tEXt/iTXt metadata chunk
- **Metadata Key**: `chara`
- **Encoding**: Base64-encoded JSON
- **Spec Version**: v2.0

### Supported Fields

When importing, the following Tavern fields are mapped to BrainDancev2:

| Tavern Field | BrainDancev2 Field |
|--------------|-------------------|
| `name` | AI Name |
| `description` + `personality` | Persona Description |
| `first_mes` | Greeting (displayed in chat) |
| `scenario` | Stored for reference |
| `mes_example` | Stored for reference |

When exporting, BrainDancev2 creates a fully compatible Tavern v2 card that includes:

- Character name
- Personality/description
- Profile picture (if set)
- Creator notes
- Spec version metadata

## Example Usage

### Creating Your Own Character Card

```python
# This is handled automatically by the web interface, but here's what happens:

# 1. Set character details in the UI
#    - Name: "Alice"
#    - Persona: "A friendly and playful AI assistant"
#    - Upload a profile picture

# 2. Click "Export Card"
# 3. Share the resulting PNG file!
```

### Importing from Other Applications

Character cards exported from Text Generation WebUI, SillyTavern, or other compatible applications can be directly imported into BrainDancev2.

Simply:
1. Download the character card PNG from the other application
2. Import it using the "Import Card" button
3. The character is ready to use!

## Compatibility

✅ **Compatible with:**
- Text Generation WebUI (oobabooga)
- SillyTavern
- Tavern AI
- Any application supporting Character Card Spec v2

⚠️ **Note:**
- Only PNG format is supported (JPEG is not compatible with the character card spec)
- Character cards must contain the 'chara' metadata field
- Images without this metadata will be rejected during import

## Development

The character card functionality is implemented in:

- `character_card_utils.py` - Core import/export logic
- `app.py` - Flask endpoints (`/import_character_card`, `/export_character_card`)
- `index.html` - UI elements and JavaScript handlers

To test the character card functionality:
```bash
python test_character_card.py
```

## References

- [Character Card Spec v2 Documentation](https://github.com/malfoyslastname/character-card-spec-v2)
- [Text Generation WebUI Character Import Code](https://github.com/oobabooga/text-generation-webui/blob/main/modules/chat.py)
- [SillyTavern](https://github.com/SillyTavern/SillyTavern)
