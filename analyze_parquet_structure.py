#!/usr/bin/env python3
"""
GraphRAG Parquet文件结构分析脚本

该脚本用于分析GraphRAG生成的所有parquet文件的结构，
包括字段名称、数据类型、样本数据等信息。

作者: AI Assistant
日期: 2025-06-27
"""

import pandas as pd
import os
import json
from pathlib import Path
from typing import Dict, List, Any
import pyarrow.parquet as pq


def analyze_parquet_file(file_path: str) -> Dict[str, Any]:
    """
    分析单个parquet文件的结构
    
    Args:
        file_path: parquet文件路径
        
    Returns:
        包含文件分析结果的字典
    """
    try:
        # 读取parquet文件
        df = pd.read_parquet(file_path)
        
        # 获取基本信息
        file_info = {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {}
        }
        
        # 分析每个列
        for col in df.columns:
            col_info = {
                "data_type": str(df[col].dtype),
                "null_count": df[col].isnull().sum(),
                "null_percentage": round((df[col].isnull().sum() / len(df)) * 100, 2),
                "sample_values": []
            }

            # 安全地计算唯一值数量
            try:
                col_info["unique_count"] = df[col].nunique()
            except Exception:
                col_info["unique_count"] = "Cannot calculate (complex data type)"
            
            # 获取样本值（非空值）
            try:
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    sample_size = min(5, len(non_null_values))
                    # 处理可能的数组类型数据
                    sample_values = []
                    for val in non_null_values.head(sample_size):
                        if isinstance(val, (list, tuple, set)):
                            sample_values.append(f"[Array with {len(val)} items]")
                        elif hasattr(val, '__array__'):  # numpy数组
                            sample_values.append(f"[Array with {len(val)} items]")
                        else:
                            sample_values.append(str(val)[:100])  # 限制字符串长度
                    col_info["sample_values"] = sample_values
            except Exception as e:
                col_info["sample_values"] = [f"Error getting samples: {str(e)}"]
            
            # 对于数值类型，添加统计信息
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                col_info["statistics"] = {
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": round(df[col].mean(), 4) if not df[col].isnull().all() else None,
                    "std": round(df[col].std(), 4) if not df[col].isnull().all() else None
                }
            
            file_info["columns"][col] = col_info
        
        return file_info
        
    except Exception as e:
        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "error": str(e)
        }


def find_parquet_files(directory: str) -> List[str]:
    """
    在指定目录中查找所有parquet文件
    
    Args:
        directory: 搜索目录
        
    Returns:
        parquet文件路径列表
    """
    parquet_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.parquet'):
                parquet_files.append(os.path.join(root, file))
    return parquet_files


def generate_analysis_report(analysis_results: List[Dict[str, Any]]) -> str:
    """
    生成分析报告
    
    Args:
        analysis_results: 分析结果列表
        
    Returns:
        格式化的分析报告字符串
    """
    report = []
    report.append("=" * 80)
    report.append("GraphRAG Parquet文件结构分析报告")
    report.append("=" * 80)
    report.append(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析文件数量: {len(analysis_results)}")
    report.append("")
    
    # 总览
    total_size = sum(result.get("file_size_mb", 0) for result in analysis_results if "error" not in result)
    total_rows = sum(result.get("row_count", 0) for result in analysis_results if "error" not in result)
    
    report.append("📊 总览统计")
    report.append("-" * 40)
    report.append(f"总文件大小: {total_size:.2f} MB")
    report.append(f"总记录数: {total_rows:,}")
    report.append("")
    
    # 详细分析每个文件
    for result in analysis_results:
        if "error" in result:
            report.append(f"❌ 错误文件: {result['file_name']}")
            report.append(f"   错误信息: {result['error']}")
            report.append("")
            continue
            
        report.append(f"📁 文件: {result['file_name']}")
        report.append("-" * 60)
        report.append(f"路径: {result['file_path']}")
        report.append(f"大小: {result['file_size_mb']} MB")
        report.append(f"行数: {result['row_count']:,}")
        report.append(f"列数: {result['column_count']}")
        report.append("")
        
        # 列信息
        report.append("📋 列信息:")
        for col_name, col_info in result["columns"].items():
            report.append(f"  • {col_name}")
            report.append(f"    类型: {col_info['data_type']}")
            report.append(f"    空值: {col_info['null_count']} ({col_info['null_percentage']}%)")
            report.append(f"    唯一值: {col_info['unique_count']}")
            
            if col_info["sample_values"]:
                sample_str = ", ".join(str(v)[:50] for v in col_info["sample_values"])
                report.append(f"    样本: {sample_str}")
            
            if "statistics" in col_info and col_info["statistics"]:
                stats = col_info["statistics"]
                report.append(f"    统计: min={stats['min']}, max={stats['max']}, mean={stats['mean']}")
            
            report.append("")
        
        report.append("")
    
    return "\n".join(report)


def main():
    """主函数"""
    print("🔍 开始分析GraphRAG Parquet文件结构...")
    
    # 查找output目录中的所有parquet文件
    output_dir = "output"
    if not os.path.exists(output_dir):
        print(f"❌ 错误: 找不到输出目录 '{output_dir}'")
        return
    
    parquet_files = find_parquet_files(output_dir)
    
    if not parquet_files:
        print(f"❌ 在目录 '{output_dir}' 中未找到parquet文件")
        return
    
    print(f"📂 找到 {len(parquet_files)} 个parquet文件:")
    for file in parquet_files:
        print(f"  - {file}")
    print("")
    
    # 分析每个文件
    analysis_results = []
    for file_path in parquet_files:
        print(f"🔍 分析文件: {os.path.basename(file_path)}")
        result = analyze_parquet_file(file_path)
        analysis_results.append(result)
    
    # 生成报告
    report = generate_analysis_report(analysis_results)
    
    # 保存报告到文件
    report_file = "parquet_analysis_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 保存JSON格式的详细数据
    json_file = "parquet_analysis_data.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print("✅ 分析完成!")
    print(f"📄 报告已保存到: {report_file}")
    print(f"📊 详细数据已保存到: {json_file}")
    print("")
    print("📋 分析摘要:")
    print("-" * 40)
    
    # 显示关键信息
    for result in analysis_results:
        if "error" not in result:
            print(f"{result['file_name']}: {result['row_count']:,} 行, {result['column_count']} 列")
            if result['file_name'] in ['relationships.parquet', 'relationships_with_types.parquet']:
                print(f"  关系文件列名: {list(result['columns'].keys())}")
    
    print("")
    print("🎯 重点关注:")
    print("- entities.parquet: 实体数据（用于生成节点）")
    print("- relationships.parquet: 关系数据（用于生成边）")
    print("- relationships_with_types.parquet: 带类型的关系数据")
    print("- communities.parquet: 社区数据（用于节点分组）")


if __name__ == "__main__":
    main()
