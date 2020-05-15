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
#// Random_* Compatibility Library
#// for using the new PHP 7 random_* API in PHP 5 projects
#// 
#// The MIT License (MIT)
#// 
#// Copyright (c) 2015 - 2017 Paragon Initiative Enterprises
#// 
#// Permission is hereby granted, free of charge, to any person obtaining a copy
#// of this software and associated documentation files (the "Software"), to deal
#// in the Software without restriction, including without limitation the rights
#// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#// copies of the Software, and to permit persons to whom the Software is
#// furnished to do so, subject to the following conditions:
#// 
#// The above copyright notice and this permission notice shall be included in
#// all copies or substantial portions of the Software.
#// 
#// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#// SOFTWARE.
#//
if (not php_is_callable("random_bytes")):
    #// 
    #// If the libsodium PHP extension is loaded, we'll use it above any other
    #// solution.
    #// 
    #// libsodium-php project:
    #// @ref https://github.com/jedisct1/libsodium-php
    #// 
    #// @param int $bytes
    #// 
    #// @throws Exception
    #// 
    #// @return string
    #//
    def random_bytes(bytes=None, *args_):
        
        try: 
            bytes = RandomCompat_intval(bytes)
        except TypeError as ex:
            raise php_new_class("TypeError", lambda : TypeError("random_bytes(): $bytes must be an integer"))
        # end try
        if bytes < 1:
            raise php_new_class("Error", lambda : Error("Length must be greater than 0"))
        # end if
        #// 
        #// @var string
        #//
        buf = ""
        #// 
        #// \Sodium\randombytes_buf() doesn't allow more than 2147483647 bytes to be
        #// generated in one invocation.
        #//
        if bytes > 2147483647:
            i = 0
            while i < bytes:
                
                n = 1073741824 if bytes - i > 1073741824 else bytes - i
                buf += Sodium.randombytes_buf(int(n))
                i += 1073741824
            # end while
        else:
            buf += Sodium.randombytes_buf(int(bytes))
        # end if
        if php_is_string(buf):
            if RandomCompat_strlen(buf) == bytes:
                return buf
            # end if
        # end if
        raise php_new_class("Exception", lambda : Exception("Could not gather sufficient random data"))
    # end def random_bytes
# end if