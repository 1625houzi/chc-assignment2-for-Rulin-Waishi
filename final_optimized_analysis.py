import re
import json
import csv
from collections import Counter
import jieba
import jieba.analyse

# 配置jieba
print("初始化jieba分词，优化地名识别...")

# 增强的自定义词典 - 重点加强地名权重并排除非地名
custom_words = [
    # 南京相关变体（提高权重）
    "南京 2000 ns", "南京城 1800 ns", "金陵 1800 ns", "應天府 1800 ns", "江寧府 1800 ns", 
    "白下 1500 ns", "南都 1500 ns", "建康 1500 ns", "秣陵 1500 ns", "建業 1500 ns",
    "江寧 1500 ns", "到南京 1200 ns", "在南京 1200 ns", "自南京 1200 ns", "往南京 1200 ns",
    "南京來 1200 ns", "南京去 1200 ns", "南京的 1200 ns", 
    
    # 北京相关变体
    "北京 1800 ns", "北京城 1600 ns", "京師 1600 ns", "到北京 1300 ns", "在京師 1300 ns",
    
    # 扬州相关变体
    "揚州 1800 ns", "揚州城 1600 ns", "到揚州 1300 ns", "在揚州 1300 ns", "揚州府 1500 ns",
    
    # 其他主要城市
    "蘇州 1600 ns", "杭州 1600 ns", "濟南 1500 ns", "湖州 1500 ns", "徽州 1500 ns", 
    "成都 1500 ns", "安東 1400 ns", "五河 1400 ns", "天長 1400 ns",
    
    # 地名后缀模式
    "[\u4e00-\u9fa5]{1,4}縣 1000 ns", "[\u4e00-\u9fa5]{1,4}府 1000 ns",
    "[\u4e00-\u9fa5]{1,4}州 1000 ns", "[\u4e00-\u9fa5]{1,4}鎮 1000 ns",
    "[\u4e00-\u9fa5]{1,4}城 1000 ns", "[\u4e00-\u9fa5]{1,4}鄉 800 ns",
    "[\u4e00-\u9fa5]{1,4}村 800 ns", "[\u4e00-\u9fa5]{1,4}街 700 ns",
    
    # 降低非地名的权重
    "知道 0 v", "說道 0 v", "問道 0 v", "人道 0 v", "難道 0 d", "道理 0 n", "路上 0 n",
    "一路 0 n", "府上 0 n", "尊府 0 n", "州府 0 n", "鄉紳 0 n", "那人道 0 v", "十里 0 m",
    "街上 0 n", "大道 0 n", "小道 0 n", "便道 0 v", "強盜 0 n", "道路 0 n", "一道 0 m",
    "知道了 0 v", "不知道 0 v", "知道的 0 v", "知道要 0 v", "知道是 0 v",
    "說道是 0 v", "說道你 0 v", "說道我 0 v", "說道他 0 v", "說道這 0 v",
    "問道他 0 v", "問道你 0 v", "問道我 0 v", "問道這 0 v", "問道是 0 v"
]

