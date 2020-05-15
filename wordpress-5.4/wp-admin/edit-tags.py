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
#// Edit Tags Administration Screen.
#// 
#// @package WordPress
#// @subpackage Administration
#// 
#// WordPress Administration Bootstrap
php_include_file(__DIR__ + "/admin.php", once=True)
if (not taxnow):
    wp_die(__("Invalid taxonomy."))
# end if
tax = get_taxonomy(taxnow)
if (not tax):
    wp_die(__("Invalid taxonomy."))
# end if
if (not php_in_array(tax.name, get_taxonomies(Array({"show_ui": True})))):
    wp_die(__("Sorry, you are not allowed to edit terms in this taxonomy."))
# end if
if (not current_user_can(tax.cap.manage_terms)):
    wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to manage terms in this taxonomy.") + "</p>", 403)
# end if
#// 
#// $post_type is set when the WP_Terms_List_Table instance is created
#// 
#// @global string $post_type
#//
global post_type
php_check_if_defined("post_type")
wp_list_table = _get_list_table("WP_Terms_List_Table")
pagenum = wp_list_table.get_pagenum()
title = tax.labels.name
if "post" != post_type:
    parent_file = "upload.php" if "attachment" == post_type else str("edit.php?post_type=") + str(post_type)
    submenu_file = str("edit-tags.php?taxonomy=") + str(taxonomy) + str("&amp;post_type=") + str(post_type)
elif "link_category" == tax.name:
    parent_file = "link-manager.php"
    submenu_file = "edit-tags.php?taxonomy=link_category"
else:
    parent_file = "edit.php"
    submenu_file = str("edit-tags.php?taxonomy=") + str(taxonomy)
# end if
add_screen_option("per_page", Array({"default": 20, "option": "edit_" + tax.name + "_per_page"}))
get_current_screen().set_screen_reader_content(Array({"heading_pagination": tax.labels.items_list_navigation, "heading_list": tax.labels.items_list}))
location = False
referer = wp_get_referer()
if (not referer):
    #// For POST requests.
    referer = wp_unslash(PHP_SERVER["REQUEST_URI"])
# end if
referer = remove_query_arg(Array("_wp_http_referer", "_wpnonce", "error", "message", "paged"), referer)
for case in Switch(wp_list_table.current_action()):
    if case("add-tag"):
        check_admin_referer("add-tag", "_wpnonce_add-tag")
        if (not current_user_can(tax.cap.edit_terms)):
            wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to create terms in this taxonomy.") + "</p>", 403)
        # end if
        ret = wp_insert_term(PHP_POST["tag-name"], taxonomy, PHP_POST)
        if ret and (not is_wp_error(ret)):
            location = add_query_arg("message", 1, referer)
        else:
            location = add_query_arg(Array({"error": True, "message": 4}), referer)
        # end if
        break
    # end if
    if case("delete"):
        if (not (php_isset(lambda : PHP_REQUEST["tag_ID"]))):
            break
        # end if
        tag_ID = int(PHP_REQUEST["tag_ID"])
        check_admin_referer("delete-tag_" + tag_ID)
        if (not current_user_can("delete_term", tag_ID)):
            wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to delete this item.") + "</p>", 403)
        # end if
        wp_delete_term(tag_ID, taxonomy)
        location = add_query_arg("message", 2, referer)
        #// When deleting a term, prevent the action from redirecting back to a term that no longer exists.
        location = remove_query_arg(Array("tag_ID", "action"), location)
        break
    # end if
    if case("bulk-delete"):
        check_admin_referer("bulk-tags")
        if (not current_user_can(tax.cap.delete_terms)):
            wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to delete these items.") + "</p>", 403)
        # end if
        tags = PHP_REQUEST["delete_tags"]
        for tag_ID in tags:
            wp_delete_term(tag_ID, taxonomy)
        # end for
        location = add_query_arg("message", 6, referer)
        break
    # end if
    if case("edit"):
        if (not (php_isset(lambda : PHP_REQUEST["tag_ID"]))):
            break
        # end if
        term_id = int(PHP_REQUEST["tag_ID"])
        term = get_term(term_id)
        if (not type(term).__name__ == "WP_Term"):
            wp_die(__("You attempted to edit an item that doesn&#8217;t exist. Perhaps it was deleted?"))
        # end if
        wp_redirect(esc_url_raw(get_edit_term_link(term_id, taxonomy, post_type)))
        php_exit(0)
    # end if
    if case("editedtag"):
        tag_ID = int(PHP_POST["tag_ID"])
        check_admin_referer("update-tag_" + tag_ID)
        if (not current_user_can("edit_term", tag_ID)):
            wp_die("<h1>" + __("You need a higher level of permission.") + "</h1>" + "<p>" + __("Sorry, you are not allowed to edit this item.") + "</p>", 403)
        # end if
        tag = get_term(tag_ID, taxonomy)
        if (not tag):
            wp_die(__("You attempted to edit an item that doesn&#8217;t exist. Perhaps it was deleted?"))
        # end if
        ret = wp_update_term(tag_ID, taxonomy, PHP_POST)
        if ret and (not is_wp_error(ret)):
            location = add_query_arg("message", 3, referer)
        else:
            location = add_query_arg(Array({"error": True, "message": 5}), referer)
        # end if
        break
    # end if
    if case():
        if (not wp_list_table.current_action()) or (not (php_isset(lambda : PHP_REQUEST["delete_tags"]))):
            break
        # end if
        check_admin_referer("bulk-tags")
        screen = get_current_screen().id
        tags = PHP_REQUEST["delete_tags"]
        #// This action is documented in wp-admin/edit.php
        location = apply_filters(str("handle_bulk_actions-") + str(screen), location, wp_list_table.current_action(), tags)
        break
    # end if
