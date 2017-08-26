def formatter(text):
    formatted_text = ''
    prev_char = None
    for char in text:
        if not char.islower() \
                and char.isalpha() \
                and len(formatted_text) > 0 \
                and prev_char is not None \
                and prev_char.isalpha():
            formatted_text += ' '
        formatted_text += char
        prev_char = char

    return formatted_text

