import requests
import pandas as pd
from datetime import datetime

def parse_metric_value(line):
    """解析指标值，处理科学计数法"""
    try:
        return float(line.split()[-1])
    except:
        return 0

def parse_traffic_metric(line):
    """解析流量指标，包含维度信息"""
    parts = line.split()
    value = float(parts[-1])
    dimension = parts[-2].split('"')[1]
    target = parts[-2].split('"')[3]
    return value, dimension, target

def parse_prometheus_metric(line):
    """解析Prometheus格式的指标"""
    parts = line.split()
    if '{' in line:
        metric_name = line.split('{')[0]
        labels = line[line.index('{')+1:line.index('}')].split(',')
        label_dict = {}
        for label in labels:
            if '=' in label:
                k, v = label.split('=')
                label_dict[k] = v.strip('"')
        value = float(parts[-1])
        return metric_name, label_dict, value
    else:
        metric_name = parts[0]
        value = float(parts[-1])
        return metric_name, {}, value

def fetch_metrics(base_url):
    """获取所有监控指标"""
    try:
        # 获取V2Ray指标
        v2ray_response = requests.get(f"{base_url}/scrape")
        # 获取Go指标
        go_response = requests.get(f"{base_url}/metrics")
        
        if v2ray_response.status_code != 200 or go_response.status_code != 200:
            return None
        
        metrics = {}
        
        # 处理V2Ray指标
        for line in v2ray_response.text.split('\n'):
            if line.startswith('#') or not line.strip():
                continue
                
            if 'traffic' in line:
                value, dimension, target = parse_traffic_metric(line)
                metric_name = line.split('{')[0]
                metrics[f"{metric_name}_{dimension}_{target}"] = value
            else:
                metric_name = line.split()[0]
                metrics[metric_name] = parse_metric_value(line)
        
        # 处理Go指标
        for line in go_response.text.split('\n'):
            if line.startswith('#') or not line.strip():
                continue
            
            try:
                metric_name, labels, value = parse_prometheus_metric(line)
                if labels:
                    label_str = '_'.join(f"{k}_{v}" for k, v in labels.items())
                    metrics[f"{metric_name}_{label_str}"] = value
                else:
                    metrics[metric_name] = value
            except:
                continue
        
        # 添加时间戳
        metrics['timestamp'] = datetime.now()
        
        return metrics
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return None

def format_bytes(bytes_value):
    """将字节转换为可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} TB"

def format_memory(bytes_value):
    """将内存数值转换为可读格式（MB）"""
    return f"{bytes_value / 1024 / 1024:.2f} MB"