# end for
if (not location) and (not php_empty(lambda : PHP_REQUEST["_wp_http_referer"])):
    location = remove_query_arg(Array("_wp_http_referer", "_wpnonce"), wp_unslash(PHP_SERVER["REQUEST_URI"]))
# end if
if location:
    if pagenum > 1:
        location = add_query_arg("paged", pagenum, location)
        pass
    # end if
    #// 
    #// Filters the taxonomy redirect destination URL.
    #// 
    #// @since 4.6.0
    #// 
    #// @param string      $location The destination URL.
    #// @param WP_Taxonomy $tax      The taxonomy object.
    #//
    wp_redirect(apply_filters("redirect_term_location", location, tax))
    php_exit(0)
# end if
wp_list_table.prepare_items()
total_pages = wp_list_table.get_pagination_arg("total_pages")
if pagenum > total_pages and total_pages > 0:
    wp_redirect(add_query_arg("paged", total_pages))
    php_exit(0)
# end if
wp_enqueue_script("admin-tags")
if current_user_can(tax.cap.edit_terms):
    wp_enqueue_script("inline-edit-tax")
# end if
if "category" == taxonomy or "link_category" == taxonomy or "post_tag" == taxonomy:
    help = ""
    if "category" == taxonomy:
        help = "<p>" + php_sprintf(__("You can use categories to define sections of your site and group related posts. The default category is &#8220;Uncategorized&#8221; until you change it in your <a href=\"%s\">writing settings</a>."), "options-writing.php") + "</p>"
    elif "link_category" == taxonomy:
        help = "<p>" + __("You can create groups of links by using Link Categories. Link Category names must be unique and Link Categories are separate from the categories you use for posts.") + "</p>"
    else:
        help = "<p>" + __("You can assign keywords to your posts using <strong>tags</strong>. Unlike categories, tags have no hierarchy, meaning there&#8217;s no relationship from one tag to another.") + "</p>"
    # end if
    if "link_category" == taxonomy:
        help += "<p>" + __("You can delete Link Categories in the Bulk Action pull-down, but that action does not delete the links within the category. Instead, it moves them to the default Link Category.") + "</p>"
    else:
        help += "<p>" + __("What&#8217;s the difference between categories and tags? Normally, tags are ad-hoc keywords that identify important information in your post (names, subjects, etc) that may or may not recur in other posts, while categories are pre-determined sections. If you think of your site like a book, the categories are like the Table of Contents and the tags are like the terms in the index.") + "</p>"
    # end if
    get_current_screen().add_help_tab(Array({"id": "overview", "title": __("Overview"), "content": help}))
    if "category" == taxonomy or "post_tag" == taxonomy:
        if "category" == taxonomy:
            help = "<p>" + __("When adding a new category on this screen, you&#8217;ll fill in the following fields:") + "</p>"
        else:
            help = "<p>" + __("When adding a new tag on this screen, you&#8217;ll fill in the following fields:") + "</p>"
        # end if
        help += "<ul>" + "<li>" + __("<strong>Name</strong> &mdash; The name is how it appears on your site.") + "</li>"
        if (not global_terms_enabled()):
            help += "<li>" + __("<strong>Slug</strong> &mdash; The &#8220;slug&#8221; is the URL-friendly version of the name. It is usually all lowercase and contains only letters, numbers, and hyphens.") + "</li>"
        # end if
        if "category" == taxonomy:
            help += "<li>" + __("<strong>Parent</strong> &mdash; Categories, unlike tags, can have a hierarchy. You might have a Jazz category, and under that have child categories for Bebop and Big Band. Totally optional. To create a subcategory, just choose another category from the Parent dropdown.") + "</li>"
        # end if
        help += "<li>" + __("<strong>Description</strong> &mdash; The description is not prominent by default; however, some themes may display it.") + "</li>" + "</ul>" + "<p>" + __("You can change the display of this screen using the Screen Options tab to set how many items are displayed per screen and to display/hide columns in the table.") + "</p>"
        get_current_screen().add_help_tab(Array({"id": "adding-terms", "title": __("Adding Categories") if "category" == taxonomy else __("Adding Tags"), "content": help}))
    # end if
    help = "<p><strong>" + __("For more information:") + "</strong></p>"
    if "category" == taxonomy:
        help += "<p>" + __("<a href=\"https://wordpress.org/support/article/posts-categories-screen/\">Documentation on Categories</a>") + "</p>"
    elif "link_category" == taxonomy:
        help += "<p>" + __("<a href=\"https://codex.wordpress.org/Links_Link_Categories_Screen\">Documentation on Link Categories</a>") + "</p>"
    else:
        help += "<p>" + __("<a href=\"https://wordpress.org/support/article/posts-tags-screen/\">Documentation on Tags</a>") + "</p>"
    # end if
    help += "<p>" + __("<a href=\"https://wordpress.org/support/\">Support</a>") + "</p>"
    get_current_screen().set_help_sidebar(help)
    help = None
