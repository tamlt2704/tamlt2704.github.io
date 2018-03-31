# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1522472605.320261
_enable_loop = True
_template_filename = u'/home/tam/devtools/venv/local/lib/python2.7/site-packages/nikola/data/themes/base/templates/math_helper.tmpl'
_template_uri = u'math_helper.tmpl'
_source_encoding = 'ascii'
_exports = ['math_scripts', 'math_styles', 'math_styles_ifposts', 'math_styles_ifpost', 'math_scripts_ifpost', 'math_scripts_ifposts']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer(u'\n\n')
        __M_writer(u'\n\n')
        __M_writer(u'\n\n')
        __M_writer(u'\n\n')
        __M_writer(u'\n\n')
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_scripts(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        mathjax_config = context.get('mathjax_config', UNDEFINED)
        use_katex = context.get('use_katex', UNDEFINED)
        katex_auto_render = context.get('katex_auto_render', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if use_katex:
            __M_writer(u'        <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.7.1/katex.min.js" integrity="sha384-/y1Nn9+QQAipbNQWU65krzJralCnuOasHncUFXGkdwntGeSvQicrYkiUBwsgUqc1" crossorigin="anonymous"></script>\n        <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.7.1/contrib/auto-render.min.js" integrity="sha256-ExtbCSBuYA7kq1Pz362ibde9nnsHYPt6JxuxYeZbU+c=" crossorigin="anonymous"></script>\n')
            if katex_auto_render:
                __M_writer(u'            <script>\n                renderMathInElement(document.body,\n                    {\n                        ')
                __M_writer(unicode(katex_auto_render))
                __M_writer(u'\n                    }\n                );\n            </script>\n')
            else:
                __M_writer(u'            <script>\n                renderMathInElement(document.body);\n            </script>\n')
        else:
            __M_writer(u'        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML" integrity="sha256-SDRP1VVYu+tgAGKhddBSl5+ezofHKZeI+OzxakbIe/Y=" crossorigin="anonymous"></script>\n')
            if mathjax_config:
                __M_writer(u'        ')
                __M_writer(unicode(mathjax_config))
                __M_writer(u'\n')
            else:
                __M_writer(u'        <script type="text/x-mathjax-config">\n        MathJax.Hub.Config({tex2jax: {inlineMath: [[\'$latex \',\'$\'], [\'\\\\(\',\'\\\\)\']]}});\n        </script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_styles(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        use_katex = context.get('use_katex', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if use_katex:
            __M_writer(u'        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.7.1/katex.min.css" integrity="sha384-wITovz90syo1dJWVh32uuETPVEtGigN07tkttEqPv+uR2SE/mbQcG7ATL28aI9H0" crossorigin="anonymous">\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_styles_ifposts(context,posts):
    __M_caller = context.caller_stack._push_frame()
    try:
        def math_styles():
            return render_math_styles(context)
        any = context.get('any', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if any(post.is_mathjax for post in posts):
            __M_writer(u'        ')
            __M_writer(unicode(math_styles()))
            __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_styles_ifpost(context,post):
    __M_caller = context.caller_stack._push_frame()
    try:
        def math_styles():
            return render_math_styles(context)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if post.is_mathjax:
            __M_writer(u'        ')
            __M_writer(unicode(math_styles()))
            __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_scripts_ifpost(context,post):
    __M_caller = context.caller_stack._push_frame()
    try:
        def math_scripts():
            return render_math_scripts(context)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if post.is_mathjax:
            __M_writer(u'        ')
            __M_writer(unicode(math_scripts()))
            __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_math_scripts_ifposts(context,posts):
    __M_caller = context.caller_stack._push_frame()
    try:
        def math_scripts():
            return render_math_scripts(context)
        any = context.get('any', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if any(post.is_mathjax for post in posts):
            __M_writer(u'        ')
            __M_writer(unicode(math_scripts()))
            __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "ascii", "line_map": {"130": 44, "131": 45, "132": 46, "133": 46, "134": 46, "140": 134, "16": 0, "21": 30, "22": 36, "23": 42, "24": 48, "25": 54, "26": 60, "32": 2, "39": 2, "40": 3, "41": 4, "42": 6, "43": 7, "44": 10, "45": 10, "46": 14, "47": 15, "48": 19, "49": 21, "50": 22, "51": 23, "52": 23, "53": 23, "54": 24, "55": 25, "61": 32, "66": 32, "67": 33, "68": 34, "74": 56, "81": 56, "82": 57, "83": 58, "84": 58, "85": 58, "91": 50, "97": 50, "98": 51, "99": 52, "100": 52, "101": 52, "107": 38, "113": 38, "114": 39, "115": 40, "116": 40, "117": 40, "123": 44}, "uri": "math_helper.tmpl", "filename": "/home/tam/devtools/venv/local/lib/python2.7/site-packages/nikola/data/themes/base/templates/math_helper.tmpl"}
__M_END_METADATA
"""
