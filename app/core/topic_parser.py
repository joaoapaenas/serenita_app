# app/core/topic_parser.py

import logging
import re
from typing import List

log = logging.getLogger(__name__)


def parse_edital_topics(text: str) -> List[str]:
    """
    Parses a block of text from an exam syllabus into a clean list of topic names.
    This is a robust, two-pass parser designed to handle complex formatting.

    Pass 1: Joins multi-line topics into single lines.
    Pass 2: Splits single lines that contain multiple topics.
    """
    if not text:
        return []

    # This pass cleans up the input by joining lines that are continuations of a topic.

    # Regex to detect if a line starts with a topic number (e.g., "1.", "4.2", "7")
    line_start_pattern = re.compile(r'^\s*\d[\d\.]*\s*[.\-]?\s*')

    raw_lines = text.splitlines()
    concatenated_lines = []

    for line in raw_lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # If the line starts with a number, it's a new topic.
        if line_start_pattern.match(stripped_line):
            concatenated_lines.append(stripped_line)
        # Otherwise, it's a continuation of the previous topic.
        elif concatenated_lines:
            # Append it to the last line in our list.
            concatenated_lines[-1] += " " + stripped_line
        else:
            # This is a line without a number prefix at the very beginning of the text.
            # We'll treat it as a valid topic.
            concatenated_lines.append(stripped_line)

    # At this point, `concatenated_lines` looks like this for Input 1:
    # [
    #  '1 Compreensão e interpretação de textos de gêneros variados. 2 Reconhecimento de tipos e gêneros textuais. 3 Domínio da ortografia oficial. 4 Domínio dos mecanismos de coesão textual.',
    #  '4.1 Emprego de elementos de referenciação, substituição e repetição, de conectores e de outros elementos de sequenciação textual.',
    #  '4.2 Emprego de tempos e modos verbais.',
    #  ...
    # ]

    # This pass takes the cleaned lines and splits any that contain multiple topics.

    final_topics = []

    # Regex to split a line by a number pattern, but keeping the delimiter.
    # It looks for whitespace followed by a number pattern. The `()` capture the delimiter.
    split_pattern = re.compile(r'(\s+\d[\d\.]*\s*[.\-]?\s+)')

    for line in concatenated_lines:
        # Split the line by the pattern. This will result in something like:
        # ['1 Compreensão...', ' 2 ', 'Reconhecimento...', ' 3 ', 'Domínio...']
        parts = split_pattern.split(line)

        # Re-assemble the parts into proper topics
        current_topic = ""
        for i, part in enumerate(parts):
            # If the part is a delimiter (a number pattern)
            if split_pattern.match(part):
                # Save the previously assembled topic
                if current_topic:
                    final_topics.append(current_topic.strip())
                # Start the new topic with the number
                current_topic = part.strip()
            else:
                # If it's not a delimiter, it's text. Append it.
                if i == 0:  # The very first part has no preceding delimiter
                    current_topic = part
                else:
                    current_topic += part

        # Add the last assembled topic
        if current_topic:
            final_topics.append(current_topic.strip())

    # Remove the leading numbers from each topic string

    result = []
    for topic in final_topics:
        match = line_start_pattern.match(topic)
        if match:
            # The actual topic is the part of the string after the matched prefix
            clean_topic = topic[match.end():].strip().rstrip('.')
            if clean_topic:
                result.append(clean_topic)
        elif topic:  # Handle cases where a topic might not start with a number
            result.append(topic.strip().rstrip('.'))

    log.info(f"Parser processed input into {len(result)} topics.")
    return result
