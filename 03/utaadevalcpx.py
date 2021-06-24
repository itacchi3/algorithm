import json, re, parser, collections

# 2021.6.23
def evaluateCpx(str_filename, str_exname, dic_varinfo, str_code):
    
    if str_code != "...":
         return  analyzeCodeForCpx(str_code, dic_varinfo)

    f = open(str_filename, "r", encoding="utf-8")
    dic_ipynbfile = json.load(f)
    f.close()
    
    reg1 = '### この行のコメントを改変してはいけません %(\d-\d)% ###'
    for list_cell in dic_ipynbfile["cells"]:
        
        if len(list_cell["source"]) == 0:
            continue
        str1 = list_cell["source"][0]
        ma1 = re.search(reg1, str1)
        
        if ma1 is not None and ma1.group(1) == str_exname:
            str_code = "".join(list_cell["source"][1:])
            return  analyzeCodeForCpx(str_code, dic_varinfo)
    return "Invalid Call"


def analyzeCodeForCpx(str_code, dic_varinfo):
    dic_warning = {
        "WM:FEWCOMMENTS": "解答のコードには適宜コメントを入れて下さい。正しくても評価者が読解できない場合は減点となる可能性があります。", 
        "WM:OVERTIMECOMPLEXITY": "模範解答よりも大きな時間計算量になっています", 
        "WM:OVERSPACECOMPLEXITY": "模範解答よりも大きな領域計算量になっています", 
        "WM:LESSTIMECOMPLEXITY": "正しく時間計算量が求められていない可能性があります（模範解答よりも少ない時間計算量になっています）", 
        "WM:LESSSPACECOMPLEXITY": "正しく領域計算量が求められていない可能性があります（模範解答よりも少ない領域計算量になっています）", 
    }
    list_warningcheck = []
    
    tup_info = abstractAnswerInfo(str_code)
    
    threshold = 6
    if tup_info[0] > 0 and tup_info[1] / tup_info[0] < threshold:
        list_warningcheck.append("WM:FEWCOMMENTS") 
    pst_res = parser.suite(tup_info[2])
    tup_code = pst_res.totuple()
    list_code = removeAllBrackets(tup_code)
    dic_rename = {"bisect":"bisect", "heapq":"heapq"}
    list_res = analyzeCodeInList(list_code, dic_varinfo, dic_rename, True)
    
    str_timecpx = "時間計算量：" + decodeSetValue(list_res[-1][1]) + ", "
    str_spacecpx = "領域計算量：" + decodeSetValue(list_res[-1][2]) + "\n" 
    str_warning = ""
    if len(list_warningcheck) > 0:
        str_warning = ""
    for key1 in list_warningcheck:
        str_warning += dic_warning[key1]
    
    return str_timecpx, str_spacecpx, str_warning


def abstractAnswerInfo(str_answer):
    cntline = str_answer.count("\n")
    str_answernocom = str_answer + "\n"
    str_reg = r"#.*\n"
    iter1 = re.finditer(str_reg, str_answernocom)
    cntstr = 0
    for ma1 in iter1:
        cntstr += len(ma1.group(0))
        str_answernocom = str_answernocom.replace(ma1.group(0), "\n", 1) 
    return cntline, cntstr, str_answernocom 


def removeBrackets(tup1):
    while(len(tup1) == 2 and type(tup1[1]) is not str):
        tup1 = tup1[1]
    return tup1
    
def removeAllBrackets(tup1):
    if len(tup1) == 2:
        tup1 = removeBrackets(tup1)
        list1 = list(tup1)
    if len(tup1) > 2:
        index1 = 1
        list1 = [tup1[0]]
        while(index1 < len(tup1)):
            list_res = removeAllBrackets(tup1[index1])
            list1.append(list_res)
            index1 += 1
    else:
        list1 = list(tup1)
    return list1

############################################################################################################################################