# end if
php_include_file(ABSPATH + "wp-admin/admin-header.php", once=True)
#// Also used by the Edit Tag  form
php_include_file(ABSPATH + "wp-admin/includes/edit-tag-messages.php", once=True)
class_ = "error" if (php_isset(lambda : PHP_REQUEST["error"])) else "updated"
if is_plugin_active("wpcat2tag-importer/wpcat2tag-importer.php"):
    import_link = admin_url("admin.php?import=wpcat2tag")
else:
    import_link = admin_url("import.php")
# end if
php_print("\n<div class=\"wrap nosubsub\">\n<h1 class=\"wp-heading-inline\">")
php_print(esc_html(title))
php_print("</h1>\n\n")
if (php_isset(lambda : PHP_REQUEST["s"])) and php_strlen(PHP_REQUEST["s"]):
    #// translators: %s: Search query.
    printf("<span class=\"subtitle\">" + __("Search results for &#8220;%s&#8221;") + "</span>", esc_html(wp_unslash(PHP_REQUEST["s"])))
# end if
php_print("""
<hr class=\"wp-header-end\">
""")
if message:
    php_print("<div id=\"message\" class=\"")
    php_print(class_)
    php_print(" notice is-dismissible\"><p>")
    php_print(message)
    php_print("</p></div>\n ")
    PHP_SERVER["REQUEST_URI"] = remove_query_arg(Array("message", "error"), PHP_SERVER["REQUEST_URI"])