# 保存自定义词典
with open('final_jieba_dict.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(custom_words))

# 加载自定义词典
jieba.load_userdict('final_jieba_dict.txt')

# 读取《儒林外史》文本
print("读取《儒林外史》文本...")
with open('/Users/yangtuotuo/Documents/trae_projects/CHC assignment2/儒林外史.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 按章节分割文本
chapters = re.split(r'\n\*(.*?)\n', text)
chapter_data = []

for i in range(1, len(chapters), 2):
    chapter_title = chapters[i]
    chapter_content = chapters[i+1] if i+1 < len(chapters) else ''
    chapter_data.append({
        'chapter_number': (i + 1) // 2,
        'chapter_title': chapter_title,
        'content': chapter_content
    })

print(f"共找到 {len(chapter_data)} 个章节")

# 城市名称归一化字典
city_normalization = {
    '南京': ['南京', '應天府', '江寧府', '白下', '金陵', '南京城', '南都', '建康', '秣陵', '建業', '江寧',
            '到南京', '在南京', '自南京', '往南京', '南京來', '南京去', '南京的'],
    '北京': ['北京', '京師', '北京城', '到北京', '在京師', '往京師'],
    '揚州': ['揚州', '揚州城', '到揚州', '在揚州', '揚州府', '往揚州'],
    '蘇州': ['蘇州', '吳縣', '吳中', '蘇州城', '到蘇州', '在蘇州'],
    '杭州': ['杭州', '武林', '錢塘', '杭州城', '到杭州', '在杭州'],
    '濟南': ['濟南', '濟南府', '到濟南', '在濟南'],
    '湖州': ['湖州', '湖郡', '到湖州', '在湖州'],
    '徽州': ['徽州', '新安', '到徽州', '在徽州'],
    '成都': ['成都', '成都府', '到成都', '在成都']
}

# 常见地名后缀
city_suffixes = ['縣', '府', '州', '鎮', '城', '鄉', '村', '街', '里', '坊', '巷', '道', '路']

# 大幅扩展排除词汇列表
exclude_words = [
    # 常用动词短语
    '知道', '說道', '問道', '人道', '難道', '道理', '路上', '一路', '府上', '尊府', '州府', 
    '鄉紳', '那人道', '十里', '街上', '大道', '小道', '便道', '強盜', '道路', '一道',
    '知道了', '不知道', '知道的', '知道要', '知道是', '說道是', '說道你', '說道我', '說道他', 
    '說道這', '問道他', '問道你', '問道我', '問道這', '問道是',
    # 其他常用非地名
    '自己', '不是', '只是', '可是', '但是', '要是', '就是', '正是', '于是', '因此', '所以', 
    '忽然', '果然', '竟然', '居然', '虽然', '然而', '因为', '由于', '对于', '关于', '此外', 
    '另外', '这个', '那个', '这些', '那些', '这里', '那里', '这么', '那么', '这样', '那样'
]

# 正则表达式模式匹配非地名
non_place_patterns = [
    # 动词+道模式
    r'^[\u4e00-\u9fa5]道$',  # 如：知道、說道
    r'^[\u4e00-\u9fa5]{2,3}道$',  # 如：問道、那人道
    # 数量词+里模式
    r'^[\d一二三四五六七八九十百千]+里$',  # 如：十里、百里
    # 其他模式
    r'^[\u4e00-\u9fa5]+道的$',
    r'^[\u4e00-\u9fa5]+道是$',
    r'^[\u4e00-\u9fa5]+道你$',
    r'^[\u4e00-\u9fa5]+道我$',
    r'^[\u4e00-\u9fa5]+道他$',
    r'^[\u4e00-\u9fa5]+道這$',
    # 排除单个字符
    r'^.$'
]

# 改进的有效性判断函数 - 严格过滤非地名
def is_valid_city(word):
    # 检查是否在排除列表中
    if word in exclude_words:
        return False
    
    # 使用正则表达式检查非地名模式
    for pattern in non_place_patterns:
        if re.match(pattern, word):
            return False
    
    # 检查是否在预定义城市变体中
    for variants in city_normalization.values():
        if word in variants:
            return True
    
    # 检查是否包含地名后缀
    if any(suffix in word for suffix in city_suffixes):
        # 但排除包含"道"作为后缀且不是真正地名的词汇
        if '道' in word and not any(s in word for s in ['街道', '道路', '河道', '官道', '省道', '国道']):
            # 进一步检查是否为真正的地名
            if not re.search(r'[縣府州鎮城鄉村街巷坊]', word):
                return False
        return True
    
    # 检查是否包含方向词+地名的模式
    direction_patterns = ['到', '在', '往', '自']
    for direction in direction_patterns:
        if word.startswith(direction) and len(word) > 2:
            # 截取方向词后的部分，检查是否包含地名特征
            remaining = word[1:]
            if any(suffix in remaining for suffix in ['縣', '府', '州', '鎮', '城']):
                return True
            # 或者剩余部分是已知城市
            for city in ['南京', '北京', '揚州', '蘇州', '杭州', '濟南', '湖州', '徽州', '成都']:
                if remaining == city:
                    return True
    
    return False

# 使用jieba精确模式进行分词
def identify_cities_with_jieba(text):
    # 使用精确模式分词
    words_exact = list(jieba.cut(text, cut_all=False))
    
    # 收集潜在的地名
    potential_places = []
    for word in words_exact:
        if is_valid_city(word):
            potential_places.append(word)
    
    # 另外，直接在文本中搜索预定义的城市变体
    for city, variants in city_normalization.items():
        for variant in variants:
            # 直接统计每个变体的出现次数
            count = text.count(variant)
            if count > 0:
                # 添加到潜在地名列表中（按实际出现次数）
                potential_places.extend([variant] * count)
    
    return potential_places

# 归一化函数
def normalize_and_count_cities(place_list):
    normalized_counts = Counter()
    variant_details = {}
    
    # 初始化变体详情字典
    for city, variants in city_normalization.items():
        variant_details[city] = {variant: 0 for variant in variants}
    
    # 统计变体
    temp_counter = Counter(place_list)
    
    # 处理预定义的城市变体
    for city, variants in city_normalization.items():
        total = 0
        for variant in variants:
            if variant in temp_counter:
                count = temp_counter[variant]
                total += count
                variant_details[city][variant] = count
                del temp_counter[variant]  # 从临时计数器中删除已处理的变体
        if total > 0:
            normalized_counts[city] = total
    
    # 处理未在预定义字典中的地名（带后缀的）
    for place, count in temp_counter.items():
        if is_valid_city(place):  # 再次验证
            normalized_counts[place] = count
            variant_details[place] = {place: count}
    
    return normalized_counts, variant_details

# 直接字符串搜索
def direct_city_search(text):
    direct_counts = Counter()
    
    # 对每个城市的所有变体进行直接文本搜索
    for city, variants in city_normalization.items():
        total = 0
        for variant in variants:
            count = text.count(variant)
            total += count
        if total > 0:
            direct_counts[city] = total
    
    return direct_counts

# 分析每个章节
total_places = []
chapter_analysis = []

print("开始章节分析...")

# 只分析第30-50章
filtered_chapters = [chapter for chapter in chapter_data if 30 <= chapter['chapter_number'] <= 50]
print(f"过滤后待分析章节数：{len(filtered_chapters)}")

for chapter in filtered_chapters:
    chapter_number = chapter['chapter_number']
    chapter_title = chapter['chapter_title']
    chapter_text = chapter['content']
    
    # 组合多种方法：jieba分词 + 直接字符串搜索
    chapter_places = identify_cities_with_jieba(chapter_text)
    
    # 归一化并统计
    city_counts, variant_details = normalize_and_count_cities(chapter_places)
    
    # 计算城市密集度
    total_words = len(list(jieba.cut(chapter_text)))
    city_density = sum(city_counts.values()) / total_words if total_words > 0 else 0
    
    # 记录分析结果
    chapter_analysis.append({
        'chapter_number': chapter_number,
        'chapter_title': chapter_title,
        'cities': city_counts,
        'total_city_mentions': sum(city_counts.values()),
        'city_density': city_density,
        'variant_details': variant_details
    })
    
    # 添加到总列表
    total_places.extend(chapter_places)

# 使用jieba方法进行分析
filtered_text = '\n'.join([chapter['content'] for chapter in filtered_chapters])
filtered_city_counts, filtered_variant_details = normalize_and_count_cities(total_places)

# 进一步过滤结果，移除可能的非地名
filtered_counts = {}
for city, count in filtered_city_counts.items():
    if is_valid_city(city):
        filtered_counts[city] = count

# 区域分类
region_classification = {
    '江南地区': ['南京', '蘇州', '杭州', '揚州', '湖州', '徽州', '鎮江', '常州', '嘉興', '寧波', '松江', '太倉'],
    '华北地区': ['北京', '濟南', '開封', '大名', '保定', '天津'],
    '西南地区': ['成都', '重慶', '貴陽'],
    '其他地区': []
}

# 按区域分类统计
region_stats = {region: Counter() for region in region_classification.keys()}
for city, count in filtered_counts.items():
    region_found = False
    for region, cities_in_region in region_classification.items():
        if city in cities_in_region:
            region_stats[region][city] = count
            region_found = True
            break
    if not region_found:
        region_stats['其他地区'][city] = count

# 提取所有城市列表
all_cities_list = []
for city, count in sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True):
    # 确定区域
    region = '其他地区'
    for r, cities_in_region in region_classification.items():
        if city in cities_in_region:
            region = r
            break
    
    all_cities_list.append({
        'city': city,
        'count': count,
        'region': region,
        'variants': filtered_variant_details.get(city, {city: count})
    })

# 输出结果
print("\n=== 第30-50章城市识别结果 ===")
print(f"共识别出 {len(filtered_counts)} 个城市")
print("\n出现次数最多的前20个城市：")

for i, (city, count) in enumerate(sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)[:20], 1):
    print(f"{i:2d}. {city}: {count} 次")
    # 打印南京的变体详情
    if city == '南京' and city in all_variant_details:
        print("   南京变体详情：")
        for variant, v_count in sorted(all_variant_details[city].items(), key=lambda x: x[1], reverse=True):
            if v_count > 0:
                print(f"     - {variant}: {v_count} 次")

