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
#// Block Serialization Parser
#// 
#// @package WordPress
#// 
#// 
#// Class WP_Block_Parser_Block
#// 
#// Holds the block structure in memory
#// 
#// @since 3.8.0
#//
class WP_Block_Parser_Block():
    blockName = Array()
    attrs = Array()
    innerBlocks = Array()
    innerHTML = Array()
    innerContent = Array()
    #// 
    #// Constructor.
    #// 
    #// Will populate object properties from the provided arguments.
    #// 
    #// @since 3.8.0
    #// 
    #// @param string $name         Name of block.
    #// @param array  $attrs        Optional set of attributes from block comment delimiters.
    #// @param array  $innerBlocks  List of inner blocks (of this same class).
    #// @param string $innerHTML    Resultant HTML from inside block comment delimiters after removing inner blocks.
    #// @param array  $innerContent List of string fragments and null markers where inner blocks were found.
    #//
    def __init__(self, name=None, attrs=None, innerBlocks=None, innerHTML=None, innerContent=None):
        
        self.blockName = name
        self.attrs = attrs
        self.innerBlocks = innerBlocks
        self.innerHTML = innerHTML
        self.innerContent = innerContent
    # end def __init__
# end class WP_Block_Parser_Block
#// 
#// Class WP_Block_Parser_Frame
#// 
#// Holds partial blocks in memory while parsing
#// 
#// @internal
#// @since 3.8.0
#//
class WP_Block_Parser_Frame():
    block = Array()
    token_start = Array()
    token_length = Array()
    prev_offset = Array()
    leading_html_start = Array()
    #// 
    #// Constructor
    #// 
    #// Will populate object properties from the provided arguments.
    #// 
    #// @since 3.8.0
    #// 
    #// @param WP_Block_Parser_Block $block              Full or partial block.
    #// @param int                   $token_start        Byte offset into document for start of parse token.
    #// @param int                   $token_length       Byte length of entire parse token string.
    #// @param int                   $prev_offset        Byte offset into document for after parse token ends.
    #// @param int                   $leading_html_start Byte offset into document where leading HTML before token starts.
    #//
    def __init__(self, block=None, token_start=None, token_length=None, prev_offset=None, leading_html_start=None):
        
        self.block = block
        self.token_start = token_start
        self.token_length = token_length
        self.prev_offset = prev_offset if (php_isset(lambda : prev_offset)) else token_start + token_length
        self.leading_html_start = leading_html_start
    # end def __init__
