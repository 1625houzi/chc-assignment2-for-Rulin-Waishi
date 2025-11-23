import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import streamlit.components.v1 as components

# ==========================================
# 1. 设置页面配置 (必须是第一个 Streamlit 命令)
# ==========================================
st.set_page_config(
    page_title="《儒林外史》地点分布分析",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化语言设置
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# 中英文翻译字典
translations = {
    'zh': {
        'page_title': '《儒林外史》地点分布分析',
        'main_header': '《儒林外史》地点分布分析系统',
        'sub_header': '基于第30-50章文本分析的交互式可视化',
        'sidebar_settings': '筛选设置',
        'chapter_range': '章节范围',
        'start_chapter': '开始章节',
        'end_chapter': '结束章节',
        'chapter_error': '开始章节不能大于结束章节！',
        'select_places': '选择地点',
        'select_places_label': '选择要分析的地点',
        'place_error': '请至少选择一个地点！',
        'analysis_stats': '分析统计',
        'analysis_chapter_range': '分析章节范围:',
        'analysis_place_count': '分析地点数量:',
        'tab_map': '地图视图',
        'tab_overview': '数据概览',
        'tab_charts': '图表分析',
        'tab_table': '详细表格',
        'map_header': '地点分布地图',
        'location_data': '地点坐标数据',
        'available_locations': '以下是当前可用的地点及其坐标：',
        'place': '地点',
        'modern_name': '现代名称',
        'latitude': '纬度',
        'longitude': '经度',
        'mention_count': '出现次数',
        'visualization_title': '《儒林外史》第{start}-{end}回地点分布可视化',
        'map_description': 'GIS地图说明：',
        'map_desc_point1': '使用Leaflet交互式地图展示《儒林外史》中的地点地理分布',
        'map_desc_point2': '颜色深浅表示地点出现频率（红色：高频，绿色：中频，蓝色：低频）',
        'map_desc_point3': '圆点大小表示出现次数',
        'map_desc_point4': '每个地点显示名称标签',
        'map_desc_point5': '点击标记可查看详细信息',
        'map_desc_point6': '悬停时显示简要信息',
        'map_desc_point7': '可缩放、平移地图以查看更多细节',
        'map_desc_point8': '地图自动调整视野，确保所有地点可见',
        'overview_header': '数据统计概览',
        'total_mentions': '筛选范围总出现次数',
        'avg_per_chapter': '平均每章出现次数',
        'presence_rate': '章节存在率',
        'present_chapters': '出现在章节数',
        'frequency_comparison': '地点出现频率对比',
        'frequency_title': '第{start}-{end}回各地点出现总次数',
        'distribution_ratio': '地点分布比例',
        'distribution_title': '第{start}-{end}回地点分布比例',
        'percentage': '百分比(%)',
        'no_data': '所选范围内没有数据可供分析',
        'trends_header': '趋势与对比分析',
        'trend_analysis': '地点出现趋势分析',
        'trend_title': '第{start}-{end}回各地点出现趋势',
        'chapter': '章节',
        'chapter_number': '章节号',
        'heatmap': '地点-章节频率热力图',
        'heatmap_title': '第{start}-{end}回地点出现频率热力图',
        'detailed_table': '详细数据表格',
        'matrix_header': '地点-章节出现次数矩阵',
        'chapter_title': '章节标题',
        'total_places': '总地点数',
        'data_export': '数据导出',
        'export_csv': '导出详细数据为CSV',
        'export_json': '导出筛选数据为JSON',
        'footer_line1': '《儒林外史》地点分布分析系统 © 2024',
        'footer_line2': '基于jieba分词和Streamlit开发的交互式文本分析工具',
        'error_visualization': '创建可视化时出错: {error}',
        'error_details': '错误详情',
        'error_type': '错误类型:',
        'error_message': '错误信息:',
        'location_list': '地点数据列表',
        'no_location_data': '没有可用的地点坐标数据',
        'modern_name_popup': '现代名称：',
        'total_mentions_popup': '总出现次数：',
        'mentions_text': '出现{count}次',
        'legend': '图例',
        'high_frequency': '高频地点',
        'medium_frequency': '中频地点',
        'low_frequency': '低频地点',
    },
    'en': {
        'page_title': 'Rulin Wai Shi Place Distribution Analysis',
        'main_header': 'Rulin Wai Shi Place Distribution Analysis System',
        'sub_header': 'Interactive Visualization Based on Chapters 30-50 Text Analysis',
        'sidebar_settings': 'Filter Settings',
        'chapter_range': 'Chapter Range',
        'start_chapter': 'Start Chapter',
        'end_chapter': 'End Chapter',
        'chapter_error': 'Start chapter cannot be greater than end chapter!',
        'select_places': 'Select Places',
        'select_places_label': 'Select places to analyze',
        'place_error': 'Please select at least one place!',
        'analysis_stats': 'Analysis Statistics',
        'analysis_chapter_range': 'Analysis chapter range:',
        'analysis_place_count': 'Number of analyzed places:',
        'tab_map': 'Map View',
        'tab_overview': 'Data Overview',
        'tab_charts': 'Chart Analysis',
        'tab_table': 'Detailed Table',
        'map_header': 'Place Distribution Map',
        'location_data': 'Location Coordinate Data',
        'available_locations': 'The following are the currently available locations and their coordinates:',
        'place': 'Place',
        'modern_name': 'Modern Name',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'mention_count': 'Mention Count',
        'visualization_title': 'Rulin Wai Shi Place Distribution Visualization (Chapters {start}-{end})',
        'map_description': 'GIS Map Description:',
        'map_desc_point1': 'Using Leaflet interactive map to display the geographical distribution of places in Rulin Wai Shi',
        'map_desc_point2': 'Color depth indicates the frequency of place mentions (red: high frequency, green: medium frequency, blue: low frequency)',
        'map_desc_point3': 'Circle size represents the number of mentions',
        'map_desc_point4': 'Each location displays a name label',
        'map_desc_point5': 'Click on markers to view detailed information',
        'map_desc_point6': 'Hover to display brief information',
        'map_desc_point7': 'You can zoom and pan the map to view more details',
        'map_desc_point8': 'The map automatically adjusts the view to ensure all locations are visible',
        'overview_header': 'Data Statistics Overview',
        'total_mentions': 'Total Mentions in Filtered Range',
        'avg_per_chapter': 'Average Mentions Per Chapter',
        'presence_rate': 'Chapter Presence Rate',
        'present_chapters': 'Number of Chapters Present',
        'frequency_comparison': 'Place Frequency Comparison',
        'frequency_title': 'Total Mentions of Each Place (Chapters {start}-{end})',
        'distribution_ratio': 'Place Distribution Ratio',
        'distribution_title': 'Place Distribution Ratio (Chapters {start}-{end})',
        'percentage': 'Percentage(%)',
        'no_data': 'No data available for analysis in the selected range',
        'trends_header': 'Trend and Comparison Analysis',
        'trend_analysis': 'Place Mention Trend Analysis',
        'trend_title': 'Mention Trends of Each Place (Chapters {start}-{end})',
        'chapter': 'Chapter',
        'chapter_number': 'Chapter Number',
        'heatmap': 'Place-Chapter Frequency Heatmap',
        'heatmap_title': 'Place Mention Frequency Heatmap (Chapters {start}-{end})',
        'detailed_table': 'Detailed Data Table',
        'matrix_header': 'Place-Chapter Mention Count Matrix',
        'chapter_title': 'Chapter Title',
        'total_places': 'Total Places',
        'data_export': 'Data Export',
        'export_csv': 'Export Detailed Data as CSV',
        'export_json': 'Export Filtered Data as JSON',
        'footer_line1': '《儒林外史》地点分布分析系统 © 2024',
        'footer_line2': 'Interactive text analysis tool developed based on jieba segmentation and Streamlit',
        'error_visualization': 'Error creating visualization: {error}',
        'error_details': 'Error Details',
        'error_type': 'Error Type:',
        'error_message': 'Error Message:',
        'location_list': 'Location Data List',
        'no_location_data': 'No location coordinate data available',
        'modern_name_popup': 'Modern Name: ',
        'total_mentions_popup': 'Total Mentions: ',
        'mentions_text': '{count} mentions',
        'legend': 'Legend',
        'high_frequency': 'High Frequency',
        'medium_frequency': 'Medium Frequency',
        'low_frequency': 'Low Frequency',
    }
}

# 获取当前语言的翻译函数
def t(key, **kwargs):
    """获取指定键的翻译文本"""
    text = translations[st.session_state.language].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .data-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 生成模拟数据的函数
def generate_mock_data(place_coordinates):
    places = list(place_coordinates.keys())
    chapters = list(range(30, 51))
    
    # 构建 DataFrame
    data = {'章节': [f'第{i}回' for i in chapters], '章节标题': [f'第{i}回标题' for i in chapters]}
    for place in places:
        # 生成一些随机数据 (0-10次)
        data[place] = np.random.randint(0, 10, size=len(chapters))
    
    df_matrix = pd.DataFrame(data)
    
    analysis_data = {
        'target_places': places,
        'target_place_stats': {},
        'place_chapter_matrix': {}
    }
    
    return analysis_data, df_matrix

@st.cache_data
def load_data():
    # 地理坐标数据
    place_coordinates = {
        '南京': {'lat': 32.0603, 'lng': 118.7969, 'modern_name': '南京市'},
        '北京': {'lat': 39.9042, 'lng': 116.4074, 'modern_name': '北京市'},
        '揚州': {'lat': 32.3930, 'lng': 119.4941, 'modern_name': '扬州市'},
        '蘇州': {'lat': 31.2989, 'lng': 120.5853, 'modern_name': '苏州市'},
        '杭州': {'lat': 30.2741, 'lng': 120.1551, 'modern_name': '杭州市'},
        '濟南': {'lat': 36.6512, 'lng': 117.1201, 'modern_name': '济南市'},
        '湖州': {'lat': 30.8690, 'lng': 119.9107, 'modern_name': '湖州市'}
    }

    try:
        # 尝试读取CSV数据
        df_matrix = pd.read_csv('place_chapter_matrix.csv')
        # 尝试读取JSON数据
        with open('place_frequency_analysis.json', 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
            
    except FileNotFoundError:
        # 如果文件不存在，使用模拟数据
        analysis_data, df_matrix = generate_mock_data(place_coordinates)

    # 构建字典时确保 key 是整数 (int)
    csv_place_matrix = {}
    
    # 确保 target_places 存在
    if 'target_places' not in analysis_data:
        analysis_data['target_places'] = list(place_coordinates.keys())
        
    for place in analysis_data['target_places']:
        csv_place_matrix[place] = {}
        # 如果 CSV 中有这个地点的数据
        if place in df_matrix.columns:
            for idx, row in df_matrix.iterrows():
                try:
                    # 提取数字
                    chapter_str = str(row['章节'])
                    # 简单过滤出数字
                    chapter_num = int(''.join(filter(str.isdigit, chapter_str)))
                    csv_place_matrix[place][chapter_num] = int(row[place])
                except (ValueError, KeyError, TypeError):
                    continue
        else:
            # 如果 CSV 没有，尝试从 JSON 恢复并转换 key 为 int
            if 'place_chapter_matrix' in analysis_data and place in analysis_data['place_chapter_matrix']:
                json_data = analysis_data['place_chapter_matrix'][place]
                for k, v in json_data.items():
                    try:
                        csv_place_matrix[place][int(k)] = v
                    except ValueError:
                        pass

    analysis_data['place_chapter_matrix'] = csv_place_matrix

    return analysis_data, df_matrix, place_coordinates

# 加载数据
analysis_data, df_matrix, place_coordinates = load_data()

# 提取关键数据
target_places = analysis_data.get('target_places', [])
place_chapter_matrix = analysis_data.get('place_chapter_matrix', {})

# 准备章节数据
chapter_numbers = []
chapter_titles = {}
for idx, row in df_matrix.iterrows():
    try:
        c_str = str(row['章节'])
        c_num = int(''.join(filter(str.isdigit, c_str)))
        chapter_numbers.append(c_num)
        chapter_titles[c_num] = row.get('章节标题', c_str)
    except:
        pass

# 主标题
st.markdown(f'<div class="main-header">{t("main_header")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{t("sub_header")}</div>', unsafe_allow_html=True)

# 侧边栏设置
with st.sidebar:
    # 语言切换控件
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("🌐")
    with col2:
        language = st.selectbox(
            "语言 / Language",
            options=['zh', 'en'],
            index=0 if st.session_state.language == 'zh' else 1,
            format_func=lambda x: '中文' if x == 'zh' else 'English',
            key="language_select"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
    
    st.header(t("sidebar_settings"))
    
    # 章节范围选择器
    st.subheader(t("chapter_range"))
    col1, col2 = st.columns(2)
    with col1:
        start_chapter = st.number_input(t("start_chapter"), min_value=30, max_value=49, value=30)
    with col2:
        end_chapter = st.number_input(t("end_chapter"), min_value=31, max_value=50, value=50)
    
    # 确保开始章节小于等于结束章节
    if start_chapter > end_chapter:
        st.error(t("chapter_error"))
        st.stop()
    
    # 地点选择器
    st.subheader(t("select_places"))
    
    # 默认选择
    default_selection = [p for p in target_places if p in target_places]
    if len(default_selection) > 5:
        default_selection = default_selection[:5]

    selected_places = st.multiselect(
        t("select_places_label"),
        options=target_places,
        default=default_selection
    )
    
    # 确保至少选择一个地点
    if not selected_places:
        st.error(t("place_error"))
        st.stop()
    
    # 显示统计信息
    st.subheader(t("analysis_stats"))
    st.info(f"{t('analysis_chapter_range')} 第{start_chapter}-{end_chapter}回")
    st.info(f"{t('analysis_place_count')} {len(selected_places)}")

# 主要内容区域
selected_chapters = list(range(start_chapter, end_chapter + 1))

# 创建选项卡
main_tabs = st.tabs([t("tab_map"), t("tab_overview"), t("tab_charts"), t("tab_table")])

# 1. 地图视图选项卡
with main_tabs[0]:
    st.header(t("map_header"))
    
    # 计算筛选后的统计数据
    filtered_stats = {}
    for place in selected_places:
        filtered_count = sum(place_chapter_matrix.get(place, {}).get(ch, 0) for ch in selected_chapters)
        filtered_stats[place] = {
            'total_count': filtered_count
        }
    
    # 创建地点数据表格
    st.write(f"### {t('location_data')}")
    st.write(t("available_locations"))
    
    locations = []
    js_locations = []

    for place in selected_places:
        if place in place_coordinates:
            coord = place_coordinates[place]
            count = filtered_stats.get(place, {}).get('total_count', 0)
            
            # 表格显示用
            locations.append({
                t('place'): place,
                t('modern_name'): coord['modern_name'],
                t('latitude'): coord['lat'],
                t('longitude'): coord['lng'],
                t('mention_count'): count
            })

            # JS地图用 (Key固定为英文)
            js_locations.append({
                'name': place,
                'modern_name': coord['modern_name'],
                'lat': coord['lat'],
                'lng': coord['lng'],
                'count': count
            })
    
    # 显示坐标数据表格
    if locations:
        df_locations = pd.DataFrame(locations)
        st.dataframe(df_locations)
    
        try:
            # 预处理翻译文本
            modern_name_popup = t('modern_name_popup')
            total_mentions_popup = t('total_mentions_popup')
            legend_text = t('legend')
            high_frequency_text = t('high_frequency')
            medium_frequency_text = t('medium_frequency')
            low_frequency_text = t('low_frequency')
            
            # =======================================================
            # 关键修复：HTML/JS 字符串中的大括号全部改为 {{ }}
            # 只有 Python 变量才使用单大括号 {}
            # =======================================================
            
            leaflet_map_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
                <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
                <style>
                    html, body {{
                        width: 100%;
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
                    #map {{
                        height: 600px;
                        width: 100%;
                    }}
                    .leaflet-popup-content h4 {{
                        margin-top: 0;
                        color: #333;
                    }}
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([33.35, 118.92], 6);
                    
                    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                        attribution: '&copy; OpenStreetMap contributors',
                        maxZoom: 20
                    }}).addTo(map);
                    
                    L.control.scale().addTo(map);
                    
                    var legend = L.control({{ position: 'topright' }});
                    
                    legend.onAdd = function (map) {{
                        var div = L.DomUtil.create('div', 'info legend');
                        div.style.background = "white";
                        div.style.padding = "10px";
                        div.style.borderRadius = "5px";
                        div.style.boxShadow = "0 0 15px rgba(0,0,0,0.2)";

                        div.innerHTML = '<h4>{legend_text}</h4>' +
                                      '<div style="display: flex; align-items: center; margin-bottom: 5px;">' +
                                      '<div style="width: 20px; height: 20px; border-radius: 50%; background-color: red; margin-right: 5px;"></div>' +
                                      '<span>{high_frequency_text}</span>' +
                                      '</div>' +
                                      '<div style="display: flex; align-items: center; margin-bottom: 5px;">' +
                                      '<div style="width: 20px; height: 20px; border-radius: 50%; background-color: green; margin-right: 5px;"></div>' +
                                      '<span>{medium_frequency_text}</span>' +
                                      '</div>' +
                                      '<div style="display: flex; align-items: center;">' +
                                      '<div style="width: 20px; height: 20px; border-radius: 50%; background-color: blue; margin-right: 5px;"></div>' +
                                      '<span>{low_frequency_text}</span>' +
                                      '</div>';
                        return div;
                    }};
                    
                    legend.addTo(map);
                    
                    var featureGroup = L.featureGroup().addTo(map);
                    
                    var locations = {json.dumps(js_locations, ensure_ascii=False)};
                    
                    locations.forEach(function(loc) {{
                        var radius = Math.max(5, Math.min(loc.count / 5, 20));
                        var color = loc.count > 100 ? 'red' : (loc.count > 30 ? 'green' : 'blue');
                        
                        var circleMarker = L.circleMarker([loc.lat, loc.lng], {{
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.6,
                            radius: radius,
                            weight: 2
                        }}).addTo(featureGroup);
                        
                        var popupContent = '<div>' +
                                            '<h4>' + loc.name + '</h4>' +
                                           '<p><b>{modern_name_popup}</b>' + loc.modern_name + '</p>' +
                                           '<p><b>{total_mentions_popup}</b>' + loc.count + '</p>' +
                                            '</div>';
                        circleMarker.bindPopup(popupContent);
                         
                        circleMarker.bindTooltip(loc.name + ' (' + loc.count + ')', {{
                              sticky: true
                        }});
                        
                        // 文字标签
                        L.marker([loc.lat + 0.05, loc.lng], {{
                            icon: L.divIcon({{
                                html: '<div style="font-size: 10pt; font-weight: bold; color: #333; text-shadow: 1px 1px 0 #fff;">' + loc.name + '</div>',
                                iconSize: [100, 20],
                                iconAnchor: [50, 0],
                                className: 'text-label'
                            }})
                        }}).addTo(featureGroup);
                    }});
                    
                    if(locations.length > 0) {{
                        map.fitBounds(featureGroup.getBounds().pad(0.2));
                    }}
                </script>
            </body>
            </html>
            '''
            
            st.subheader(t("visualization_title", start=start_chapter, end=end_chapter))
            components.html(leaflet_map_html, height=700, scrolling=False)
            
            # 图表说明
            st.markdown(f"""
            <div class="info-box">
            <h5>{t('map_description')}</h5>
            <ul>
                <li>{t('map_desc_point1')}</li>
                <li>{t('map_desc_point2')}</li>
                <li>{t('map_desc_point3')}</li>
                <li>{t('map_desc_point4')}</li>
                <li>{t('map_desc_point5')}</li>
                <li>{t('map_desc_point6')}</li>
                <li>{t('map_desc_point7')}</li>
                <li>{t('map_desc_point8')}</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(t("error_visualization", error=str(e)))
    else:
        st.info(t("no_location_data"))

# 2. 数据概览选项卡
with main_tabs[1]:
    st.header(t("overview_header"))
    
    overview_data = []
    for place in selected_places:
        filtered_count = sum(place_chapter_matrix.get(place, {}).get(ch, 0) for ch in selected_chapters)
        filtered_chapter_count = sum(1 for ch in selected_chapters if place_chapter_matrix.get(place, {}).get(ch, 0) > 0)
        filtered_presence_rate = filtered_chapter_count / len(selected_chapters) if len(selected_chapters) > 0 else 0
        
        overview_data.append({
            t('place'): place,
            t('modern_name'): place_coordinates.get(place, {}).get('modern_name', ''),
            t('total_mentions'): filtered_count,
            t('avg_per_chapter'): filtered_count / len(selected_chapters) if len(selected_chapters) > 0 else 0,
            t('presence_rate'): filtered_presence_rate,
            t('present_chapters'): filtered_chapter_count
        })
    
    if overview_data:
        df_overview = pd.DataFrame(overview_data)
        df_overview = df_overview.sort_values(t('total_mentions'), ascending=False)
        
        # 格式化
        df_overview[t('avg_per_chapter')] = df_overview[t('avg_per_chapter')].round(2)
        df_overview[t('presence_rate')] = (df_overview[t('presence_rate')] * 100).round(1).astype(str) + '%'
        
        st.dataframe(df_overview, use_container_width=True, hide_index=True)
        
        st.subheader(t("frequency_comparison"))
        fig_bar = px.bar(
            df_overview,
            x=t('place'),
            y=t('total_mentions'),
            color=t('place'),
            text_auto=True,
            title=t("frequency_title", start=start_chapter, end=end_chapter),
            labels={t('total_mentions'): t('mention_count')}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # 饼图
        st.subheader(t("distribution_ratio"))
        if df_overview[t('total_mentions')].sum() > 0:
            fig_pie = px.pie(
                df_overview,
                values=t('total_mentions'),
                names=t('place'),
                title=t("distribution_title", start=start_chapter, end=end_chapter),
                hole=0.3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info(t("no_data"))

# 3. 图表分析选项卡
with main_tabs[2]:
    st.header(t("trends_header"))
    
    trend_data = []
    for chapter in selected_chapters:
        for place in selected_places:
            count = place_chapter_matrix.get(place, {}).get(chapter, 0)
            trend_data.append({
                t('chapter'): chapter,
                t('place'): place,
                t('mention_count'): count
            })
    
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        fig_trend = px.line(
            df_trend,
            x=t('chapter'),
            y=t('mention_count'),
            color=t('place'),
            markers=True,
            title=t("trend_title", start=start_chapter, end=end_chapter)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 热力图
        st.subheader(t("heatmap"))
        # 构建矩阵
        heat_matrix = []
        for chapter in selected_chapters:
            row = []
            for place in selected_places:
                row.append(place_chapter_matrix.get(place, {}).get(chapter, 0))
            heat_matrix.append(row)
            
        fig_heat = px.imshow(
            heat_matrix,
            x=selected_places,
            y=[f"第{c}回" for c in selected_chapters],
            labels=dict(x=t("place"), y=t("chapter"), color=t("mention_count")),
            title=t("heatmap_title", start=start_chapter, end=end_chapter)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info(t("no_data"))

# 4. 详细表格选项卡
with main_tabs[3]:
    st.header(t("detailed_table"))
    
    detailed_data = []
    for chapter in selected_chapters:
        row = {
            t('chapter'): chapter,
            t('chapter_title'): chapter_titles.get(chapter, f"第{chapter}回"),
            t('total_places'): sum(place_chapter_matrix.get(place, {}).get(chapter, 0) for place in selected_places)
        }
        for place in selected_places:
            row[place] = place_chapter_matrix.get(place, {}).get(chapter, 0)
        detailed_data.append(row)
    
    if detailed_data:
        df_detailed = pd.DataFrame(detailed_data)
        st.dataframe(df_detailed, use_container_width=True, hide_index=True)
        
        # 导出
        st.subheader(t("data_export"))
        csv_data = df_detailed.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label=t("export_csv"),
            data=csv_data,
            file_name='place_analysis.csv',
            mime='text/csv'
        )
    else:
        st.info(t("no_data"))

# 页脚
st.markdown(f"""
---
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>{t('footer_line1')}</p>
    <p>{t('footer_line2')}</p>
</div>
""", unsafe_allow_html=True)