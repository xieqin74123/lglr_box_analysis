import pandas as pd
import numpy as np

class Box_data:
    def __init__(self, box_data:np.ndarray) -> None:
        # 日期
        self.date = ""
        if box_data[1] != 0:
            self.date = box_data[1]
        # 箱子类型
        box_name = box_data[2]
        self.box_type = 10
        if box_name == "电子币":
            self.box_type = 3
        elif box_name == "15保底" or box_name == "赛季奖励":
            self.box_type = 100
        # 技术值蓝点
        self.frigate_tech = int(float(box_data[3]))
        self.destroyer_tech = int(float(box_data[4]))
        self.cruiser_tech = int(float(box_data[5]))
        self.battlecruiser_tech = int(float(box_data[6]))
        self.auxiliary_tech = int(float(box_data[7]))
        self.carrier_tech = int(float(box_data[8]))
        self.covette_tech = int(float(box_data[9]))
        self.fighter_tech = int(float(box_data[10]))
        # 舰船
        self.blueprint = False
        self.blueprint_name = None
        if box_data[11] != "0":
            self.blueprint = True
            self.blueprint_name = box_data[12]

class Series:
    def __init__(self, name:str) -> None:
        self.data = np.empty(0, dtype=Box_data)
        self.name = name
    
    def append (self, add_data:Box_data) -> None:
        self.data = np.append(self.data, add_data)
    
    def print_summary (self):
        tier_title = np.array(["frigate", "destroyer", "cruiser", "battlecrusier", "auxiliary", "carrier", "covette", "fighter"])
        print("series name:", self.name)
        print("time period:", self.date_period[0], "-", self.date_period[-1], "("+ str(np.unique(self.date_period).shape[0]) + " days)")
        print()
        print("box number:", self.count_box)
        print("\t3% box number:", str(self.count_box_3), "(" + str(round(self.count_box_3 / self.count_box, 2)) + ")")
        print("\t10% box number:", str(self.count_box_10), "(" + str(round(self.count_box_10 / self.count_box, 2)) + ")")
        print("\t100% box number:", str(self.count_box_100), "(" + str(round(self.count_box_100 / self.count_box, 2)) + ")")
        print()
        print("tech point number:")
        temp = np.array((tier_title, self.count_tech), dtype=str)
        temp_df = pd.DataFrame(temp)
        print(temp_df.to_string(index=False, header=False))
        print()
        print("blueprint number:", self.count_ship)
        temp = np.array((tier_title, 
                         self.count_ship_tier_by_box_type(3), 
                         self.count_ship_tier_by_box_type(10), 
                         self.count_ship_tier_by_box_type(100),
                         self.count_ship_tier),
                         dtype=str)
        temp_title = np.array(["tier", "3% box", "10% box", "100% box", "total"], dtype=str)
        temp = np.concatenate((temp_title[:, np.newaxis], temp), dtype=str, axis=1)
        temp_df = pd.DataFrame(temp)
        print(temp_df.to_string(index=False, header=False))

    @property
    def date_period (self) -> np.ndarray:
        date = np.empty(0, dtype=str)
        for box in self.data:
            if box.date != "" and box.date != "0":
                date = np.append(date, box.date)
        
        return np.asarray(date, dtype=str)

    @property
    def count_box (self) -> int:
        return len(self.data)
    
    def count_box_type (self, type:int) -> int:
        count = 0
        for data in self.data:
            if data.box_type == type:
                count += 1
        return count
    
    @property
    def count_box_10 (self) -> int:
        return self.count_box_type(10)
    
    @property
    def count_box_100 (self) -> int:
        return self.count_box_type(100)
    
    @property
    def count_box_3 (self) -> int:
        return self.count_box_type(3)

    @property
    def count_tech (self) -> np.ndarray:
        # in order [frigate, destroyer, cruiser, battlecrusier, auxiliary, carrier, covette, fighter]
        count = np.zeros(8, dtype=int)
        for box in self.data:
            count[0] += box.frigate_tech
            count[1] += box.destroyer_tech
            count[2] += box.cruiser_tech
            count[3] += box.battlecruiser_tech
            count[4] += box.auxiliary_tech
            count[5] += box.carrier_tech
            count[6] += box.covette_tech
            count[7] += box.fighter_tech
        return count
    
    @property
    def count_ship (self) -> int:
        count = 0
        for box in self.data:
            if box.blueprint is True:
                count += 1
        return count
    
    @property
    def count_ship_tier (self) -> np.ndarray:
        count = np.zeros(8, dtype=int)
        for box in self.data:
            if box.blueprint is True:
                count[get_ship_tier(box.blueprint_name)] += 1
        return count
    
    def count_ship_tier_by_box_type (self, box_type:int) -> np.ndarray:
        data = Series("temp")
        for box in self.data:
            if box.box_type == box_type:
                data.append(box)
        return data.count_ship_tier
    
    def occurace_of_ship (self, tier:int=None) -> np.ndarray:
        ship = np.empty(0, dtype=str)
        for box in self.data:
            if box.blueprint is True:
                if tier is None:
                    ship = np.append(ship, correct_ship_name(box.blueprint_name))
                elif get_ship_tier(box.blueprint_name) == tier:
                    ship = np.append(ship, correct_ship_name(box.blueprint_name))
        
        uniq_ship, occu = np.unique(ship, return_counts=True)
        return np.concatenate(([uniq_ship], [occu]), axis=0)
    
    def del_data_by_type (self, type:int) -> None:
        for box in self.data:
            if box.box_type == type:
                self.data = np.delete(self.data, np.where(self.data == box))
    
