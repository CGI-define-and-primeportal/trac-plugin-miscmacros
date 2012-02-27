# Nick Piper, Logica, 2012
# 0.1

from trac.wiki.macros import WikiMacroBase
from trac.wiki.api import parse_args

import re

class MediahubPlayerMacro(WikiMacroBase):
    def expand_macro(self, formatter, name, content):

        args, kw = parse_args(content)
        
        if not ('site' in kw and 'chapter' in kw):
            raise Exception("'site' and 'chapter' are required arguments")

        if not (re.match("^[a-zA-Z0-9-]+$",kw['site']) and re.match("^[a-zA-Z0-9-]+$",kw['site'])):
            raise Exception("'site' or 'chapter' setting contains invalid characters")

        template_dict = {'height': int(kw.get('height', 253)),
                         'width':  int(kw.get('width', 450)),
                         'SiteId': kw['site'],
                         'chapterId': kw['chapter']}
        template = """
<object id="%(SiteId)s" 
        name="MediahubVideoPlayer"  
        type="application/x-shockwave-flash" 
        data="http://players.mymediahub.com/MediaHubPlayer.swf" height="%(height)s" width="%(width)s">
<param name="movie" value="http://players.mymediahub.com/MediaHubPlayer.swf" />
<param name="allowFullScreen" value="true" />
<param name="allowScriptAccess" value="always" />
<param name="wmode" value="transparent" />
<param name="flashvars" value="ServiceUrl=http://sites.mymediahub.com/Services/&SiteId=%(SiteId)s" />
<a href="http://sites.mymediahub.com/Devices/Services/GetChapterVideo.ashx?chapterId=%(chapterId)s&siteId=%(SiteId)s">
<img border="0" alt="Video" src="http://sites.mymediahub.com/Devices/Services/GetEmbedPreviewStill.ashx?siteId=%(SiteId)s" 
     width="%(width)s" height="%(height)s" 
     class="MediahubPreviewStill" />
</a>
</object>
"""
        return template % template_dict
