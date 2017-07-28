from SPARQLWrapper import SPARQLWrapper, JSON, POST


class ontology_sparql:
    """查询展示知识图谱和学习方案需要的本体数据"""

    def __init__(self, dataset="math", userid=None):

        self.sqlstr_PREFIX = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX math:<http://www.semanticweb.org/chengboya/ontologies/%s#>
        """ % dataset

        self.sparql = SPARQLWrapper("http://localhost:3030/%s/sparql" % dataset,
                                    updateEndpoint="http://localhost:3030/%s/update" % dataset)

        if userid is None:
            self.sqlstr_FROM = ""
            self.sqlstr_WITH = ""
            self.sqlstr_WITH = ""
        else:
            self.userid = userid
            # 指定了数据处理的范围，即sparql查哪一张图graph
            self.sqlstr_FROM = "FROM <http://www.semanticweb.org/chengboya/ontologies/users/%s>" % userid
            self.sqlstr_WITH = "WITH <http://www.semanticweb.org/chengboya/ontologies/users/%s>" % userid
            self.sqlstr_GRAPH = "GRAPH <http://www.semanticweb.org/chengboya/ontologies/users/%s>" % userid
            # 以上三种语句作用都是将SPARQL作用限制在具体的图（GRAPH）中，在用户未登录时，使用默认的graph，也即领域知识本体；
            # 当用户登录后，所以本体操作在在用户本体中进行——使用具体的图

        self.myid = 0
        self.depth = 0


    # 查询知识图谱所需数据
    def weighted(self, nodes, knowledge_name, depth=0):

        nodes.setdefault("key", knowledge_name)
        # nodes.setdefault("depth", depth)

        # 查询信息
        demand = float(self.search_demand(knowledge_name))  # 查询信息1——大纲要求难度
        if demand >= 1.0:
            nodes.setdefault("demand", "掌握")
        elif demand >= 0.6:
            nodes.setdefault("demand", "理解")
        else:
            nodes.setdefault("demand", "了解")

        description = self.search_description(knowledge_name)  # 查询信息1——大纲要求难度
        nodes.setdefault("description", description)

        # weight = self.search_weight(knowledge_name)  # 查询信息2——大纲要求难度
        # nodes.setdefault("weight", weight)

        # 判断是否是傀儡
        #if self.search_equi(knowledge_name) == "yes":
        #    temp = self.search_equivalent_knowledge(knowledge_name)
        #else:
        #    temp = knowledge_name

        videos = self.search_resource(knowledge_name)  # 查询信息3——学习资源示例 要想办法跟nodestr中的href对上
        nodes.setdefault("videos", videos)

        results = self.search_subClass(knowledge_name)  # 查询给定知识点的子知识点
        if results:
            nodes.setdefault("values", [])  # 这里不能是字典 要是列表
            i = 0
            depth += 1
            for result in results:  # 迭代
                d = {}
                nodes["values"].append(d)
                self.weighted(nodes["values"][i], result, depth=depth)
                i += 1
        else:
            weight = self.search_weight(knowledge_name)  # 查询信息2——大纲要求难度
            nodes.setdefault("weight", weight)
            # nodes.setdefault("depth", depth)
        return nodes


    def search_resource_with_difficulty_re(self, knowledge_name, difficulty_index):
        difficulty = [1.0, 0.6, 0.2]
        videos = self.search_resource_with_difficulty(knowledge_name, difficulty[difficulty_index])
        if videos:
            return videos
        else:
            difficulty_index -= 1#只考虑提高的难度 没有 降低难度
            if difficulty_index < 0:
                return videos
            else:
                return self.search_resource_with_difficulty_re(knowledge_name, difficulty_index)

    # 查询用户知识体系所需数据
    def weighted_user(self, nodes, knowledge_name):
        math_graph = ontology_sparql()
        nodes.setdefault("key", knowledge_name)

        # 查询信息
        demand = self.search_demand(knowledge_name)  # 查询信息1——大纲要求难度
        nodes.setdefault("demand", demand)

        description = self.search_description(knowledge_name)  # 查询信息1——大纲要求难度
        nodes.setdefault("description", description)

        achieve = float(self.search_achieve(knowledge_name))  # 查询信息3——用户掌握程度
        #nodes.setdefault("achieve", achieve)

        # difficulty = [1.0, 0.6, 0.2]
        if achieve < 0.2:  # 依据用户掌握程度选择合适的视频资源
            difficulty_index = 2
            nodes.setdefault("achieve", "差")
        elif achieve < 0.6:
            difficulty_index = 1
            nodes.setdefault("achieve", "一般")
        elif achieve < 1.0:
            difficulty_index = 0
            nodes.setdefault("achieve", "良")
        else:
            difficulty_index = 0
            nodes.setdefault("achieve", "优秀")

        # 判断是否是傀儡
        #if self.search_equi(knowledge_name) == "yes":
        #    temp = self.search_equivalent_knowledge(knowledge_name)
        #else:
        #    temp = knowledge_name

        videos = math_graph.search_resource_with_difficulty_re(knowledge_name, difficulty_index)
        nodes.setdefault("videos", videos)

        results = self.search_subClass(knowledge_name)  # 查询给定知识点的子知识点
        if results:
            nodes.setdefault("values", [])  # 这里不能是字典 要是列表
            i = 0
            for result in results:  # 迭代
                d = {}
                nodes["values"].append(d)
                self.weighted_user(nodes["values"][i], result)
                i += 1
        else:
            weight = self.search_weight(knowledge_name)  # 查询信息2——大纲要求难度
            nodes.setdefault("weight", weight)
            nodes.setdefault("achievee", achieve)
        return nodes


    # 提取完整的学习方案 即 def user_weighted_tree
    def allpath(self, nodes, knowledge_name, depth=0):
        nodes.setdefault("key", knowledge_name)

        # 查询信息
        demand = self.search_demand(knowledge_name)  # 查询信息1——大纲要求难度
        nodes.setdefault("demand", demand)

        weight = self.search_weight(knowledge_name)  # 查询信息2——大纲要求难度
        nodes.setdefault("weight", weight)

        videos = self.search_resource(knowledge_name)  # 查询信息3——学习资源示例 要想办法跟nodestr中的href对上
        if videos:
            nodes.setdefault("href", "/category/1")

        results = self.search_subClass(knowledge_name)  # 查询给定知识点的子知识点
        if results:
            nodes.setdefault("children", [])  # 这里不能是字典 要是列表
            i = 0
            depth += 1
        for result in results:  # 迭代
            d = {}
            nodes["children"].append(d)
            self.allpath(nodes["children"][i], result, depth=depth)
            i += 1
        return nodes

    # 查询知识图谱所需数据 提供给前端知识点设计
    def all_knowledge(self, nodes, knowledge_name, father=None):
        nodes.setdefault("name", knowledge_name)

        if father is not None:
            nodes.setdefault("father", father)
        # 查询信息
        demand = float(self.search_demand(knowledge_name))  # 查询信息1——大纲要求难度
        if demand >= 1.0:
            nodes.setdefault("demand", "掌握（100%）")
        elif demand >= 0.6:
            nodes.setdefault("demand", "理解（60%）")
        else:
            nodes.setdefault("demand", "了解（20%）")
        results = self.search_subClass(knowledge_name)  # 查询给定知识点的子知识点
        if results:
            nodes.setdefault("children", [])  # 这里不能是字典 要是列表
            i = 0
        for result in results:  # 迭代
            d = {}
            nodes["children"].append(d)
            self.all_knowledge(nodes["children"][i], result, father=knowledge_name)
            i += 1
        return nodes

    # 查询知识图谱所需数据 提供给前端知识点设计
    def all_knowledge_except_dummy(self, nodes, knowledge_name, father=None):
        nodes.setdefault("name", knowledge_name)
        if father is not None:
            nodes.setdefault("father", father)
        # 查询信息
        demand = self.search_demand(knowledge_name)  # 查询信息1——大纲要求难度
        nodes.setdefault("demand", demand)

        results = self.search_subClass(knowledge_name)  # 查询给定知识点的子知识点
        if results:
            nodes.setdefault("children", [])  # 这里不能是字典 要是列表
            i = 0
        for result in results:  # 迭代
            # 判断是否是傀儡
            if self.search_equi(result) == "yes":
                pass
            else:
                d = {}
                nodes["children"].append(d)
                self.all_knowledge_except_dummy(nodes["children"][i], result, father=knowledge_name)
                i += 1
        return nodes

    # 依据用户正在学习的知识点，确定部分学习方案的起点——沿着学习次序向上找
    def get_learning_start(self, knowledge):
        ans = ""
        # step1 检查用户对该知识点的掌握情况
        achieve = float(self.search_achieve(knowledge))
        # step2 分向
        # 掌握程度在0.6，就不去找先修知识点的麻烦了
        if (achieve >= 0.6) or (knowledge == "math"):
            ans = knowledge
            #return knowledge
        # 此时知识点目前掌握的不好，要去看看其先修怎么样，来决定起点放在这两个点哪个
        else:
            # step3找上一个知识点
            Up = self.get_Up(knowledge)
            # 取上一知识点的掌握程度
            Up_achieve = float(self.search_achieve(Up))
            # step4 根据先后两个知识点的掌握程度来分向
            if (1.0 > Up_achieve >= 0.6 > achieve) or (Up == "math"):
                ans = Up
                #return Up
            elif Up_achieve >= 1.0:
                ans = knowledge
                #return knowledge
            else:
                # 上一知识点也不过关，需要再向上找原因
                ans = self.get_learning_start(Up)
        return ans

    # 根据学习起点，形成学习路径——沿着学习次序向下找
    def get_part_path(self, knowledge, now, to_study_set, father=None):
        d = {}
        d.setdefault("name", knowledge)
        d.setdefault("father", father)
        achieve = float(self.search_achieve(knowledge))
        if achieve >= 1:
            d.setdefault("need", False)  # 不需要推荐资源
            d.setdefault("achieve", achieve)  # 但还是要把achieve放进去 前端显示圆圈时使用
            to_study_set.append(d)
            Next = self.get_Next(knowledge)
            # Next = "数列极限的定义"
        elif not self.search_subClass(knowledge):
            d.setdefault("need", True)
            d.setdefault("achieve", achieve)
            to_study_set.append(d)
            Next = self.get_Next(knowledge)
            # Next = "数列极限的定义"
        else:
            d.setdefault("need", True)
            d.setdefault("achieve", achieve)
            to_study_set.append(d)
            Next = self.search_beginning_with_knowledge(knowledge)
            # Next = "数列极限的定义"
        if knowledge == now and Next:
            achieve = float(self.search_achieve(Next))
            if achieve < 1:
                d = {}
                d.setdefault("name", Next)
                d.setdefault("father", knowledge)
                d.setdefault("need", True)
                d.setdefault("achieve", achieve)
                to_study_set.append(d)
                return to_study_set
            else:  # 如何学习起点的下一知识点用户已经掌握了，那么再找一个,这时候停止条件已经过了，所以要更新停止条件
                self.get_part_path(Next, Next, to_study_set, father=knowledge)
        elif not Next:  # 没有下一个了 这是学习的尽头
            return to_study_set
        else:
            self.get_part_path(Next, now, to_study_set, father=knowledge)

    # 根据学习路径，依次筛选合适的视频资源
    def filling_path(self, nodes, knowledge, x, y):
        d = {}

        achieve = knowledge["achieve"]
        # 不同的掌握程度用不同颜色的circle表示  并根据掌握程度，选定合适的视频难度
        if achieve < 0.2:
            d.setdefault("index", 3)
            d.setdefault("name", knowledge["name"] + "  (差)")
            difficulty_index = 2
        elif achieve < 0.6:
            d.setdefault("index", 1)
            d.setdefault("name", knowledge["name"] + "  (一般)")
            difficulty_index = 1
        elif achieve < 1.0:
            d.setdefault("index", 4)
            d.setdefault("name", knowledge["name"] + "  (良)")
            difficulty_index = 0
        else:
            d.setdefault("index", 2)
            d.setdefault("name", knowledge["name"] + "  (优秀)")
            difficulty_index = 0

        if knowledge["need"]:
            d.setdefault("need", True)
            # 依据视频难度，选择质量好的视频资源
            videos = self.search_resource_with_difficulty_re(knowledge["name"], difficulty_index)  # 得出的结果是字典
            d.setdefault("videos", videos)
        else:
            d.setdefault("need", False)  # 不需要推荐资源了

        d.setdefault("x", x)
        d.setdefault("y", y)
        nodes.append(d)
        return nodes

    # 为<确定部分学习方案的起点>
    def get_Up(self, knowledge):
        # 先看看没有有先修知识点
        Up = self.search_ak_knowledge(knowledge)
        if not Up:  # 没有先修知识点,找父知识点
            father = self.search_father_knowledge(knowledge)
            if father == "math":
                return "math"
            else:
                father_ak = self.search_ak_knowledge(father)
                if father_ak:
                    #    Next = self.get_Next(father_ak)
                    return father_ak
                else:  # 父节点没有先修知识点时，说明是所在层的学习起点
                    self.get_Up(father)
        else:
            return Up

    # 为<形成学习路径>
    def get_Next(self, knowledge):
        # 先看看没有有后续知识点
        Up = self.search_sk_knowledge(knowledge)
        if not Up:  # 没有后续知识点,找父知识点
            father = self.search_father_knowledge(knowledge)
            if father == "math":
                ans = False  # 没有下一个知识点，此时的知识点是学习的尽头
            else:
                father_sk = self.search_sk_knowledge(father)
                if father_sk:
                    ans = father_sk
                else:
                    # 父节点没有先修知识点时，说明是所在层的学习起点
                    ans = self.get_Next(father)
        else:
            ans = Up
        return ans
        # default graph 、named graph 查询

    # math和user的default graph 均可以
    def search_subClass(self, knowledge_name):

        sqlstr_SELECT = """
        SELECT ?subclass
        """
        sqlstr_WHERE = """
        WHERE {
            ?subclass rdfs:subClassOf math:%s.
        }
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        subClass = []
        for result in results["results"]["bindings"]:
            subClass.append(result["subclass"]["value"].split("#")[-1])
        return subClass

    # math和user的default graph 均可以  找知识点的父知识点
    def search_father_knowledge(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?father
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s rdfs:subClassOf ?father.
        }
        """ % knowledge  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if result["results"]["bindings"]:
            return result["results"]["bindings"][0]["father"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math和user的default graph 均可以  找知识点的begin 没用
    def search_begin(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?begin
        """
        sqlstr_WHERE = """
        WHERE {
            ?begin math:beginningwith math:%s.
        }
        """ % knowledge  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if result["results"]["bindings"]:
            return result["results"]["bindings"][0]["begin"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math和user的default graph 均可以  找知识点的父知识点
    def search_equivalent_knowledge(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?equivalent
        """
        sqlstr_WHERE = """
        WHERE {
            OPTIONAL{math:%s owl:equivalentClass ?equivalent}
            OPTIONAL{?equivalent  owl:equivalentClass math:%s}
        }
        """ % (knowledge, knowledge)  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        ans = []
        if results["results"]["bindings"][0]:
            for result in results["results"]["bindings"]:
                ans.append(result["equivalent"]["value"].split("#")[-1])
            return ans
        else:
            return False


    # math和user的default graph 均可以  找知识点的父知识点
    def search_equi(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?equi
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:equi ?equi.
        }
        """ % knowledge  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["equi"]["value"]
        else:
            return False

    # math和user的default graph 均可以 demand不允许update
    def search_demand(self, knowledge_name) -> object:
        sqlstr_SELECT = """
        SELECT ?demand
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:demand_is ?demand.
        }
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["demand"]["value"]
        else:
            return "Undefined"

    # math和user的default graph 均可以  demand不允许update
    def search_description(self, knowledge_name) -> object:
        sqlstr_SELECT = """
        SELECT ?description
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:description ?description.
        }
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["description"]["value"]
        else:
            return "No description"

    # math和user的default graph 均可以 使用FROM weight不允许update
    def search_weight(self, knowledge_name):
        sqlstr_SELECT = """
        SELECT ?weight
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:weight_is ?weight.
        }
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        #         # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["weight"]["value"]
        else:
            return 0
            #return 0.6  # 权益之计 主要想看看weighted tree展示哪里有突破口

    # math的default graph  不考虑视频难度，筛选出质量TOP10视频资源
    def search_resource(self, knowledge_name):
        sqlstr_SELECT = """
        SELECT ?resource ?quality_value
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:resource ?resource.
            ?resource math:quality_is ?quality_value
        }
        ORDER BY DESC(?quality_value)
        LIMIT 10
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        video = ""
        i = 0
        for result in results["results"]["bindings"]:
            if i > 0:
                video = video + "," + result["resource"]["value"].split("#")[-1]
            else:
                video = result["resource"]["value"].split("#")[-1]
            i +=1
        return video

        #return "id_0002" + "," + "id_0004"

    # math的default graph 考虑视频难度，筛选出与用户掌握程度匹配的质量TOP10视频资源，用于学习方案的制定
    def search_resource_with_difficulty(self, knowledge_name, difficulty):
        sqlstr_SELECT = """
        SELECT ?resource ?quality_value
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:resource ?resource.
            ?resource math:difficulty_is ?difficulty_value
            FILTER( ?difficulty_value = %f)
            ?resource math:quality_is ?quality_value
        }
        ORDER BY DESC(?quality_value)
        """ % (knowledge_name, difficulty)  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + self.sqlstr_FROM + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        video = ""
        i = 0
        for result in results["results"]["bindings"]:
            if i > 0:
                video = video + "," + result["resource"]["value"].split("#")[-1]
            else:
                video = result["resource"]["value"].split("#")[-1]
            i +=1
        return video

    # math的default graph 找视频对应的知识点
    def search_knowledge(self, video_id):
        sqlstr_SELECT = """
        SELECT ?knowledge
        """
        sqlstr_WHERE = """
        WHERE {
            ?knowledge math:resource math:%s.
        }
        """ % video_id

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["knowledge"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math和user的default graph 均可以 找知识点的先修知识点
    def search_ak_knowledge(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?ak_knowledge
        """
        sqlstr_WHERE = """
        WHERE {
            ?ak_knowledge math:sk_is math:%s.
        }
        """ % knowledge

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["ak_knowledge"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math和user的default graph 均可以  没有用FROM 找知识点的后续知识点
    def search_sk_knowledge(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?sk_knowledge
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:sk_is ?sk_knowledge.
        }
        """ % knowledge

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["sk_knowledge"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # default graph 、named graph 均可以。没有用FROM 找知识点的子知识点的学习起点
    def search_beginning_with_knowledge(self, knowledge):
        sqlstr_SELECT = """
        SELECT ?start
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:beginningwith ?start.
        }
        """ % knowledge

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["start"]["value"].split("#")[-1]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math 查询某一视频的质量
    def search_video_quality(self, video_id):
        sqlstr_SELECT = """
        SELECT ?quality
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:quality_is ?quality.
        }
        """ % video_id  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["quality"]["value"]
            # ["bindings"]的值是列表，列表的元素是字典，所以中间要添个[0]
            # 其实只应该有一个的，但是我在protege中不知道怎么限定住
        else:
            return False

    # math 查询某一视频的难度 （默认一个视频对应一个知识点，但一个知识点可以对应多个视频资源实例）
    def search_video_difficulty(self, video_id):
        sqlstr_SELECT = """
        SELECT ?difficulty
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:difficulty_is ?difficulty.
        }
        """ % video_id  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["difficulty"]["value"]
        else:
            return False

    # user的named graph 查询当前用户对某一知识点的掌握程度 使用FROM
    def search_achieve(self, knowledge_name):
        sqlstr_SELECT = """
        SELECT ?achieve
        """
        sqlstr_WHERE = """
        WHERE {
            math:%s math:achieve_is ?achieve.
        }
        """ % knowledge_name  # 这个术语称为字符串格式化，记着了

        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + self.sqlstr_FROM + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["achieve"]["value"]
        else:
            # return False
            return 0

    # math的default graph 创建资源本体实例，一个实例对应一个知识点
    def create_video_instance(self, knowledge_name, video_id):
        sqlstr_INSERT = """
        INSERT DATA{
            math:%s math:resource math:%s.
        }
        """ % (knowledge_name, video_id)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    # math的default graph 为资源本体实例添加难度属性值，添加意味着加之前该属性还没有限定到该实例上
    def add_video_difficulty(self, video_id, video_difficulty):
        sqlstr_INSERT = """
        INSERT DATA{
            math:%s math:difficulty_is %f.
        }
        """ % (video_id, video_difficulty)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    # math的default graph 为资源本体实例更新质量属性值，更新意味着之前该属性已限定到该实例上，所以更新之前要先删除该属性，后添加
    def update_video_difficulty(self, video_id, video_difficulty):
        sqlstr_INSERT = """
        DELETE { math:%s math:difficulty_is ?old }
        INSERT { math:%s math:difficulty_is %f }
        WHERE
          { math:%s math:difficulty_is ?old.
          }
        """ % (video_id, video_id, video_difficulty, video_id)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        # self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    #  math的default graph 为资源本体实例添加质量属性值
    def add_video_quality(self, video_id, video_quality):
        sqlstr_INSERT = """
        INSERT DATA{
            math:%s math:quality_is %f.
        }
        """ % (video_id, video_quality)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    #  math的default graph 为资源本体实例更新质量属性值
    def update_video_quality(self, video_id, video_quality):
        sqlstr_INSERT = """
        DELETE { math:%s math:quality_is ?old }
        INSERT { math:%s math:quality_is %f }
        WHERE
          { math:%s math:quality_is ?old.
          }
        """ % (video_id, video_id, video_quality, video_id)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        # self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False


    # user的named graph 创建和更新(用户本体创建和更新)
    # 用户注册成功后通过修改领域知识本体来创建用户本体实例，使用Graph Management语法中的ADD或COPY
    def create_user_instance(self):

        sqlstr_COPY = """
        COPY DEFAULT TO %s
        """ % self.sqlstr_GRAPH  # 这个GRAPH是目前所在dataset中的graph

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_COPY)  # 这一步编辑查询语句
        # self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    # 为用户本体实例添加掌握程度属性值
    def add_user_achieve(self, knowledge_name, achieve):
        # time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        sqlstr_INSERT = """
        INSERT DATA{
            %s
            {
            math:%s math:achieve_is  %f.
            }
        }
        """ % (self.sqlstr_GRAPH, knowledge_name, achieve)  # 将当前知识点的掌握程度属性填上属性值

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    # 为用户本体实例更新掌握程度属性值
    def update_user_achieve(self, knowledge_name, achieve):
        sqlstr_INSERT = """
        DELETE { math:%s math:achieve_is ?old }
        INSERT { math:%s math:achieve_is %f }
        WHERE
          { math:%s math:achieve_is ?old.
          }
        """ % (knowledge_name, knowledge_name, achieve, knowledge_name)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + self.sqlstr_WITH + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    # 为了更新用户本体，先删除所有的achieve属性值
    def delete_all_achieve(self):
        sqlstr_DELETE = """
        DELETE {
            ?know math:achieve_is  ?f.
        }
        WHERE{
            ?know math:achieve_is  ?f.
        }
        """

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + self.sqlstr_WITH + sqlstr_DELETE)
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    # 为用户本体的掌握程度添加同一属性值
    def add_same_achieve(self, achieve):  # 当value为0时，也即初始化用户本体
        sqlstr_INSERT = """
        INSERT {
            %s
            {
                ?know math:achieve_is  %f.
            }
        }
        WHERE{
            ?know rdfs:subClassOf ?l.
        }
        """ % (self.sqlstr_GRAPH, achieve)  # where语句是用来筛选出知识点，而没有知识点对应实例，也没有属性，
        # 没有where的筛选，本体中所有的概念、属性和实例都会有这个。若math:achieve_is限定了定义域，则可能不需要where
        # 通过插入的方式可以直接为本体添加新的概念、属性；间接添加实例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False


"""
ISOTIMEFORMAT="%Y-%m-%d %X"
print(time.localtime())
t = time.localtime()
time1 = time.strftime(ISOTIMEFORMAT, time.localtime())#结果是str
print(time1)

ISOTIMEFORMAT="%Y-%m-%d %X"
time1 = time.time()#flaot类型 以秒为单位
time1 = time1 / 3600
re = int(time1)
print(re)

ISOTIMEFORMAT="%Y-%m-%d %X"
print("1")
time1 = time.time()
print(time1)
#print("2")
#print(time.localtime())
print("3")
time1 = time.strftime(ISOTIMEFORMAT, time.localtime())#结果是str
time.sleep(1)
time2 = time.strftime(ISOTIMEFORMAT, time.localtime())
interval = time2 - time1
print(interval)
#print("4")
#print(time.strptime(s, ISOTIMEFORMAT))#from:2006-04-12 16:46:40 to:23123123
#s = 2356151
#print("5")
#print(time.strftime(ISOTIMEFORMAT, time.localtime(float(s))))#from: 23123123 to: 2006-04-12 16:46:40
"""

"""
graph = ontology_sparql("math")
result = graph.create_video_instance("函数", "id2222").decode("utf-8")
result = graph.search_video_quality("id2222")#查询视频是否已填入视频质量属性
if result:#已存在则更新
    result = graph.update_video_quality("id2222", 5.2).decode("utf-8")
    if "Success" in result:  # 从网络读取数据是字节流，使用decode(“utf-8”)来转成字符
        print("success!")
    else:
        print("Failed in update video quality!")
else:#不存在则添加
    result = graph.add_video_quality("id2222", 5.2).decode("utf-8")
    if "Success" in result:  # 从网络读取数据是字节流，使用decode(“utf-8”)来转成字符
        print("success!")
    else:
        print("Failed in add video quality!")
"""
