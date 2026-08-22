import math
import re
from datetime import datetime, timezone

# JavaScript ၏ Math.round() နှင့် ကိုက်ညီစေရန် helper function
def js_round(x):
    return math.floor(x + 0.5)


class ceDateTime:
    def __init__(self, m_jd=None, m_tz=None, m_ct=0, m_SG=2361222):
        self.m_tz = self.ltzoh() if m_tz is None else m_tz
        self.m_jd = self.jdnow() if m_jd is None else m_jd
        self.m_ct = m_ct
        self.m_SG = m_SG

    @staticmethod
    def j2w(jd, ct=0, SG=2361222):
        j = math.floor(jd + 0.5)
        jf = jd + 0.5 - j
        if ct == 2 or (ct == 0 and jd < SG):
            b = j + 1524
            c = math.floor((b - 122.1) / 365.25)
            f = math.floor(365.25 * c)
            e = math.floor((b - f) / 30.6001)
            m = (e - 13) if e > 13 else (e - 1)
            d = b - f - math.floor(30.6001 * e)
            y = (c - 4715) if m < 3 else (c - 4716)
        else:
            j -= 1721119
            y = math.floor((4 * j - 1) / 146097)
            j = 4 * j - 1 - 146097 * y
            d = math.floor(j / 4)
            j = math.floor((4 * d + 3) / 1461)
            d = 4 * d + 3 - 1461 * j
            d = math.floor((d + 4) / 4)
            m = math.floor((5 * d - 3) / 153)
            d = 5 * d - 3 - 153 * m
            d = math.floor((d + 5) / 5)
            y = 100 * y + j
            if m < 10: m += 3
            else: m -= 9; y += 1
        jf *= 24; h = math.floor(jf); jf = (jf - h) * 60
        n = math.floor(jf); s = (jf - n) * 60
        return {'y': y, 'm': m, 'd': d, 'h': h, 'n': n, 's': s}

    @staticmethod
    def t2d(h, n, s):
        return ((h - 12) / 24 + n / 1440 + s / 86400)

    @staticmethod
    def w2j(y, m, d, h=12, n=0, s=0, ct=0, SG=2361222):
        a = math.floor((14 - m) / 12)
        y_adj = y + 4800 - a
        m_adj = m + (12 * a) - 3
        jd = d + math.floor((153 * m_adj + 2) / 5) + (365 * y_adj) + math.floor(y_adj / 4)
        if ct == 1:
            jd = jd - math.floor(y_adj / 100) + math.floor(y_adj / 400) - 32045
        elif ct == 2:
            jd = jd - 32083
        else:
            jd = jd - math.floor(y_adj / 100) + math.floor(y_adj / 400) - 32045
            if jd < SG:
                jd = d + math.floor((153 * m_adj + 2) / 5) + (365 * y_adj) + math.floor(y_adj / 4) - 32083
                if jd > SG: jd = SG
        return jd + ceDateTime.t2d(h, n, s)

    @staticmethod
    def u2j(ut): return 2440587.5 + ut / 86400.0

    @staticmethod
    def j2u(jd): return (jd - 2440587.5) * 86400.0 + 0.5

    @staticmethod
    def jdnow():
        dt = datetime.now(timezone.utc)
        return ceDateTime.u2j(dt.timestamp())

    @staticmethod
    def ltzoh():
        dt = datetime.now()
        return dt.astimezone().utcoffset().total_seconds() / 3600.0

    @staticmethod
    def GetDigits(s):
        return ''.join(c for c in s if c.isdigit())

    @staticmethod
    def wml(y, m, ct=0, SG=2361222):
        m2 = m + 1; y2 = y
        if m2 > 12: y2 += 1; m2 %= 12
        j1 = ceDateTime.w2j(y, m, 1, 12, 0, 0, ct, SG)
        j2 = ceDateTime.w2j(y2, m2, 1, 12, 0, 0, ct, SG)
        return j2 - j1

    @staticmethod
    def j2s(jd, fs="%Www %y-%mm-%dd %HH:%nn:%ss %zz", tz=0, ct=0, SG=2361222):
        jd += tz / 24.0
        dt = ceDateTime.j2w(jd, ct, SG)
        s = math.floor(dt['s'])
        l = math.floor((dt['s'] - s) * 1000)
        jdn = math.floor(jd + 0.5)
        wd = (jdn + 2) % 7
        h = dt['h'] % 12
        if h == 0: h = 12
        W = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        M = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        fm = fs
        fm = re.sub(r'%yyyy', f"{dt['y']:04d}", fm)
        fm = re.sub(r'%yy', f"{dt['y'] % 100:02d}", fm)
        fm = re.sub(r'%y', str(dt['y']), fm)
        fm = re.sub(r'%MMM', M[dt['m'] - 1][:3].upper(), fm)
        fm = re.sub(r'%Mmm', M[dt['m'] - 1][:3], fm)
        fm = re.sub(r'%mm', f"{dt['m']:02d}", fm)
        fm = re.sub(r'%M', M[dt['m'] - 1], fm)
        fm = re.sub(r'%m', str(dt['m']), fm)
        fm = re.sub(r'%dd', f"{dt['d']:02d}", fm)
        fm = re.sub(r'%d', str(dt['d']), fm)
        fm = re.sub(r'%HH', f"{dt['h']:02d}", fm)
        fm = re.sub(r'%H', str(dt['h']), fm)
        fm = re.sub(r'%hh', f"{h:02d}", fm)
        fm = re.sub(r'%h', str(h), fm)
        fm = re.sub(r'%AA', "AM" if dt['h'] < 12 else "PM", fm)
        fm = re.sub(r'%aa', "am" if dt['h'] < 12 else "pm", fm)
        fm = re.sub(r'%nn', f"{dt['n']:02d}", fm)
        fm = re.sub(r'%n', str(dt['n']), fm)
        fm = re.sub(r'%ss', f"{s:02d}", fm)
        fm = re.sub(r'%s', str(s), fm)
        fm = re.sub(r'%lll', f"{l:03d}", fm)
        fm = re.sub(r'%l', str(l), fm)
        fm = re.sub(r'%WWW', W[wd][:3].upper(), fm)
        fm = re.sub(r'%Www', W[wd][:3], fm)
        fm = re.sub(r'%W', W[wd], fm)
        fm = re.sub(r'%w', str(wd), fm)
        tzs = "-" if tz < 0 else "+"
        tzi = math.floor(tz)
        tzh = f"{tzi:02d}"
        rstr = tzs + tzh
        tzf = tz - tzi
        if tzf > 0:
            rstr += ":" + f"{math.floor(tzf * 60.0 + 0.5):02d}"
        fm = re.sub(r'%zz', rstr, fm)
        return fm

    @staticmethod
    def s2j(tstr, tz=0, ct=0, SG=2361222):
        s = ceDateTime.GetDigits(tstr)
        if len(s) in (8, 14, 17):
            y, m, d = int(s[0:4]), int(s[4:6]), int(s[6:8])
            h, n, sec, ls = 12, 0, 0, 0
            if len(s) in (14, 17):
                h, n, sec = int(s[8:10]), int(s[10:12]), int(s[12:14])
                if len(s) == 17:
                    ls = int(s[14:17])
                    sec += ls / 1000.0
            return ceDateTime.w2j(y, m, d, h, n, sec, ct, SG) - tz / 24.0
        return -1

    @property
    def jd(self): return self.m_jd
    @property
    def jdl(self): return self.m_jd + self.m_tz / 24.0
    @property
    def jdn(self): return js_round(self.m_jd)
    @property
    def jdnl(self): return js_round(self.m_jd + self.m_tz / 24.0)
    @property
    def y(self): return self.j2w(self.jdl, self.m_ct, self.m_SG)['y']
    @property
    def m(self): return self.j2w(self.jdl, self.m_ct, self.m_SG)['m']
    @property
    def d(self): return self.j2w(self.jdl, self.m_ct, self.m_SG)['d']
    @property
    def h(self): return self.j2w(self.jdl, self.m_ct, self.m_SG)['h']
    @property
    def n(self): return self.j2w(self.jdl, self.m_ct, self.m_SG)['n']
    @property
    def s(self): return math.floor(self.j2w(self.jdl, self.m_ct, self.m_SG)['s'])
    @property
    def l(self):
        dt = self.j2w(self.jdl, self.m_ct, self.m_SG)
        return math.floor((dt['s'] - math.floor(dt['s'])) * 1000)
    @property
    def w(self): return (self.jdnl + 2) % 7
    @property
    def ut(self): return self.j2u(self.m_jd)
    @property
    def tz(self): return self.m_tz
    @property
    def ct(self): return self.m_ct
    @property
    def SG(self): return self.m_SG
    @property
    def mlen(self): return self.wml(self.y, self.m, self.m_ct, self.m_SG)

    def ToString(self, fs="%Www %y-%mm-%dd %HH:%nn:%ss %zz"):
        return self.j2s(self.m_jd, fs, self.m_tz, self.m_ct, self.m_SG)


