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
#// Customize API: WP_Widget_Area_Customize_Control class
#// 
#// @package WordPress
#// @subpackage Customize
#// @since 3.4.0
#// 
#// 
#// Widget Area Customize Control class.
#// 
#// @since 3.9.0
#// 
#// @see WP_Customize_Control
#//
class WP_Widget_Area_Customize_Control(WP_Customize_Control):
    type = "sidebar_widgets"
    sidebar_id = Array()
    #// 
    #// Refreshes the parameters passed to the JavaScript via JSON.
    #// 
    #// @since 3.9.0
    #//
    def to_json(self):
        
        super().to_json()
        exported_properties = Array("sidebar_id")
        for key in exported_properties:
            self.json[key] = self.key
        # end for
    # end def to_json
    #// 
    #// Renders the control's content.
    #// 
    #// @since 3.9.0
    #//
    def render_content(self):
        
        id = "reorder-widgets-desc-" + php_str_replace(Array("[", "]"), Array("-", ""), self.id)
        php_print("     <button type=\"button\" class=\"button add-new-widget\" aria-expanded=\"false\" aria-controls=\"available-widgets\">\n          ")
        _e("Add a Widget")
        php_print("     </button>\n     <button type=\"button\" class=\"button-link reorder-toggle\" aria-label=\"")
        esc_attr_e("Reorder widgets")
        php_print("\" aria-describedby=\"")
        php_print(esc_attr(id))
        php_print("\">\n            <span class=\"reorder\">")
        _e("Reorder")
        php_print("</span>\n            <span class=\"reorder-done\">")
        _e("Done")
        php_print("</span>\n        </button>\n     <p class=\"screen-reader-text\" id=\"")
        php_print(esc_attr(id))
        php_print("\">")
        _e("When in reorder mode, additional controls to reorder widgets will be available in the widgets list above.")
        php_print("</p>\n       ")
    # end def render_content
# end class WP_Widget_Area_Customize_Control