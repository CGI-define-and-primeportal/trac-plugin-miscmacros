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


import datetime
import time
from trac.wiki.macros import WikiMacroBase
from trac.ticket import Milestone, Ticket
from trac.util.datefmt import localtz
from trac.ticket.roadmap import get_tickets_for_milestone
from genshi.builder import tag
from trac.wiki.api import parse_args

class MilestoneTrafficLightsMacro(WikiMacroBase):
    def expand_macro(self, formatter, name, content):

        db = self.env.get_read_db()

        args, kwargs = parse_args(content)
        milestone_arg      = args[0].strip()
        hoursavailable_arg = float(args[1].strip())
        start_arg          = datetime.datetime(*(time.strptime(args[2].strip(), "%Y-%m-%d")[0:6])).replace(tzinfo=localtz)

        milestone = Milestone(self.env, milestone_arg, db)

        if milestone.due is None:
            raise Exception("Milestone %s has no due date set." % milestone.name)
        
        formatter.req.perm.require("MILESTONE_VIEW", milestone.resource)

        estimatedhours = 0.0
        remaininghours = 0.0        
        totalhours     = 0.0
        for row in get_tickets_for_milestone(self.env, db, milestone.name):
            ticket = Ticket(self.env, row['id'], db)
            if ticket['status'] == "closed":
                continue
            if ticket['estimatedhours']:
                estimatedhours += float(ticket['estimatedhours'])
            if ticket['remaininghours']:
                remaininghours += float(ticket['remaininghours'])
            if ticket['totalhours']:
                totalhours += float(ticket['totalhours'])

        table = tag.table(class_='MilestoneTrafficLights')

        days_to_go = (milestone.due - datetime.datetime.now(localtz)).days

        table.append(tag.tr(tag.td('Milestone'),
                            tag.td(milestone.name)))
        table.append(tag.tr(tag.td('Due Date'),
                            tag.td(milestone.due.strftime("%Y-%m-%d"))))
        table.append(tag.tr(tag.td('Days to Go'),
                            tag.td(days_to_go)))
        table.append(tag.tr(tag.td('Work Hours Available'),
                            tag.td("%d between %s and %s" % (hoursavailable_arg,
                                                             start_arg.strftime("%Y-%m-%d"),
                                                             milestone.due.strftime("%Y-%m-%d")))))

        table.append(tag.tr(tag.td('Originally Estimated Hours'),
                            tag.td(estimatedhours)))
        table.append(tag.tr(tag.td('Currently Estimated Hours'),
                            tag.td(remaininghours)))        
        table.append(tag.tr(tag.td('Ticket Spent Hours'),
                            tag.td(totalhours)))

        #return hoursavailable_arg / float((datetime.datetime.now() - start_arg).days)
        

        hours_avail_per_day = hoursavailable_arg / float((milestone.due - start_arg).days)
        work_hours_left = hours_avail_per_day * days_to_go
        table.append(tag.tr(tag.td('Work Pro-rota Hours Left'),
                            tag.td("%.1f" % work_hours_left)))

        sparehours = work_hours_left - remaininghours

        if sparehours > 100:
            colour = "green"
        elif sparehours > 48:
            colour = "orange"
        else:            
            colour = "red"
            
        table.append(tag.tr(tag.td('Spare Hours'),
                            tag.td("%.1f" % sparehours,style="background: %s" % colour)))
        
        return table


