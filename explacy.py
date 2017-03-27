# -*- coding: utf-8 -*-

from collections import defaultdict

from pprint import pprint

do_print_debug_info = False

def print_table(rows):
    col_widths = [max(len(s) for s in col) for col in zip(*rows)]
    fmt = ' '.join('%%-%ds' % width for width in col_widths)
    rows.insert(1, [u'─' * width for width in col_widths])
    for row in rows:
        print fmt % tuple(row)

def start_end(arrow):
    start, end = arrow['from'].i, arrow['to'].i
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx

def print_parse_info(nlp, sent):

    assert type(sent) is unicode

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
        num_deps = 0
        start, end, mn, mx = start_end(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = start_end(other)
            if ((start == o_start and mn <= o_end <= mx) or
                (start != o_start and mn <= o_start <= mx)):
                num_deps += 1
                if do_print_debug_info:
                    print '%d is over %d' % (i, j)
                arrow['underset'].add(j)
        arrow['num_deps_left'] = arrow['num_deps'] = num_deps
        arrows_with_deps[num_deps].add(i)

    if do_print_debug_info:
        print ''
        print 'arrows:'
        pprint(arrows)

        print ''
        print 'arrows_with_deps:'
        pprint(arrows_with_deps)

    # Render the arrows in characters. Some heights will be raised to make room for arrowheads.

    lines = [[] for token in doc]
    num_arrows_left = len(arrows)
    while num_arrows_left > 0:

        assert len(arrows_with_deps[0])

        arrow_index = arrows_with_deps[0].pop()
        arrow = arrows[arrow_index]
        src, dst = arrow['from'].i, arrow['to'].i  # TODO Consistentize names.


        # Check the height needed.
        height = 3
        if arrow['underset']:
            height = max(arrows[i]['height'] for i in arrow['underset']) + 1
        height = max(height, 3, len(lines[dst]) + 3)
        arrow['height'] = height

        if do_print_debug_info:
            print ''
            print 'Rendering arrow %d from %s to %s' % (arrow_index, arrow['from'], arrow['to'])
            print '  height = %d' % height

        goes_up = src > dst

        # Draw the outgoing src line.
        if lines[src]:
            lines[src][-1].add('w')
        while len(lines[src]) < height:
            lines[src].append(set(['e', 'w']))
        lines[src][-1] = set(['e', 'n']) if goes_up else set(['e', 's'])

        # Draw the incoming dst line.
        lines[dst].append(u'►')
        while len(lines[dst]) < height:
            lines[dst].append(set(['e', 'w']))
        lines[dst][-1] = set(['e', 's']) if goes_up else set(['e', 'n'])

        # Draw the adjoining vertical line.
        for i in range(min(src, dst) + 1, max(src, dst)):
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

    arr_chars = {'ew': u'─',
                 'ns': u'│',
                 'en': u'└',
                 'es': u'┌',
                 'enw': u'┴',
                 'esw': u'┬'}

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
    print_table(rows)
