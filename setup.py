from setuptools import setup

setup(
    name = 'MiscMacrosPlugin',
    version = '0.2',
    author = 'Nick Piper',
    author_email = 'nick.piper@logica.com',
    description = 'Miscellaneous Trac macros which are not packaged with setuptools upstream.',
    license = "Mixed",
    url = "http://d4.define.logica.com",
    packages = ['miscmacrosplugin'],
    entry_points = {'trac.plugins': [
        'miscmacrosplugin.MilestoneCompactMacro = miscmacrosplugin.MilestoneCompactMacro',
        'miscmacrosplugin.PlannedMilestones = miscmacrosplugin.PlannedMilestones',
        'miscmacrosplugin.TicketBox = miscmacrosplugin.TicketBox',
        'miscmacrosplugin.WikiCalendarMacro = miscmacrosplugin.WikiCalendarMacro',
        'miscmacrosplugin.EmailProcessor = miscmacrosplugin.EmailProcessor',
        'miscmacrosplugin.MilestoneTrafficLights = miscmacrosplugin.MilestoneTrafficLights',
        'miscmacrosplugin.Charts = miscmacrosplugin.Charts',
        'miscmacrosplugin.TicketsForReviewQuery = miscmacrosplugin.TicketsForReviewQuery',
        'miscmacrosplugin.DateMacro = miscmacrosplugin.DateMacro',
        'miscmacrosplugin.MediahubPlayerMacro = miscmacrosplugin.MediahubPlayerMacro',
        'miscmacrosplugin.TimelineMacro = miscmacrosplugin.TimelineMacro',
        ]},
    install_requires = ['GChartWrapper'],
)
