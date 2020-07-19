"""
Tagging utilities - from user tag input parsing to tag cloud
calculation.
"""
import math

from django.db.models.query import QuerySet
from django.utils.encoding import force_str
from django.utils.translation import gettext as _

# Font size distribution algorithms
LOGARITHMIC, LINEAR = 1, 2


def parse_tag_input(input):
    """
    Parses tag input, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas.
    Returns a sorted list of unique tag names.
    """
    if not input:
        return []

    input = force_str(input)

    # Special case - if there are no commas or double quotes in the
    # input, we don't *do* a recall... I mean, we know we only need to
    # split on spaces.
    if "," not in input and '"' not in input:
        words = list(set(split_strip(input, " ")))
        words.sort()
        return words

    words = []
    buffer = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(input)
    try:
        while 1:
            c = next(i)
            if c == '"':
                if buffer:
                    to_be_split.append("".join(buffer))
                    buffer = []
                # Find the matching quote
                open_quote = True
                c = next(i)
                while c != '"':
                    buffer.append(c)
                    c = next(i)
                if buffer:
                    word = "".join(buffer).strip()
                    if word:
                        words.append(word)
                    buffer = []
                open_quote = False
            else:
                if not saw_loose_comma and c == ",":
                    saw_loose_comma = True
                buffer.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if buffer:
            if open_quote and "," in buffer:
                saw_loose_comma = True
            to_be_split.append("".join(buffer))
    if to_be_split:
        if saw_loose_comma:
            delimiter = ","
        else:
            delimiter = " "
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words


def split_strip(input, delimiter=","):
    """
    Splits ``input`` on ``delimiter``, stripping each resulting string
    and returning a list of non-empty strings.
    """
    words = [w.strip() for w in input.split(delimiter)]
    return [w for w in words if w]