def analyzeCodeInList(list_code, dic_var, dic_rename, f_debug):
    if len(list_code) == 2:
        if type(list_code[1]) is list:
            return analyzeCodeInList(list_code[1], dic_var, f_debug)
        else:
            
            var = get_var(list_code, dic_var, [], dic_rename)
            
            list_res = [list_code[0], list_code[1], var]
            
            
            set_time_cpx  = {(1, )}
            
            set_space_cpx = {(1, )}
            
            
            return list_res
    elif len(list_code) >= 3:
        list_tmp = []
        list_time = []
        list_space = []
        
        list_tmp.append(list_code[0])
        
        for i in range(1,len(list_code)):
            if list_code[i][1] == "":
                continue
            
            
            
            list_res = analyzeCodeInList(list_code[i], dic_var, dic_rename, f_debug)
            
            list_tmp.append(list_res)
            
            adjustAfterwards(list_code, i, dic_var, dic_rename, f_debug)
            
            
        
        
        var = get_var(list_code, dic_var, list_tmp, dic_rename)
        
        
        
        
        
        list_tmp.append(var)
        
        adjustAfterwards2(list_tmp, dic_var, dic_rename, f_debug)
        
        return list_tmp
    else:
        return False


set_var = {"in", "if", "elif", "else", "for", "pass", "return", "not", "def", "is"}

def get_var(list_code, dic_var, list_tmp, dic_rename):
    if len(list_code) == 2:
        var = get_var2(list_code, dic_var, dic_rename)
        
    else:
        var = get_var3(list_code, dic_var, list_tmp, dic_rename)
    
    return var


    

def adjustAfterwards(list_code, index1, dic_var, dic_rename, f_debug):
    if list_code[1][0] == 1:
        
        
        if list_code[1][1] == "for":
            
            if index1 == 4 and list_code[4][0] == 1: 
                str_var = list_code[4][1] + "*" 
                if str_var in dic_var: 
                    dic_var[list_code[2][1]] = dic_var[str_var]
                    return
            
            if index1 == 4 and list_code[4][0] == 323 and list_code[4][1][1] == "enumerate": 
                str_var = list_code[4][2][2][1] + "*" 
                if str_var in dic_var: 
                    dic_var[list_code[2][3][1]] = dic_var[str_var]
                    return
            
    return

def adjustAfterwards2(list_tmp, dic_var, dic_rename, f_debug):
    if list_tmp[0] == 299:# or list_tmp[0] == 298: # for:299, while:298
        list_name = []
        list_check = [["append", "list"], ["add", "set"], ["enqueue", "FIFOClass"], ["push", "StackClass"]]
        #for/while本体
        if list_tmp[0] == 299:
            list1 = list_tmp[6]
        else:
            list1 = list_tmp[4]
        checkExp(list_check, list1, list_name, dic_var)
        for str_name in list_name:
            set_timecpx = set() #  
            
            set_spacecpx = list_tmp[4][-1][2] 
            if str_name in dic_var:
                
                set_spacecpx = setproduct(set_spacecpx, dic_var[str_name][2])
            dic_var[str_name] = ["list", set_timecpx, set_spacecpx]    
            
                
    return
    
set_method_time_n = {"count", "index", "reverse", "remove"}
set_method_time_nlogn = {"sort"}
set_method_bisect = {"bisect_left", "bisect_right", "bisect", "insort_left", "insort_right"}

def get_var2(list_code, dic_var, dic_rename):
    
    if list_code[0] == 1: 
        
        if list_code[1] in set_var:
            return ["sig", set(), set()]
        if list_code[1] in dic_var: 
            
            pass
        else: 
            dic_var[list_code[1]] = ["int", set(), set()]
        return dic_var[list_code[1]]
    
    dic1 = {
                2:"int", 
                7:"(", 8:")", 9:"[", 10:"]", 25:"{", 26:"}", 
                11:":", 12:",", 
                20:"<", 21:">", 22:"=", 23:".", 27:"==", 28:"!=", 29:"<=", 30:">=", 
                14:"+", 15:"-", 16:"*", 17:"/", 18:"|", 19:"&", 24:"%", 32:"^", 35:"**", 
                36:"+=", 37:"-=", 38:"*=", 39:"/=", 42:"|=", 41:"&=", 47:"//", 
           }
    str1 = ""
    if list_code[0] in dic1:
        str1 = "sig:" + dic1[list_code[0]]
        return [str1, set(), set()]
    
def get_var3(list1, dic_var, list_tmp, dic_rename):
    
    set_time_cpx = set()
    set_space_cpx = set()
    
    
    if list_tmp[0] == 274: 
        return ["mul", set(), set()]
    
    if list_tmp[0] == 325: 
        if len(list_tmp) >= 3 and list_tmp[2][0] == 337:
            set_time_cpx = setproduct(list_tmp[1][-1][1], list_tmp[2][-1][2])
            set_space_cpx = setproduct(list_tmp[1][-1][2], list_tmp[2][-1][2])
            return ["list", set_time_cpx, set_space_cpx]  
        return ["list", set(), set()] 
    
    if list_tmp[0] == 332: 
        if len(list_tmp) >= 3 and list_tmp[2][0] == 337:
            set_time_cpx = setproduct(list_tmp[1][-1][1], list_tmp[2][-1][2])
            set_space_cpx = setproduct(list_tmp[1][-1][2], list_tmp[2][-1][2])
            return ["set", set_time_cpx, set_space_cpx]  
        return ["set", set(), set()] 
    
    
    
    if list_tmp[0] == 324: 
        
        if list_tmp[1][1] == "(" or list_tmp[1][1] == "[":
            return ["list", list_tmp[2][-1][1], list_tmp[2][-1][2]] 
        
        if list_tmp[1][1] == "{":
            return ["set", list_tmp[2][-1][1], list_tmp[2][-1][2]] 
    
    
    if list_tmp[0] == 332:
        return ["set", set(), set()]
    
    if list_tmp[0] == 272:
        
        if list_tmp[2][0] == 36:
            str_name = list_tmp[1][1]
            indentnum = 0
            if list_tmp[1][0] == 323:
                # インデックスの深さを取得する
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp[1])
            str_name2 = list_tmp[3][1]
            set_timecpx = setunion(dic_var[str_name][1], dic_var[str_name2][2]) 
            set_spacecpx = setunion(dic_var[str_name][2], dic_var[str_name2][2])
            dic_var[str_name] = ["list", dic_var[str_name][1], set_spacecpx]
            return ["exp:method:list:+=", set_timecpx, set_spacecpx]
        
        type1 = list_tmp[-1][-1]
        
        
        for index1 in range(1, len(list_tmp)):
            list2 = list_tmp[index1]
            
            
            if list2[0] == 22:
                continue
            
            if list2[0] == 1:
                
                dic_var[list2[1]] = type1
                
                
                
                
            
            
            
            
            if list2[0] == 323:
                
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list2)
                
                if str_name in dic_var:
                    type1[1] = setunion(type1[1], dic_var[str_name][1])
                    type1[2] = setunion(type1[2], dic_var[str_name][2])
                    
                dic_var[str_name] = type1
                
                
                
                
    
    
    if list_tmp[0] == 320:
        
        f1 = False
        for index1 in range(1, len(list_tmp)):
            list2 = list_tmp[index1]
            
            if list2[0] == 16:
                continue
            
            
            if list2[-1][0] == "list":
                f1 = True
            
            set_time_cpx = setproduct(set_time_cpx, list2[-1][1])
            set_time_cpx = setproduct(set_time_cpx, list2[-1][2])
            set_space_cpx = setproduct(set_space_cpx, list2[-1][2])
        
        if f1 is True:
            return ["list", set_time_cpx, set_space_cpx]
        
    
    if list_tmp[0] == 319:
        f1 = False
        for index1 in range(1, len(list_tmp)):
            list2 = list_tmp[index1]
            
            if list2[0] == 14:
                continue
            
            
            if list2[-1][0] == "list":
                f1 = True
            
            set_time_cpx = setunion(set_time_cpx, list2[-1][1])
            set_space_cpx = setunion(set_space_cpx, list2[-1][2])
        if f1 is True:
            return ["list", set_time_cpx, set_space_cpx]
        
    
    
    if list_tmp[0] == 297:
        
        
        for index1 in range(1, len(list_tmp)):
            
            if list_tmp[index1][1] == "if" or list_tmp[index1][1] == "elif":
                
                set_time_cpx = setunion(set_time_cpx, list_tmp[index1+1][-1][1])
                set_space_cpx = setunion(set_space_cpx, list_tmp[index1+1][-1][2])
                
                set_time_cpx = setunion(set_time_cpx, list_tmp[index1+3][-1][1])
                set_space_cpx = setunion(set_space_cpx, list_tmp[index1+3][-1][2])
            
            
            if list_tmp[index1][1] == "else":
                set_time_cpx = setunion(set_time_cpx, list_tmp[index1+2][-1][1])
                set_space_cpx = setunion(set_space_cpx, list_tmp[index1+2][-1][2])
                
            
        
        
        
        
        
        
        
        
        
        return ["exp:if", set_time_cpx, set_space_cpx]
        
    
    if list_tmp[0] == 312:  
        if list_tmp[2][1] == "in":
            if list_tmp[3][-1][0] == "list":
                
                set_time_cpx = setunion(set_time_cpx, list_tmp[3][-1][2])
            if list_tmp[3][-1][0] == "dic" or list_tmp[3][-1][0] == "set":
                #
                set_time_cpx = setunion(set_time_cpx, set())
            
            set_space_cpx = setunion(set_space_cpx, list_tmp[1][-1][2])
            set_space_cpx = setunion(set_space_cpx, list_tmp[3][-1][2])
            
            return ["exp:in", set_time_cpx, set_space_cpx]
    
    if list_tmp[0] == 299:
        
        
        
        
        
        
        set_time_cpx = setproduct(list_tmp[4][-1][2], list_tmp[6][-1][1])

        
        
        set_space_cpx = setproduct(list_tmp[4][-1][2], list_tmp[6][-1][2])
        return ["exp:for", set_time_cpx, set_space_cpx]
    
    
    
    if list_tmp[0] == 298:
        
        
        
        
        
        
        set_time_cpx = setproduct(list_tmp[2][-1][2], list_tmp[4][-1][1])

        
        set_space_cpx = setunion(set_space_cpx, list_tmp[2][-1][2])
        set_space_cpx = setunion(set_space_cpx, list_tmp[4][-1][2])
        
        
        return ["exp:while", set_time_cpx, set_space_cpx]
    
    
    
    if list_tmp[0] == 285:
        if list_tmp[2][0] == 288: 
            dic_rename[list_tmp[2][1][1]] = list_tmp[2][3][1]
        return ["exp:import", set(), set()]
        
    
    if list_tmp[0] == 323:
        
        if list_tmp[1][1] == "FIFOClass":
            return ["FIFO", set(), set()]
        
        if list_tmp[1][1] == "StackClass":
            return ["Stack", set(), set()]
        
        if list_tmp[1][1] == "set":
            # 
            if list_tmp[2][2][0] == 323:
                
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp[2][2])
            elif list_tmp[2][2][0] == 1:
                str_name = list_tmp[2][2][1]
            else:
            	return ["set", set(), set()]
            if str_name in dic_var:
                set_timecpx = dic_var[str_name][2]
                set_spacecpx = dic_var[str_name][2]
            else: # 実際には起こらない気がする
                set_timecpx = set()
                set_spacecpx = set()
            return ["set", set_timecpx, set_spacecpx]
        # list
        if list_tmp[1][1] == "list":
            # 
            if list_tmp[2][2][0] == 323:
                
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp[2][2])
            elif list_tmp[2][2][0] == 1:
                str_name = list_tmp[2][2][1]
            else:
            	return ["list", set(), set()]
            if str_name in dic_var:
                set_timecpx = dic_var[str_name][2]
                set_spacecpx = dic_var[str_name][2]
            else: # 実際には起こらない気がする
                set_timecpx = set()
                set_spacecpx = set()
            return ["list", set_timecpx, set_spacecpx]
        
        
        if list_tmp[1][1] == "enumerate":
            # 
            if list_tmp[2][2][0] == 323:
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp[2][2])
            elif list_tmp[2][2][0] == 1:
                str_name = list_tmp[2][2][1]
            else:
                return ["list", set(), set()] 
            if str_name in dic_var:
                set_timecpx = dic_var[str_name][1]
                set_spacecpx = dic_var[str_name][2]
            else:  
                set_timecpx = set()
                set_spacecpx = set()
            return ["exp:func:enumerate", set_timecpx, set_spacecpx] 
        
        if list_tmp[1][1] == "range":
            return ["exp:func:range", list_tmp[2][2][-1][1], list_tmp[2][2][-1][2]]
        
        
        
        if list_tmp[1][1] == "sorted":
            set1 = logarithmize(list_tmp[2][2][-1][2])
            
            set_time_cpx = setproduct(set1, list_tmp[2][2][-1][2])
            return ["exp:func:sorted:O(nlogn)", set_time_cpx, list_tmp[2][2][-1][2]]
        
        
        
        
        
        
        indentnum = 0
        f_ref = False
        if list_tmp[2][1][0] == 9: 
            set_timecpx = list_tmp[2][2][-1][1]
            set_spacecpx = list_tmp[2][2][-1][2]
            
            str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp)
            if f_ref is True: 
                if str_name in dic_var:
                    set_timecpx = setunion(set_timecpx, dic_var[str_name][1])
                    set_spacecpx = setunion(set_timecpx, dic_var[str_name][2])
                    return ["exp:ref*", set_timecpx, set_spacecpx]
                return ["exp:ref", set_timecpx, set_spacecpx]
            
        
        
        
        
        if list_tmp[2+indentnum][1][0] == 23:
            if f_ref is False:
                str_name = list_tmp[1][1]
            
            if list_tmp[1][-1][0] == "list":
                
                if indentnum > 0:
                    
                    if str_name in dic_var:
                        list_var = dic_var[str_name]
                    else:
                    
                        dic_var[str_name] = ["int", set(), set()]
                else: 
                    list_var = list_tmp[1][-1]
                
                
                
                
                
                if list_tmp[2+indentnum][2][1] in set_method_time_n:
                    
                    return ["exp:method:list:O(n)", list_var[2], list_var[2]]
                
                
                if list_tmp[2+indentnum][2][1] in set_method_time_nlogn:
                    
                    set1 = logarithmize(list_var[2])
                    
                    set_time_cpx = setproduct(set1, list_var[2])
                    
                    return ["exp:method:list:O(nlogn)", set_time_cpx, list_var[2]]
                
                if list_tmp[2+indentnum][2][1] == "extend":
                    #print(list_tmp[3+indentnum][2][1]
                    str_name2 = list_tmp[3+indentnum][2][1]
                    set_timecpx = setunion(list_var[1], dic_var[str_name2][2]) 
                    set_spacecpx = setunion(list_var[2], dic_var[str_name2][2])
                    dic_var[str_name] = ["list", list_var[1], set_spacecpx]
                    return ["exp:method:list:extend", set_timecpx, set_spacecpx]
        
        
        if list_tmp[1][1] == dic_rename["bisect"]:
            if list_tmp[2][2][1] in set_method_bisect:
                set_timecpx = setunion(logarithmize(list_tmp[3][2][1][-1][2]), list_tmp[3][2][3][-1][1])
                set_spacecpx = setunion(list_tmp[3][2][1][-1][2], list_tmp[3][2][3][-1][2])
                return ["exp:bisect", set_timecpx, set_spacecpx]        
        
        
        
    
    if len(list_tmp) >= 3: 
        
        
        
        for index1 in range(1, len(list_tmp)):
            
            
            
            
            
            set_time_cpx = setunion(set_time_cpx, list_tmp[index1][-1][1])
            
            set_space_cpx = setunion(set_space_cpx, list_tmp[index1][-1][2])
            
            
        return ["context", set_time_cpx, set_space_cpx]    
    
    
    return list_tmp[-1][-1]
    


def getIndexDepth(dic_var, list_tmp):
    pcnt = 0
    f_ref = True
    for index2 in range(2, len(list_tmp)):
        if list_tmp[index2][0] == 326:
            if list_tmp[index2][1][0] == 9:
                pcnt += 1
            
            else:
                f_ref = False
    str_name = list_tmp[1][1] + pcnt * "*"
    
    return str_name, pcnt, f_ref

def setunion(set1, set2):
    set1 |= set2
    
    return clearupCpxSet(set1)

def setproduct(set1, set2):
    set_res = set1.union( set2)
    
    for str1 in set1:
        
        for str2 in set2:
            
            str_con1 = str1 + str2
            
            list1 = []
            logcnt = 0
            str_tmp = ""
            for str3 in str_con1:
                
                
                if str3 == "(":
                    str_tmp = str_tmp + "("
                    logcnt += 1
                    continue
                
                if str3 == ")":
                    str_tmp = str_tmp + ")"
                    logcnt -= 1
                    
                    if logcnt == 0:
                        list1.append(str_tmp)
                        str_tmp = ""
                    continue
                
                if logcnt > 0:
                    str_tmp = str_tmp + str3
                else:
                
                    list1.append(str3)
            list_res = sorted(list1)
            str_res = "".join(list_res)
            
            set_res.add(str_res)
    
    set_res = clearupCpxSet(set_res)
    return set_res


