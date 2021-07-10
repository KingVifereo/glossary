# encoding: utf-8
"""
This script generates a sidebar structure for Docsify (https://docsify.js.org/)
projects. It's intended as a way to make the sidebar a little more
straight-forward but the result will probably need some re-arranging.
Usage:
- Download this file to your project's directory
- "cd" into that directory
- Run "python3 generate_sidebar.py"
The script will:
- Generate a sidebar with links to all files, recursively
- Generate an index file (prefix _i_) for each sub-folder, also accessible via
  sidebar
Tip: On VSCode you can add the file .vscode/settings.json on the project's root
folder to hide the generated index files like so:
{
  "files.exclude": {
    "**/_i_*": true
  }
}
Remember to reload the window or restart the editor afterwards.
Credits:
Initially based on indaviande's script (https://github.com/docsifyjs/docsify/issues/610)
"""

from __future__ import print_function
import os
import glob
import sys
import io

"""
扫描目录生成索引文件（阿里云 ECS Linux 系统）

@param dir_path 要扫描的目录，默认为文件所在目录
@param level 扫描层级
"""
def scan_dir(dir_path='.', level=0):
    """
    查看项目中的每个目录，看看是否有什么要添加到侧边栏
    Look inside each directory in the project to see if there's anything good to
    add to the sidebar
    """
    def make_display_name_from_path(path):
        parts = path.split('/')
        name = parts[-1]
        name = name.split(".md")[0]  # Remove .md extension
        name = name.replace('_i_', '')  # Always remove _i_ index flag
        name = name.replace('_', ' ')  # Add space instead of -
        # Capitalize all words
        # (Exclude some words from capitalization)
        # forbidden = ['a', 'on', 'to', 'and', 'with', 'how', 'at', 'the']
        # forbidden = ['on', 'to', 'and', 'with', 'how', 'at', 'the']
        # capitalized = ''
        # for word in name.split(' '):
        #     if (word.lower() not in forbidden):
        #         capitalized += word.capitalize()
        #     else:
        #         capitalized += word.lower()
        #     capitalized += ' '
        # name = capitalized.strip()

        return name

    def create_dir_index_file(dir_path):
        # Create index file name
        dir_path_cols = dir_path.split('/')
        dir_name = dir_path_cols[-1]
        dir_path_cols[-1] = '_i_' + dir_name
        dir_index_file_path = "/".join(dir_path_cols) + '.md'

        if (os.path.isfile(dir_index_file_path)):
            # Clear existing file
            open(dir_index_file_path, 'w').close()

        # Compose the index file
        index_file = open(dir_index_file_path, 'w')

        # Write a link to parent index (skip root level)
        if (level > 1):
            parent_dir_path = os.path.split(dir_path)[0]
            parent_dir_path_dirname = os.path.dirname(parent_dir_path)
            parent_dir_path_basename = os.path.basename(parent_dir_path)
            parent_dir_display_name = make_display_name_from_path(
                parent_dir_path)
            # parent_index = f"{parent_dir_path_dirname}/_i_{parent_dir_path_basename}"
            parent_index = "{}/_i_{}".format(parent_dir_path_dirname, parent_dir_path_basename)
            index_file.write(
                # f"**Go back:** [{parent_dir_display_name}]({parent_index})\n"
                "**Go back:** [{}]({})\n".format(parent_dir_display_name, parent_index)
            )

        # Write a title
        dir_display_name = make_display_name_from_path(dir_path)
        index_file.write(
            # f"# {dir_display_name}\n"
            "# {}\n".format(dir_display_name)
        )

        # Write a link for each entry in this directory
        entries = [entry for entry in os.listdir(dir_path)]
        entries = sorted(entries) 
        for entry_file_name in entries:
            # Ignore entries starting with _ (so also _i_ for indexes) or .
            if (any(i in entry_file_name[0] for i in ['_', '.'])):
                continue

            entry_path = dir_path + '/' + entry_file_name
            entry_display_name = make_display_name_from_path(entry_path)
            # URL 转义
            entry_path_encode = dir_path + '/' + entry_file_name.replace(" ","%20")

            if os.path.isdir(entry_path):
                entry_path = dir_path + '/_i_' + entry_file_name
                # URL 转义
                entry_path_encode = dir_path + '/_i_' + entry_file_name.replace(" ","%20")

            # print(entry_path_encode)
            index_file.write(
                # f"- [{entry_display_name}]({entry_path_encode})\n"
                "- [{}]({})\n".format(entry_display_name, entry_path_encode)
            )

        index_file.close()

    def write_entry_in_sidebar(entry_path, index=False):
        """
        Write the sidebar entry, on the right level
        """
        # Max levels control
        if level >= max_levels:
            return

        entry_path_cols = entry_path.split('/')
        entry_file_name = entry_path_cols[-1]
        entry_path_encode = ''

        # Add prefix for index files
        if index:
            # URL 转义
            entry_path_cols[-1] = '_i_' + entry_file_name.replace(" ","%20")
            entry_path_encode = "/".join(entry_path_cols) + '.md'
            entry_path_cols[-1] = '_i_' + entry_file_name
            entry_path = "/".join(entry_path_cols) + '.md'
        else:
            # URL 转义
            entry_path_cols[-1] = entry_file_name.replace(" ","%20")
            entry_path_encode = "/".join(entry_path_cols)

        # Open sidebar file for writing
        sidebar_file = open('_sidebar.md', 'a')

        # Write entry in the sidebar file
        entry_display_name = make_display_name_from_path(entry_path)

        sidebar_file.write(
            # f"{'  ' * level}* [{entry_display_name}]({entry_path_encode})\n"
            "{}* [{}]({})\n".format('  '*level, entry_display_name, entry_path_encode)
        )

        # Save file
        sidebar_file.close()

    def remove_index_files(directory):
        # Remove indexes in this directory
        index_files = glob.glob(os.path.join(directory, '_i_*.md'))
        for file_name in index_files:
            try:
                os.remove(file_name)
                # print(file_name)
            except:
                print('Error while deleting file : ', file_name)
                print(sys.exc_info()[0])

    def execute():
        # Remove all old index files
        remove_index_files(dir_path)

        if level == 0:
            # Erase sidebar's content
            open('_sidebar.md', 'w').close()

            # Write the default header, if exists
            if default_header:
                sidebar_file = open('_sidebar.md', 'a')
                sidebar_file.write(default_header)
                sidebar_file.close()

        entries = [entry for entry in os.listdir(dir_path)]
        entries = sorted(entries)
        sublevel = level + 1

        if level > 0:
            # Create folder index (skip root directory)
            create_dir_index_file(dir_path)

        for entry_file_name in entries:
            # Ignore entries starting with _ (so also _i_ for indexes) or .
            if (any(i in entry_file_name[0] for i in ['_', '.'])):
                continue

            # Compose full path for this entry
            entry_path = dir_path + '/' + entry_file_name

            if os.path.isfile(entry_path):
                # Ignore files that are not markdown files
                if '.md' not in entry_file_name:
                    continue

                # README.md 不加入侧边栏目录
                if 'README.md' == entry_file_name:
                    continue

                # Found suitable sidebar item, write it down
                write_entry_in_sidebar(entry_path)

            if os.path.isdir(entry_path):
                # Ignore folders: assets
                if 'assets' == entry_file_name:
                    continue
                # Create a higher lever entry for this directory
                write_entry_in_sidebar(entry_path, index=True)

                # Scan this directory to add the entries it contains
                scan_dir(entry_path, sublevel)

    execute()


# 定义一个索引文件通头
# Define a section that is always going to be at the top of the sidebar. The
# format is regular Markdown. Example:
# default_header = '''
# * [Home](./home.md)
# * [Summary](./summary.md)
# '''
default_header = '''
'''

# Max levels
max_levels = 10

# 开始扫描目录，生成索引文件
# Start process
scan_dir()

print('✅ All done!')