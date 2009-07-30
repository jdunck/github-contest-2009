import datetime
import cPickle as pickle

#assumes python2.5

f_data = open('data.txt', 'r')
f_repos = open('repos.txt', 'r')
f_lang = open('lang.txt', 'r')

t_data = [
"43642:123344",
"742:22132",
"5414:2373",
"8660:1160",
"10218:409",
"301:6979"
]

t_repos = [
"123335:seivan/portfolio_python,2009-02-18",
"123336:sikanrong/Nautilus-OGL,2009-05-19",
"123337:edlebowitz/Downloads,2009-05-05",
"123338:DylanFM/roro-faces,2009-05-31,13635",
"123339:amazingsyco/technicolor-networking,2008-11-22",
"123340:netzpirat/radiant-scoped-admin-extension,2009-02-27,53611"
]

t_lang = [
"57493:C;29382",
"73920:JavaScript;9759,ActionScript;12781"
]

t_test = [
"55640",
"55670",
"55879",
"56215",
"56230"
]

"""
data features:
    repo lang
        maybe lang nerds care more/less about lang?
    repo popularity
        wish: repo commits over time (api)
    maintainer popularity
        wish: user join date (api)
    repo family
        # forks, depth of tree, existing rel position in tree
    repo create date - maybe older repos win?

questions
    how sparse?
    

repos:
    2-way links between forks
    lang attr as % of codebase or None.
"""

#repo = {
#    'path':'django/django',
#    'followers':[str(uid),],
#    'num_followers': int,
#    'created': datetime,
#    'upstream': str(rid),
#    'langs': {'C': (1000, 1.0),...},
#    'locl': 1000,
#}

def ingest():
    try:
        repos = pickle.load(open('ingest.pickle', 'rb')) #fast-path saves about 60% time after first-run.
        return repos
    except (IOError, TypeError):
        repos = {}
    for l in f_repos.xreadlines():
        l=l[:-1] #i have somehow used python for quite a while without learning a nicer idiom.
        rid, info = l.split(':')
        try:
            (path, s_create) = info.split(',')
            upstream_rid = None
        except ValueError:
            (path, s_create, upstream_rid) = info.split(',')
        created = datetime.datetime.strptime(s_create, "%Y-%m-%d")
        repos[rid] = {
            'raw':info,
            'path':path,
            'followers':[],
            'num_followers':0,
            'created': created,
            'upstream': upstream_rid,
            'langs': {},
            'loc':0
        }
    for l in f_lang.xreadlines():
        l=l[:-1]
        rid, info = l.split(':')
        if rid in repos:
            repo = repos[rid]
        else:
            continue
            
        for (pair) in info.split(','):
            lang, loc = pair.split(';')
            loc = int(loc)
            if loc > 0:
                repo['langs'][lang] = (loc,0)
                repo['loc'] += loc
        for lang, (loc, relative) in repo['langs'].items():
            repo['langs'][lang] = (loc, float(loc) / repo['loc'])
    for l in f_data.xreadlines():
        l=l[:-1]
        uid, rid = l.split(":")
        if rid in repos:
            repos[rid]['followers'].append(uid)
            repos[rid]['num_followers'] += 1
    f = open("ingest.pickle", 'wb')
    pickle.dump(repos, f)
    f.close()
    return repos

if __name__ == '__main__':
    ingest()
