import simplejson as json
from pathlib import Path as OSPath

def load_item_list(path, language='en', server='gf_servers'):
    items = {}
    real_path = OSPath(path + '/' + 'Resources/' + server + '/' + language + '/' + 'item_names.txt')
    with open(real_path, encoding='utf_8') as file:
        data = file.readlines()
        for line in data:
            word = line.split()
            item_id = word[0]
            item_name = ''
            for name in range(1, len(word)):
                if name == len(word)-1:
                    item_name += str(word[name])
                else:
                    item_name += str(word[name]) + ' ' 
            try:
                items[int(item_id)] = {
                    'name': item_name
                }
            except ValueError:
                continue
    return items

def load_mob_list(path, language='en', server='gf_servers'):
    mobs = {}
    real_path = OSPath(path + '/' + 'Resources/' + server + '/' + language + '/' + 'mob_names.txt')
    with open(real_path, encoding='utf_8') as file:
        data = file.readlines()
        for line in data:
            word = line.split()
            mob_id = word[0]
            mob_name = ''
            for name in range(1, len(word)):
                if name == len(word)-1:
                    mob_name += str(word[name])
                else:
                    mob_name += str(word[name]) + ' '
                
            try:
                mobs[int(mob_id)] = {
                    'name': mob_name
                }
            except ValueError:
                continue
    return mobs

def load_skill_names(path, language='en', server='gf_servers'):
    skills = {}
    real_path = OSPath(path + '/' + 'Resources/' + server + '/' + language + '/' + 'skill_names.txt')
    with open(real_path, encoding='utf_8') as file:
        data = file.readlines()
        for line in data:
            word = line.split()
            item_id = word[0]
            item_name = ''
            for name in range(1, len(word)):
                if name == len(word)-1:
                    item_name += str(word[name])
                else:
                    item_name += str(word[name]) + ' '
            try:
                skills[int(item_id)] = {
                    'name': item_name
                }
            except ValueError:
                continue
    return skills

def load_item_icon(path):
    skills = {}
    real_path = OSPath(path + '/' + 'Resources/item_icons.txt')
    with open(real_path, encoding='utf_8') as file:
        data = file.readlines()
        for line in data:
            word = line.split()
            item_id = word[0]
            item_name = ''
            for name in range(1, len(word)):
                if name == len(word)-1:
                    item_name += str(word[name])
                else:
                    item_name += str(word[name]) + ' '
            try:
                skills[int(item_id)] = {
                    'name': item_name
                }
            except ValueError:
                continue
    return skills

def load_schema_by_name(path, schema_name):
    real_path = OSPath(path + '/' + 'Resources/Schemas/' + schema_name + '.schema')
    try:
        with open(real_path, encoding='utf_8') as file:
            data = json.loads(file.read())
    except Exception as e:
        print(e)
        return False
    return data