from random import choice

from command.cmd_default import CmdDefault
from command.common import DiscordData

class Donate(CmdDefault):
    """description of class"""

    CHARITIES = (
        ('Extra Life', 'https://www.extra-life.org/'),
        ('Games Aid', 'https://www.gamesaid.org/'),
        ('Make-A-Wish', 'https://wish.org/'),
        ('Red Cross', 'https://www.redcross.org/'),
        ('Save the Children', 'https://www.savethechildren.org/'),
        ('War Child', 'http://www.warchild.org/'),
        ('Worldreader', 'https://www.worldreader.org/'),
        ('World Wildlife Fund', 'https://www.worldwildlife.org/'),
        ('Zidisha', 'https://www.zidisha.org/'),
        ('Doctors Without Borders (Médecins Sans Frontières)', 'https://www.msf.org/'),
        ('National Institute on Mental Illness', 'https://www.nami.org/'),
        ('Child Rights and You', 'https://www.cry.org/'),
        ('Compassion', 'https://www.compassion.com/about/about-us.htm'),
        ('Human Rights Campaign', 'https://www.hrc.org/')
    )


    DONATE_TEXT = (
        'Please consider donating to {}:\n{}'
    )


    help_text = (
        'The ``donate`` command shows how you can contribute.\n\n'
        'Usage: ``f?donate``'
    )


    @staticmethod
    async def cmd(params):
        charity = choice(Donate.CHARITIES)
        return (
            Donate.DONATE_TEXT.format(*charity),
            None, None
        )
