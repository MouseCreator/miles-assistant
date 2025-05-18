from typing import List


class Tokenizer:

    def __init__(self):
        pass

    def tokenize(self, command: str) -> List[str]:
        special = [',', '.', ':', ';']
        tokens = []
        current_token = ''

        for char in command.strip():
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            elif char in special:
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens
