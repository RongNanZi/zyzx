from collections import Counter
import re
import numpy as np

class FindKey(object):
    def __init__(self, texts):

        self.texts = []
        for s in texts:
            # filter special character
            re_chinese = re.compile(u'[^a-zA-Z0-9\u4e00-\u9fa5]+')
            s = re_chinese.sub('', s.strip())
            self.texts.append(s)
        self.freq = self.get_freq()

    def get_limited(d, limited, bigger=True):
        wanted ={}

        for k, v in d.items():
            if v == limited:
                wanted.update({k, v})
                continue
            if ((v > limited) == bigger):
                wanted.update({k, v})
        return wanted



    def get_freq(self, min_gram=1, max_gram=6, freq_limit=1):
        """
        from texts find n_gram tokens and its frequency, return waned gram tokens over freq_limit

        :param texts: list string, parsed text
        :param min_gram: int, return wanted token's min length
        :param max_gram: int, return wanted token's max length
        :param freq_limit: int[1,) or float(0,1), the min occurrence of token
        :return: wanted: dict object,{word: its frequency

        """
        wanted = Counter()
        for s in self.texts:
            l_s = len(s)
            for gram in range(min_gram, max_gram+1):
                wanted.update(s[i: i+gram] for i in range(0, l_s-gram))
        if freq_limit < 1:
            freq_limit = int(len(self.texts)*freq_limit)
        if freq_limit == 1:
            return wanted
        else:
            return self.get_limited(wanted, freq_limit)


    def get_inner(self, min_gram=2, use_log=True, inner_limit=0):
        """
        from token counter find token's  mutual information entropy, return wanted token over in inner_limit
        :param min_gram: int, return wanted token's min length
        :param use_log: boolean, use log(p(x,y)/[p(x)*p(y)]) instead p(x,y)/[p(x)*p(y)]
        :param inner_limit: float, if use_log is True, it must > 0, else it must > 1
        :return: wanted： dict, {token: its MIE(mutual information entropy) }
        """

        wanted = {}
        n = len(self.freq)
        for t, f in self.freq.items():
            if len(t) >= min_gram:
                cut_x = range(len(t))[1:-1]
                if len(t) == 2:
                    words = [(t[0], t[1])]
                else:
                    words = [(t[:c], t[c:]) for c in cut_x]

                if use_log:
                    w_mie = [np.log(self.freq[t] * n/ (self.freq[t0]*self.freq[t1])) for t0, t1 in words]
                else:
                    w_mie = [self.freq[t] * n / (self.freq[t0]*self.freq[t1]) for t0, t1 in words]

                t_inner = min(w_mie)
                wanted.update({t:t_inner})
        if (use_log & (inner_limit == 0)) | (use_log==False & (inner_limit == 1)):
            return wanted
        else:
            return self.get_limited(wanted, inner_limit)



    def get_free(self, min_gram=2, free_limit=0):
        """
        get the token whoes free score over free_limit and length over min_gram in t_counter
        :param min_gram: int
        :param free_limit:folat
        :return wanted : dict, {token: its free score}
        """
        wanted ={}
        def get_entropy(a):
            sum_a = len(a)
            a = list(Counter(a).values())
            a_pro = [item/sum_a for item in a]
            wanted = sum(item*np.log(item)*-1 for item in a_pro )
            return wanted


        for t, f in self.freq.items():
            l_t = len(t)
            if l_t  >= min_gram:
                l_w, r_w = [],[]
                for text in self.texts:
                    l_text = len(text)

                    if l_text <= len(t):
                        continue
                    idx = text.find(t)
                    if idx == -1:
                        continue
                    elif idx == 0:
                        r_w.append(text[idx+l_t])
                    elif idx == l_text-l_t:
                        l_w.append(text[idx-1])
                    else:
                        l_w.append(text[idx-1])
                        r_w.append(text[idx+l_t])


                wanted.update({t: min(get_entropy(l_w), get_entropy(r_w))})

        if free_limit == 0:
            return wanted
        else:
            return self.get_limited(wanted, free_limit)




