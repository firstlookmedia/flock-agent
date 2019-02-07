# -*- coding: utf-8 -*-
import sys
from colored import fg, bg, attr


class Display(object):
    """
    All of the pretty CLI output
    """
    def __init__(self, version):
        self.version = version

    def banner(self):
        s = 'Flock Agent {}'.format(self.version)

        print('{}{}╔{}╗{}'.format( attr('bold'), fg('dark_green_sea'), '═'*(len(s)+2), attr('reset') ))
        print('{}{}║ {}{}{} ║{}'.format( attr('bold'), fg('light_sky_blue_3a'), fg('light_yellow'), s, fg('light_sky_blue_3a'), attr('reset') ))
        print('{}{}╚{}╝{}'.format( attr('bold'), fg('light_sky_blue_3b'), '═'*(len(s)+2), attr('reset') ))

    def status_check(self, message, passed):
        if passed:
            status = '{}{}✓{}'.format(attr('bold'), fg('green'), attr('reset'))
        else:
            status = '{}{}✘{}'.format(attr('bold'), fg('red'), attr('reset'))
        print('{} {}'.format(status, message))

    def info(self, message):
        print('{}{}○{} {}'.format(attr('bold'), fg('light_blue'), attr('reset'), message))

    def error(self, message):
        print('{}{}!{} {}'.format(attr('bold'), fg('red'), attr('reset'), message))

    def install_message(self):
        print('Fix by running: {}sudo flock-agent --install{}'.format(fg('light_blue'), attr('reset')))

    def root_message(self):
        print('This action requires root: {}sudo {}{}'.format(fg('light_blue'), ' '.join(sys.argv), attr('reset')))

    def newline(self):
        print('')
