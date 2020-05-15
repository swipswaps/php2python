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
#// Base WordPress Filesystem
#// 
#// @package WordPress
#// @subpackage Filesystem
#// 
#// 
#// Base WordPress Filesystem class which Filesystem implementations extend.
#// 
#// @since 2.5.0
#//
class WP_Filesystem_Base():
    verbose = False
    cache = Array()
    method = ""
    errors = None
    options = Array()
    #// 
    #// Returns the path on the remote filesystem of ABSPATH.
    #// 
    #// @since 2.7.0
    #// 
    #// @return string The location of the remote path.
    #//
    def abspath(self):
        
        folder = self.find_folder(ABSPATH)
        #// Perhaps the FTP folder is rooted at the WordPress install.
        #// Check for wp-includes folder in root. Could have some false positives, but rare.
        if (not folder) and self.is_dir("/" + WPINC):
            folder = "/"
        # end if
        return folder
    # end def abspath
    #// 
    #// Returns the path on the remote filesystem of WP_CONTENT_DIR.
    #// 
    #// @since 2.7.0
    #// 
    #// @return string The location of the remote path.
    #//
    def wp_content_dir(self):
        
        return self.find_folder(WP_CONTENT_DIR)
    # end def wp_content_dir
    #// 
    #// Returns the path on the remote filesystem of WP_PLUGIN_DIR.
    #// 
    #// @since 2.7.0
    #// 
    #// @return string The location of the remote path.
    #//
    def wp_plugins_dir(self):
        
        return self.find_folder(WP_PLUGIN_DIR)
    # end def wp_plugins_dir
    #// 
    #// Returns the path on the remote filesystem of the Themes Directory.
    #// 
    #// @since 2.7.0
    #// 
    #// @param string|false $theme Optional. The theme stylesheet or template for the directory.
    #// Default false.
    #// @return string The location of the remote path.
    #//
    def wp_themes_dir(self, theme=False):
        
        theme_root = get_theme_root(theme)
        #// Account for relative theme roots.
        if "/themes" == theme_root or (not php_is_dir(theme_root)):
            theme_root = WP_CONTENT_DIR + theme_root
        # end if
        return self.find_folder(theme_root)
    # end def wp_themes_dir
    #// 
    #// Returns the path on the remote filesystem of WP_LANG_DIR.
    #// 
    #// @since 3.2.0
    #// 
    #// @return string The location of the remote path.
    #//
    def wp_lang_dir(self):
        
        return self.find_folder(WP_LANG_DIR)
    # end def wp_lang_dir
    #// 
    #// Locates a folder on the remote filesystem.
    #// 
    #// @since 2.5.0
    #// @deprecated 2.7.0 use WP_Filesystem::abspath() or WP_Filesystem::wp_*_dir() instead.
    #// @see WP_Filesystem::abspath()
    #// @see WP_Filesystem::wp_content_dir()
    #// @see WP_Filesystem::wp_plugins_dir()
    #// @see WP_Filesystem::wp_themes_dir()
    #// @see WP_Filesystem::wp_lang_dir()
    #// 
    #// @param string $base The folder to start searching from.
    #// @param bool   $echo True to display debug information.
    #// Default false.
    #// @return string The location of the remote path.
    #//
    def find_base_dir(self, base=".", echo=False):
        
        _deprecated_function(__FUNCTION__, "2.7.0", "WP_Filesystem::abspath() or WP_Filesystem::wp_*_dir()")
        self.verbose = echo
        return self.abspath()
    # end def find_base_dir
    #// 
    #// Locates a folder on the remote filesystem.
    #// 
    #// @since 2.5.0
    #// @deprecated 2.7.0 use WP_Filesystem::abspath() or WP_Filesystem::wp_*_dir() methods instead.
    #// @see WP_Filesystem::abspath()
    #// @see WP_Filesystem::wp_content_dir()
    #// @see WP_Filesystem::wp_plugins_dir()
    #// @see WP_Filesystem::wp_themes_dir()
    #// @see WP_Filesystem::wp_lang_dir()
    #// 
    #// @param string $base The folder to start searching from.
    #// @param bool   $echo True to display debug information.
    #// @return string The location of the remote path.
    #//
    def get_base_dir(self, base=".", echo=False):
        
        _deprecated_function(__FUNCTION__, "2.7.0", "WP_Filesystem::abspath() or WP_Filesystem::wp_*_dir()")
        self.verbose = echo
        return self.abspath()
    # end def get_base_dir
    #// 
    #// Locates a folder on the remote filesystem.
    #// 
    #// Assumes that on Windows systems, Stripping off the Drive
    #// letter is OK Sanitizes \\ to / in Windows filepaths.
    #// 
    #// @since 2.7.0
    #// 
    #// @param string $folder the folder to locate.
    #// @return string|false The location of the remote path, false on failure.
    #//
    def find_folder(self, folder=None):
        
        if (php_isset(lambda : self.cache[folder])):
            return self.cache[folder]
        # end if
        if php_stripos(self.method, "ftp") != False:
            constant_overrides = Array({"FTP_BASE": ABSPATH, "FTP_CONTENT_DIR": WP_CONTENT_DIR, "FTP_PLUGIN_DIR": WP_PLUGIN_DIR, "FTP_LANG_DIR": WP_LANG_DIR})
            #// Direct matches ( folder = CONSTANT/ ).
            for constant,dir in constant_overrides:
                if (not php_defined(constant)):
                    continue
                # end if
                if folder == dir:
                    return trailingslashit(constant(constant))
                # end if
            # end for
            #// Prefix matches ( folder = CONSTANT/subdir ),
            for constant,dir in constant_overrides:
                if (not php_defined(constant)):
                    continue
                # end if
                if 0 == php_stripos(folder, dir):
                    #// $folder starts with $dir.
                    potential_folder = php_preg_replace("#^" + preg_quote(dir, "#") + "/#i", trailingslashit(constant(constant)), folder)
                    potential_folder = trailingslashit(potential_folder)
                    if self.is_dir(potential_folder):
                        self.cache[folder] = potential_folder
                        return potential_folder
                    # end if
                # end if
            # end for
        elif "direct" == self.method:
            folder = php_str_replace("\\", "/", folder)
            #// Windows path sanitisation.
            return trailingslashit(folder)
        # end if
        folder = php_preg_replace("|^([a-z]{1}):|i", "", folder)
        #// Strip out Windows drive letter if it's there.
        folder = php_str_replace("\\", "/", folder)
        #// Windows path sanitisation.
        if (php_isset(lambda : self.cache[folder])):
            return self.cache[folder]
        # end if
        if self.exists(folder):
            #// Folder exists at that absolute path.
            folder = trailingslashit(folder)
            self.cache[folder] = folder
            return folder
        # end if
        return_ = self.search_for_folder(folder)
        if return_:
            self.cache[folder] = return_
        # end if
        return return_
    # end def find_folder
    #// 
    #// Locates a folder on the remote filesystem.
    #// 
    #// Expects Windows sanitized path.
    #// 
    #// @since 2.7.0
    #// 
    #// @param string $folder The folder to locate.
    #// @param string $base   The folder to start searching from.
    #// @param bool   $loop   If the function has recursed. Internal use only.
    #// @return string|false The location of the remote path, false to cease looping.
    #//
    def search_for_folder(self, folder=None, base=".", loop=False):
        
        if php_empty(lambda : base) or "." == base:
            base = trailingslashit(self.cwd())
        # end if
        folder = untrailingslashit(folder)
        if self.verbose:
            #// translators: 1: Folder to locate, 2: Folder to start searching from.
            printf("\n" + __("Looking for %1$s in %2$s") + "<br/>\n", folder, base)
        # end if
        folder_parts = php_explode("/", folder)
        folder_part_keys = php_array_keys(folder_parts)
        last_index = php_array_pop(folder_part_keys)
        last_path = folder_parts[last_index]
        files = self.dirlist(base)
        for index,key in folder_parts:
            if index == last_index:
                continue
                pass
            # end if
            #// 
            #// Working from /home/ to /user/ to /wordpress/ see if that file exists within
            #// the current folder, If it's found, change into it and follow through looking
            #// for it. If it can't find WordPress down that route, it'll continue onto the next
            #// folder level, and see if that matches, and so on. If it reaches the end, and still
            #// can't find it, it'll return false for the entire function.
            #//
            if (php_isset(lambda : files[key])):
                #// Let's try that folder:
                newdir = trailingslashit(path_join(base, key))
                if self.verbose:
                    #// translators: %s: Directory name.
                    printf("\n" + __("Changing to %s") + "<br/>\n", newdir)
                # end if
                #// Only search for the remaining path tokens in the directory, not the full path again.
                newfolder = php_implode("/", php_array_slice(folder_parts, index + 1))
                ret = self.search_for_folder(newfolder, newdir, loop)
                if ret:
                    return ret
                # end if
            # end if
        # end for
        #// Only check this as a last resort, to prevent locating the incorrect install.
        #// All above procedures will fail quickly if this is the right branch to take.
        if (php_isset(lambda : files[last_path])):
            if self.verbose:
                #// translators: %s: Directory name.
                printf("\n" + __("Found %s") + "<br/>\n", base + last_path)
            # end if
            return trailingslashit(base + last_path)
        # end if
        #// Prevent this function from looping again.
        #// No need to proceed if we've just searched in `/`.
        if loop or "/" == base:
            return False
        # end if
        #// As an extra last resort, Change back to / if the folder wasn't found.
        #// This comes into effect when the CWD is /home/user/ but WP is at /var/www/....
        return self.search_for_folder(folder, "/", True)
    # end def search_for_folder
    #// 
    #// Returns the *nix-style file permissions for a file.
    #// 
    #// From the PHP documentation page for fileperms().
    #// 
    #// @link https://www.php.net/manual/en/function.fileperms.php
    #// 
    #// @since 2.5.0
    #// 
    #// @param string $file String filename.
    #// @return string The *nix-style representation of permissions.
    #//
    def gethchmod(self, file=None):
        
        perms = php_intval(self.getchmod(file), 8)
        if perms & 49152 == 49152:
            #// Socket.
            info = "s"
        elif perms & 40960 == 40960:
            #// Symbolic Link.
            info = "l"
        elif perms & 32768 == 32768:
            #// Regular.
            info = "-"
        elif perms & 24576 == 24576:
            #// Block special.
            info = "b"
        elif perms & 16384 == 16384:
            #// Directory.
            info = "d"
        elif perms & 8192 == 8192:
            #// Character special.
            info = "c"
        elif perms & 4096 == 4096:
            #// FIFO pipe.
            info = "p"
        else:
            #// Unknown.
            info = "u"
        # end if
        #// Owner.
        info += "r" if perms & 256 else "-"
        info += "w" if perms & 128 else "-"
        info += "s" if perms & 2048 else "x" if perms & 64 else "S" if perms & 2048 else "-"
        #// Group.
        info += "r" if perms & 32 else "-"
        info += "w" if perms & 16 else "-"
        info += "s" if perms & 1024 else "x" if perms & 8 else "S" if perms & 1024 else "-"
        #// World.
        info += "r" if perms & 4 else "-"
        info += "w" if perms & 2 else "-"
        info += "t" if perms & 512 else "x" if perms & 1 else "T" if perms & 512 else "-"
        return info
    # end def gethchmod
    #// 
    #// Gets the permissions of the specified file or filepath in their octal format.
    #// 
    #// @since 2.5.0
    #// 
    #// @param string $file Path to the file.
    #// @return string Mode of the file (the last 3 digits).
    #//
    def getchmod(self, file=None):
        
        return "777"
    # end def getchmod
    #// 
    #// Converts *nix-style file permissions to a octal number.
    #// 
    #// Converts '-rw-r--r--' to 0644
    #// From "info at rvgate dot nl"'s comment on the PHP documentation for chmod()
    #// 
    #// @link https://www.php.net/manual/en/function.chmod.php#49614
    #// 
    #// @since 2.5.0
    #// 
    #// @param string $mode string The *nix-style file permission.
    #// @return int octal representation
    #//
    def getnumchmodfromh(self, mode=None):
        
        realmode = ""
        legal = Array("", "w", "r", "x", "-")
        attarray = php_preg_split("//", mode)
        i = 0
        c = php_count(attarray)
        while i < c:
            
            key = php_array_search(attarray[i], legal)
            if key:
                realmode += legal[key]
            # end if
            i += 1
        # end while
        mode = php_str_pad(realmode, 10, "-", STR_PAD_LEFT)
        trans = Array({"-": "0", "r": "4", "w": "2", "x": "1"})
        mode = php_strtr(mode, trans)
        newmode = mode[0]
        newmode += mode[1] + mode[2] + mode[3]
        newmode += mode[4] + mode[5] + mode[6]
        newmode += mode[7] + mode[8] + mode[9]
        return newmode
    # end def getnumchmodfromh
    #// 
    #// Determines if the string provided contains binary characters.
    #// 
    #// @since 2.7.0
    #// 
    #// @param string $text String to test against.
    #// @return bool True if string is binary, false otherwise.
    #//
    def is_binary(self, text=None):
        
        return bool(php_preg_match("|[^\\x20-\\x7E]|", text))
        pass
    # end def is_binary
    #// 
    #// Changes the owner of a file or directory.
    #// 
    #// Default behavior is to do nothing, override this in your subclass, if desired.
    #// 
    #// @since 2.5.0
    #// 
    #// @param string     $file      Path to the file or directory.
    #// @param string|int $owner     A user name or number.
    #// @param bool       $recursive Optional. If set to true, changes file owner recursively.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def chown(self, file=None, owner=None, recursive=False):
        
        return False
    # end def chown
    #// 
    #// Connects filesystem.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @return bool True on success, false on failure (always true for WP_Filesystem_Direct).
    #//
    def connect(self):
        
        return True
    # end def connect
    #// 
    #// Reads entire file into a string.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Name of the file to read.
    #// @return string|false Read data on success, false on failure.
    #//
    def get_contents(self, file=None):
        
        return False
    # end def get_contents
    #// 
    #// Reads entire file into an array.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to the file.
    #// @return array|false File contents in an array on success, false on failure.
    #//
    def get_contents_array(self, file=None):
        
        return False
    # end def get_contents_array
    #// 
    #// Writes a string to a file.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string    $file     Remote path to the file where to write the data.
    #// @param string    $contents The data to write.
    #// @param int|false $mode     Optional. The file permissions as octal number, usually 0644.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def put_contents(self, file=None, contents=None, mode=False):
        
        return False
    # end def put_contents
    #// 
    #// Gets the current working directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @return string|false The current working directory on success, false on failure.
    #//
    def cwd(self):
        
        return False
    # end def cwd
    #// 
    #// Changes current directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $dir The new current directory.
    #// @return bool True on success, false on failure.
    #//
    def chdir(self, dir=None):
        
        return False
    # end def chdir
    #// 
    #// Changes the file group.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string     $file      Path to the file.
    #// @param string|int $group     A group name or number.
    #// @param bool       $recursive Optional. If set to true, changes file group recursively.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def chgrp(self, file=None, group=None, recursive=False):
        
        return False
    # end def chgrp
    #// 
    #// Changes filesystem permissions.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string    $file      Path to the file.
    #// @param int|false $mode      Optional. The permissions as octal number, usually 0644 for files,
    #// 0755 for directories. Default false.
    #// @param bool      $recursive Optional. If set to true, changes file permissions recursively.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def chmod(self, file=None, mode=False, recursive=False):
        
        return False
    # end def chmod
    #// 
    #// Gets the file owner.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to the file.
    #// @return string|false Username of the owner on success, false on failure.
    #//
    def owner(self, file=None):
        
        return False
    # end def owner
    #// 
    #// Gets the file's group.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to the file.
    #// @return string|false The group on success, false on failure.
    #//
    def group(self, file=None):
        
        return False
    # end def group
    #// 
    #// Copies a file.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string    $source      Path to the source file.
    #// @param string    $destination Path to the destination file.
    #// @param bool      $overwrite   Optional. Whether to overwrite the destination file if it exists.
    #// Default false.
    #// @param int|false $mode        Optional. The permissions as octal number, usually 0644 for files,
    #// 0755 for dirs. Default false.
    #// @return bool True on success, false on failure.
    #//
    def copy(self, source=None, destination=None, overwrite=False, mode=False):
        
        return False
    # end def copy
    #// 
    #// Moves a file.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $source      Path to the source file.
    #// @param string $destination Path to the destination file.
    #// @param bool   $overwrite   Optional. Whether to overwrite the destination file if it exists.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def move(self, source=None, destination=None, overwrite=False):
        
        return False
    # end def move
    #// 
    #// Deletes a file or directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string       $file      Path to the file or directory.
    #// @param bool         $recursive Optional. If set to true, deletes files and folders recursively.
    #// Default false.
    #// @param string|false $type      Type of resource. 'f' for file, 'd' for directory.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def delete(self, file=None, recursive=False, type=False):
        
        return False
    # end def delete
    #// 
    #// Checks if a file or directory exists.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file or directory.
    #// @return bool Whether $file exists or not.
    #//
    def exists(self, file=None):
        
        return False
    # end def exists
    #// 
    #// Checks if resource is a file.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file File path.
    #// @return bool Whether $file is a file.
    #//
    def is_file(self, file=None):
        
        return False
    # end def is_file
    #// 
    #// Checks if resource is a directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $path Directory path.
    #// @return bool Whether $path is a directory.
    #//
    def is_dir(self, path=None):
        
        return False
    # end def is_dir
    #// 
    #// Checks if a file is readable.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file.
    #// @return bool Whether $file is readable.
    #//
    def is_readable(self, file=None):
        
        return False
    # end def is_readable
    #// 
    #// Checks if a file or directory is writable.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file or directory.
    #// @return bool Whether $file is writable.
    #//
    def is_writable(self, file=None):
        
        return False
    # end def is_writable
    #// 
    #// Gets the file's last access time.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file.
    #// @return int|false Unix timestamp representing last access time, false on failure.
    #//
    def atime(self, file=None):
        
        return False
    # end def atime
    #// 
    #// Gets the file modification time.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file.
    #// @return int|false Unix timestamp representing modification time, false on failure.
    #//
    def mtime(self, file=None):
        
        return False
    # end def mtime
    #// 
    #// Gets the file size (in bytes).
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file Path to file.
    #// @return int|false Size of the file in bytes on success, false on failure.
    #//
    def size(self, file=None):
        
        return False
    # end def size
    #// 
    #// Sets the access and modification times of a file.
    #// 
    #// Note: If $file doesn't exist, it will be created.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $file  Path to file.
    #// @param int    $time  Optional. Modified time to set for file.
    #// Default 0.
    #// @param int    $atime Optional. Access time to set for file.
    #// Default 0.
    #// @return bool True on success, false on failure.
    #//
    def touch(self, file=None, time=0, atime=0):
        
        return False
    # end def touch
    #// 
    #// Creates a directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string     $path  Path for new directory.
    #// @param int|false  $chmod Optional. The permissions as octal number (or false to skip chmod).
    #// Default false.
    #// @param string|int $chown Optional. A user name or number (or false to skip chown).
    #// Default false.
    #// @param string|int $chgrp Optional. A group name or number (or false to skip chgrp).
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def mkdir(self, path=None, chmod=False, chown=False, chgrp=False):
        
        return False
    # end def mkdir
    #// 
    #// Deletes a directory.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $path      Path to directory.
    #// @param bool   $recursive Optional. Whether to recursively remove files/directories.
    #// Default false.
    #// @return bool True on success, false on failure.
    #//
    def rmdir(self, path=None, recursive=False):
        
        return False
    # end def rmdir
    #// 
    #// Gets details for files in a directory or a specific file.
    #// 
    #// @since 2.5.0
    #// @abstract
    #// 
    #// @param string $path           Path to directory or file.
    #// @param bool   $include_hidden Optional. Whether to include details of hidden ("." prefixed) files.
    #// Default true.
    #// @param bool   $recursive      Optional. Whether to recursively include file details in nested directories.
    #// Default false.
    #// @return array|false {
    #// Array of files. False if unable to list directory contents.
    #// 
    #// @type string $name        Name of the file or directory.
    #// @type string $perms       *nix representation of permissions.
    #// @type int    $permsn      Octal representation of permissions.
    #// @type string $owner       Owner name or ID.
    #// @type int    $size        Size of file in bytes.
    #// @type int    $lastmodunix Last modified unix timestamp.
    #// @type mixed  $lastmod     Last modified month (3 letter) and day (without leading 0).
    #// @type int    $time        Last modified time.
    #// @type string $type        Type of resource. 'f' for file, 'd' for directory.
    #// @type mixed  $files       If a directory and $recursive is true, contains another array of files.
    #// }
    #//
    def dirlist(self, path=None, include_hidden=True, recursive=False):
        
        return False
    # end def dirlist
# end class WP_Filesystem_Base