def logarithmize(set1):
    set2 = set()
    for str1 in set1:
        str1 = "(" + str1 + ")"
        set2.add(str1)
    return set2

def clearupCpxSet(set_value):
    
    list_check = [True] * len(set_value)
    for index1, str_value1 in enumerate(set_value):
        for index2, str_value2 in enumerate(set_value):
            if index1 == index2:
                continue
            if compareStrValue(str_value1, str_value2, []) is True:
                
                list_check[index2] = False
    
    set_res = set()
    for index1, str_value1 in enumerate(set_value):
        if list_check[index1] is True:
            set_res.add(str_value1)
    
    return set_res

def decodeSetValue(set_cpx):
    str_res = ""
    for str_cpx in set_cpx:
        if str_res != "":
            str_res += "+"
        str_res += str_cpx.replace("(", "log(")
    if str_res == "":
        return "O(1)"
    return "O(" + str_res + ")"

def getSetValueFromStrValue(str_value):
    ctr = collections.Counter(str_value)
    set_res = set()
    for key1, value1 in ctr.items():
        for cnt1 in range(1, 1 + value1):
            set_res.add(key1 * cnt1)
    return set_res

def getStrValueFromSetValue(set_value):
    list_check = [True] * len(set_value)
    for index1, str1 in enumerate(set_value):
        for index2, str2 in enumerate(set_value):
            if index1 == index2:
                continue
            if str1 in str2:
                list_check[index1] = False
    set_res = set()
    for index1, str1 in enumerate(set_value):
        if list_check[index1] is True:
            set_res.add(str1)
    str_res = "".join(sorted(set_res))
    return str_res

