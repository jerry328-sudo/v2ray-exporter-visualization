import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time
from data_fetch import fetch_metrics, format_bytes, format_memory

# 使用缓存来优化数据获取
@st.cache_data(ttl=1)  # 1秒的缓存时间
def get_cached_metrics(api_url):
    return fetch_metrics(api_url)

# 页面配置
st.set_page_config(
    page_title="V2Ray 监控面板",
    page_icon="📊",
    layout="wide"
)

# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame()

# 读取保存的API地址
def load_api_url():
    try:
        with open('api.txt', 'r') as f:
            return f.read().strip()
    except:
        return "http://localhost:9550"

def save_api_url(url):
    with open('api.txt', 'w') as f:
        f.write(url)

# 侧边栏配置
st.sidebar.title("⚙️ 配置")
api_base_url = st.sidebar.text_input(
    "API地址",
    value=load_api_url(),
    help="V2Ray API的基础地址，例如：http://localhost:9550"
)

# 当API地址改变时保存
if 'last_api_url' not in st.session_state:
    st.session_state.last_api_url = api_base_url

if st.session_state.last_api_url != api_base_url:
    save_api_url(api_base_url)
    st.session_state.last_api_url = api_base_url
auto_refresh = st.sidebar.checkbox('自动刷新', value=True)
refresh_interval = st.sidebar.slider(
    '刷新间隔 (秒)',
    min_value=1,
    max_value=60,
    value=5
)

# 页面标题
st.title("📊 V2Ray 监控面板")

# 保存配置到session_state
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = api_base_url

if st.session_state.api_base_url != api_base_url:
    st.session_state.api_base_url = api_base_url
    st.session_state.history = pd.DataFrame()

# 创建占位符
metrics_placeholder = st.empty()
charts_placeholder = st.empty()
details_placeholder = st.empty()

# 更新数据和显示
def update_display():
    metrics = get_cached_metrics(api_base_url)
    if metrics:
        new_data = pd.DataFrame([metrics])
        if st.session_state.history.empty:
            st.session_state.history = new_data
        else:
            st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
            # 只保留最近30分钟的数据
            cutoff_time = datetime.now() - timedelta(minutes=30)
            st.session_state.history = st.session_state.history[
                st.session_state.history['timestamp'] > cutoff_time
            ]
        
        # 使用占位符更新指标
        with metrics_placeholder.container():
            # 创建四列布局
            col1, col2, col3, col4 = st.columns(4)
            
            # 第一列：系统状态
            with col1:
                st.metric(
                    label="系统状态",
                    value="正常运行" if metrics['v2ray_up'] == 1 else "异常",
                    delta=f"运行时间: {metrics['v2ray_uptime_seconds'] / 3600:.1f} 小时"
                )

            # 第二列：内存使用
            with col2:
                st.metric(
                    label="内存使用",
                    value=format_memory(metrics['v2ray_memstats_alloc_bytes']),
                    delta=f"系统分配: {format_memory(metrics['v2ray_memstats_sys_bytes'])}"
                )

            # 第三列：Goroutines
            with col3:
                st.metric(
                    label="Goroutines 数量",
                    value=int(metrics['go_goroutines']),
                    delta=f"线程数: {int(metrics['go_threads'])}"
                )

            # 第四列：CPU使用
            with col4:
                st.metric(
                    label="CPU 使用时间",
                    value=f"{metrics['process_cpu_seconds_total']:.2f}s",
                    delta=f"GC CPU占用: {metrics['go_memstats_gc_cpu_fraction']:.2%}"
                )

        # 使用占位符更新图表
        with charts_placeholder.container():
            row1, row2 = st.columns(2)
            
            # 内存使用趋势图
            with row1:
                st.subheader("内存使用趋势")
                if not st.session_state.history.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=st.session_state.history['timestamp'],
                        y=st.session_state.history['go_memstats_heap_alloc_bytes'],
                        name="堆内存使用",
                        line=dict(color="blue")
                    ))
                    fig.add_trace(go.Scatter(
                        x=st.session_state.history['timestamp'],
                        y=st.session_state.history['go_memstats_heap_sys_bytes'],
                        name="系统分配",
                        line=dict(color="red")
                    ))
                    fig.update_layout(
                        title="内存使用趋势",
                        xaxis_title="时间",
                        yaxis_title="内存使用 (bytes)"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 流量监控图
            with row2:
                st.subheader("流量监控")
                if not st.session_state.history.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=st.session_state.history['timestamp'],
                        y=st.session_state.history['v2ray_traffic_uplink_bytes_total_inbound_api'],
                        name="上行流量",
                        line=dict(color="blue")
                    ))
                    fig.add_trace(go.Scatter(
                        x=st.session_state.history['timestamp'],
                        y=st.session_state.history['v2ray_traffic_downlink_bytes_total_inbound_api'],
                        name="下行流量",
                        line=dict(color="red")
                    ))
                    fig.update_layout(
                        title="流量统计",
                        xaxis_title="时间",
                        yaxis_title="流量 (bytes)"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # 使用占位符更新系统详细指标
        with details_placeholder.container():
            st.subheader("系统详细指标")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
            with metrics_col1:
                st.info("内存统计")
                st.write(f"🔸 堆对象数量: {int(metrics['go_memstats_heap_objects']):,}")
                st.write(f"🔸 下次GC阈值: {format_memory(metrics['go_memstats_next_gc_bytes'])}")
                st.write(f"🔸 栈内存使用: {format_memory(metrics['go_memstats_stack_inuse_bytes'])}")

            with metrics_col2:
                st.info("GC统计")
                st.write(f"🔸 GC暂停总时间: {metrics['go_gc_duration_seconds_sum']:.3f}s")
                st.write(f"🔸 GC次数: {int(metrics.get('go_gc_duration_seconds_count', 0))}")
                st.write(f"🔸 最后GC时间: {datetime.fromtimestamp(metrics['go_memstats_last_gc_time_seconds']).strftime('%H:%M:%S') if metrics['go_memstats_last_gc_time_seconds'] > 0 else '无'}")

            with metrics_col3:
                st.info("系统资源")
                st.write(f"🔸 进程内存占用: {format_memory(metrics['process_resident_memory_bytes'])}")
                st.write(f"🔸 打开文件数: {int(metrics['process_open_fds'])}")
                st.write(f"🔸 最大文件句柄: {int(metrics['process_max_fds']):,}")

    else:
        with metrics_placeholder.container():
            st.error("无法获取监控数据，请检查 V2Ray 服务是否正常运行")

# 主循环
while True:
    update_display()
    if not auto_refresh:
        break
    time.sleep(refresh_interval)
