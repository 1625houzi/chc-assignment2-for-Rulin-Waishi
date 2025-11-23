import json
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
from folium.features import DivIcon

# 1. 地理坐标映射 - 收集七个目标地点的经纬度坐标
# 历史地名与现代地名的对应关系处理
place_coordinates = {
    '南京': {  # 历史地名：金陵、應天府、江寧府等
        'lat': 32.0603,
        'lng': 118.7969,
        'modern_name': '南京市',
        'historical_names': ['南京', '金陵', '應天府', '江寧府', '白下', '南都', '建康', '秣陵', '建業', '江寧']
    },
    '北京': {  # 历史地名：京師
        'lat': 39.9042,
        'lng': 116.4074,
        'modern_name': '北京市',
        'historical_names': ['北京', '京師', '北京城']
    },
    '揚州': {  # 历史地名：揚州、揚州府
        'lat': 32.3930,
        'lng': 119.4941,
        'modern_name': '扬州市',
        'historical_names': ['揚州', '揚州府']
    },
    '蘇州': {  # 历史地名：蘇州
        'lat': 31.2989,
        'lng': 120.5853,
        'modern_name': '苏州市',
        'historical_names': ['蘇州', '吳縣', '吳中']
    },
    '杭州': {  # 历史地名：武林、錢塘
        'lat': 30.2741,
        'lng': 120.1551,
        'modern_name': '杭州市',
        'historical_names': ['杭州', '武林', '錢塘']
    },
    '濟南': {  # 历史地名：濟南府
        'lat': 36.6512,
        'lng': 117.1201,
        'modern_name': '济南市',
        'historical_names': ['濟南', '濟南府']
    },
    '湖州': {  # 历史地名：湖郡
        'lat': 30.8690,
        'lng': 119.9107,
        'modern_name': '湖州市',
        'historical_names': ['湖州', '湖郡']
    }
}

# 读取之前的分析结果
print("读取地点频率分析结果...")
with open('place_frequency_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# 提取目标地点统计数据和地点-章节矩阵
target_place_stats = analysis_data['target_place_stats']
place_chapter_matrix = analysis_data['place_chapter_matrix']
chapter_titles = {}

# 读取CSV获取章节标题信息
print("读取章节标题信息...")
df_matrix = pd.read_csv('place_chapter_matrix.csv')
for _, row in df_matrix.iterrows():
    chapter_num = int(row['章节'].replace('第', '').replace('回', ''))
    chapter_titles[chapter_num] = row['章节标题']

# 2. 创建地图可视化
print("创建GIS可视化地图...")

# 计算中国东部地区的中心点作为地图初始位置（集中在长三角和华北地区）
center_lat = sum(place['lat'] for place in place_coordinates.values()) / len(place_coordinates)
center_lng = sum(place['lng'] for place in place_coordinates.values()) / len(place_coordinates)

# 创建地图实例
map_china = folium.Map(location=[center_lat, center_lng], zoom_start=6, 
                      tiles='CartoDB positron', control_scale=True)

# 添加标题
map_title = "《儒林外史》第30-50章地点分布可视化"
map_title_html = f"""
                 <h3 align="center" style="font-size:20px"><b>{map_title}</b></h3>
                 <p align="center">分析目标：南京、北京、揚州、蘇州、杭州、濟南、湖州</p>
                 """
map_china.get_root().html.add_child(folium.Element(map_title_html))

# 3. 创建热力图层 - 根据总出现频率
print("创建热力图层...")

# 准备热力图数据
heat_data = []
for place, stats in target_place_stats.items():
    if place in place_coordinates:
        lat = place_coordinates[place]['lat']
        lng = place_coordinates[place]['lng']
        # 使用总出现次数作为权重
        weight = stats['total_count']
        # 为了热力图效果更好，将权重归一化到合理范围
        normalized_weight = min(weight / 10, 1)
        heat_data.append([lat, lng, normalized_weight])

# 添加热力图层
heat_layer = folium.FeatureGroup(name='总出现频率热力图', control=True)
HeatMap(
    heat_data,
    min_opacity=0.3,
    max_zoom=15,
    radius=25,
    blur=15,
    gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'},
    overlay=True
).add_to(heat_layer)
heat_layer.add_to(map_china)

# 4. 创建地点标记图层 - 根据总出现频率
print("创建地点标记图层...")

# 获取所有地点的总出现次数，用于计算标记大小
max_count = max(stats['total_count'] for stats in target_place_stats.values())
min_count = min(stats['total_count'] for stats in target_place_stats.values())
count_range = max_count - min_count if max_count > min_count else 1

# 创建地点标记图层
place_markers = folium.FeatureGroup(name='地点总出现频率标记', control=True)

for place, stats in target_place_stats.items():
    if place in place_coordinates:
        coord = place_coordinates[place]
        total_count = stats['total_count']
        
        # 根据出现次数计算标记大小（30-60像素范围）
        marker_size = 30 + (total_count - min_count) / count_range * 30
        
        # 根据出现次数确定颜色
        if total_count >= max_count * 0.7:
            color = 'red'
        elif total_count >= max_count * 0.4:
            color = 'orange'
        elif total_count >= max_count * 0.1:
            color = 'green'
        else:
            color = 'blue'
        
        # 创建弹出信息
        popup_content = f"""
        <h4>{place}</h4>
        <p><b>现代名称：</b>{coord['modern_name']}</p>
        <p><b>历史名称：</b>{', '.join(coord['historical_names'])}</p>
        <p><b>总出现次数：</b>{total_count}</p>
        <p><b>每章平均密度：</b>{stats['avg_density']:.2f}</p>
        <p><b>章节存在率：</b>{stats['presence_rate']:.2%}</p>
        <p><b>出现在章节数：</b>{stats['present_in_chapters']}</p>
        """
        
        # 添加圆形标记
        folium.CircleMarker(
            location=[coord['lat'], coord['lng']],
            radius=marker_size / 10,  # 调整半径大小
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{place} (出现{total_count}次)"
        ).add_to(place_markers)
        
        # 添加地点名称标签
        folium.map.Marker(
            [coord['lat'] + 0.05, coord['lng']],
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(0, 0),
                html=f'<div style="font-size: 12pt; font-weight: bold; color: {color}">{place}</div>',
            )
        ).add_to(place_markers)