# end if
php_print("""<div id=\"ajax-response\"></div>
<form class=\"search-form wp-clearfix\" method=\"get\">
<input type=\"hidden\" name=\"taxonomy\" value=\"""")
php_print(esc_attr(taxonomy))
php_print("\" />\n<input type=\"hidden\" name=\"post_type\" value=\"")
php_print(esc_attr(post_type))
php_print("\" />\n\n")
wp_list_table.search_box(tax.labels.search_items, "tag")
php_print("""
</form>
""")
can_edit_terms = current_user_can(tax.cap.edit_terms)
if can_edit_terms:
    php_print("""<div id=\"col-container\" class=\"wp-clearfix\">
    <div id=\"col-left\">
    <div class=\"col-wrap\">
    """)
    if "category" == taxonomy:
        #// 
        #// Fires before the Add Category form.
        #// 
        #// @since 2.1.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_pre_add_form'} instead.
        #// 
        #// @param object $arg Optional arguments cast to an object.
        #//
        do_action_deprecated("add_category_form_pre", Array(Array({"parent": 0})), "3.0.0", "{$taxonomy}_pre_add_form")
    elif "link_category" == taxonomy:
        #// 
        #// Fires before the link category form.
        #// 
        #// @since 2.3.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_pre_add_form'} instead.
        #// 
        #// @param object $arg Optional arguments cast to an object.
        #//
        do_action_deprecated("add_link_category_form_pre", Array(Array({"parent": 0})), "3.0.0", "{$taxonomy}_pre_add_form")
    else:
        #// 
        #// Fires before the Add Tag form.
        #// 
        #// @since 2.5.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_pre_add_form'} instead.
        #// 
        #// @param string $taxonomy The taxonomy slug.
        #//
        do_action_deprecated("add_tag_form_pre", Array(taxonomy), "3.0.0", "{$taxonomy}_pre_add_form")
    # end if
    #// 
    #// Fires before the Add Term form for all taxonomies.
    #// 
    #// The dynamic portion of the hook name, `$taxonomy`, refers to the taxonomy slug.
    #// 
    #// @since 3.0.0
    #// 
    #// @param string $taxonomy The taxonomy slug.
    #//
    do_action(str(taxonomy) + str("_pre_add_form"), taxonomy)
    php_print("\n<div class=\"form-wrap\">\n<h2>")
    php_print(tax.labels.add_new_item)
    php_print("</h2>\n<form id=\"addtag\" method=\"post\" action=\"edit-tags.php\" class=\"validate\"\n ")
    #// 
    #// Fires inside the Add Tag form tag.
    #// 
    #// The dynamic portion of the hook name, `$taxonomy`, refers to the taxonomy slug.
    #// 
    #// @since 3.7.0
    #//
    do_action(str(taxonomy) + str("_term_new_form_tag"))
    php_print(">\n<input type=\"hidden\" name=\"action\" value=\"add-tag\" />\n<input type=\"hidden\" name=\"screen\" value=\"")
    php_print(esc_attr(current_screen.id))
    php_print("\" />\n<input type=\"hidden\" name=\"taxonomy\" value=\"")
    php_print(esc_attr(taxonomy))
    php_print("\" />\n<input type=\"hidden\" name=\"post_type\" value=\"")
    php_print(esc_attr(post_type))
    php_print("\" />\n  ")
    wp_nonce_field("add-tag", "_wpnonce_add-tag")
    php_print("\n<div class=\"form-field form-required term-name-wrap\">\n  <label for=\"tag-name\">")
    _ex("Name", "term name")
    php_print("</label>\n   <input name=\"tag-name\" id=\"tag-name\" type=\"text\" value=\"\" size=\"40\" aria-required=\"true\" />\n   <p>")
    _e("The name is how it appears on your site.")
    php_print("</p>\n</div>\n   ")
    if (not global_terms_enabled()):
        php_print("<div class=\"form-field term-slug-wrap\">\n  <label for=\"tag-slug\">")
        _e("Slug")
        php_print("</label>\n   <input name=\"slug\" id=\"tag-slug\" type=\"text\" value=\"\" size=\"40\" />\n  <p>")
        _e("The &#8220;slug&#8221; is the URL-friendly version of the name. It is usually all lowercase and contains only letters, numbers, and hyphens.")
        php_print("</p>\n</div>\n")
    # end if
    pass
    php_print(" ")
    if is_taxonomy_hierarchical(taxonomy):
        php_print("<div class=\"form-field term-parent-wrap\">\n    <label for=\"parent\">")
        php_print(esc_html(tax.labels.parent_item))
        php_print("</label>\n       ")
        dropdown_args = Array({"hide_empty": 0, "hide_if_empty": False, "taxonomy": taxonomy, "name": "parent", "orderby": "name", "hierarchical": True, "show_option_none": __("None")})
        #// 
        #// Filters the taxonomy parent drop-down on the Edit Term page.
        #// 
        #// @since 3.7.0
        #// @since 4.2.0 Added `$context` parameter.
        #// 
        #// @param array  $dropdown_args {
        #// An array of taxonomy parent drop-down arguments.
        #// 
        #// @type int|bool $hide_empty       Whether to hide terms not attached to any posts. Default 0|false.
        #// @type bool     $hide_if_empty    Whether to hide the drop-down if no terms exist. Default false.
        #// @type string   $taxonomy         The taxonomy slug.
        #// @type string   $name             Value of the name attribute to use for the drop-down select element.
        #// Default 'parent'.
        #// @type string   $orderby          The field to order by. Default 'name'.
        #// @type bool     $hierarchical     Whether the taxonomy is hierarchical. Default true.
        #// @type string   $show_option_none Label to display if there are no terms. Default 'None'.
        #// }
        #// @param string $taxonomy The taxonomy slug.
        #// @param string $context  Filter context. Accepts 'new' or 'edit'.
        #//
        dropdown_args = apply_filters("taxonomy_parent_dropdown_args", dropdown_args, taxonomy, "new")
        wp_dropdown_categories(dropdown_args)
        php_print("     ")
        if "category" == taxonomy:
            php_print("     <p>")
            _e("Categories, unlike tags, can have a hierarchy. You might have a Jazz category, and under that have children categories for Bebop and Big Band. Totally optional.")
            php_print("</p>\n   ")
        else:
            php_print("     <p>")
            _e("Assign a parent term to create a hierarchy. The term Jazz, for example, would be the parent of Bebop and Big Band.")
            php_print("</p>\n   ")
        # end if
        php_print("</div>\n ")
    # end if
    pass
    php_print("<div class=\"form-field term-description-wrap\">\n   <label for=\"tag-description\">")
    _e("Description")
    php_print("</label>\n   <textarea name=\"description\" id=\"tag-description\" rows=\"5\" cols=\"40\"></textarea>\n  <p>")
    _e("The description is not prominent by default; however, some themes may show it.")
    php_print("""</p>
    </div>
    """)
    if (not is_taxonomy_hierarchical(taxonomy)):
        #// 
        #// Fires after the Add Tag form fields for non-hierarchical taxonomies.
        #// 
        #// @since 3.0.0
        #// 
        #// @param string $taxonomy The taxonomy slug.
        #//
        do_action("add_tag_form_fields", taxonomy)
    # end if
    #// 
    #// Fires after the Add Term form fields.
    #// 
    #// The dynamic portion of the hook name, `$taxonomy`, refers to the taxonomy slug.
    #// 
    #// @since 3.0.0
    #// 
    #// @param string $taxonomy The taxonomy slug.
    #//
    do_action(str(taxonomy) + str("_add_form_fields"), taxonomy)
    php_print(" <p class=\"submit\">\n      ")
    submit_button(tax.labels.add_new_item, "primary", "submit", False)
    php_print("     <span class=\"spinner\"></span>\n   </p>\n  ")
    if "category" == taxonomy:
        #// 
        #// Fires at the end of the Edit Category form.
        #// 
        #// @since 2.1.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_add_form'} instead.
        #// 
        #// @param object $arg Optional arguments cast to an object.
        #//
        do_action_deprecated("edit_category_form", Array(Array({"parent": 0})), "3.0.0", "{$taxonomy}_add_form")
    elif "link_category" == taxonomy:
        #// 
        #// Fires at the end of the Edit Link form.
        #// 
        #// @since 2.3.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_add_form'} instead.
        #// 
        #// @param object $arg Optional arguments cast to an object.
        #//
        do_action_deprecated("edit_link_category_form", Array(Array({"parent": 0})), "3.0.0", "{$taxonomy}_add_form")
    else:
        #// 
        #// Fires at the end of the Add Tag form.
        #// 
        #// @since 2.7.0
        #// @deprecated 3.0.0 Use {@see '{$taxonomy}_add_form'} instead.
        #// 
        #// @param string $taxonomy The taxonomy slug.
        #//
        do_action_deprecated("add_tag_form", Array(taxonomy), "3.0.0", "{$taxonomy}_add_form")
    # end if
    #// 
    #// Fires at the end of the Add Term form for all taxonomies.
    #// 
    #// The dynamic portion of the hook name, `$taxonomy`, refers to the taxonomy slug.
    #// 
    #// @since 3.0.0
    #// 
    #// @param string $taxonomy The taxonomy slug.
    #//
    do_action(str(taxonomy) + str("_add_form"), taxonomy)
    php_print("""</form></div>
    </div>
    </div><!-- /col-left -->
    <div id=\"col-right\">
    <div class=\"col-wrap\">
    """)
