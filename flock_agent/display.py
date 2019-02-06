from colored import fg, bg, attr

def banner(version):
    s = 'Flock Agent {}'.format(version)

    print('{}{}╔{}╗{}'.format( attr('bold'), fg('dark_green_sea'), '═'*(len(s)+2), attr('reset') ))
    print('{}{}║ {}{}{} ║{}'.format( attr('bold'), fg('light_sky_blue_3a'), fg('light_yellow'), s, fg('light_sky_blue_3a'), attr('reset') ))
    print('{}{}╚{}╝{}'.format( attr('bold'), fg('light_sky_blue_3b'), '═'*(len(s)+2), attr('reset') ))

def status_check(message, passed):
    if passed:
        status = '{}{}✓{}'.format(attr('bold'), fg('green'), attr('reset'))
    else:
        status = '{}{}✘{}'.format(attr('bold'), fg('red'), attr('reset'))
    print('{} {}'.format(status, message))

def info(message):
    print('{}{}○{} {}'.format(attr('bold'), fg('light_blue'), attr('reset'), message))

def error(message):
    print('{}{}!{} {}'.format(attr('bold'), fg('red'), attr('reset'), message))

def install_message():
    print('Fix by running: {}flock-agent --install{}'.format(fg('light_blue'), attr('reset')))