class ceMmDateTime(ceDateTime):
    def __init__(self, m_jd=None, m_tz=None, m_ct=0, m_SG=2361222, m_syt=0):
        super().__init__(m_jd, m_tz, m_ct, m_SG)
        self.m_syt = m_syt

    @staticmethod
    def GetMyConst(my):
        if my >= 1312:
            EI, WO, NM = 3, -0.5, 8
            fme, wte = [[1377, 1]], [1344, 1345]
        elif my >= 1217:
            EI, WO, NM = 2, -1, 4
            fme, wte = [[1234, 1], [1261, -1]], [1263, 1264]
        elif my >= 1100:
            EI, WO, NM = 1.3, -0.85, -1
            fme, wte = [[1120, 1], [1126, -1], [1150, 1], [1172, -1], [1207, 1]], [1201, 1202]
        elif my >= 798:
            EI, WO, NM = 1.2, -1.1, -1
            fme = [[813, -1], [849, -1], [851, -1], [854, -1], [927, -1], [933, -1], [936, -1],
                   [938, -1], [949, -1], [952, -1], [963, -1], [968, -1], [1039, -1]]
            wte = []
        else:
            EI, WO, NM = 1.1, -1.1, -1
            fme = [[205, 1], [246, 1], [471, 1], [572, -1], [651, 1], [653, 2], [656, 1], [672, 1],
                   [729, 1], [767, -1]]
            wte = []
        i = ceMmDateTime.bSearch2(my, fme)
        if i >= 0: WO += fme[i][1]
        i = ceMmDateTime.bSearch1(my, wte)
        EW = 1 if i >= 0 else 0
        return {'EI': EI, 'WO': WO, 'NM': NM, 'EW': EW}

    @staticmethod
    def bSearch2(k, A):
        l, u = 0, len(A) - 1
        while u >= l:
            i = math.floor((l + u) / 2)
            if A[i][0] > k: u = i - 1
            elif A[i][0] < k: l = i + 1
            else: return i
        return -1

    @staticmethod
    def bSearch1(k, A):
        l, u = 0, len(A) - 1
        while u >= l:
            i = math.floor((l + u) / 2)
            if A[i] > k: u = i - 1
            elif A[i] < k: l = i + 1
            else: return i
        return -1

    @staticmethod
    def cal_watat(my):
        SY = 1577917828.0 / 4320000.0
        LM = 1577917828.0 / 53433336.0
        MO = 1954168.050623
        c = ceMmDateTime.GetMyConst(my)
        TA = (SY / 12 - LM) * (12 - c['NM'])
        ed = (SY * (my + 3739)) % LM
        if ed < TA: ed += LM
        fm = js_round(SY * my + MO - ed + 4.5 * LM + c['WO'])
        if c['EI'] >= 2:
            TW = LM - (SY / 12 - LM) * c['NM']
            watat = 1 if ed >= TW else 0
        else:
            watat = (my * 7 + 2) % 19
            if watat < 0: watat += 19
            watat = math.floor(watat / 12)
        watat ^= c['EW']
        return {'fm': fm, 'watat': watat}

    @staticmethod
    def cal_my(my):
        yd, werr, fm = 0, 0, 0
        y2 = ceMmDateTime.cal_watat(my)
        myt = y2['watat']
        while True:
            yd += 1
            y1 = ceMmDateTime.cal_watat(my - yd)
            if y1['watat'] != 0 or yd >= 3: break
        if myt:
            nd = (y2['fm'] - y1['fm']) % 354
            myt = math.floor(nd / 31) + 1
            fm = y2['fm']
            if nd != 30 and nd != 31: werr = 1
        else:
            fm = y1['fm'] + 354 * yd
        tg1 = y1['fm'] + 354 * yd - 102
        return {'myt': myt, 'tg1': tg1, 'fm': fm, 'werr': werr}

    @staticmethod
    def j2m(jdn):
        jdn = js_round(jdn)
        SY = 1577917828.0 / 4320000.0
        MO = 1954168.050623
        my = math.floor((jdn - 0.5 - MO) / SY)
        yo = ceMmDateTime.cal_my(my)
        dd = jdn - yo['tg1'] + 1
        b = math.floor(yo['myt'] / 2)
        c = math.floor(1 / (yo['myt'] + 1))
        myl = 354 + (1 - c) * 30 + b
        mmt = math.floor((dd - 1) / myl)
        dd -= mmt * myl
        a = math.floor((dd + 423) / 512)
        mm = math.floor((dd - b * a + c * a * 30 + 29.26) / 29.544)
        e = math.floor((mm + 12) / 16)
        f = math.floor((mm + 11) / 16)
        md = dd - math.floor(29.544 * mm - 29.26) - b * e + c * f * 30
        mm += f * 3 - e * 4 + 12 * mmt
        return {'myt': yo['myt'], 'my': my, 'mm': mm, 'md': md}

    @staticmethod
    def cal_mp(md, mm, myt):
        mml = ceMmDateTime.cal_mml(mm, myt)
        return math.floor((md + 1) / 16) + math.floor(md / 16) + math.floor(md / mml)

    @staticmethod
    def cal_mml(mm, myt):
        mml = 30 - mm % 2
        if mm == 3: mml += math.floor(myt / 2)
        return mml

    @staticmethod
    def cal_myl(myt):
        return 354 + (1 - math.floor(1 / (myt + 1))) * 30 + math.floor(myt / 2)

    @staticmethod
    def cal_mf(md):
        return md - 15 * math.floor(md / 16)

    @staticmethod
    def cal_md(mf, mp, mm, myt):
        mml = ceMmDateTime.cal_mml(mm, myt)
        m1 = mp % 2
        m2 = math.floor(mp / 2)
        return m1 * (15 + m2 * (mml - 15)) + (1 - m1) * (mf + 15 * m2)

    @staticmethod
    def m2j(my, mm, md):
        yo = ceMmDateTime.cal_my(my)
        mmt = math.floor(mm / 13)
        mm = mm % 13 + mmt
        b = math.floor(yo['myt'] / 2)
        c = 1 - math.floor((yo['myt'] + 1) / 2)
        mm += 4 - math.floor((mm + 15) / 16) * 4 + math.floor((mm + 12) / 16)
        dd = md + math.floor(29.544 * mm - 29.26) - c * math.floor((mm + 11) / 16) * 30 + b * math.floor((mm + 12) / 16)
        myl = 354 + (1 - c) * 30 + b
        dd += mmt * myl
        return dd + yo['tg1'] - 1

    @staticmethod
    def my2sy(my, mm, md, k=0):
        buddhistEraOffset = 1182
        if k == 1:
            if mm >= 13: buddhistEraOffset = 1183
        elif k == 2:
            if mm == 1 or (mm == 2 and md < 15): buddhistEraOffset = 1181
        return my + buddhistEraOffset

    @staticmethod
    def cal_sabbath(md, mm, myt):
        mml = ceMmDateTime.cal_mml(mm, myt)
        s = 0
        if md in (8, 15, 23, mml): s = 1
        if md in (7, 14, 22, mml - 1): s = 2
        return s

    @staticmethod
    def cal_yatyaza(mm, wd):
        m1 = mm % 4
        wd1 = math.floor(m1 / 2) + 4
        wd2 = ((1 - math.floor(m1 / 2)) + m1 % 2) * (1 + 2 * (m1 % 2))
        return 1 if (wd == wd1 or wd == wd2) else 0

    @staticmethod
    def cal_pyathada(mm, wd):
        m1 = mm % 4
        wda = [1, 3, 3, 0, 2, 1, 2]
        if m1 == 0 and wd == 4: return 2
        return 1 if m1 == wda[wd] else 0

    @staticmethod
    def cal_nagahle(mm):
        if mm <= 0: mm = 4
        return math.floor((mm % 12) / 3)

    @staticmethod
    def cal_mahabote(my, wd):
        return (my - wd) % 7

    @staticmethod
    def cal_nakhat(my):
        return my % 3

    @staticmethod
    def cal_thamanyo(mm, wd):
        mmt = math.floor(mm / 13)
        mm = mm % 13 + mmt
        if mm <= 0: mm = 4
        m1 = mm - 1 - math.floor(mm / 9)
        wd1 = (m1 * 2 - math.floor(m1 / 8)) % 7
        wd2 = (wd + 7 - wd1) % 7
        return 1 if wd2 <= 1 else 0

    @staticmethod
    def cal_amyeittasote(md, wd):
        mf = md - 15 * math.floor(md / 16)
        wda = [5, 8, 3, 7, 2, 4, 1]
        return 1 if mf == wda[wd] else 0

    @staticmethod
    def cal_warameittugyi(md, wd):
        mf = md - 15 * math.floor(md / 16)
        wda = [7, 1, 4, 8, 9, 6, 3]
        return 1 if mf == wda[wd] else 0

    @staticmethod
    def cal_warameittunge(md, wd):
        mf = md - 15 * math.floor(md / 16)
        wn = (wd + 6) % 7
        return 1 if (12 - mf) == wn else 0

    @staticmethod
    def cal_yatpote(md, wd):
        mf = md - 15 * math.floor(md / 16)
        wda = [8, 1, 4, 6, 9, 8, 7]
        return 1 if mf == wda[wd] else 0

    @staticmethod
    def cal_thamaphyu(md, wd):
        mf = md - 15 * math.floor(md / 16)
        wda = [1, 2, 6, 6, 5, 6, 7]
        wdb = [0, 1, 0, 0, 0, 3, 3]
        if mf == wda[wd] or mf == wdb[wd]: return 1
        if mf == 4 and wd == 5: return 1
        return 0

    @staticmethod
    def cal_nagapor(md, wd):
        wda = [26, 21, 2, 10, 18, 2, 21]
        wdb = [17, 19, 1, 0, 9, 0, 0]
        if md == wda[wd] or md == wdb[wd]: return 1
        if (md == 2 and wd == 1): return 1
        if (md in (12, 4, 18) and wd == 2): return 1
        return 0

    @staticmethod
    def cal_yatyotema(mm, md):
        mmt = math.floor(mm / 13)
        mm = mm % 13 + mmt
        if mm <= 0: mm = 4
        mf = md - 15 * math.floor(md / 16)
        m1 = mm if (mm % 2) else ((mm + 9) % 12)
        m1 = (m1 + 4) % 12 + 1
        return 1 if mf == m1 else 0

    @staticmethod
    def cal_mahayatkyan(mm, md):
        if mm <= 0: mm = 4
        mf = md - 15 * math.floor(md / 16)
        m1 = (math.floor((mm % 12) / 2) + 4) % 6 + 1
        return 1 if mf == m1 else 0

    @staticmethod
    def cal_shanyat(mm, md):
        mmt = math.floor(mm / 13)
        mm = mm % 13 + mmt
        if mm <= 0: mm = 4
        mf = md - 15 * math.floor(md / 16)
        sya = [8, 8, 2, 2, 9, 3, 3, 5, 1, 4, 7, 4]
        return 1 if mf == sya[mm - 1] else 0

    @staticmethod
    def cal_astro(jdn):
        jdn = js_round(jdn)
        yo = ceMmDateTime.j2m(jdn)
        my, mm, md, myt = yo['my'], yo['mm'], yo['md'], yo['myt']
        wd = (jdn + 2) % 7
        hs = []
        if ceMmDateTime.cal_thamanyo(mm, wd): hs.append("Thamanyo")
        if ceMmDateTime.cal_amyeittasote(md, wd): hs.append("Amyeittasote")
        if ceMmDateTime.cal_warameittugyi(md, wd): hs.append("Warameittugyi")
        if ceMmDateTime.cal_warameittunge(md, wd): hs.append("Warameittunge")
        if ceMmDateTime.cal_yatpote(md, wd): hs.append("Yatpote")
        if ceMmDateTime.cal_thamaphyu(md, wd): hs.append("Thamaphyu")
        if ceMmDateTime.cal_nagapor(md, wd): hs.append("Nagapor")
        if ceMmDateTime.cal_yatyotema(mm, md): hs.append("Yatyotema")
        if ceMmDateTime.cal_mahayatkyan(mm, md): hs.append("Mahayatkyan")
        if ceMmDateTime.cal_shanyat(mm, md): hs.append("Shanyat")
        return hs

    @staticmethod
    def cal_holiday(jdn):
        jdn = js_round(jdn)
        yo = ceMmDateTime.j2m(jdn)
        my, mm, md, myt = yo['my'], yo['mm'], yo['md'], yo['myt']
        mp = ceMmDateTime.cal_mp(md, mm, myt)
        mmt = math.floor(mm / 13)
        hs = []
        go = ceDateTime.j2w(jdn)
        gy, gm, gd = go['y'], go['m'], go['d']
        SY = 1577917828.0 / 4320000.0
        MO = 1954168.050623
        BGNTG, SE3 = 1100, 1312
        ja = SY * (my + mmt) + MO
        jk = ja - 2.169918982 if my >= SE3 else ja - 2.1675
        akn, atn = js_round(jk), js_round(ja)
        if jdn == (atn + 1): hs.append("Myanmar New Year's Day")
        if (my + mmt) >= BGNTG:
            if jdn == atn: hs.append("Thingyan Atat")
            elif akn < jdn < atn: hs.append("Thingyan Akyat")
            elif jdn == akn: hs.append("Thingyan Akya")
            elif jdn == (akn - 1): hs.append("Thingyan Akyo")
            elif 1369 <= (my + mmt) < 1379 and (jdn == (akn - 2) or (atn + 2) <= jdn <= (akn + 7)):
                hs.append("Holiday")
            elif 1384 <= (my + mmt) <= 1385 and jdn in (akn - 5, akn - 4, akn - 3, akn - 2):
                hs.append("Holiday")
            elif (my + mmt) >= 1386 and (atn + 2) <= jdn <= (akn + 7):
                hs.append("Holiday")
        if 2018 <= gy <= 2021 and gm == 1 and gd == 1: hs.append("New Year's Day")
        elif gy >= 1948 and gm == 1 and gd == 4: hs.append("Independence Day")
        elif gy >= 1947 and gm == 2 and gd == 12: hs.append("Union Day")
        elif gy >= 1958 and gm == 3 and gd == 2: hs.append("Peasants' Day")
        elif gy >= 1945 and gm == 3 and gd == 27: hs.append("Resistance Day")
        elif gy >= 1923 and gm == 5 and gd == 1: hs.append("Labour Day")
        elif gy >= 1947 and gm == 7 and gd == 19: hs.append("Martyrs' Day")
        elif gy >= 1752 and gm == 12 and gd == 25: hs.append("Christmas Day")
        elif gy == 2017 and gm == 12 and gd == 30: hs.append("Holiday")
        elif 2017 <= gy <= 2021 and gm == 12 and gd == 31: hs.append("Holiday")
        if mm == 2 and mp == 1: hs.append("Buddha Day")
        elif mm == 4 and mp == 1: hs.append("Start of Buddhist Lent")
        elif mm == 7 and mp == 1: hs.append("End of Buddhist Lent")
        elif my >= 1379 and mm == 7 and md in (14, 16): hs.append("Holiday")
        elif mm == 8 and mp == 1: hs.append("Tazaungdaing")
        elif my >= 1379 and mm == 8 and md == 14: hs.append("Holiday")
        elif my >= 1282 and mm == 8 and md == 25: hs.append("National Day")
        elif mm == 10 and md == 1: hs.append("Karen New Year's Day")
        elif mm == 12 and mp == 1: hs.append("Tabaung Pwe")
        if 2019 <= gy <= 2021:
            substituteHoliday = [
                2458768, 2458772, 2458785, 2458800,
                2458855, 2458918, 2458950, 2459051, 2459062,
                2459152, 2459156, 2459167, 2459181, 2459184,
                2459300, 2459303, 2459323, 2459324,
                2459335, 2459548, 2459573,
            ]
            if ceMmDateTime.bSearch1(jdn, substituteHoliday) >= 0:
                hs.append("Holiday")
        return hs

    @staticmethod
    def DoE(y):
        a = y % 19
        b = math.floor(y / 100)
        c = y % 100
        d = math.floor(b / 4)
        e = b % 4
        f = math.floor((b + 8) / 25)
        g = math.floor((b - f + 1) / 3)
        h = (19 * a + b - d - g + 15) % 30
        i = math.floor(c / 4)
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = math.floor((a + 11 * h + 22 * l) / 451)
        q = h + l - 7 * m + 114
        p = (q % 31) + 1
        n = math.floor(q / 31)
        return js_round(ceDateTime.w2j(y, n, p, 12, 0, 0, 1))

    @staticmethod
    def cal_holiday2(jdn):
        jdn = js_round(jdn)
        yo = ceMmDateTime.j2m(jdn)
        my, mm, md, myt = yo['my'], yo['mm'], yo['md'], yo['myt']
        mp = ceMmDateTime.cal_mp(md, mm, myt)
        hs = []
        go = ceDateTime.j2w(jdn)
        gy, gm, gd = go['y'], go['m'], go['d']
        doe = ceMmDateTime.DoE(gy)
        if gy <= 2017 and gm == 1 and gd == 1: hs.append("New Year's Day")
        elif gy >= 1915 and gm == 2 and gd == 13: hs.append("G. Aung San BD")
        elif gy >= 1969 and gm == 2 and gd == 14: hs.append("Valentines Day")
        elif gy >= 1970 and gm == 4 and gd == 22: hs.append("Earth Day")
        elif gy >= 1392 and gm == 4 and gd == 1: hs.append("April Fools' Day")
        elif gy >= 1948 and gm == 5 and gd == 8: hs.append("Red Cross Day")
        elif gy >= 1994 and gm == 10 and gd == 5: hs.append("World Teachers' Day")
        elif gy >= 1947 and gm == 10 and gd == 24: hs.append("United Nations Day")
        elif gy >= 1753 and gm == 10 and gd == 31: hs.append("Halloween")
        if gy >= 1876 and jdn == doe: hs.append("Easter")
        elif gy >= 1876 and jdn == (doe - 2): hs.append("Good Friday")
        if my >= 1309 and mm == 11 and md == 16: hs.append("'Mon' National Day")
        elif mm == 9 and md == 1:
            hs.append("Shan New Year's Day")
            if my >= 1306: hs.append("Authors' Day")
        elif mm == 3 and mp == 1: hs.append("Mahathamaya Day")
        elif mm == 6 and mp == 1: hs.append("Garudhamma Day")
        elif my >= 1356 and mm == 10 and mp == 1: hs.append("Mothers' Day")
        elif my >= 1370 and mm == 12 and mp == 1: hs.append("Fathers' Day")
        elif mm == 5 and mp == 1: hs.append("Metta Day")
        elif mm == 5 and md == 10: hs.append("Taungpyone Pwe")
        elif mm == 5 and md == 23: hs.append("Yadanagu Pwe")
        return hs

    @staticmethod
    def j2ms(jd, fs="&y &M &P &ff", tz=0):
        jd += tz / 24.0
        jdn = js_round(jd)
        yo = ceMmDateTime.j2m(jdn)
        my, mm, md, myt = yo['my'], yo['mm'], yo['md'], yo['myt']
        mp = ceMmDateTime.cal_mp(md, mm, myt)
        mf = ceMmDateTime.cal_mf(md)
        mma = ["First Waso", "တန်ခူး", "ကဆုန်", "နယုန်", "ဝါဆို", "ဝါခေါင်", "တော်သလင်း",
               "သီတင်းကျွတ်", "တန်ဆောင်မုန်း", "နတ်တော်", "ပြာသို", "တပို့တွဲ", "တပေါင်း", "နှောင်းတန်ခူး", "နှောင်းကဆုန်"]
        mpa = ["လဆန်း", "လပြည့်", "လဆုတ်", "လကွယ်"] ####["Waxing", "Full Moon", "Waning", "New Moon"]
        fm = fs
        fm = re.sub(r'&yyyy', f"{my:04d}", fm)
        sy = ceMmDateTime.my2sy(my, mm, md, 0)
        fm = re.sub(r'&YYYY', f"{sy:04d}", fm)
        sy1 = ceMmDateTime.my2sy(my, mm, md, 1)
        fm = re.sub(r'&XXXX', f"{sy1:04d}", fm)
        sy2 = ceMmDateTime.my2sy(my, mm, md, 2)
        fm = re.sub(r'&ZZZZ', f"{sy2:04d}", fm)
        fm = re.sub(r'&y', str(my), fm)
        fm = re.sub(r'&mm', f"{mm:02d}", fm)
        month_name = mma[mm]
        if mm == 4 and myt > 0: month_name = "Second " + month_name
        fm = re.sub(r'&M', month_name, fm)
        fm = re.sub(r'&m', str(mm), fm)
        fm = re.sub(r'&P', mpa[mp], fm)
        fm = re.sub(r'&dd', f"{md:02d}", fm)
        fm = re.sub(r'&d', str(md), fm)
        fm = re.sub(r'&ff', f"{mf:02d}", fm)
        fm = re.sub(r'&f', str(mf), fm)
        return fm

    @property
    def myt(self): return self.j2m(self.jdnl)['myt']
    @property
    def my(self): return self.j2m(self.jdnl)['my']
    @property
    def syt(self): return self.m_syt
    @syt.setter
    def syt(self, val): self.m_syt = val
    @property
    def sy(self): return self.my2sy(self.my, self.mm, self.md, self.syt)
    @property
    def my_name(self):
        yna = ["Hpusha", "Magha", "Phalguni", "Chitra", "Visakha", "Jyeshtha",
               "Ashadha", "Sravana", "Bhadrapaha", "Asvini", "Krittika", "Mrigasiras"]
        return yna[self.my % 12]
    @property
    def mm(self): return self.j2m(self.jdnl)['mm']
    @property
    def md(self): return self.j2m(self.jdnl)['md']
    @property
    def mp(self):
        yo = self.j2m(self.jdnl)
        return self.cal_mp(yo['md'], yo['mm'], yo['myt'])
    @property
    def mf(self): return self.cal_mf(self.md)
    @property
    def mmlen(self): return self.cal_mml(self.mm, self.myt)
    @property
    def sabbath(self):
        yo = self.j2m(self.jdnl)
        sb = self.cal_sabbath(yo['md'], yo['mm'], yo['myt'])
        if sb == 1: return "Sabbath"
        if sb == 2: return "Sabbath Eve"
        return ""
    @property
    def yatyaza(self):
        return "Yatyaza" if self.cal_yatyaza(self.mm, self.w) else ""
    @property
    def pyathada(self):
        v = self.cal_pyathada(self.mm, self.w)
        return ["", "Pyathada", "Afternoon Pyathada"][v % 3]
    @property
    def nagahle(self):
        return ["West", "North", "East", "South"][self.cal_nagahle(self.mm) % 4]
    @property
    def mahabote(self):
        return ["Binga", "Atun", "Yaza", "Adipati", "Marana", "Thike", "Puti"][self.cal_mahabote(self.my, self.w) % 7]
    @property
    def nakhat(self):
        return ["Ogre", "Elf", "Human"][self.cal_nakhat(self.my) % 3]
    @property
    def astro(self): return self.cal_astro(self.jdnl)
    @property
    def holidays(self): return self.cal_holiday(self.jdnl)
    @property
    def holidays2(self): return self.cal_holiday2(self.jdnl)

    def ToMString(self, fs="&yyyy &M &P &ff"):
        if self.m_syt == 1: fs = fs.replace("&YYYY", "&XXXX")
        elif self.m_syt == 2: fs = fs.replace("&YYYY", "&ZZZZ")
        return self.j2ms(self.jd, fs, self.tz)

    @classmethod
    def from_gregorian(cls, y, m, d, tz=6.5):
        jd = cls.w2j(y, m, d, 12, 0, 0, 0)
        return cls(jd, tz)


