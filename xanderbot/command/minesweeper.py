import re
from random import sample

from discord import Embed

from command.cmd_default import CmdDefault
from command.common import ReplyPayload, TRANSTAB
from feh.emojilib import EmojiLib as em

EASY_LEN = 9
EASY_WID = 9
EASY_MINES = 10
EASY_STR = 'Easy'
MED_LEN = 17
MED_WID = 15
MED_MINES = 40
MED_STR = 'Intermediate'
HARD_LEN = 32
HARD_WID = 15
HARD_MINES = 99
HARD_STR = 'Hard'
CUSTOM_STR = 'Custom'
MIN_LEN = 9
MAX_LEN = 32
MIN_WID = 9
MAX_WID = 16
MIN_MINES = 10
MULTIPLY_X = re.compile(r'(?<=\d)x(?=\d)')

INT_2_EMOJI = {
    0: '||:zero:||',
    1: '||:one:||',
    2: '||:two:||',
    3: '||:three:||',
    4: '||:four:||',
    5: '||:five:||',
    6: '||:six:||',
    7: '||:seven:||',
    8: '||:eight:||',
    9: '||💥||', # overload this dict because _getattr_ faster than get()
    10: '||💥||',
    11: '||💥||',
    12: '||💥||',
    13: '||💥||',
    14: '||💥||',
    15: '||💥||',
    16: '||💥||',
    17: '||💥||',
}

class Minesweeper(CmdDefault):
    """description of class"""

    help_text = 'No help is available for this command.'

    @staticmethod
    async def cmd(params, user_id):
        length = EASY_LEN
        width = EASY_WID
        mines = EASY_MINES
        difficulty_str = EASY_STR
        for param in params.lower().replace('*', 'by').split(','):
            param = param.translate(TRANSTAB)
            if 'easy' in param:
                length = EASY_LEN
                width = EASY_WID
                mines = EASY_MINES
                difficulty_str = EASY_STR
            elif ('med' in param or 'interm' in param or 'mid' in param
                  or 'normal' in param):
                length = MED_LEN
                width = MED_WID
                mines = MED_MINES
                difficulty_str = MED_STR
            elif 'hard' in param or 'difficult' in param:
                length = HARD_LEN
                width = HARD_WID
                mines = HARD_MINES
                difficulty_str = HARD_STR
            elif 'infern' in param: # maybe ill do something with these someday
                length = HARD_LEN
                width = HARD_WID
                mines = HARD_MINES
                difficulty_str = HARD_STR
            elif 'abys' in param:
                length = HARD_LEN
                width = HARD_WID
                mines = HARD_MINES
                difficulty_str = HARD_STR
            elif ('mine' in param or param.startswith('m')
                  or param.endswith('m')):
                param = (param.replace('mines', '').replace('mine', '')
                         .replace('m', ''))
                if param.isdecimal():
                    mines = int(param)
                    difficulty_str = CUSTOM_STR
            elif 'by' in param:
                dim = param.split('by')
                if len(dim) == 2 and dim[0].isdecimal() and dim[1].isdecimal():
                    length = int(dim[0])
                    width = int(dim[1])
                    difficulty_str = CUSTOM_STR
            elif ('len' in param or 'height' in param or param.startswith('l')
                  or param.endswith('l') or param.startswith('h')
                  or param.endswith('h')):
                param = (param.replace('length', '').replace('len', '')
                         .replace('height', '').replace('l', '')
                         .replace('h', ''))
                if param.isdecimal():
                    length = int(param)
                    difficulty_str = CUSTOM_STR
            elif ('wid' in param or param.startswith('w')
                  or param.endswith('w')):
                param = (param.replace('width', '').replace('wid', '')
                         .replace('w', ''))
                if param.isdecimal():
                    width = int(param)
                    difficulty_str = CUSTOM_STR
            elif MULTIPLY_X.search(param):
                dim = MULTIPLY_X.split(param, maxsplit=1)
                if dim[0].isdecimal() and dim[1].isdecimal():
                    length = int(dim[0])
                    width = int(dim[1])
                    difficulty_str = CUSTOM_STR
        length = max(min(length, MAX_LEN), MIN_LEN)
        width = max(min(width, MAX_WID), MIN_WID)
        mines = max(min(mines, (length - 1) * (width - 1)), MIN_MINES)
        grid = [row[:] for row in [[0] * width] * length]
        for mine in sample(range(length * width), mines):
            row = mine // width
            col = mine % width
            grid[row][col] = 9
            if col > 0:
                grid[row][col - 1] += 1
            if col < width - 1:
                grid[row][col + 1] += 1
            if row > 0:
                grid[row - 1][col] += 1
                if col > 0:
                    grid[row - 1][col - 1] += 1
                if col < width - 1:
                    grid[row - 1][col + 1] += 1
            if row < length - 1:
                grid[row + 1][col] += 1
                if col > 0:
                    grid[row + 1][col - 1] += 1
                if col < width - 1:
                    grid[row + 1][col + 1] += 1
        embed = Embed()
        embed.title = (f'Minesweeper: {difficulty_str} difficulty, '
                       f'{length} x {width}, {mines} mines')
        if length * width * 11 < 2000:
            embed.description = '\n'.join([' '.join([
                INT_2_EMOJI[val] for val in row]) for row in grid]
            )
        else:
            max_field = 1000 // (width * 11) # good enough approximation
            num_fields = length // max_field + (length % max_field > 0)
            disp_grid = [
                '\n'.join([
                    ' '.join([INT_2_EMOJI[val] for val in row])
                    for row in grid[start : start+max_field]])
                for start in range(0, num_fields * max_field, max_field)
            ]
            for segment in disp_grid:
                embed.add_field(name='-', value=segment, inline=False)
        embed.color = em.get_color(None)
        return ReplyPayload(embed=embed)
