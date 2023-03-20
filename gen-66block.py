#!/usr/bin/python3

import pathlib
import json

INCLUDE_PIC = False

if INCLUDE_PIC:
    PNG_BORDER_W = 80
    PNG_BORDER_H = 14
else:
    # template png borders
    PNG_BORDER_W = 0
    PNG_BORDER_H = 0

# width of label space/cable mgmt housing
# LABEL_W = 50
LABEL_W = 80

# total pair count
TOTAL_PAIRS = 25

# width of the pins, and the gaps between them
PIN_WIDTH = 22
PIN_GAP = 16

# distance between the inner pins and the outside housing plate they're mounted on
PIN_BORDER_W = 12
PIN_BORDER_H = 18

# how tall each pin/space row is
ROW_HEIGHT = 8

# logical borders for cursor selection
BDR_W = PIN_GAP/3
BDR_H = 2

WIDTH = LABEL_W*2 + PIN_BORDER_W*2 + PIN_WIDTH*4 + PIN_GAP*3 if not INCLUDE_PIC else 417
HEIGHT = PIN_BORDER_H*2 + ROW_HEIGHT*2*TOTAL_PAIRS*2 if not INCLUDE_PIC else 1200

# colors in the color code
COLORS = {
    'primary': ['white', 'red', 'black', 'yellow', 'violet'],
    'secondary': ['blue', 'orange', 'green', 'brown', 'slate'],
}
COLORS_SHORT = {
    'white': 'WH',
    'red': 'RD',
    'black': 'BK',
    'yellow': 'YE',
    'violet': 'VT',
    'blue': 'BU',
    'orange': 'OG',
    'green': 'GN',
    'brown': 'BN',
    'slate': 'GY'
}
PAIRS = [(p, s) for p in COLORS['primary'] for s in COLORS['secondary']]

def pin(pin_type, x, y, primary, secondary):
    """ generate individual pins"""
    
    fill_core  = primary if pin_type == "tip" else secondary
    fill_strip = secondary if pin_type == "tip" else primary

    # pin, pin stripe
    return f"""
    <g class="pin pin-{pin_type} pri-{primary} sec-{secondary}" data-primary="{primary}" data-secondary="{secondary}">
        <rect
        class="pin-core rj-{fill_core}"
        x="{x}px" y="{y}px"
        width="{PIN_WIDTH}px" height="{ROW_HEIGHT}px"
        ></rect>
        <rect
        class="pin-stripe rj-{fill_strip}"
        x="{x + PIN_WIDTH/8*5}px" y="{y}px"
        width="{PIN_WIDTH/8}px" height="{ROW_HEIGHT}px"
        transform="skewX(-30)"
        ></rect>
    </g>
    """

def pin_group(side, pair_idx, x, y, lbl=None):
    primary, secondary = PAIRS[pair_idx]
    if side == 'a':
        border_x = x-PIN_BORDER_W
        label_x = x - PIN_BORDER_W - LABEL_W + BDR_W
    else:
        border_x = x - PIN_GAP/2
        label_x = x + PIN_WIDTH*2 + PIN_BORDER_W + PIN_GAP + BDR_W
    
    default_label = True
    label_top = f'({side.upper()}-{pair_idx+1}) {COLORS_SHORT[primary]}/{COLORS_SHORT[secondary]}'
    label_btm = ''

    if lbl is None:
        pass
    elif type(lbl) == list and len(lbl) == 2 and all(type(e) == str for e in lbl):
        label_top = lbl[0]
        label_btm = lbl[1]
        default_label = False
    else:
        print(f'unknown type/value for label {side.upper()}-{(pair_idx+1).zfill(2)}. expected a list with one or two strings.')
    
    return f"""
        <g class="pin-group" id="side_{side}_pair_{primary}_{secondary}">
        <title>Pair: {primary}/{secondary} on side {side.upper()}</title>
        
        <g class="pin-label {'label-default' if default_label else 'label-custom'}">
            <text class="pin-label-top" x="{label_x}px" y="{y}px" dominant-baseline="hanging" style="font-size: 10px;">{label_top}</text>
            <text class="pin-label-bottom" x="{label_x}px" y="{y + ROW_HEIGHT*2 }px" dominant-baseline="hanging" style="font-size: 10px;">{label_btm}</text>
        </g>

        <rect class="pin-group-bkg" x="{x - BDR_W}px" y="{y - BDR_H}" width="{PIN_WIDTH*2+PIN_GAP + BDR_W*2}px" height="{ROW_HEIGHT*3+BDR_H*2}px"></rect>
        
        <g class="pin-pair">
            <g class="pin-pair-connection pin-pair-tip" id="side_{side}_pair_{primary}_{secondary}_tip">
            {pin('tip', x, y, primary, secondary)}
            {pin('tip', x + PIN_WIDTH+PIN_GAP, y, primary, secondary) }
            <rect class="pin-bridge" x="{x+PIN_WIDTH}px" y="{y+ROW_HEIGHT/8*3}px" width="{PIN_GAP}px" height="{ROW_HEIGHT/4}px"></rect>
            </g>

            <g class="pin-pair-connection pin-pair-ring"  id="side_{side}_pair_{primary}_{secondary}_ring">
            {pin('ring', x, y + ROW_HEIGHT*2, primary, secondary)}
            {pin('ring', x + PIN_WIDTH+PIN_GAP, y + ROW_HEIGHT*2, primary, secondary) }
            <rect class="pin-bridge" x="{x+PIN_WIDTH}px" y="{y+ROW_HEIGHT*2 + ROW_HEIGHT/8*3}px" width="{PIN_GAP}px" height="{ROW_HEIGHT/4}px"></rect>
            </g>
        </g>

        <rect class="pin-group-border" x="{border_x}px" y="{y-ROW_HEIGHT/2}px" width="{PIN_BORDER_W + PIN_WIDTH*2 + PIN_GAP*1.5}px" height="{ROW_HEIGHT*4}px"></rect>
        </g>"""