class ceMmTranslate:
    def __init__(self):
        self.m_lang = self.Init()

    def T(self, s, toLn=1, fromLn=0):
        for item in self.m_lang:
            if len(item) > max(toLn, fromLn):
                fstr = item[fromLn]
                rstr = item[toLn]
                s = re.sub(re.escape(fstr), rstr, s)
        return s

    @staticmethod
    def Init():
        return [
            ["Myanmar Year", "မြန်မာနှစ်", "ျမန္မာႏွစ္", "သက္ကရာဇ်ဍုၚ်", "ပီၵေႃးၸႃႇ", "ကီၢ်ပယီၤ"],
            ["Tagu", "တန်ခူး", "တန္ခူး", "ဂိတုစဲ", "ႁႃႈ", "လါချံ"],
            ["Kason", "ကဆုန်", "ကဆုန္", "ဂိတုပသာ်", "ႁူၵ်း", "ဒ့ၣ်ညါ"],
            ["Nayon", "နယုန်", "နယုန္", "ဂိတုဇှေ်", "ၸဵတ်း", "လါနွံ"],
            ["Waso", "ဝါဆို", "ဝါဆို", "ဂိတုဒ္ဂိုန်", "ပႅတ်ႇ", "လါဃိး"],
            ["Wagaung", "ဝါခေါင်", "ဝါေခါင္", "ဂိတုခ္ဍဲသဳ", "ၵဝ်ႈ", "လါခူး"],
            ["Tawthalin", "တော်သလင်း", "ေတာ္သလင္း", "ဂိတုဘတ်", "သိပ်း", "ဆံးမုၢ်"],
            ["Thadingyut", "သီတင်းကျွတ်", "သီတင္းကြ်တ္", "ဂိတုဝှ်", "သိပ်းဢဵတ်း", "ဆံးဆၣ်"],
            ["Tazaungmon", "တန်ဆောင်မုန်း", "တန္ေဆာင္မုန္း", "ဂိတုက္ထိုန်", "သိပ်းသွင်", "လါနီ"],
            ["Nadaw", "နတ်တော်", "နတ္ေတာ္", "ဂိတုမြေက္ကသဵု", "ၸဵင်", "လါပျုၤ"],
            ["Pyatho", "ပြာသို", "ျပာသို", "ဂိတုပှော်", "ၵမ်", "သလ့ၤ"],
            ["Tabodwe", "တပို့တွဲ", "တပို႔တြဲ", "ဂိတုမာ်", "သၢမ်", "ထ့ကူး"],
            ["Tabaung", "တပေါင်း", "တေပါင္း", "ဂိတုဖဝ်ရဂိုန်", "သီႇ", "သွ့ကီ"],
            ["Waxing", "လဆန်း", "လဆန္း", "မံက်", "လိူၼ်မႂ်ႇ", "လါထီၣ်"],
            ["Full Moon", "လပြည့်", "လျပည့္", "ပေၚ်", "လိူၼ်မူၼ်း", "လါပှဲၤ"],
            ["Waning", "လဆုတ်", "လဆုတ္", "စွေက်", "လိူၼ်လွင်ႈ", "လါလီၤ"],
            ["New Moon", "လကွယ်", "လကြယ္", "အိုတ်", "လိူၼ်လပ်း", "လါဘၢ"],
            ["Sunday", "တနင်္ဂနွေ", "တနဂၤေႏြ", "တ္ၚဲအဒိုတ်", "ဝၼ်းဢႃးတိတ်ႉ", "မုၢ်ဒဲး"],
            ["Monday", "တနင်္လာ", "တနလၤာ", "တ္ၚဲစန်", "ဝၼ်းၸၼ်", "မုၢ်ဆၣ်"],
            ["Tuesday", "အင်္ဂါ", "အဂၤါ", "တ္ၚဲအင္ၚာ", "ဝၼ်းဢၢင်းၵၢၼ်း", "မုၢ်ယူာ်"],
            ["Wednesday", "ဗုဒ္ဓဟူး", "ဗုဒၶဟူး", "တ္ၚဲဗုဒ္ဓဝါ", "ဝၼ်းပုတ်ႉ", "မုၢ်ပျဲၤ"],
            ["Thursday", "ကြာသပတေး", "ၾကာသပေတး", "တ္ၚဲဗြဴဗတိ", "ဝၼ်းၽတ်း", "မုၢ်လ့ၤဧိၤ"],
            ["Friday", "သောကြာ", "ေသာၾကာ", "တ္ၚဲသိုက်", "ဝၼ်းသုၵ်း", "မုၢ်ဖီဖး"],
            ["Saturday", "စနေ", "စေန", "တ္ၚဲသ္ၚိသဝ်", "ဝၼ်းသဝ်", "မုၢ်ဘူၣ်"],
            ["Sabbath", "ဥပုသ်", "ဥပုသ္", "တ္ၚဲသဳ", "သိၼ်", "အိၣ်ဘှံး"],
            ["Sabbath Eve", "အဖိတ်", "အဖိတ္", "တ္ၚဲတိၚ်", "ၽိတ်ႈ", "အဖိတ်"],
            ["Yatyaza", "ရက်ရာဇာ", "ရက္ရာဇာ", "တ္ၚဲရာဇာ", "ဝၼ်းထုၼ်း", "ရက်ရာဇာ"],
            ["Pyathada", "ပြဿဒါး", "ျပႆဒါး", "တ္ၚဲပြာဗ္ဗဒါ", "ဝၼ်းပျၢတ်ႈ", "ပြဿဒါး"],
            ["Thamanyo", "သမားညို", "သမားညိဳ", "ကိုန်ဟုံဗြမ်", "သမားညို", "သမားညို"],
            ["Nagapor", "နဂါးပေါ်", "နဂါးေပၚ", "နာ်မံက်", "နဂါးပေါ်", "နဂါးပေါ်"],
            ["Amyeittasote", "အမြိတ္တစုတ်", "အၿမိတၱစုတ္", "ကိုန်အမြိုတ်", "အမြိတ္တစုတ်", "အမြိတ္တစုတ်"],
            ["Warameittugyi", "ဝါရမိတ္တုကြီး", "ဝါရမိတၱဳႀကီး", "ကိုန်ဝါရမိတ္တုဇၞော်", "ဝါရမိတ္တုကြီး", "ဝါရမိတ္တုကြီး"],
            ["Warameittunge", "ဝါရမိတ္တုငယ်", "ဝါရမိတၱဳငယ္", "ကိုန်ဝါရမိတ္တုဍောတ်", "ဝါရမိတ္တုငယ်", "ဝါရမိတ္တုငယ်"],
            ["Thamaphyu", "သမားဖြူ", "သမားျဖဴ", "ကိုန်လေၚ်ဒိုက်", "သမားဖြူ", "သမားဖြူ"],
            ["Yatpote", "ရက်ပုပ်", "ရက္ပုပ္", "ကိုန်လီုလာ်", "ရက်ပုပ်", "ရက်ပုပ်"],
            ["Yatyotema", "ရက်ယုတ်မာ", "ရက္ယုတ္မာ", "ကိုန်ယုတ်မာ", "ရက်ယုတ်မာ", "ရက်ယုတ်မာ"],
            ["Mahayatkyan", "မဟာရက်ကြမ်း", "မဟာရက္ၾကမ္း", "ကိုန်ဟွံခိုဟ်", "မဟာရက်ကြမ်း", "မဟာရက်ကြမ်း"],
            ["Shanyat", "ရှမ်းရက်", "ရွမ္းရက္", "တ္ၚဲဒတန်", "ရှမ်းရက်", "ရှမ်းရက်"],
            ["0", "၀", "၀", "၀", "0", "၀"], ["1", "၁", "၁", "၁", "1", "၁"],
            ["2", "၂", "၂", "၂", "2", "၂"], ["3", "၃", "၃", "၃", "3", "၃"],
            ["4", "၄", "၄", "၄", "4", "၄"], ["5", "၅", "၅", "၅", "5", "၅"],
            ["6", "၆", "၆", "၆", "6", "၆"], ["7", "၇", "၇", "၇", "7", "၇"],
            ["8", "၈", "၈", "၈", "8", "၈"], ["9", "၉", "၉", "၉", "9", "၉"],
        ]


