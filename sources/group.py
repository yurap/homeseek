# coding: utf-8


class Group(object):
    def __init__(self, gid, name, alias=None):
        self.id = gid
        self.name = name
        self.alias = alias

    def check_is_vk(self):
        return self.id.startswith('-')

    def get_url(self):
        base = 'https://vk.com/' if self.check_is_vk() else 'https://www.facebook.com/'
        alias = self.alias
        if alias is None:
            if self.check_is_vk():
                alias = 'club{}'.format(self.id[1:])
            else:
                alias = 'groups/{}'.format(self.id)
        return '{}{}'.format(base, alias)

    @staticmethod
    def list():
        return [
            Group('294101960601372' , u'(fb) посредников нет'),
            Group('341762229296973' , u'(fb) abagyr'),
            Group('509679185734909' , u'(fb) flats for friends'),
            Group('559042337578566' , u'(fb) homerenta'),
            Group('608689485811439' , u'(fb) kvartira.msk', 'kvartira.msk'),
            Group('785282138220080' , u'(fb) циан-авито'),
            Group('1425743251057302', u'(fb) аренда квартир москва'),
            Group('-14685598'       , u'(вк) добрая квартира'),
            Group('-29403745'       , u'(вк) сдать снять в москве'),
            Group('-36052766'       , u'(вк) адекватная аренда'),
            Group('-49428949'       , u'(вк) новоселье'),
            Group('-50263215'       , u'(вк) аренда7'),
            Group('-62069824'       , u'(вк) rentm'),
            Group('-95396194'       , u'(вк) уютное гнездышко'),
            Group('-111348472'      , u'(вк) epejitop'),
        ]

