#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// Template Name: Cover Template
#// Template Post Type: post, page
#// 
#// @package WordPress
#// @subpackage Twenty_Twenty
#// @since Twenty Twenty 1.0
#//
get_header()
php_print("""
<main id=\"site-content\" role=\"main\">
""")
if have_posts():
    while True:
        
        if not (have_posts()):
            break
        # end if
        the_post()
        get_template_part("template-parts/content-cover")
    # end while
# end if
php_print("""
</main><!-- #site-content -->
""")
get_template_part("template-parts/footer-menus-widgets")
php_print("\n")
get_footer()