class ceMmChronicle:
    def __init__(self):
        self.m_ev = self.InitChronicle()
        self.m_rul = self.InitRulers()
        self.m_dyn = self.InitDynasties()

    def chronicle(self, jdn):
        i = self.hSearch(jdn)
        return self.m_ev[i]["Description"] if i >= 0 else ""

    def hSearch(self, jdn):
        l, u = 0, len(self.m_ev) - 1
        while u >= l:
            i = math.floor((l + u) / 2)
            if self.m_ev[i]["Julian Day Number"] < jdn: l = i + 1
            elif self.m_ev[i]["Julian Day Number"] > jdn: u = i - 1
            else: return i
        return -1

    def ruler(self, jdn):
        return [r for r in self.m_rul if r["Beginning_JDN"] <= jdn <= r["Ending_JDN"]]

    def dynasty(self, name):
        return self.m_dyn.get(name)

    @staticmethod
    def InitRulers():
        return [
            {"Name": "Anawrahta Minsaw", "Beginning_JDN": 2102602, "Ending_JDN": 2114533, "Dynasty": "Pagan"},
            {"Name": "Bayinnaung", "Beginning_JDN": 2287315, "Ending_JDN": 2298801, "Dynasty": "Taungoo"},
            {"Name": "Alaungpaya", "Beginning_JDN": 2361024, "Ending_JDN": 2364018, "Dynasty": "Konbaung"},
            {"Name": "Thibaw Min", "Beginning_JDN": 2407259, "Ending_JDN": 2409875, "Dynasty": "Konbaung"},
            # (အခြားမင်းများကို မူရင်း JS မှ ကူးထည့်ပါ - နေရာလွတ်ရှည်လျှင်းစေရန် အကျဉ်းချုံးထားပါသည်)
        ]

    @staticmethod
    def InitDynasties():
        return {
            "Pagan": {"Description": "Pagan Kingdom (ပုဂံခေတ်)"},
            "Taungoo": {"Description": "Taungoo (တောင်ငူခေတ်)"},
            "Konbaung": {"Description": "Konbaung (ကုန်းဘောင်ခေတ်)"},
            "Ava": {"Description": "Ava Dynasty (အင်းဝခေတ်)"},
            "Hanthawaddy": {"Description": "Hanthawaddy Dynasty (ဟံသာဝတီ)"},
        }

    @staticmethod
    def InitChronicle():
        return [
            {"Julian Day Number": 2031512, "Myanmar Year": 211, "Description": "Foundation of Pagan."},
            {"Julian Day Number": 2219652, "Myanmar Year": 726, "Description": "Foundation of Inwa."},
            # (အခြားမှတ်တမ်းများကို မူရင်း JS မှ ကူးထည့်ပါ)
        ]