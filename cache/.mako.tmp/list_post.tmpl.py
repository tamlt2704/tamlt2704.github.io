# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1522472605.425934
_enable_loop = True
_template_filename = u'/home/tam/devtools/venv/local/lib/python2.7/site-packages/nikola/data/themes/base/templates/list_post.tmpl'
_template_uri = 'list_post.tmpl'
_source_encoding = 'utf-8'
_exports = [u'content']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    ns = runtime.TemplateNamespace(u'feeds_translations', context._clean_inheritance_tokens(), templateuri=u'feeds_translations_helper.tmpl', callables=None,  calling_uri=_template_uri)
    context.namespaces[(__name__, u'feeds_translations')] = ns

    ns = runtime.TemplateNamespace(u'archive_nav', context._clean_inheritance_tokens(), templateuri=u'archive_navigation_helper.tmpl', callables=None,  calling_uri=_template_uri)
    context.namespaces[(__name__, u'archive_nav')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'base.tmpl', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        _import_ns = {}
        _mako_get_namespace(context, u'feeds_translations')._populate(_import_ns, [u'*'])
        _mako_get_namespace(context, u'archive_nav')._populate(_import_ns, [u'*'])
        date_format = _import_ns.get('date_format', context.get('date_format', UNDEFINED))
        title = _import_ns.get('title', context.get('title', UNDEFINED))
        feeds_translations = _mako_get_namespace(context, 'feeds_translations')
        messages = _import_ns.get('messages', context.get('messages', UNDEFINED))
        posts = _import_ns.get('posts', context.get('posts', UNDEFINED))
        def content():
            return render_content(context._locals(__M_locals))
        archive_nav = _mako_get_namespace(context, 'archive_nav')
        __M_writer = context.writer()
        __M_writer(u'\n')
        __M_writer(u'\n')
        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        _import_ns = {}
        _mako_get_namespace(context, u'feeds_translations')._populate(_import_ns, [u'*'])
        _mako_get_namespace(context, u'archive_nav')._populate(_import_ns, [u'*'])
        date_format = _import_ns.get('date_format', context.get('date_format', UNDEFINED))
        title = _import_ns.get('title', context.get('title', UNDEFINED))
        feeds_translations = _mako_get_namespace(context, 'feeds_translations')
        messages = _import_ns.get('messages', context.get('messages', UNDEFINED))
        posts = _import_ns.get('posts', context.get('posts', UNDEFINED))
        def content():
            return render_content(context)
        archive_nav = _mako_get_namespace(context, 'archive_nav')
        __M_writer = context.writer()
        __M_writer(u'\n<article class="listpage">\n    <header>\n        <h1>')
        __M_writer(filters.html_escape(unicode(title)))
        __M_writer(u'</h1>\n    </header>\n    ')
        __M_writer(unicode(archive_nav.archive_navigation()))
        __M_writer(u'\n    ')
        __M_writer(unicode(feeds_translations.translation_link()))
        __M_writer(u'\n')
        if posts:
            __M_writer(u'    <ul class="postlist">\n')
            for post in posts:
                __M_writer(u'        <li><time class="listdate" datetime="')
                __M_writer(unicode(post.formatted_date('webiso')))
                __M_writer(u'" title="')
                __M_writer(filters.html_escape(unicode(post.formatted_date(date_format))))
                __M_writer(u'">')
                __M_writer(filters.html_escape(unicode(post.formatted_date(date_format))))
                __M_writer(u'</time> <a href="')
                __M_writer(unicode(post.permalink()))
                __M_writer(u'" class="listtitle">')
                __M_writer(filters.html_escape(unicode(post.title())))
                __M_writer(u'</a></li>\n')
            __M_writer(u'    </ul>\n')
        else:
            __M_writer(u'    <p>')
            __M_writer(unicode(messages("No posts found.")))
            __M_writer(u'</p>\n')
        __M_writer(u'</article>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"23": 4, "26": 3, "32": 0, "48": 2, "49": 3, "50": 4, "55": 23, "61": 6, "76": 6, "77": 9, "78": 9, "79": 11, "80": 11, "81": 12, "82": 12, "83": 13, "84": 14, "85": 15, "86": 16, "87": 16, "88": 16, "89": 16, "90": 16, "91": 16, "92": 16, "93": 16, "94": 16, "95": 16, "96": 16, "97": 18, "98": 19, "99": 20, "100": 20, "101": 20, "102": 22, "108": 102}, "uri": "list_post.tmpl", "filename": "/home/tam/devtools/venv/local/lib/python2.7/site-packages/nikola/data/themes/base/templates/list_post.tmpl"}
__M_END_METADATA
"""
