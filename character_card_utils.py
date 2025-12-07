"""
Character Card Utilities for Tavern/SillyTavern Character Card Spec v2

This module provides functions to import and export character cards in the
Tavern/SillyTavern format, which embeds character data as base64-encoded JSON
in PNG image metadata (tEXt/iTXt chunks).
"""

import base64
import json
import io
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def import_character_card(image_data, user_name='YOU'):
    """
    Import a character card from a PNG image with embedded Tavern metadata.
    
    Args:
        image_data: Binary image data (bytes) or file-like object
        user_name: Name to use for {{user}} placeholder replacement (default: 'YOU')
        
    Returns:
        dict: A dictionary containing:
            - 'character_data': Parsed character information
            - 'image': PIL Image object
            - 'success': Boolean indicating success
            - 'error': Error message if any
    """
    try:
        # Open the image
        if isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            img = Image.open(image_data)
        
        # Check if the 'chara' metadata exists
        if 'chara' not in img.info:
            return {
                'success': False,
                'error': 'No character card metadata found in image. Make sure this is a valid Tavern/SillyTavern character card.',
                'image': img,
                'character_data': None
            }
        
        # Decode the base64-encoded JSON
        chara_data_b64 = img.info['chara']
        chara_data_json = base64.b64decode(chara_data_b64)
        character_card = json.loads(chara_data_json)
        
        # Map Tavern fields to internal format with custom user name
        mapped_data = map_tavern_to_internal(character_card, user_name)
        
        return {
            'success': True,
            'error': None,
            'image': img,
            'character_data': mapped_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error importing character card: {str(e)}',
            'image': None,
            'character_data': None
        }


def replace_placeholders(text, char_name='BOT', user_name='YOU'):
    """
    Replace {{char}} and {{user}} placeholders in text.
    
    Args:
        text: String containing placeholders
        char_name: Name to replace {{char}} with
        user_name: Name to replace {{user}} with
        
    Returns:
        str: Text with placeholders replaced
    """
    if not text:
        return text
    
    # Replace placeholders (case-insensitive using regex)
    import re
    text = re.sub(r'\{\{char\}\}', char_name, text, flags=re.IGNORECASE)
    text = re.sub(r'\{\{user\}\}', user_name, text, flags=re.IGNORECASE)
    
    return text


def map_tavern_to_internal(tavern_card, user_name='YOU'):
    """
    Map Tavern/SillyTavern card fields to internal format.
    
    Tavern cards typically have fields like:
    - name: Character name
    - description: Character description/personality
    - first_mes: First message/greeting
    - mes_example: Example messages
    - scenario: Scenario description
    - personality: Personality traits
    
    Args:
        tavern_card: Dict with Tavern format fields
        user_name: Name to use for {{user}} placeholder replacement
        
    Returns:
        dict: Mapped character data for internal use
    """
    # Check if data is wrapped in a 'data' field (some card versions do this)
    if 'data' in tavern_card:
        tavern_card = tavern_card['data']
    
    # Extract basic fields
    ai_name = tavern_card.get('name', 'BOT')
    
    # Build persona description from available fields
    persona_parts = []
    
    if 'personality' in tavern_card and tavern_card['personality']:
        persona_parts.append(tavern_card['personality'])
    
    if 'description' in tavern_card and tavern_card['description']:
        persona_parts.append(tavern_card['description'])
    
    persona_desc = ' '.join(persona_parts) if persona_parts else 'An AI companion'
    
    # Replace placeholders in persona description
    persona_desc = replace_placeholders(persona_desc, ai_name, user_name)
    
    # Get first message/greeting and replace placeholders
    greeting = tavern_card.get('first_mes', tavern_card.get('greeting', ''))
    greeting = replace_placeholders(greeting, ai_name, user_name)
    
    # Get scenario and replace placeholders
    scenario = tavern_card.get('scenario', '')
    scenario = replace_placeholders(scenario, ai_name, user_name)
    
    # Get example messages and replace placeholders
    mes_example = tavern_card.get('mes_example', '')
    mes_example = replace_placeholders(mes_example, ai_name, user_name)
    
    # Return mapped data
    return {
        'ai_name': ai_name,
        'persona_desc': persona_desc,
        'greeting': greeting,
        'scenario': scenario,
        'mes_example': mes_example,
        'raw_card': tavern_card  # Keep original for reference
    }


def export_character_card(character_data, image=None):
    """
    Export character data as a Tavern-compatible character card PNG.
    
    Args:
        character_data: Dict with character information:
            - ai_name: Character name
            - persona_desc: Character description/personality
            - greeting: (optional) First message
            - scenario: (optional) Scenario description
        image: PIL Image object to embed data into, or None to create a default
        
    Returns:
        bytes: PNG image data with embedded character card metadata
    """
    try:
        # Create Tavern-format card
        tavern_card = map_internal_to_tavern(character_data)
        
        # Convert to JSON and base64 encode
        card_json = json.dumps(tavern_card, ensure_ascii=False)
        card_b64 = base64.b64encode(card_json.encode('utf-8')).decode('ascii')
        
        # Create or use provided image
        if image is None:
            # Create a simple default image if none provided
            image = Image.new('RGB', (400, 600), color='#282a36')
        
        # Create PNG metadata
        pnginfo = PngInfo()
        pnginfo.add_text('chara', card_b64)
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format='PNG', pnginfo=pnginfo)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        raise Exception(f'Error exporting character card: {str(e)}')


def map_internal_to_tavern(character_data):
    """
    Map internal format to Tavern/SillyTavern card format.
    
    Args:
        character_data: Dict with internal format fields
        
    Returns:
        dict: Tavern-format character card
    """
    return {
        'name': character_data.get('ai_name', 'BOT'),
        'description': character_data.get('persona_desc', ''),
        'personality': character_data.get('persona_desc', ''),
        'first_mes': character_data.get('greeting', ''),
        'scenario': character_data.get('scenario', ''),
        'mes_example': character_data.get('mes_example', ''),
        'creator_notes': 'Exported from BrainDancev2',
        'system_prompt': '',
        'post_history_instructions': '',
        'tags': [],
        'creator': 'BrainDancev2',
        'character_version': '1.0',
        'spec': 'chara_card_v2',
        'spec_version': '2.0'
    }


def open_image_safely(image_path_or_data):
    """
    Safely open an image file or data.
    
    Utility function for safely opening images from various sources.
    Currently not used internally but provided as a convenience function
    for external scripts or future extensions.
    
    Args:
        image_path_or_data: File path (str), bytes, or file-like object
        
    Returns:
        PIL.Image: Opened image or None if failed
    """
    try:
        if isinstance(image_path_or_data, str):
            return Image.open(image_path_or_data)
        elif isinstance(image_path_or_data, bytes):
            return Image.open(io.BytesIO(image_path_or_data))
        else:
            return Image.open(image_path_or_data)
    except Exception as e:
        print(f"Error opening image: {e}")
        return None