def pin_groups(labels):
    for i in range(len(PAIRS)):
        x_left = PNG_BORDER_W + LABEL_W + PIN_BORDER_W
        x_right = PNG_BORDER_W + LABEL_W + PIN_BORDER_W + PIN_WIDTH*2 + PIN_GAP*2
        y = PNG_BORDER_H + PIN_BORDER_H + i*ROW_HEIGHT*4
        lbl_key_a = 'A-' + str(i+1).zfill(2)
        lbl_key_b = 'B-' + str(i+1).zfill(2)
        yield pin_group('a', i, x_left, y, lbl=labels.get(lbl_key_a))
        yield pin_group('b', i, x_right, y, lbl=labels.get(lbl_key_b))

def housing_elems():
    PANEL_HEIGHT = PIN_BORDER_H*2 + ROW_HEIGHT*2*TOTAL_PAIRS*2-ROW_HEIGHT
    BOUNDS = [
        [ # main backing
          PNG_BORDER_W + LABEL_W,
          PNG_BORDER_H,
          PIN_BORDER_W*2 + PIN_WIDTH*4 + PIN_GAP*3,
          PANEL_HEIGHT,
        ],
        [ # left label area
          PNG_BORDER_W,
          PNG_BORDER_H,
          LABEL_W,
          PANEL_HEIGHT,
        ],
        [ # right label area
          PNG_BORDER_W + LABEL_W + PIN_BORDER_W*2 + PIN_WIDTH*4 + PIN_GAP*3,
          PNG_BORDER_H,
          LABEL_W,
          PANEL_HEIGHT,
        ],
      ]
    yield from [
        f'<rect x="{x}px" y="{y}px" width="{w}px" height="{h}px"></rect>'
        for x,y,w,h in BOUNDS
    ]

def main():
    labels = json.loads(pathlib.Path('block66-labels.json').read_text())
    cfgclses = list()

    ELEMS_PINS_STR = '\n\t'.join(pin_groups(labels["pins"]))
    ELEMS_HOUSING_STR = '\n\t'.join(housing_elems())

    elem_img = '' if not INCLUDE_PIC else f"""
    <image
            x="0" y="0" width="{WIDTH}px" height="{HEIGHT}px"
            href="block66-model-front.png"
            transform="scale(1 0.975) translate(-80 -12)"
        />
    """

    styling = pathlib.Path('styling-66block.css').read_text()
    if not labels["colored_pins"]:
        cfgclses.append('greypins')

    print(f"""
        <svg id="block66" width="{WIDTH}" height="{HEIGHT}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" >
        {elem_img}
        <g id="housing">{ELEMS_HOUSING_STR}</g>
        <g id="pins" class="{' '.join(cfgclses)}">{ELEMS_PINS_STR}</g>
        <style>
        {styling}
        </style>
        </svg>
    """)
    pass

if __name__ == "__main__":
    main()