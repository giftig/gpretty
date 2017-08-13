import logging
import optparse


class ColourMixin(object):
    """Mix this into classes to provide nice colourised text support"""
    _default_colours = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'grey': '\033[90m',
        'reset': '\033[0m'
    }
    _colours = _default_colours.copy()

    def _deactivate_colours(self):
        self._colours = {
            k: '' for k, v in self._default_colours.iteritems()
        }

    def _activate_colours(self):
        self._colours = self._default_colours.copy()

    def with_colours(self, data):
        """
        Insert colours into the given data dict. Intended to allow easy
        formatting of colourised strings. Used something like:

            print '%(red)sUh oh... %(msg)s%(reset)s' % (
                self.with_colours({'msg': 'Something bad happened!'})
            )
        """
        data.update(self._colours)
        return data

    def colourise(self, msg, colour='yellow'):
        """
        Convenience method to turn the given string a particular colour.
        """
        return '%s%s%s' % (self._colours[colour], msg, self._colours['reset'])


class ColouriseCommand(ColourMixin):
    """Mix this into management commands to provide nice colouring control"""
    colourise_option = optparse.make_option(
        '--nocolourise', dest='colourise', action='store_false',
        help='Do not colourise output'
    )

    @property
    def log_handler(outer):
        class LogHandler(logging.Handler):
            """
            A custom log handler to log colourised console output when using
            management commands
            """
            def emit(self, record):
                msg = record.msg % record.args
                if record.exc_info is not None:
                    msg = '%s %s' % (msg, record.exc_info)

                if record.levelno < logging.INFO:
                    outer._print(msg, 'grey')
                elif record.levelno < logging.ERROR:
                    outer._print(msg, 'yellow')
                else:
                    outer._print(msg, 'red')

        outer._log_handler = getattr(
            outer, '_log_handler', None
        ) or LogHandler()
        return outer._log_handler

    def configure_logger(self, logger):
        """
        Set up the logger to make verbosity handling prettier

        This assumes that self.verbosity is set based on parsed arguments
        """
        logger.addHandler(self.log_handler)
        logger.setLevel(
            [logging.ERROR, logging.INFO, logging.DEBUG][
                min(2, self.verbosity)
            ]
        )

    def handle_colourise(self, *args, **options):
        """Strip colours if colourise is false"""
        if options.get('colourise', True) is False:
            self._deactivate_colours()
        else:
            self._activate_colours()

    def _print(self, msg, colour):
        print self.colourise(msg, colour)
