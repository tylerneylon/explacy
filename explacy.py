# -*- coding: utf-8 -*-
#
# Box-drawing characters are the thin variants, and can be found here:
# https://en.wikipedia.org/wiki/Box-drawing_character
#
""" explacy.py

    This module uses unicode box-drawing characters to draw the spacy-derived
    dependency tree of whichever (unicode) string you provide as input.

    Usage:

        import explacy
        import spacy

        nlp = spacy.load('en')

        explacy.print_parse_info(nlp, 'The salad was surprisingly tasty.')

        # Use a unicode string as input (eg u'The dog jumped.') in Python 2.

    Example tree rendering:

        Dep tree Token        Dep type Lemma        Part of Sp
        ──────── ──────────── ──────── ──────────── ──────────
            ┌─►  The          det      the          DET
         ┌─►└──  salad        nsubj    salad        NOUN
        ┌┼─────  was          ROOT     be           VERB
        ││  ┌─►  surprisingly advmod   surprisingly ADV
        │└─►└──  tasty        acomp    tasty        ADJ
        └─────►  .            punct    .            PUNCT
"""

import sys
from collections import defaultdict

from pprint import pprint

_do_print_debug_info = False

def _print_table(rows):
    col_widths = [max(len(s) for s in col) for col in zip(*rows)]
    fmt = ' '.join('%%-%ds' % width for width in col_widths)
    rows.insert(1, ['─' * width for width in col_widths])
    for row in rows:
        # Uncomment this version to see code points printed out (for debugging).
        # print(list(map(hex, map(ord, list(fmt % tuple(row))))))
        print(fmt % tuple(row))

def _start_end(arrow):
    start, end = arrow['from'].i, arrow['to'].i
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx

def print_parse_info(nlp, sent):
    """ Print the dependency tree of `sent` (sentence), along with the lemmas
        (de-inflected forms) and parts-of-speech of the words.

        The input `sent` is expected to be a unicode string (of type unicode in
        Python 2; of type str in Python 3). The input `nlp` (for natural
        language parser) is expected to be the return value from a call to
        spacy.load(), in other words, it's the callable instance of a spacy
        language model.
    """

    unicode_type = unicode if sys.version_info[0] < 3 else str
    assert type(sent) is unicode_type

    # Parse our sentence.
    doc = nlp(sent)

    # Build a list of arrow heights (distance from tokens) per token.
    heights = [[] for token in doc]

    # Build the arrows.

    # Set the from and to tokens for each arrow.
    arrows = [{'from': src, 'to': dst, 'underset': set()}
              for src in doc
              for dst in src.children]

    # Set the base height; these may increase to allow room for arrowheads after this.
    arrows_with_deps = defaultdict(set)
    for i, arrow in enumerate(arrows):
        if _do_print_debug_info:
            print('Arrow %d: "%s" -> "%s"' % (i, arrow['from'], arrow['to']))
        num_deps = 0
        start, end, mn, mx = _start_end(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = _start_end(other)
            if ((start == o_start and mn <= o_end <= mx) or
                (start != o_start and mn <= o_start <= mx)):
                num_deps += 1
                if _do_print_debug_info:
                    print('%d is over %d' % (i, j))
                arrow['underset'].add(j)
        arrow['num_deps_left'] = arrow['num_deps'] = num_deps
        arrows_with_deps[num_deps].add(i)

    if _do_print_debug_info:
        print('')
        print('arrows:')
        pprint(arrows)

        print('')
        print('arrows_with_deps:')
        pprint(arrows_with_deps)

    # Render the arrows in characters. Some heights will be raised to make room for arrowheads.

    lines = [[] for token in doc]
    num_arrows_left = len(arrows)
    while num_arrows_left > 0:

        assert len(arrows_with_deps[0])

        arrow_index = arrows_with_deps[0].pop()
        arrow = arrows[arrow_index]
        src, dst, mn, mx = _start_end(arrow)

        # Check the height needed.
        height = 3
        if arrow['underset']:
            height = max(arrows[i]['height'] for i in arrow['underset']) + 1
        height = max(height, 3, len(lines[dst]) + 3)
        arrow['height'] = height

        if _do_print_debug_info:
            print('')
            print('Rendering arrow %d: "%s" -> "%s"' % (arrow_index,
                                                        arrow['from'],
                                                        arrow['to']))
            print('  height = %d' % height)

        goes_up = src > dst

        # Draw the outgoing src line.
        if lines[src] and len(lines[src]) < height:
            lines[src][-1].add('w')
        while len(lines[src]) < height - 1:
            lines[src].append(set(['e', 'w']))
        if len(lines[src]) < height:
            lines[src].append({'e'})
        lines[src][height - 1].add('n' if goes_up else 's')

        # Draw the incoming dst line.
        lines[dst].append(u'►')
        while len(lines[dst]) < height:
            lines[dst].append(set(['e', 'w']))
        lines[dst][-1] = set(['e', 's']) if goes_up else set(['e', 'n'])

        # Draw the adjoining vertical line.
        for i in range(mn + 1, mx):
            while len(lines[i]) < height - 1:
                lines[i].append(' ')
            lines[i].append(set(['n', 's']))

        # Update arrows_with_deps.
        for arr_i, arr in enumerate(arrows):
            if arrow_index in arr['underset']:
                arrows_with_deps[arr['num_deps_left']].remove(arr_i)
                arr['num_deps_left'] -= 1
                arrows_with_deps[arr['num_deps_left']].add(arr_i)

        num_arrows_left -= 1

    arr_chars = {'ew'  : u'─',
                 'ns'  : u'│',
                 'en'  : u'└',
                 'es'  : u'┌',
                 'ens' : u'├',
                 'enw' : u'┴',
                 'ensw': u'┼',
                 'esw' : u'┬'}

    # Convert the character lists into strings.
    max_len = max(len(line) for line in lines)
    for i in range(len(lines)):
        lines[i] = [arr_chars[''.join(sorted(ch))] if type(ch) is set else ch
                    for ch in lines[i]]
        lines[i] = ''.join(reversed(lines[i]))
        lines[i] = ' ' * (max_len - len(lines[i])) + lines[i]

    # Compile full table to print out.
    rows = [['Dep tree', 'Token', 'Dep type', 'Lemma', 'Part of Sp']]
    for i, token in enumerate(doc):
        rows.append([lines[i], token, token.dep_, token.lemma_, token.pos_])
    _print_table(rows)
