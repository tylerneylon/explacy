# -*- coding: utf-8 -*-
from collections import defaultdict

from pprint import pprint

def start_end(arrow):
    start, end = arrow[0].i, arrow[1].i
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx

def sort_from_partial_order(items, cmp):
    """ Interpret cmp(a, b) == 0 as meaning tht the order between a and b is unspecified. """
    pass

def f1(nlp):

    # Parse our sentence.
    doc = nlp(u'The dog ate the delicious pizza.')

    # Build a list of arrow heights (distance from tokens) per token.
    heights = [[] for token in doc]

    # XXX
    for t in doc:
        print '%9s %s' % (t, list(t.children))

    print 'heya'

    # Build a list of arrows as [from, to] pairs.
    arrows = [[src, dst] for src in doc for dst in src.children]

    # Determine the height of each arrow.
    # This is 2 + #arrows_beneath.
    arrow_heights = []
    for i, arrow in enumerate(arrows):
        height = 3
        start, end, mn, mx = start_end(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = start_end(other)
            if start == o_start:
                if mn <= o_end <= mx:
                    height += 1
                    print '%d is over %d' % (i, j)
            elif mn <= o_start <= mx:
                height += 1
                print '%d is over %d' % (i, j)
        arrow_heights.append(height)
    
    print ''
    print 'Arrows; heights:'
    for i in range(len(arrows)):
        print '%s %s %d' % (arrows[i], [arrows[i][0].i, arrows[i][1].i], arrow_heights[i])
    print ''

    # Sort the arrow indexes from lowest (nearest to text) to highest.

    # Build one string per line.
    max_height = max(arrow_heights)
    lines = [list(' ' * max_height) for token in doc]
    for i, arrow in enumerate(arrows):
        start, end, mn, mx = start_end(arrow)
        h = arrow_heights[i]
        lines[start][max_height - h:max_height] = '-' * h
        lines[start][max_height - h] = '+'
        lines[end][max_height - h:max_height] = '-' * h
        lines[end][max_height - h] = '+'
        lines[end][max_height - 1] = '>'
        for j in range(mn + 1, mx):
            lines[j][max_height - h] = '|'

    # Print stuff out.
    for i in range(len(doc)):
        print '%s %s' % (''.join(lines[i]), doc[i])

def start_end2(arrow):
    start, end = arrow['from'].i, arrow['to'].i
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx

def f2(nlp):

    # XXX
    print 'v2'

    # Parse our sentence.
    doc = nlp(u'The dog ate the delicious pizza.')

    # Build a list of arrow heights (distance from tokens) per token.
    heights = [[] for token in doc]

    # XXX
    for t in doc:
        print '%9s %s' % (t, list(t.children))

    print 'heya'

    # Build the arrows.

    # Set the from and to tokens for each arrow.
    arrows = [{'from': src, 'to': dst, 'underset': set()}
              for src in doc
              for dst in src.children]

    # Set the base height; these may increase to allow room for arrowheads after this.
    arrows_with_deps = defaultdict(set)
    for i, arrow in enumerate(arrows):
        num_deps = 0
        start, end, mn, mx = start_end2(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = start_end2(other)
            if ((start == o_start and mn <= o_end <= mx) or
                (start != o_start and mn <= o_start <= mx)):
                num_deps += 1
                print '%d is over %d' % (i, j)
                arrow['underset'].add(j)
        arrow['num_deps_left'] = arrow['num_deps'] = num_deps
        arrows_with_deps[num_deps].add(i)

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

        print ''
        print 'Rendering arrow %d from %s to %s' % (arrow_index, arrow['from'], arrow['to'])

        # Check the height needed.
        height = 3
        if arrow['underset']:
            height = max(arrows[i]['height'] for i in arrow['underset']) + 1
        height = max(height, 3, len(lines[dst]) + 3)
        arrow['height'] = height

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

        # XXX
        # num_arrows_left = 0

        # XXX
        if False:
            print ''
            print 'After processing arrow %d, arrows_with_deps is:' % arrow_index
            pprint(arrows_with_deps)

    arr_chars = {'ew': u'─',
                 'ns': u'│',
                 'en': u'└',
                 'es': u'┌',
                 'enw': u'┴',
                 'esw': u'┬'}

    # XXX
    print ''
    print 'Before conversion, lines:'
    pprint(lines)

    # Convert the character lists into strings.
    max_len = max(len(line) for line in lines)
    for i in range(len(lines)):
        lines[i] = [arr_chars[''.join(sorted(ch))] if type(ch) is set else ch
                    for ch in lines[i]]
        lines[i] = ''.join(reversed(lines[i]))
        lines[i] = ' ' * (max_len - len(lines[i])) + lines[i]

    # Print stuff out.
    print ''
    for i in range(len(doc)):
        print '%s %s' % (lines[i], doc[i])
