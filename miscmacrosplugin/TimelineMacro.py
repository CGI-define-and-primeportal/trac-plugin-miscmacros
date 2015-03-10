# Author: Danny Milsom
# (C) CGI 2013
# 0.1

from trac.core import *
from trac.web.chrome import Chrome
from trac.wiki.macros import WikiMacroBase
from trac.timeline.api import ITimelineEventProvider
from trac.timeline.web_ui import TimelineModule
from trac.util.datefmt import to_utimestamp
from trac.mimeview import Context
from trac.util.datefmt import format_date, pretty_age
from sidebarplugin.api import ISidebarBoxProvider

from genshi.builder import tag, Markup
from datetime import datetime, timedelta
from itertools import groupby

class TimelineMacro(WikiMacroBase):
    """
    A macro which lists recent project activity. 

    The TimelineMacro collects project wide activity and displays 
    the results inside a wiki page. To improve the appearance of the macro, 
    user profile images (currently take from gravatar) are also shown.

    This is not to be confused with the TicketQuery macro, which allows 
    users to query the ticket system and returns ticket information. 

    In contrast this macro returns all any project changes,
    to give a quick overview of recent activity across the project.

    The only parameter you can pass is a 'max' keyword argument, which will 
    limit the number of results returned. This defaults to 10 if no keyword 
    argument is passed.

    Examples:
    {{{
    [[TimelineMacro]] # shows the 10 most recent ticket changes
    [[TimelineMacro(max=10)]] # shows the 20 more recent ticket changes
    }}}
    """

    implements(ISidebarBoxProvider)

    event_providers = ExtensionPoint(ITimelineEventProvider)

    # ISidebarBoxProvider
    def get_box(self, req):
        """
        ISideBarBoxProvider is implemeted so we can automatically include 
        the timeline macro on the wiki start page.
        """

        return self.get_timeline_markup(req, 'sidebar')

    def expand_macro(self, formatter, name, content):

        # check to see if a max kwarg argument was passed
        req = formatter.req
        maxrows = 10 # default
        if content:
            arg_list = content.split()
            for a in arg_list:
                if a.startswith("max"):
                    try:
                        maxrows = int(content.split("=")[1])
                    except ValueError:
                        return "The max argument passed was not an integer."

        return self.get_timeline_markup(req, 'macro', maxrows)

    def get_timeline_markup(self, req, call, maxrows=10):
        """
        Generates the markup needed when this component is called both 
        explicitly inside wiki pages and implicitly by the ISideBarBoxProvider.

        Note this code uses methods from the trac TimelineModule module.
        """

        chrome = Chrome(self.env)

        # last 14 days should be enough
        stop = datetime.now(req.tz)
        start = stop - timedelta(days=50)

        # use code from trac/timeline to generate event data
        timeline = TimelineModule(self.env)
        available_filters, filters = timeline.get_filters(req)
        include_authors, exclude_authors = timeline.authors()
        events = timeline.get_events(req, start, stop, filters, available_filters, 
                                     include_authors, exclude_authors, maxrows)
        show_gravatar = self.config.get('avatar','mode').lower() != 'off'

        # create the mark up
        context = Context.from_request(req)
        event_list = tag.ul(class_="timeline-list no-style")
        for event in events:
            event_title = event['render']('title', context)
            event_url = event['render']('url', context)
            event_list.append(tag.li(
                show_gravatar and tag.img(
                    src=req.href.avatar(event['author'] if event['author'] else 'anonymous'),
                    class_="avatar",
                ) or "",
                tag.span(
                    chrome.authorinfo(req, event['author']),
                    class_="author"
                ),
                tag.span(
                    pretty_age(event['date']),
                    class_="date",
                ),
                tag.div(
                    tag.i(class_="event-type fa fa-" + event['kind']),
                    tag.a(
                        event_title,
                        href=event_url,
                    ),
                    class_="event-summary"
                ),
                class_="cf"
            ))

        # if the markup is being generated via ISideBarBoxProvider we don't 
        # need to add a span3 class 
        div_classes = "box-sidebar"
        if call == "macro":
            div_classes += " span3 right"
        return tag.div(
                    tag.h3(
                        tag.i(
                            class_="fa fa-calendar"
                        ),
                        " Recent Project Activity"
                    ),
                    event_list,
                    class_=div_classes,
                )