# end class WP_Block_Parser_Frame
#// 
#// Class WP_Block_Parser
#// 
#// Parses a document and constructs a list of parsed block objects
#// 
#// @since 3.8.0
#// @since 4.0.0 returns arrays not objects, all attributes are arrays
#//
class WP_Block_Parser():
    document = Array()
    offset = Array()
    output = Array()
    stack = Array()
    empty_attrs = Array()
    #// 
    #// Parses a document and returns a list of block structures
    #// 
    #// When encountering an invalid parse will return a best-effort
    #// parse. In contrast to the specification parser this does not
    #// return an error on invalid inputs.
    #// 
    #// @since 3.8.0
    #// 
    #// @param string $document Input document being parsed.
    #// @return WP_Block_Parser_Block[]
    #//
    def parse(self, document=None):
        
        self.document = document
        self.offset = 0
        self.output = Array()
        self.stack = Array()
        self.empty_attrs = php_json_decode("{}", True)
        while True:
            pass
            
            if self.proceed():
                break
            # end if
        # end while
        return self.output
    # end def parse
    #// 
    #// Processes the next token from the input document
    #// and returns whether to proceed eating more tokens
    #// 
    #// This is the "next step" function that essentially
    #// takes a token as its input and decides what to do
    #// with that token before descending deeper into a
    #// nested block tree or continuing along the document
    #// or breaking out of a level of nesting.
    #// 
    #// @internal
    #// @since 3.8.0
    #// @return bool
    #//
    def proceed(self):
        
        next_token = self.next_token()
        token_type, block_name, attrs, start_offset, token_length = next_token
        stack_depth = php_count(self.stack)
        #// we may have some HTML soup before the next block.
        leading_html_start = self.offset if start_offset > self.offset else None
        for case in Switch(token_type):
            if case("no-more-tokens"):
                #// if not in a block then flush output.
                if 0 == stack_depth:
                    self.add_freeform()
                    return False
                # end if
                #// 
                #// Otherwise we have a problem
                #// This is an error
                #// 
                #// we have options
                #// - treat it all as freeform text
                #// - assume an implicit closer (easiest when not nesting)
                #// 
                #// for the easy case we'll assume an implicit closer.
                if 1 == stack_depth:
                    self.add_block_from_stack()
                    return False
                # end if
                #// 
                #// for the nested case where it's more difficult we'll
                #// have to assume that multiple closers are missing
                #// and so we'll collapse the whole stack piecewise
                #//
                while True:
                    
                    if not (0 < php_count(self.stack)):
                        break
                    # end if
                    self.add_block_from_stack()
                # end while
                return False
            # end if
            if case("void-block"):
                #// 
                #// easy case is if we stumbled upon a void block
                #// in the top-level of the document
                #//
                if 0 == stack_depth:
                    if (php_isset(lambda : leading_html_start)):
                        self.output[-1] = self.freeform(php_substr(self.document, leading_html_start, start_offset - leading_html_start))
                    # end if
                    self.output[-1] = php_new_class("WP_Block_Parser_Block", lambda : WP_Block_Parser_Block(block_name, attrs, Array(), "", Array()))
                    self.offset = start_offset + token_length
                    return True
                # end if
                #// otherwise we found an inner block.
                self.add_inner_block(php_new_class("WP_Block_Parser_Block", lambda : WP_Block_Parser_Block(block_name, attrs, Array(), "", Array())), start_offset, token_length)
                self.offset = start_offset + token_length
                return True
            # end if
            if case("block-opener"):
                #// track all newly-opened blocks on the stack.
                php_array_push(self.stack, php_new_class("WP_Block_Parser_Frame", lambda : WP_Block_Parser_Frame(php_new_class("WP_Block_Parser_Block", lambda : WP_Block_Parser_Block(block_name, attrs, Array(), "", Array())), start_offset, token_length, start_offset + token_length, leading_html_start)))
                self.offset = start_offset + token_length
                return True
            # end if
            if case("block-closer"):
                #// 
                #// if we're missing an opener we're in trouble
                #// This is an error
                #//
                if 0 == stack_depth:
                    #// 
                    #// we have options
                    #// - assume an implicit opener
                    #// - assume _this_ is the opener
                    #// - give up and close out the document
                    #//
                    self.add_freeform()
                    return False
                # end if
                #// if we're not nesting then this is easy - close the block.
                if 1 == stack_depth:
                    self.add_block_from_stack(start_offset)
                    self.offset = start_offset + token_length
                    return True
                # end if
                #// 
                #// otherwise we're nested and we have to close out the current
                #// block and add it as a new innerBlock to the parent
                #//
                stack_top = php_array_pop(self.stack)
                html = php_substr(self.document, stack_top.prev_offset, start_offset - stack_top.prev_offset)
                stack_top.block.innerHTML += html
                stack_top.block.innerContent[-1] = html
                stack_top.prev_offset = start_offset + token_length
                self.add_inner_block(stack_top.block, stack_top.token_start, stack_top.token_length, start_offset + token_length)
                self.offset = start_offset + token_length
                return True
            # end if
            if case():
                #// This is an error.
                self.add_freeform()
                return False
            # end if
        # end for
    # end def proceed
    #// 
    #// Scans the document from where we last left off
    #// and finds the next valid token to parse if it exists
    #// 
    #// Returns the type of the find: kind of find, block information, attributes
    #// 
    #// @internal
    #// @since 3.8.0
    #// @since 4.6.1 fixed a bug in attribute parsing which caused catastrophic backtracking on invalid block comments
    #// @return array
    #//
    def next_token(self):
        
        matches = None
        #// 
        #// aye the magic
        #// we're using a single RegExp to tokenize the block comment delimiters
        #// we're also using a trick here because the only difference between a
        #// block opener and a block closer is the leading `/` before `wp:` (and
        #// a closer has no attributes). we can trap them both and process the
        #// match back in PHP to see which one it was.
        #//
        has_match = php_preg_match("/<!--\\s+(?P<closer>\\/)?wp:(?P<namespace>[a-z][a-z0-9_-]*\\/)?(?P<name>[a-z][a-z0-9_-]*)\\s+(?P<attrs>{(?:(?:[^}]+|}+(?=})|(?!}\\s+\\/?-->).)*+)?}\\s+)?(?P<void>\\/)?-->/s", self.document, matches, PREG_OFFSET_CAPTURE, self.offset)
        #// if we get here we probably have catastrophic backtracking or out-of-memory in the PCRE.
        if False == has_match:
            return Array("no-more-tokens", None, None, None, None)
        # end if
        #// we have no more tokens.
        if 0 == has_match:
            return Array("no-more-tokens", None, None, None, None)
        # end if
        match, started_at = matches[0]
        length = php_strlen(match)
        is_closer = (php_isset(lambda : matches["closer"])) and -1 != matches["closer"][1]
        is_void = (php_isset(lambda : matches["void"])) and -1 != matches["void"][1]
        namespace = matches["namespace"]
        namespace = namespace[0] if (php_isset(lambda : namespace)) and -1 != namespace[1] else "core/"
        name = namespace + matches["name"][0]
        has_attrs = (php_isset(lambda : matches["attrs"])) and -1 != matches["attrs"][1]
        #// 
        #// Fun fact! It's not trivial in PHP to create "an empty associative array" since all arrays
        #// are associative arrays. If we use `array()` we get a JSON `[]`
        #//
        attrs = php_json_decode(matches["attrs"][0], True) if has_attrs else self.empty_attrs
        #// 
        #// This state isn't allowed
        #// This is an error
        #//
        if is_closer and is_void or has_attrs:
            pass
        # end if
        if is_void:
            return Array("void-block", name, attrs, started_at, length)
        # end if
        if is_closer:
            return Array("block-closer", name, None, started_at, length)
        # end if
        return Array("block-opener", name, attrs, started_at, length)
    # end def next_token
    #// 
    #// Returns a new block object for freeform HTML
    #// 
    #// @internal
    #// @since 3.9.0
    #// 
    #// @param string $innerHTML HTML content of block.
    #// @return WP_Block_Parser_Block freeform block object.
    #//
    def freeform(self, innerHTML=None):
        
        return php_new_class("WP_Block_Parser_Block", lambda : WP_Block_Parser_Block(None, self.empty_attrs, Array(), innerHTML, Array(innerHTML)))
    # end def freeform
    #// 
    #// Pushes a length of text from the input document
    #// to the output list as a freeform block.
    #// 
    #// @internal
    #// @since 3.8.0
    #// @param null $length how many bytes of document text to output.
    #//
    def add_freeform(self, length=None):
        
        length = length if length else php_strlen(self.document) - self.offset
        if 0 == length:
            return
        # end if
        self.output[-1] = self.freeform(php_substr(self.document, self.offset, length))
    # end def add_freeform
    #// 
    #// Given a block structure from memory pushes
    #// a new block to the output list.
    #// 
    #// @internal
    #// @since 3.8.0
    #// @param WP_Block_Parser_Block $block        The block to add to the output.
    #// @param int                   $token_start  Byte offset into the document where the first token for the block starts.
    #// @param int                   $token_length Byte length of entire block from start of opening token to end of closing token.
    #// @param int|null              $last_offset  Last byte offset into document if continuing form earlier output.
    #//
    def add_inner_block(self, block=None, token_start=None, token_length=None, last_offset=None):
        
        parent = self.stack[php_count(self.stack) - 1]
        parent.block.innerBlocks[-1] = block
        html = php_substr(self.document, parent.prev_offset, token_start - parent.prev_offset)
        if (not php_empty(lambda : html)):
            parent.block.innerHTML += html
            parent.block.innerContent[-1] = html
        # end if
        parent.block.innerContent[-1] = None
        parent.prev_offset = last_offset if last_offset else token_start + token_length
    # end def add_inner_block
    #// 
    #// Pushes the top block from the parsing stack to the output list.
    #// 
    #// @internal
    #// @since 3.8.0
    #// @param int|null $end_offset byte offset into document for where we should stop sending text output as HTML.
    #//
    def add_block_from_stack(self, end_offset=None):
        
        stack_top = php_array_pop(self.stack)
        prev_offset = stack_top.prev_offset
        html = php_substr(self.document, prev_offset, end_offset - prev_offset) if (php_isset(lambda : end_offset)) else php_substr(self.document, prev_offset)
        if (not php_empty(lambda : html)):
            stack_top.block.innerHTML += html
            stack_top.block.innerContent[-1] = html
        # end if
        if (php_isset(lambda : stack_top.leading_html_start)):
            self.output[-1] = self.freeform(php_substr(self.document, stack_top.leading_html_start, stack_top.token_start - stack_top.leading_html_start))
        # end if
        self.output[-1] = stack_top.block
    # end def add_block_from_stack
# end class WP_Block_Parser