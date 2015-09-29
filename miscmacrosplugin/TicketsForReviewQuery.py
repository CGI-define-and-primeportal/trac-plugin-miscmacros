"""Macro to return tickets which are ready for review."""
from trac.core import *
from trac.wiki.macros import WikiMacroBase
from trac.resource import get_resource_url , get_resource_shortname, Resource
		    
from genshi.builder import tag

from datetime import *
from trac.util.datefmt import format_datetime

class TicketsForReviewQuery(WikiMacroBase):
        """
Shows all tickets that need reviewing. This identifies tickets that have either not had a review, or have had changes applied since the last review comment.

It relies upon the following:

* All commits must reference the Ticket in the commit comment
* Review comments must be made as ticket comments with the heading `== Review ==`

This is a macro contributed to #define by a Logica project. It is not
part of any particular recommeded best practice or workflow.
"""
	
        def expand_macro(self, formatter, name, args):
            # Create a HTML div tag to contain our return tables formatted in HTML
            returnDiv = tag.div()
	    # Create a connection to the database.
	    db = self.env.get_read_db()
	    cursor = db.cursor()
	    # Execute the SQL query on the #define ticket database. This query returns all tickets which have been updated with a '[number]:' tag since review.
	    cursor.execute("""SELECT t.id AS ticket, summary, milestone AS __group__, last_committed AS modified, t.owner as owner, t.component as component, t.status as status
                                FROM ticket t 
                                LEFT OUTER JOIN (
                                        SELECT ticket, MAX(time) AS last_reviewed
                                        FROM ticket_change
                                        WHERE field = 'comment' AND newvalue LIKE '%= Review%'
                                        GROUP BY ticket
                                ) rev ON rev.ticket = t.id
                                LEFT OUTER JOIN (
                                        SELECT ticket, MAX(time) AS last_committed
                                        FROM ticket_change
                                        WHERE field = 'comment' AND newvalue LIKE '[%]:%'
                                        GROUP BY ticket
                                ) ch ON ch.ticket = t.id
                                INNER JOIN milestone m ON m.name = milestone
                                WHERE last_committed > COALESCE(last_reviewed, 0)
                                ORDER BY milestone, component,  modified""")

	    currentMilestone = None
	    # i is used to track odd or even row numbers so the table row class can be set as either odd or even.
	    i = 0

	    # This loop iterates through the values returned by the SQL query.
	    for ticket, summary, __group__, modified, owner, component, status in cursor:
                    i+=1
		    if currentMilestone != __group__:
                            i = 0
                            if currentMilestone != None:
                                    # Print a blank line between tables but not before the first table
                                    returnDiv.append(tag.br())
			    # Start a new group.
			    currentMilestone = __group__
			    # Create a table header for the table to hold the values returned by the query.
			    currentTable = tag.table(self.table_header(),
						     class_="listing tickets")
			    # Create a heading for the group and append it to returnDiv then append currentTable.
			    returnDiv.append(tag.h2(currentMilestone or "No milestone set", class_="report-result"))
			    returnDiv.append(currentTable)
		    oddeven = (i%2 and 'odd' or 'even')
		    # oddeven is used to change the css class of the table rows to improve legibility.
		    ticket_resource = Resource('ticket',ticket)
		    # ticket_resource is used to specify the ticket resource from the trac environment. 
		    currentTable.append(tag.tr(tag.td(tag.a(get_resource_shortname(self.env, ticket_resource),
							    href=get_resource_url(self.env, ticket_resource, formatter.href))),
					       tag.td(summary),
					       tag.td(format_datetime(modified, tzinfo=formatter.req.tz)),
					       tag.td(owner),
					       tag.td(component),
					       tag.td(status), class_=oddeven))
		    # The above populates the rows with the results returned by our query.

            

	    return returnDiv

        def table_header(self):
		# use genshi to build header row, also use th for table headings
		# (note, we don't start the table here, as all genshi objects have to be self-contained)
		return tag.thead(tag.tr(tag.th('Ticket'),
			      tag.th('Summary'),
			      tag.th('Modified'),
			      tag.th('Owner'),
			      tag.th('Component'),
			      tag.th('Status')))
