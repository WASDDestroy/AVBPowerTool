"""
AVB (Android Verified Boot) 信息解析器
"""
from typing import Any, Dict
import os
import Core.ConfigParser as ConfigParser

def load_avb_data(logger) -> Dict[str, Any]:
    """
    加载AVB字典数据
    实际使用时，可以从文件读取或直接使用给定的字典
    """

    my_config_parser = ConfigParser.ConfigParser()
    return my_config_parser.json2_dic()
    
def get_chinese_key_name(key: str) -> str:
    """将英文键名转换为中文"""
    translations = {
        # 通用键名
        "Algorithm": "算法",
        "Descriptor Type": "描述符类型",
        "Hash Algorithm": "哈希算法",
        "Image File": "镜像文件",
        "Image size": "镜像大小(字节)",
        "Partition Name": "分区名称",
        "Props": "属性",
        "Public key (sha1)": "公钥(SHA1)",
        "Public key file": "对应的公钥文件",
        "Rollback Index": "回滚索引",
        "Salt": "盐值",
        "Data Block Size" : "验证数据块的大小",
        
        # 特殊列表类型
        "Chain": "链式验证分区及其回滚指数下标",
        "Chain partition key": "链分区公钥",
        "Hash": "哈希验证分区",
        "Hashtree": "哈希树验证分区",
        "FEC num roots" : "前向纠错数根",
        "FEC offset" : "前向纠错数据偏移量",
        "FEC size" : "前向纠错数据大小",
        "Hash Block Size" : "哈希数据块大小",
        "Root Digest" : "根摘要",
        "Tree Offset" : "哈希树偏移量",
        "Tree Size" : "哈希树大小",
        "Version of dm-verity" : "dm-verity 版本",
        
        # 属性内的键名会被特殊处理，这里不单独定义
    }
    return translations.get(key, key)  # 如果没有翻译，返回原键名

def format_bytes(size_str: str) -> str:
    """将字节大小格式化为更易读的形式"""
    try:
        size = int(size_str)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    except (ValueError, TypeError):
        return size_str

def print_props(props: Dict[str, str], indent: int = 4, simplify = False):
    """格式化打印属性字典，带有适当缩进"""
    if not props:
        print(" " * indent + "└─ (空)")
        return
    
    items = list(props.items())
    for i, (key, value) in enumerate(items):
        # 判断是否是最后一个元素，用于选择合适的连接符号
        is_last = (i == len(items) - 1)
        prefix = "└─ " if is_last else "├─ "
        
        # 简化属性键名显示，提取有用部分
        simplified_key = key
        
        # 继续简化，保持可读性
        if simplify:
            if key.startswith("com.android.build."):
                simplified_key = key.replace("com.android.build.", "")
            elif key.startswith("com.android."):
                simplified_key = key.replace("com.android.", "")
            simplified_key = simplified_key.replace("_fingerprint", "指纹")
            simplified_key = simplified_key.replace("_version", "版本")
            simplified_key = simplified_key.replace("_patch", "补丁")
            simplified_key = simplified_key.replace("security", "安全")
        
        print(" " * indent + prefix + f"{simplified_key}: {value}")

def print_list_value(key: str, value: list, indent: int = 4):
    """打印列表类型的值，每个元素一行"""
    if not value:
        print(" " * indent + f"└─ {key}: (空)")
        return
    
    print(" " * indent + f"├─ {key}:")
    for i, item in enumerate(value):
        is_last = (i == len(value) - 1)
        prefix = "└─ " if is_last else "├─ "
        print(" " * (indent + 4) + prefix + str(item))

def print_partition(partition_name: str, partition_data: Dict[str, Any]):
    """打印单个分区的信息"""
    # 打印分区标题
    print(f"\n【{partition_name.upper()} 分区】")
    print("=" * 60)
    
    # 获取所有键并排序，使输出更一致
    keys = sorted(partition_data.keys())
    
    # 记录是否有Props字段，最后单独处理
    props = partition_data.get("Props", {})
    
    for key in keys:
        if key == "Props":  # Props 最后特殊处理
            continue
            
        value = partition_data[key]
        chinese_key = get_chinese_key_name(key)
        
        # 根据值类型决定输出格式
        if key in ["Chain", "Chain partition key", "Hash", "Hashtree"]:
            # 列表类型
            print_list_value(chinese_key, value)
        elif key == "Image size":
            # 格式化大小
            print(f"{chinese_key}: {value} ({format_bytes(value)})")
        elif isinstance(value, list):
            # 其他列表类型
            print(f"{chinese_key}: {', '.join(map(str, value))}")
        else:
            # 普通键值对
            print(f"{chinese_key}: {value}")
    
    # 最后处理 Props
    if props:
        print(f"{get_chinese_key_name('Props')}:")
        print_props(props, indent=4)
    elif not "vbmeta" in partition_name:
        print(f"{get_chinese_key_name('Props')}: (无)")

def entry(logger):
    """主函数"""
    os.system("cls") if os.name == "nt" else os.system("clear")
    print("=" * 80)
    print("指定配置文件的信息：")
    print("=" * 80)
    
    # 加载数据
    avb_data = load_avb_data(logger)
    
    # 按顺序输出所有分区
    partition_order = [
        "vbmeta", "vbmeta_system", "boot", "init_boot", "vendor_boot",
        "recovery", "dtbo", "pvmfw"
    ]
    
    # 按指定顺序输出
    for partition in partition_order:
        if partition in avb_data:
            print_partition(partition, avb_data[partition])
    
    # 检查是否有未在顺序列表中的分区
    for partition in avb_data:
        if partition not in partition_order:
            print_partition(partition, avb_data[partition])
    
    print("\n" + "=" * 80)
    input("解析完成，按回车键继续")