def separateStrValue(str_value):
    str_reg = "\((.*)\)"
    ma1 = re.search(str_reg, str_value)
    if ma1 is None:
        return ("", str_value)
    return (ma1.group(1), str_value[ma1.span()[1]:])

def compareStrValue(str_value1, str_value2, list_pvalue):
    tup_value1 = separateStrValue(str_value1)
    tup_value2 = separateStrValue(str_value2)
    
    f1 = getSetValueFromStrValue(tup_value1[1]) >= getSetValueFromStrValue(tup_value2[1])
    
    
    if f1 is False:
        list_pvalue.append(tup_value1[1])
    f2 = False
    for index1, value1 in enumerate(list_pvalue):
        set_value1 = getSetValueFromStrValue(value1)
        set_tup_value2 = getSetValueFromStrValue(tup_value2[0])
        if set_value1 >= set_tup_value2:
            f2 = True
            set3 = set_tup_value2 - set_value1
            list_pvalue[index1] = getStrValueFromSetValue(set3)
            break
    
    if f2 is False:
        
        if tup_value1[0] != "":
            
            if tup_value2[0] != "": 
                f2 = compareStrValue(tup_value1[0], tup_value2[0], list_pvalue)
            
            else:
                f2 = True
        
        elif tup_value2[0] != "":
            
            if tup_value2[0] != "": 
                f2 = compareStrValue(tup_value1[0], tup_value2[0], list_pvalue)
            
            else:
                return False 
        
        else:
            f2 = True
    return f1 & f2 
    


def checkExp(list_name, list_tmp, list_varname, dic_var):
    if len(list_tmp) == 3:
        if type(list_tmp[1]) is list:
            return checkExp(list_name, list_tmp[1], list_varname, dic_var)
        else:
            for list1 in list_name:
                #print(list_tmp[1], list1[0])
                if list_tmp[1] == list1[0]:
                    return list1, False
            return False, False
    elif len(list_tmp) >= 4:
        
        for i in range(1, len(list_tmp)):
            
            if list_tmp[i][1] == "":
                continue
            
            f_list, f_ok = checkExp(list_name, list_tmp[i], list_varname, dic_var)
            
            if type(f_list) is list:
                
                return False, f_list
            if type(f_ok) is list:
                
                str_name, indentnum, f_ref = getIndexDepth(dic_var, list_tmp)
                
                
                if str_name in dic_var and dic_var[str_name][0] == f_ok[1]:
                    list_varname.append(str_name) 
                return False, False
        return False, False
    return False, False



