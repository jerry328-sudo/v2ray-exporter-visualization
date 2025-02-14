# V2Ray 监控面板

## 简介
这是一个用于监控V2Ray服务器性能指标的可视化面板，支持实时数据更新和历史数据趋势分析。

## 功能特点
- 实时监控V2Ray运行状态
- 可视化展示系统资源使用情况
- 支持自定义API地址和刷新间隔
- 保留30分钟历史数据用于趋势分析

## 快速开始
1. 双击运行 `run.bat`
2. 在浏览器中访问 http://localhost:8501
3. 在侧边栏配置API地址（默认为 http://localhost:9550）
   - API地址会自动保存在 api.txt 文件中
   - 下次启动时会自动读取上次配置的地址
   - 可以随时修改，修改后会立即生效并保存

## 监控指标说明

### V2Ray 核心指标

#### 系统状态
- `v2ray_up`: V2Ray运行状态（1表示正常，0表示异常）
- `v2ray_uptime_seconds`: V2Ray运行时间（秒）

#### 流量统计
- `v2ray_traffic_uplink_bytes_total`: 上行流量总字节数
- `v2ray_traffic_downlink_bytes_total`: 下行流量总字节数

### Go运行时指标

#### 内存相关
- `go_memstats_alloc_bytes`: 当前使用的堆内存字节数
- `go_memstats_sys_bytes`: 从系统获取的内存总字节数
- `go_memstats_heap_alloc_bytes`: 堆内存分配字节数
- `go_memstats_heap_idle_bytes`: 空闲堆内存字节数
- `go_memstats_heap_inuse_bytes`: 正在使用的堆内存字节数
- `go_memstats_heap_objects`: 堆对象数量
- `go_memstats_heap_released_bytes`: 释放回操作系统的堆内存字节数
- `go_memstats_stack_inuse_bytes`: 正在使用的栈内存字节数

#### 垃圾回收（GC）
- `go_gc_duration_seconds`: GC暂停时间统计
  - `sum`: GC暂停总时间
  - `count`: GC执行次数
- `go_memstats_gc_cpu_fraction`: GC占用CPU时间比例
- `go_memstats_next_gc_bytes`: 下次触发GC的堆内存阈值
- `go_memstats_last_gc_time_seconds`: 上次GC的时间戳

#### 系统资源
- `go_goroutines`: 当前goroutine数量
- `go_threads`: 当前系统线程数
- `process_cpu_seconds_total`: 进程占用的CPU时间（秒）
- `process_resident_memory_bytes`: 进程占用的物理内存
- `process_virtual_memory_bytes`: 进程占用的虚拟内存
- `process_open_fds`: 当前打开的文件描述符数量
- `process_max_fds`: 最大允许的文件描述符数量

### 面板配置选项

#### 侧边栏设置
- **API地址**: 设置V2Ray API的基础URL
- **自动刷新**: 启用/禁用自动数据更新
- **刷新间隔**: 设置数据更新频率（1-60秒）

## 图表说明

### 内存使用趋势
- 蓝线：堆内存使用量
- 红线：系统分配的内存量

### 流量监控
- 蓝线：上行流量
- 红线：下行流量

## 注意事项
1. 确保V2Ray服务已启动并开启了Metrics API
2. 默认保留30分钟的历史数据
3. 如遇到连接问题，请检查API地址配置是否正确
4. 建议根据服务器性能调整刷新间隔，避免频繁请求导致性能问题

## 技术栈
- Python 3.x
- Streamlit
- Plotly
- Pandas
- Requests