class Container:
    def __init__ (self) -> None:
        self.data = np.empty(0, dtype=Series)

    def append (self, add_data: Series) -> None:
        self.data = np.append(self.data, add_data)

    def get_data_in_series (self) -> Series:
        data = Series("All")
        for series in self.data:
            for box in series.data:
                data.append(box)
        return data

    def print_all (self) -> None:
        self.get_data_in_series().print_summary()
    
    def print_by_series (self, series:int) -> None:
        self.data[series].print_summary()

    def print_all_by_series (self) -> None:
        for series in self.data:
            series.print_summary()

def read_excel (file:str) -> Container:
    exf = pd.ExcelFile(file)
    con = Container()

    for sheet in exf.sheet_names:
        data = exf.parse(sheet).to_numpy(dtype=str)
        s = Series(sheet)
        for row in data:
            row[row=="nan"] = "0"
            box = Box_data(row)
            s.append(box)
        con.append(s)
    return con

def correct_ship_name (name:str) -> str:
    pricise_name_map = {
        ("诺玛M470", "诺玛470", "诺玛", "诺马"): "诺玛M470",
        ("刺水母", "水母"): "刺水母",
        ("澄海"): "澄海",
        ("红宝石"): "红宝石",
        ("雷里亚特", "雷利亚特"): "雷里亚特",
        ("卡利莱恩", "卡里莱恩"): "卡利莱恩",
        ("云海"): "云海",
        ("静海"): "静海",
        ("FG300", "fg300", "富贵"): "FG300",
        
        ("卫士"): "卫士",
        ("苔原"): "苔原",
        ("亚达伯拉"): "亚达伯拉",
        ("斗牛"): "斗牛",
        ("谷神星", "古神星"): "谷神星",
        ("AC721", "721"): "AC721",
        ("阋神星"): "阋神星",
        ("创神星"): "创神星",
        ("枪骑兵"): "枪骑兵",

        ("康纳马拉混沌", "康纳马拉", "混沌级", "混沌"): "康纳马拉混沌",
        ("奇美拉"): "奇美拉",
        ("光锥"): "光锥",
        ("卡利斯托", "卡里斯托"): "卡里斯托",
        ("猎兵", "列兵"): "猎兵",
        ("狩猎者", "狩猎"): "狩猎者",
        ("艾奥", "爱奥"): "艾奥",
        ("CAS066", "066"): "CAS066",
        ("KCCPV2.0", "kccpv2.0", "kccp2.0", "KCCPV", "KCC", "KCCP", "2.0"): "KCCPV2.0",

        ("雷火之星", "雷火"): "雷火之星",
        ("乌拉诺斯之毛", "大毛"): "乌拉诺斯之毛",
        ("新君士坦丁大帝", "大帝"): "新君士坦丁大帝",
        ("永恒风暴", "风暴"): "永恒风暴",
        ("ST59", "59"): "ST59",

        ("埃迪卡拉"): "埃迪卡拉",
        ("FSV830", "FSV", "830"): "FSV830",

        ("太阳鲸", "鲸鱼", "太阳镜"): "太阳鲸",
        ("南十字星元帅", "南十字", "十字", "元帅"): "南十字星元帅",
        ("CV3000", "cv3000", "CV", "3000"): "CV3000",

        ("AT021", "021"): "AT021",
        ("米斯特拉", "小米"): "米斯特拉",
        ("佩刀Aer410", "佩刀"): "佩刀Aer410",
        ("刺鳐"): "刺鳐",
        ("孢子A404", "孢子"): "孢子A404",
        ("B192新大地", "新大地"): "B192新大地",
        ("维塔斯-B010", "维塔斯B", "维B", "VB"): "维塔斯-B010",
        ("维塔斯-A021", "维塔斯A", "维A", "VA"): "维塔斯-A021",
        ("平衡安德森SC020", "安德森", "SC020"): "平衡安德森SC020",
        ("海氏追随者", "海氏", "海追", "追追"): "海氏追随者",
        ("林鸮A100", "林鸮"): "林鸮A100",
        ("牛蛙"): "牛蛙",
        ("砂龙", "沙龙", "傻龙"): "砂龙",
        ("SC002", "sc002"): "SC002",

        ("S-列维9号", "列维9号", "列维"): "S-列维9号",
        ("CV-T800", "CVT800", "T800", "800"): "CV-T800",
        ("CV-M011", "CVM011", "M011", "011"): "CV-M011",
        ("虚灵"): "虚灵",
        ("星云追逐者", "星云"): "星云追逐者",
        ("蜂巢守卫者", "蜂巢"): "蜂巢守卫者",
        ("RB7-13", "RB7"): "RB7-13",
        ("CV-II003", "CV-11003", "CVII003", "11003"): "CV-II003",
        ("鳐"): "鳐"
    }

    map_fin = {}
    for k, v in pricise_name_map.items():
        if type(k) == str:
            map_fin[k] = v
        else:
            for key in k:
                map_fin[key] = v

    return map_fin[name]