# 区域统计
print("\n=== 区域统计 ===")
for region, cities in region_stats.items():
    total_mentions = sum(cities.values())
    city_count = len(cities)
    print(f"{region}: {city_count} 个城市, 共 {total_mentions} 次提及")

# 30-50章中各章节城市出现统计
print("\n=== 第30-50章各章节城市出现统计 ===")
for chapter in chapter_analysis:
    print(f"第{chapter['chapter_number']}回《{chapter['chapter_title']}》: {chapter['total_city_mentions']} 次")

# 南京在各章节的分布
print("\n=== 南京出现次数最多的10个章节 ===")
nanjing_chapters = []
for chapter in chapter_analysis:
    if '南京' in chapter['cities']:
        nanjing_chapters.append((chapter['chapter_number'], chapter['chapter_title'], chapter['cities']['南京']))

nanjing_chapters.sort(key=lambda x: x[2], reverse=True)
for i, (ch_num, ch_title, count) in enumerate(nanjing_chapters[:10], 1):
    print(f"{i:2d}. 第{ch_num}回《{ch_title}》: {count} 次")

# 保存结果
print("\n保存最终分析结果...")

# 保存JSON结果
full_results = {
    'total_chapters_analyzed': len(filtered_chapters),
    'analyzed_chapters_range': '30-50',
    'total_valid_cities': len(filtered_counts),
    'city_counts': filtered_counts,
    'region_statistics': {region: dict(cities) for region, cities in region_stats.items()},
    'chapter_analysis': chapter_analysis,
    'city_variant_details': filtered_variant_details,
    'all_cities_list': all_cities_list
}

