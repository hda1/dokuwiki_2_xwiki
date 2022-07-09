import os
import re
import urllib.parse

from api import Client


def get_text_from_file(file_name):
    text = open(file_name, 'r', encoding='utf-8').read()
    return text


def format_text(text):
    text = text.replace('{{indexmenu_n>3}}', '')
    text = text.replace('{{indexmenu_n>5}}', '')
    text = text.replace('{{indexmenu_n>10}}', '')

    text = text.replace('--', '-')
    text = text.replace('===== Последние изменения: =====', '')
    text = text.replace('{{changes>count=30&render = list(signature, dayheaders)}}', '')
    return text

def update_links(wiki_dirs, wiki_dir, text):
    links = []
    matches = re.findall(r'\[\[(.*)\]\]', text)
    for match in matches:
        #print('****', match)
        split_link = match.split('|')
        old_link_url = split_link[0]
        link_name = split_link[1]
        link_name = link_name.strip()
        old_link_parts = old_link_url.split(':')

        #print(wiki_dirs[wiki_dir]['spaces'])
        #link_url = old_link_url.replace(':', os.sep)
        link_url = os.sep.join(old_link_url.split(':'))
        link_url = os.path.join(wiki_dir, link_url)

        #print(' = ', link_url)
        if wiki_dirs.get(link_url[:-1], ''): # dir with start.txt
            spaces = wiki_dirs[link_url[:-1]]['spaces']
            spaces_str = '.'.join(spaces)
            #print(' == ', spaces_str)
            new_link = link_name + '>>doc:' + spaces_str +'.WebHome'
            #print(' === ', new_link)
            text = text.replace(match, new_link)
            #print('\n')
            continue

        upper_dir, file_name = os.path.split(link_url)
        if wiki_dirs.get(upper_dir, ''):
            spaces = wiki_dirs[upper_dir]['spaces']
            spaces_str = '.'.join(spaces)
            #print(' ===** ', spaces)
            page_name = link_url + '.txt'

            file_data = wiki_dirs[upper_dir]['files'].get(page_name, '')
            #print('file_data = ', file_data)
            if not file_data:
                continue
            title = get_title(file_data['text']).replace('.', '\.')
            new_link = link_name + '>>doc:' + spaces_str + '.' + title
            #print('new_link = ', new_link)
            text = text.replace(match, new_link)
            #print('\n')
            continue
        #for old_link_part in old_link_parts[1:]:
            #new_link_part = wiki_dirs[]
        #    print(old_link_part)


        #print(' --- ', old_link_url, link_url, link_name)
        #print(match)

    return text


def update_imgs(text):
    image_names = []
    matches = re.findall(r'{{.*}}', text)
    for match in matches:
        if ('.png' in match) or ('.jpg' in match):
            img_name = match.split('?')[0].split(':')[1:]
            new_link = '[[image:' + img_name[-1] + ']]'
            #print(match)
            img_link = os.sep.join(img_name)
            #print(img_name)
            #print(img_link)
            text = text.replace(match, new_link)
            image_names.append(img_link)
    return text, image_names


def update_docs(text):
    docs_names = []
    matches = re.findall(r'{{.*}}', text)
    for match in matches:
        if ('.doc' in match) or ('.xls' in match) or ('.pdf' in match):
            print(match)
            doc_name = match.split('?')[0].split(':')[1:]
            doc_name[-1] = doc_name[-1].replace(' |}}', '')
            rus_doc_name = doc_name[-1]
            doc_name[-1] = urllib.parse.quote_plus(doc_name[-1])
            new_link = '[[attach:' + rus_doc_name + '||target="_blank"]]'
            doc_link = os.sep.join(doc_name)
            #print(rus_doc_name)
            #print(doc_link)
            #print(new_link)
            #print('\n')
            text = text.replace(match, new_link)
            docs_names.append([doc_link, rus_doc_name])
            #print('---- ', [doc_link, rus_doc_name])
    return text, docs_names


def get_title(text):
    title = re.findall(r'=======(.*)=======', text)
    if not title:
        title = re.findall(r'======(.*)======', text)
    if not title:
        title = re.findall(r'=====(.*)=====', text)
    if not title:
        title = re.findall(r'====(.*)====', text)
    if not title:
        title = ['Название страницы']
    return title[0].strip()


