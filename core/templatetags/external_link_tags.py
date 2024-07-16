"""
Copyright (c) 2009, Jesús Del Carpio individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# -*- coding: utf-8 -*-

"""
    External links template tags
"""

import re

from django.template import Library, Node
from django.urls import reverse
from django.utils.http import urlencode

register = Library()


@register.simple_tag
def external(link):
    """
    Replaces an external link with a redirect to
    keep track of the clicked link

    To be used as:
        {% external "http://google.com/" %}

    """
    redirect_endpoint = reverse("external_link")
    params = urlencode({"link": link})

    return redirect_endpoint + "?" + params


@register.tag(name="externalblock")
def do_external_block(parser, token):
    """
    {% externalblock %}
    text with <a href="">content</a> to be converted to external
    links
    {% endexternalblock %}
    """
    node_list = parser.parse(("endexternalblock"))
    parser.delete_first_token()
    return ExternalLink(node_list)


EXTLINKS = re.compile(r'''href="(?P<link>http[^>"]*)"''')


class ExternalLink(Node):
    """
    Should look for any href reference and translate that link
    into an externa link redirect
    """

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def replace_links(self, original_text):
        """
        Here's all the magic
            1. Split the nodes contents in pieces
            2. Translate that start with 'http' to an external link
            3. Join it all back together for printing
        """
        redirect_endpoint = reverse("external_link")
        pieces = EXTLINKS.split(original_text)
        result = []

        for piece in pieces:
            # replace http:/ with http, or it will ignore https protocol
            if piece.startswith("http"):
                # Replace the &amp; as the & will be urlencoded. If we don't do
                # this, the resulting url will be &amp;amp; and GET params
                # will get lost :(
                piece = piece.replace("&amp;", "&")
                params = urlencode({"link": piece})
                result.append('href="' + redirect_endpoint + "?" + params + '"')
            else:
                result.append(piece)

        return "".join(result)

    def render(self, context):
        output = self.nodelist.render(context)
        return self.replace_links(output)
