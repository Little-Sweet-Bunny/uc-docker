import argparse
import getpass
from src.driver import ChromeDriverFactory, MsEdgeDriverFactory, UChromeDriverFactory


class PasswordAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            print(
                '\nWarning: User set the password in plain text. Use `-p` with no arguments next time for better security.'
            )
            setattr(namespace, self.dest, values)
        else:
            prompt = f'{option_string}:'
            setattr(namespace, self.dest, getpass.getpass(prompt=prompt))


class DriverAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        mapping = {"chrome": ChromeDriverFactory, "msedge": MsEdgeDriverFactory, 'uchrome': UChromeDriverFactory}
        setattr(namespace, self.dest, mapping[value])


def print_args(args):
    protected_fields = ('password', 'telegram_api_token')
    d_args = vars(args).copy()
    for protected_field in protected_fields:
        if protected_field in d_args:
            del (d_args[protected_field])
    result = ", ".join(
        str(key) + '=' + str(value) for key, value in d_args.items()
    )

    print(f'\nCommand line options selected:\n{result}')


def check_is_valid_email_pw_combo(args):
    if (args.email and not args.password) or (not args.email and args.password):
        if args.email:
            included_arg = 'email'
            missing_arg = 'password'
        else:
            included_arg = 'password'
            missing_arg = 'email'
        raise RuntimeError(
            f'Missing {missing_arg} argument. You included {included_arg} argument, you must also include {missing_arg} argument.'
        )


def get_parent_parser():
    ''' parent parser - store default args '''
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        '-e', '--email', help='email to use, supersedes the config email'
    )
    parent_parser.add_argument(
        '-p',
        '--password',
        action=PasswordAction,
        nargs='?',
        help=
        "the email password to use. Use -p with no argument to trigger a secure pw prompt"
    )
    return parent_parser


def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def parse_setup_args():
    ''' Responsible for parsing setup.py args '''
    # main search arguments
    parent_parser = get_parent_parser()
    setup_parser = argparse.ArgumentParser(parents=[parent_parser])

    # telegram config
    setup_parser.add_argument(
        '-tu', '--telegram_userid', help='telegram userid to store in config'
    )
    setup_parser.add_argument(
        '-ta',
        '--telegram_api_token',
        action=PasswordAction,
        nargs='?',
        help="telegram api token to store in config, use with no argument to trigger a secure prompt",
    )

    # discord config
    setup_parser.add_argument(
        '-d',
        '--discord-webhook-url',
        nargs='?',
        help='Discord channel webhook. Can be generated by channel settings > integrations > webhooks > New Webhook > Name doesnt matter, copy the Webhook URL and rerun "setup.py -d <webhook URL>"'
    )

    # google sheets config
    setup_parser.add_argument(
        '-gssi',
        '--google_sheets_sheet_id',
        help='The sheetId that you want to write to. More info here: https://stackoverflow.com/a/36062068'
    )
    setup_parser.add_argument(
        '-gstn',
        '--google_sheets_tab_name',
        help="Name of the google sheet tab to write to",
    )

    args = setup_parser.parse_args()
    check_is_valid_email_pw_combo(args)
    return args


