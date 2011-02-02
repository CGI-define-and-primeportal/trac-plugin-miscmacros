from setuptools import setup

setup(
    name = 'MiscMacrosPlugin',
    version = '0.1',
    author = 'Nick Piper',
    author_email = 'nick.piper@logica.com',
    description = 'Miscellaneous Trac macros which are not packaged with setuptools upstream.',
    license = "Mixed",
    url = "http://define4.trac.uk.logica.com",
    packages = ['miscmacrosplugin'],
    entry_points = {'trac.plugins': [
        'miscmacrosplugin.MilestoneCompactMacro = miscmacrosplugin.MilestoneCompactMacro',
        'miscmacrosplugin.PlannedMilestones = miscmacrosplugin.PlannedMilestones',
        'miscmacrosplugin.TicketBox = miscmacrosplugin.TicketBox',
        'miscmacrosplugin.WikiCalendarMacro = miscmacrosplugin.WikiCalendarMacro',
        'miscmacrosplugin.EmailProcessor = miscmacrosplugin.EmailProcessor',
        'miscmacrosplugin.MilestoneTrafficLights = miscmacrosplugin.MilestoneTrafficLights',
        'miscmacrosplugin.Charts = miscmacrosplugin.Charts',
        ]},
    install_requires = ['GChartWrapper'],
)