def get_dir_titles(wiki_dirs):
    for current_dir, dir_data in wiki_dirs.items():
        start_txt = os.path.join(current_dir, 'start.txt')
        if start_txt in dir_data['files']:
            text = dir_data['files'][start_txt]['text']
            dir_data['title'] = get_title(text)
            continue
        dir_txt = current_dir + '.txt'
        if os.path.exists(dir_txt):
            parrent_dir = os.path.split(current_dir)[0]
            file_info = wiki_dirs[parrent_dir]['files'].pop(dir_txt)
            text = file_info['text']
            wiki_dirs[current_dir]['files']['start.txt'] = file_info
            dir_data['title'] = get_title(text)


def get_spaces(wiki_dir, wiki_dirs):
    for current_dir, dir_data in wiki_dirs.items():
        spaces = []

        space_dir = current_dir
        while wiki_dir in space_dir:
            current_space = wiki_dirs[space_dir]['title'].strip()
            spaces.append(current_space)
            space_dir = os.path.split(space_dir)[0]
        spaces = spaces[::-1]
        dir_data['spaces'] = spaces


def get_wiki_dirs(wiki_dir):
    wiki_dirs = {}
    for current_dir, dirs, files in os.walk(wiki_dir):
        #current_dir = root.replace(wiki_dir, '')
        #current_dir = wiki_dir
        wiki_dirs[current_dir] = {}
        wiki_dirs[current_dir]['files'] = {}
        wiki_dirs[current_dir]['title'] = ''
        #root_dir = os.path.split(wiki_dir)[0]
        #wiki_dirs[current_dir]['spaces'] = get_spaces(wiki_dirs, current_dir.replace(root_dir, ''))
        #wiki_dirs[current_dir]['spaces'] = get_spaces(wiki_dirs, current_dir)
        #wiki_dirs[current_dir]['title']
        #print(root, dirs, files)
        for file_name in files:
            full_name = os.path.join(current_dir, file_name)
            text = get_text_from_file(full_name)
            wiki_dirs[current_dir]['files'][full_name] = {}
            wiki_dirs[current_dir]['files'][full_name]['text'] = text
            title = get_title(text)
            wiki_dirs[current_dir]['files'][full_name]['title'] = title

        #    if os.path.isfile(full_name):
    return wiki_dirs


client = Client('http://10.0.0.123/xwiki/rest/wikis/xwiki/', '', '')
wiki_dir = '/home/sam/Загрузки/info/pages'
media_dir = '/home/sam/Загрузки/info/media'

start_space = ['WIKI ГК Боравто',]

wiki_dirs = get_wiki_dirs(wiki_dir)
get_dir_titles(wiki_dirs)
get_spaces(wiki_dir, wiki_dirs)

#space = wiki_dirs['/home/sam/Загрузки/info/pages/bdrsu/os']['title']

for current_dir, dir_data in wiki_dirs.items():
    #print(current_dir, dir_data['title'], dir_data['spaces'])
    for file_name, file_data in dir_data['files'].items():
        text = file_data['text']
        text = format_text(text)

        #if not 'u/peo/i/ex' in file_name:
        #    continue

        #if not 'u/start' in file_name:
        #    continue

        #if not 'И БДРСУ 04-003.04.07-21' in text:
        #    continue

        print('####', file_name, file_data['title'], text[:100].replace('\n', '\\n'))

        page_title = file_data['title']
        if 'start.txt' in file_name:
            page_title = 'WebHome'
        #print(dir_data['spaces'], page_title)
        text = update_links(wiki_dirs, wiki_dir, text)
        text, image_names = update_imgs(text)
        text, doc_names = update_docs(text)
        response = client.send_page(dir_data['spaces'], page_title, text)
        for image_name in image_names:
            img_path = os.sep.join([media_dir, image_name])
            response = client.send_file(dir_data['spaces'], page_title, img_path, image_name.split(os.sep)[-1])

        for doc_name in doc_names:
            print(doc_name)
            doc_path = os.sep.join([media_dir, doc_name[0]])
            response = client.send_file(dir_data['spaces'], page_title, doc_path, doc_name[1])

    #for data_key, data_value in dir_data.items():
    #    print(data_key)
    #print('\n')
