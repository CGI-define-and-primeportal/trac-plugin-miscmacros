#!/usr/bin/python
# Copyright (c) 2010, Logica
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright 
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <ORGANIZATION> nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

from trac.wiki.macros import WikiMacroBase
from trac.wiki.api import parse_args
from trac.versioncontrol.api import RepositoryManager
from trac.util.datefmt import format_datetime, from_utimestamp, \
                              to_utimestamp, utc

from genshi.builder import tag

from datetime import datetime, timedelta
import time

from GChartWrapper import GChart

# Examples:
#[[CommittersChart(daysback=100,type=p)]]
#[[HoursChart(daysback=12)]]
#[[TicketUpdatesChart]]
#[[TicketsToStatusChart(daysback=1)]]
#[[TicketsToStatusChart(fixed)]]

class GeneralChartMixin(object):
    def chart(self, charttype, title, dataset):
        legend, data = zip(*[("%s (%d)" % (l, c), c) for l, c in dataset.items()])
        chart = GChart(charttype,
                       data,
                       chtt=title)

        size = (600,200)
        chart.size(*size)
        if charttype == 'bar':
            chart.legend_pos('l')
            chart.legend(*legend)
        else:
            chart.label(*legend)
        chart.encoding('extended')
        return chart.img(width=size[0],height=size[1])

    def handle_kwargs(self, formatter, kwargs):
        daysback = int(kwargs.get('daysback',7))
        charttype = kwargs.get('type','p')

        stop =  datetime.now(formatter.req.tz)
        start = stop - timedelta(days=daysback + 1)
        return charttype, (start, stop)

class TicketsToStatusChartMacro(WikiMacroBase, GeneralChartMixin):
    def expand_macro(self, formatter, name, args):
        largs, kwargs = parse_args(args)
        if len(largs) > 0:
            status = largs[0]
        else:
            status = 'closed'
            
        charttype, (start, stop) = self.handle_kwargs(formatter, kwargs)
        
        dataset = {}
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""SELECT COUNT(*), author
        FROM ticket_change
        WHERE newvalue = %s
        AND   time>=%s AND time<=%s 
        GROUP BY author""", (status,
                             to_utimestamp(start),
                             to_utimestamp(stop)))
        for count, author in cursor:
            dataset[author] = count

        if not dataset:
            return "No ticket data available"

        title = "Tickets to '%s' per Person|%s to %s" % (status,
                                                         start.strftime("%c"),
                                                         stop.strftime("%c"))

        return self.chart(charttype, title, dataset)

class TicketUpdatesChartMacro(WikiMacroBase, GeneralChartMixin):
    def expand_macro(self, formatter, name, args):
        largs, kwargs = parse_args(args)
            
        charttype, (start, stop) = self.handle_kwargs(formatter, kwargs)
        
        dataset = {}
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""SELECT COUNT(DISTINCT time), author
        FROM ticket_change
        WHERE time>=%s AND time<=%s 
        GROUP BY author""", (to_utimestamp(start),
                             to_utimestamp(stop)))
        for count, author in cursor:
            dataset[author] = count

        if not dataset:
            return "No ticket data available"

        title = "Ticket updates per Person|%s to %s" % (start.strftime("%c"),
                                                        stop.strftime("%c"))

        return self.chart(charttype, title, dataset)

class HoursChartMacro(WikiMacroBase, GeneralChartMixin):
    def expand_macro(self, formatter, name, args):
        largs, kwargs = parse_args(args)
            
        charttype, (start, stop) = self.handle_kwargs(formatter, kwargs)
        
        dataset = {}
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""SELECT SUM(seconds_worked) / 3600.0 as hours, worker
        FROM ticket_time
        WHERE time_started>=%s AND time_started<=%s 
        GROUP BY worker""", (int(time.mktime(start.timetuple())),
                             int(time.mktime(stop.timetuple()))))
        for hours, author in cursor:
            dataset[author] = hours 

        if not dataset:
            return "No time data available"

        title = "Hours per Person|%s to %s" % (start.strftime("%c"),
                                               stop.strftime("%c"))

        return self.chart(charttype, title, dataset)
        
class CommittersChartMacro(WikiMacroBase, GeneralChartMixin):
    def expand_macro(self, formatter, name, args):
        largs, kwargs = parse_args(args)
        if len(largs) > 0:
            reponame = largs[0]
        else:
            reponame = None

        charttype, (start, stop) = self.handle_kwargs(formatter, kwargs)

        dataset = {}
        repo = RepositoryManager(self.env).get_repository(reponame)
        if not repo.can_view(formatter.req.perm):
            return "(No permission to view repository)"

        for changeset in repo.get_changesets(start, stop):
            dataset[changeset.author] = dataset.get(changeset.author,0) + 1
        if not dataset:
            return "No commmit information available"

        title = 'Commits per Person|%s to %s' % (start.strftime("%c"),
                                                 stop.strftime("%c"))

        return self.chart(charttype, title, dataset)