def parse_search_args():
    '''
    Search options satisfy this criteria:
    One- and only one- of the args in the search_group must be used
    Source: https://stackoverflow.com/a/15301183

    Email and pw, using getpass, https://stackoverflow.com/a/28610617

    Headless, https://stackoverflow.com/a/15008806
    '''
    # main search arguments
    parent_parser = get_parent_parser()
    search_parser = argparse.ArgumentParser(parents=[parent_parser])

    search_group = search_parser.add_mutually_exclusive_group()
    search_group.add_argument(
        '-r',
        '--remaining',
        const='remaining',
        action='store_const',
        dest='search_type',
        help="run today's remaining searches, this is the default search type"
    )
    search_group.add_argument(
        '-w',
        '--web',
        const='web',
        action='store_const',
        dest='search_type',
        help='run web search'
    )
    search_group.add_argument(
        '-m',
        '--mobile',
        const='mobile',
        action='store_const',
        dest='search_type',
        help='run mobile search'
    )
    search_group.add_argument(
        '-b',
        '--both',
        const='both',
        action='store_const',
        dest='search_type',
        help='run web and mobile search'
    )
    search_group.add_argument(
        '-o',
        '--offers',
        const='offers',
        action='store_const',
        dest='search_type',
        help='run offers'
    )
    search_group.add_argument(
        '-pc',
        '--punchcard',
        const='punch card',
        action='store_const',
        dest='search_type',
        help='run punch card'
    )
    search_group.add_argument(
        '-a',
        '--all',
        const='all',
        action='store_const',
        dest='search_type',
        help='run web, mobile, offers, and punch cards'
    )

    search_parser.add_argument(
        '-d',
        '--driver',
        dest='driver',
        type=str.lower,
        choices=['chrome', 'msedge', 'uchrome'],
        action=DriverAction
    )

    headless_group = search_parser.add_mutually_exclusive_group()
    headless_group.add_argument(
        '-hl',
        '--headless',
        dest='headless',
        action='store_true',
        help='run browser in headless mode (in the background), this is the default'
    )
    headless_group.add_argument(
        '-nhl',
        '--no-headless',
        dest='headless',
        action='store_false',
        help='run browser in non-headless mode'
    )

    cookies_group = search_parser.add_mutually_exclusive_group()
    cookies_group.add_argument(
        '-c',
        '--cookies',
        dest='cookies',
        action='store_true',
        help='run browser with cookies'
    )
    cookies_group.add_argument(
        '-nc',
        '--no-cookies',
        dest='cookies',
        action='store_false',
        help='run browser without cookies, this is the default'
    )

    nosandbox_group = search_parser.add_mutually_exclusive_group()
    nosandbox_group.add_argument(
        '-sb',
        '--sandbox',
        dest='nosandbox',
        action='store_false',
        help='run browser in sandbox mode, this is the default'
    )

    nosandbox_group.add_argument(
        '-nsb',
        '--no-sandbox',
        dest='nosandbox',
        action='store_true',
        help='run browser in no-sandbox mode'
    )

    telegram_group = search_parser.add_mutually_exclusive_group()
    telegram_group.add_argument(
        '-t',
        '--telegram',
        dest='telegram',
        action='store_true',
        help='send notification to telegram using setup.py credentials'
    )
    telegram_group.add_argument(
        '-nt',
        '--no-telegram',
        dest='telegram',
        action='store_false',
        help='do not send notifications to telegram, this is the default'
    )

    discord_group = search_parser.add_mutually_exclusive_group()
    discord_group.add_argument(
        '-di',
        '--discord',
        dest='discord',
        action='store_true',
        help='send notification to discord using setup.py credentials'
    )
    discord_group.add_argument(
        '-ndi',
        '--no-discord',
        dest='discord',
        action='store_false',
        help='do not send notifications to discord, this is the default'
    )

    google_sheets_group = search_parser.add_mutually_exclusive_group()
    google_sheets_group.add_argument(
        '-gs',
        '--google-sheets',
        dest='google_sheets',
        action='store_true',
        help='add row to Google Sheets'
    )
    google_sheets_group.add_argument(
        '-ngs',
        '--no-google-sheets',
        dest='google_sheets',
        action='store_false',
        help='do not add row to Google Sheets, this is the default'
    )

    search_parser.add_argument(
        '-gtg',
        '--google-trends-geo',
        dest='google_trends_geo',
        nargs='?',
        default='US',
        help="two-letter country code to use for Google Trends API 'geo' argument. Please note: not all country codes are supported by the API. Default is 'US'."
    )

    search_parser.set_defaults(
        search_type='remaining',
        driver=UChromeDriverFactory,
        headless=True,
        cookies=False,
        nosandbox=False,
        telegram=False,
        google_sheets=False
    )
    if is_notebook():
        args = search_parser.parse_args([])
    else:
        args = search_parser.parse_args()
    check_is_valid_email_pw_combo(args)

    print_args(args)
    return args


if __name__ == '__main__':
    args = parse_search_args()