with open('final_city_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(full_results, f, ensure_ascii=False, indent=2)

# 保存CSV结果
with open('final_cities.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['城市', '出现次数', '区域'])
    
    for city_info in all_cities_list:
        writer.writerow([
            city_info['city'],
            city_info['count'],
            city_info['region']
        ])

# 为可视化准备数据
visualization_data = {
    'cities': [],
    'regions': {}
}

# 城市数据（前30个）
for city_info in all_cities_list[:30]:
    visualization_data['cities'].append({
        'name': city_info['city'],
        'value': city_info['count'],
        'region': city_info['region']
    })

# 区域数据
for region, cities in region_stats.items():
    visualization_data['regions'][region] = {
        'city_count': len(cities),
        'total_mentions': sum(cities.values()),
        'top_cities': sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]
    }

with open('final_visualization.json', 'w', encoding='utf-8') as f:
    json.dump(visualization_data, f, ensure_ascii=False, indent=2)

print("\n最终分析完成！")
print(f"分析范围：第30-50章")
print(f"分析章节数：{len(filtered_chapters)}")
print(f"结果文件：")
print(f"1. final_city_analysis.json - 完整分析结果")
print(f"2. final_cities.csv - 城市统计表格")
print(f"3. final_visualization.json - 可视化数据")
print(f"\n总计识别城市数量：{len(filtered_counts)}")
print(f"南京出现次数：{filtered_counts.get('南京', 0)} 次")
print(f"扬州出现次数：{filtered_counts.get('揚州', 0)} 次")
print(f"\n使用jieba分词方法，通过严格过滤非地名词汇，成功排除了'知道'、'說道'等错误结果。")