# end if
php_print("\n")
wp_list_table.views()
php_print("\n<form id=\"posts-filter\" method=\"post\">\n<input type=\"hidden\" name=\"taxonomy\" value=\"")
php_print(esc_attr(taxonomy))
php_print("\" />\n<input type=\"hidden\" name=\"post_type\" value=\"")
php_print(esc_attr(post_type))
php_print("\" />\n\n")
wp_list_table.display()
php_print("""
</form>
""")
if "category" == taxonomy:
    php_print("<div class=\"form-wrap edit-term-notes\">\n<p>\n ")
    printf(__("Deleting a category does not delete the posts in that category. Instead, posts that were only assigned to the deleted category are set to the default category %s. The default category cannot be deleted."), "<strong>" + apply_filters("the_category", get_cat_name(get_option("default_category")), "", "") + "</strong>")
    php_print("</p>\n   ")
    if current_user_can("import"):
        php_print(" <p>\n       ")
        printf(__("Categories can be selectively converted to tags using the <a href=\"%s\">category to tag converter</a>."), esc_url(import_link))
        php_print(" </p>\n  ")
    # end if
    php_print("</div>\n")
elif "post_tag" == taxonomy and current_user_can("import"):
    php_print("<div class=\"form-wrap edit-term-notes\">\n<p>\n ")
    printf(__("Tags can be selectively converted to categories using the <a href=\"%s\">tag to category converter</a>."), esc_url(import_link))
    php_print(" </p>\n</div>\n  ")
# end if
#// 
#// Fires after the taxonomy list table.
#// 
#// The dynamic portion of the hook name, `$taxonomy`, refers to the taxonomy slug.
#// 
#// @since 3.0.0
#// 
#// @param string $taxonomy The taxonomy name.
#//
do_action(str("after-") + str(taxonomy) + str("-table"), taxonomy)
#// phpcs:ignore WordPress.NamingConventions.ValidHookName.UseUnderscores
if can_edit_terms:
    php_print("""</div>
    </div><!-- /col-right -->
    </div><!-- /col-container -->
    """)
# end if
php_print("""
</div><!-- /wrap -->
""")
if (not wp_is_mobile()):
    php_print("""<script type=\"text/javascript\">
try{document.forms.addtag['tag-name'].focus();}catch(e){}
    </script>
    """)
# end if
wp_list_table.inline_edit()
php_include_file(ABSPATH + "wp-admin/admin-footer.php", once=True)