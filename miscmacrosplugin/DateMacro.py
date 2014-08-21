'''
Created on 13 okt 2011

@author: enmarkp
'''
from trac.wiki.macros import WikiMacroBase
from trac.wiki.api import parse_args
import dateutil.parser

class DateMacro(WikiMacroBase):
    """ Display a date in current user's timezone. E.g., `[[Date(2011-10-14 13:00 GMT)]]`
        will show as 2011-10-14 15:00 CEST for a user in the !Europe/Stockholm (summer) timezone.
        
        Optional keyword "format" may be used. Default format is "%Y-%m-%d %H:%M %Z". See 
        [http://docs.python.org/library/time.html#time.strftime python datetime documentation] for format details.
        """
    def expand_macro(self, formatter, name, content):
        
        args, kw = parse_args(content)
        fmt = 'format' in kw and kw['format'] or '%Y-%m-%d %H:%M %Z'
        d = args and args[0].strip() or None
        if not d:
            return ''
        try:
            d = dateutil.parser.parse(d)
        except ValueError:
            raise Exception("Failed to parse date '%s', try using 'YYYY-MM-DD HH:MM +H:00'" % d)
        return d.astimezone(formatter.req.tz).strftime(fmt)