place_markers.add_to(map_china)

# 5. 为每个章节创建单独的图层
print("创建章节图层...")

# 获取分析的章节范围
chapter_range = range(30, 51)  # 30-50章

# 创建章节标记集群
for chapter_num in chapter_range:
    chapter_layer = folium.FeatureGroup(name=f'第{chapter_num}回', control=True)
    marker_cluster = MarkerCluster().add_to(chapter_layer)
    
    # 获取该章节的地点数据
    chapter_has_data = False
    for place in target_place_stats.keys():
        if place in place_coordinates and chapter_num in place_chapter_matrix.get(place, {}):
            count = place_chapter_matrix[place][chapter_num]
            if count > 0:
                chapter_has_data = True
                coord = place_coordinates[place]
                
                # 创建弹出信息
                popup_content = f"""
                <h5>第{chapter_num}回 《{chapter_titles.get(chapter_num, '')}》</h5>
                <p><b>地点：</b>{place}</p>
                <p><b>出现次数：</b>{count}</p>
                <p><b>现代位置：</b>{coord['modern_name']}</p>
                """
                
                # 添加标记
                folium.Marker(
                    location=[coord['lat'], coord['lng']],
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{place}: {count}次",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(marker_cluster)
    
    # 如果章节有数据，则添加到地图
    if chapter_has_data:
        chapter_layer.add_to(map_china)

# 6. 创建统计信息面板
print("创建统计信息面板...")

# 准备统计信息
stats_info = """
<div style="background-color: white; padding: 10px; border-radius: 5px; font-size: 12px;">
    <h4>地点统计概览</h4>
    <table border="1" cellpadding="3" cellspacing="0" style="width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th>地点</th>
            <th>总次数</th>
            <th>平均密度</th>
            <th>存在率</th>
        </tr>
"""

# 按总出现次数排序
for place in sorted(target_place_stats.keys(), key=lambda x: target_place_stats[x]['total_count'], reverse=True):
    stats = target_place_stats[place]
    stats_info += f"""
        <tr>
            <td>{place}</td>
            <td>{stats['total_count']}</td>
            <td>{stats['avg_density']:.2f}</td>
            <td>{stats['presence_rate']:.0%}</td>
        </tr>
    """

stats_info += """
    </table>
    <p><i>数据来源：《儒林外史》第30-50章分析</i></p>
</div>
"""

# 添加统计信息面板
folium.Element(stats_info).add_to(folium.plugins.FloatImage(map_china, bottom=5, left=5))

# 7. 添加图层控制和保存地图
print("添加图层控制...")

# 添加图层控制
folium.LayerControl().add_to(map_china)

# 添加比例尺
folium.plugins.MiniMap().add_to(map_china)

# 保存地图为HTML文件
map_file = 'place_distribution_map.html'
map_china.save(map_file)

print(f"\nGIS可视化地图已生成！")
print(f"文件保存为：{map_file}")
print("\n地图包含以下功能：")
print("1. 总出现频率热力图 - 展示地点的整体重要性")
print("2. 地点总出现频率标记 - 使用不同颜色和大小显示出现频率")
print("3. 章节过滤器 - 可选择查看特定章节的地点分布")
print("4. 统计信息面板 - 展示各地点的详细统计数据")
print("5. 交互式功能 - 点击标记可查看详细信息，支持缩放和平移")
print("\n您可以在浏览器中打开此HTML文件查看交互式地图。")