def get_ship_tier (name:str) -> int:
    #              0         1         2           3            4         5        6        7
    # in order [frigate, destroyer, cruiser, battlecrusier, auxiliary, carrier, covette, fighter]
    ship_tier_map = {
        ("诺玛M470", "刺水母", "澄海", "红宝石", "雷里亚特", "卡利莱恩", "云海", "静海", "FG300"): 0,
        ("卫士", "苔原", "亚达伯拉", "斗牛", "谷神星", "AC721", "阋神星", "创神星", "枪骑兵"): 1,
        ("康纳马拉混沌", "奇美拉", "光锥", "卡里斯托", "猎兵", "狩猎者", "艾奥", "CAS066", "KCCPV2.0"): 2,
        ("雷火之星", "乌拉诺斯之毛", "新君士坦丁大帝", "永恒风暴", "ST59"): 3,
        ("埃迪卡拉", "FSV830"): 4,
        ("太阳鲸", "南十字星元帅", "CV3000"): 5,
        ("S-列维9号", "CV-T800", "CV-M011", "虚灵", "星云追逐者", "蜂巢守卫者", "RB7-13", "CV-II003", "鳐"): 6,
        ("AT021", "米斯特拉", "佩刀Aer410", "刺鳐", "孢子A404", "B192新大地", "维塔斯-B010", "维塔斯-A021", "平衡安德森SC020",
         "海氏追随者", "林鸮A100", "牛蛙", "砂龙", "SC002"): 7
    }

    map_fin = {}
    for k, v in ship_tier_map.items():
        if k is str:
            map_fin[k] = v
        else:
            for key in k:
                map_fin[key] = v


    return map_fin[correct_ship_name(name)]
