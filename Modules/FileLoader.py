def load_item_list(path, language='en', server='gf_servers'):
    items = {}
    real_path = path + '\\' + 'Resources\\' + server + '\\proto\\' + language + '\\' + 'item_names.txt'
    with open(real_path, 'r') as file:
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
    real_path = path + '\\' + 'Resources\\' + server + '\\proto\\' + language + '\\' + 'mob_names.txt'
    with open(real_path, 'r') as file:
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
