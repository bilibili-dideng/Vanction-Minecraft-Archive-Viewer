import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, END, simpledialog
from mc_saver import MinecraftSaver
from datetime import datetime, timezone

# ===== 日志系统配置 =====
import logging
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "Vanction Minecraft Archive Viewer---Log.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MinecraftArchiveViewer")

# ===== 默认字体配置 =====
DEFAULT_FONT = ("微软雅黑", 10)
BIG_FONT = ("微软雅黑", 12, "bold")

class MinecraftToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 存档查看器")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        # ===== 标题栏 =====
        title_frame = tk.Frame(root, bg="#4CAF50")
        self.title_label = tk.Label(
            title_frame,
            text="✨ Minecraft 存档查看器",
            fg="white",
            bg="#4CAF50",
            font=BIG_FONT
        )
        self.title_label.pack(pady=5, padx=10, fill=tk.X)
        title_frame.pack(fill=tk.X)

        # ===== 存档路径输入框 =====
        path_frame = tk.Frame(root, bg="#f0f0f0")
        self.path_label = tk.Label(path_frame, text="存档路径:", font=DEFAULT_FONT, bg="#f0f0f0", fg="black")
        self.path_entry = tk.Entry(path_frame, width=50, font=DEFAULT_FONT, bg="white", fg="black")
        self.browse_btn = tk.Button(path_frame, text="选择路径", command=self.browse_path, font=DEFAULT_FONT, bg="#4CAF50", fg="white")
        self.path_label.pack(side=tk.LEFT, padx=5)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        path_frame.pack(pady=10, fill=tk.X)

        # ===== 显示区域 =====
        show_frame = tk.Frame(root, bg="#f0f0f0")
        self.show_text = tk.Text(
            show_frame,
            wrap=tk.WORD,
            height=15,
            width=70,
            font=DEFAULT_FONT,
            bg="white",
            fg="black"
        )
        self.show_text_scrollbar = tk.Scrollbar(show_frame, command=self.show_text.yview)
        self.show_text.config(yscrollcommand=self.show_text_scrollbar.set)
        self.show_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        show_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # ===== 按钮区域 =====
        self.load_btn = tk.Button(
            root,
            text="加载存档",
            command=self.load_world_info,
            font=BIG_FONT,
            bg="#4CAF50",
            fg="white"
        )
        self.load_btn.pack(pady=10, fill=tk.X)

        self.export_btn = tk.Button(
            root,
            text="生成为 JSON",
            command=self.export_to_json,
            font=BIG_FONT,
            bg="#4CAF50",
            fg="white"
        )
        self.export_btn.pack(pady=5, fill=tk.X)

        # ===== 存储数据 =====
        self.world_info = None
        self.player_pos = None
        self.dimension = None
        self.inventory = []

    def browse_path(self):
        """打开文件对话框选择存档路径"""
        logger.debug("打开文件选择对话框")
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            logger.info(f"用户选择了存档路径: {path}")

    def load_world_info(self):
        """加载并显示世界和背包信息"""
        logger.debug("开始加载世界信息")
        world_path = self.path_entry.get().strip()
        if not world_path:
            messagebox.showerror("错误", "请输入存档路径！")
            return

        try:
            saver = MinecraftSaver(world_path)
            self.world_info = saver.get_world_info()
            self.player_pos = saver.get_player_position()
            self.dimension = saver.get_dimension()
            self.inventory = saver.get_player_inventory()
            logger.info("成功获取世界信息、玩家坐标、背包数据")
        except FileNotFoundError:
            logger.error("找不到 level.dat 文件！路径: %s", world_path, exc_info=True)
            messagebox.showerror("错误", "找不到 level.dat 文件！")
            return
        except Exception as e:
            logger.exception("加载世界信息时发生未知错误: %s", e)
            messagebox.showerror("错误", f"发生未知错误：{e}")
            return

        # 转换 NBT 数据为原生结构
        world_info = nbt_to_primitive(self.world_info)
        player_pos = nbt_to_primitive(self.player_pos)
        dimension_info = nbt_to_primitive(self.dimension)
        inventory_info = nbt_to_primitive(self.inventory)

        # 格式化输出
        output = f"✨ 世界名称：{world_info.get('世界名称', '未知')}\n"
        output += "🌍 世界信息：\n"
        output += f"  游戏模式：{world_info.get('游戏模式', '未知')}\n"
        output += f"  出生点坐标：X={world_info['出生点']['x']}, Y={world_info['出生点']['y']}, Z={world_info['出生点']['z']}\n"
        output += f"  世界时间：{format_minecraft_time(world_info.get('世界时间', 0))}（游戏内）\n"
        output += f"  最后保存时间：{format_real_time(world_info.get('最后保存时间', 0))}\n"
        output += f"  世界难度：{world_info.get('世界难度', '未知')}\n"
        output += f"🎮 所在维度：{dimension_info}\n"
        output += "游戏角色坐标：\n"
        output += f"  X={player_pos['x']:.2f}, Y={player_pos['y']:.2f}, Z={player_pos['z']:.2f}\n"

        # 显示背包信息
        output += "\n🎒 玩家背包信息：\n"
        for item in inventory_info:
            slot = item.get('槽位', -1)
            name = item.get('物品ID', '未知').replace('minecraft:', '')
            count = item.get('数量', 0)
            nbt = item.get('NBT')
            formatted_nbt = format_nbt(nbt) if nbt else "无 NBT 数据"
            output += f"  槽位 {slot}: {name} ×{count}\n     └─ NBT: {formatted_nbt}\n"

        # 更新显示内容
        self.show_text.config(state='normal')
        self.show_text.delete(1.0, END)
        self.show_text.insert(END, output)
        self.show_text.config(state='disabled')

    def export_to_json(self):
        """导出为 JSON 文件"""
        logger.debug("开始导出为 JSON")
        if not hasattr(self, 'world_info') or not self.world_info:
            messagebox.showwarning("警告", "请先加载存档后再导出 JSON")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="保存为 JSON 文件"
        )
        if not file_path:
            logger.info("用户取消了导出操作")
            return

        try:
            export_data = {
                "世界信息": self.world_info,
                "玩家位置": self.player_pos,
                "所在维度": self.dimension,
                "玩家背包": self.inventory
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            logger.info(f"数据已保存至：{file_path}")
            messagebox.showinfo("成功", f"数据已保存至：{file_path}")
        except Exception as e:
            logger.exception(f"导出 JSON 时发生错误: {e}")
            messagebox.showerror("错误", f"导出 JSON 时发生错误：{e}")

def format_minecraft_time(tick):
    """将 tick 转换为游戏时间"""
    logger.debug(f"转换世界时间: {tick}")
    try:
        tick = int(tick)
        days = tick // 24000
        remaining = tick % 24000
        hours = remaining // 1000
        minutes = (remaining % 1000) * 60 // 1000
        logger.info(f"世界时间转换结果: {days} 天 {hours} 小时 {minutes} 分钟")
        return f"{days} 天 {hours} 小时 {minutes} 分钟"
    except Exception as e:
        logger.error(f"世界时间转换失败: {e}")
        return "未知时间"

def format_real_time(timestamp_ms):
    """将毫秒时间戳转换为现实时间"""
    logger.debug(f"转换现实时间: {timestamp_ms}")
    try:
        timestamp = int(timestamp_ms) / 1000
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        logger.info(f"现实时间转换结果: {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        return dt.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    except Exception as e:
        logger.error(f"现实时间转换失败: {e}")
        return "时间解析失败"

def roman_numeral(num):
    """将数字转为罗马数字"""
    logger.debug(f"开始转换罗马数字: {num}")
    val = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    res = ''
    num = int(num)
    for value, symbol in val:
        while num >= value:
            res += symbol
            num -= value
    logger.info(f"罗马数字转换结果: {res or 'I'}")
    return res or 'I'

def nbt_to_primitive(nbt_data, max_depth=32):
    """安全将 NBT 数据转换为 Python 原生类型"""
    logger.debug(f"转换 NBT 数据: {repr(nbt_data)}")
    if max_depth <= 0:
        logger.warning("NBT 转换超出最大递归深度")
        return "..."
    if isinstance(nbt_data, (int, float, str)):
        return nbt_data
    elif hasattr(nbt_data, 'py_data'):  # 处理 nbtlib 类型
        return nbt_to_primitive(nbt_data.py_data, max_depth - 1)
    elif isinstance(nbt_data, dict):  # 递归处理字典
        return {
            nbt_to_primitive(k, max_depth - 1): nbt_to_primitive(v, max_depth - 1)
            for k, v in nbt_data.items()
        }
    elif hasattr(nbt_data, '__iter__') and not isinstance(nbt_data, (str, bytes)):  # 处理列表
        return [nbt_to_primitive(item, max_depth - 1) for item in nbt_data]
    else:
        logger.debug(f"未知类型，返回字符串表示: {repr(nbt_data)}")
        return repr(nbt_data)

def format_nbt(nbt_data):
    """格式化显示 NBT 中的常用字段（如附魔）"""
    logger.debug(f"开始处理 NBT 数据: {nbt_data}")
    if not isinstance(nbt_data, dict):
        return "无 NBT 数据"

    result = []

    # 显示物品名称
    display = nbt_data.get('display', {})
    if 'Name' in display:
        result.append(f"名称: '{display['Name']}'")

    # 处理附魔
    enchantments = nbt_data.get('Enchantments', [])
    if enchantments and isinstance(enchantments, list):
        enchant_name_map = {
            'minecraft:sharpness': '锋利',
            'minecraft:sweeping': '横扫之刃',
            'minecraft:unbreaking': '耐久',
            'minecraft:efficiency': '效率',
            'minecraft:fortune': '时运',
            'minecraft:power': '力量',
            'minecraft:punch': '冲击',
            'minecraft:flame': '火矢',
            'minecraft:infinity': '无限',
            'minecraft:protection': '保护',
            'minecraft:fire_protection': '防火',
            'minecraft:feather_falling': '摔落保护',
            'minecraft:blast_protection': '爆炸保护',
            'minecraft:projectile_protection': '投射物保护',
            'minecraft:respiration': '水下呼吸',
            'minecraft:aqua_affinity': '水下速掘',
            'minecraft:thorns': '荆棘',
            'minecraft:depth_strider': '深海探索者',
            'minecraft:frost_walker': '冰霜行者',
            'minecraft:binding_curse': '绑定诅咒',
            'minecraft:vanishing_curse': '消失诅咒',
            'minecraft:lure': '诱饵',
            'minecraft:luck_of_the_sea': '海之眷顾',
            'minecraft:mending': '经验修补',
            'minecraft:soul_speed': '灵魂疾走',
            'minecraft:impaling': '穿刺',
            'minecraft:riptide': '激流',
            'minecraft:channeling': '引雷',
            'minecraft:multishot': '多重射击',
            'minecraft:quick_charge': '快速装填',
            'minecraft:piercing': '穿透',
            'minecraft:loyalty': '忠诚',
            'minecraft:snipe': '狙击弓步',
            'minecraft:blessing': '祝福',
            'minecraft:regality': '王者',
            'minecraft:bane_of_arthropods': '节肢杀手',
            'minecraft:smite': '亡灵杀手'
        }

        enchantment_list = []
        for enchant in enchantments:
            if isinstance(enchant, dict):
                enchant_id = enchant.get('id', '未知')
                enchant_level = enchant.get('lvl', 0)
                # 去除命名空间并翻译附魔名
                enchant_id_str = str(enchant_id).lower().replace('minecraft:', '')
                enchant_name = enchant_name_map.get(f'minecraft:{enchant_id_str}', enchant_id_str)
                level_str = roman_numeral(int(enchant_level))
                enchantment_list.append(f"{enchant_name} {level_str}")
        if enchantment_list:
            result.append("附魔: " + ", ".join(enchantment_list))

    # 显示堆叠数量（Count）
    stack_size = nbt_data.get('Count', None)
    if stack_size is not None:
        result.append(f"数量: {stack_size}")

    return " | ".join(result) if result else "无 NBT 数据"

if __name__ == "__main__":
    root = tk.Tk()
    icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icons", "mc_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
        logger.info(f"图标已加载: {icon_path}")
    root.minsize(width=561, height=633)
    app = MinecraftToolGUI(root)
    logger.info("应用启动成功")
    root.mainloop()