import os
import sys
import json
import tkinter as tk
import shutil
from tkinter import filedialog, messagebox, END, colorchooser
from mc_saver import MinecraftSaver
from datetime import datetime, timezone
import logging

# ===== 日志配置 =====
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "Vanction Minecraft Archive Viewer-Log.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Vanction Minecraft Archive Viewer")

STYLE = {
    "bg": "#f0f0f0",
    "fg": "black",
    "entry_bg": "white",
    "entry_fg": "black",
    "text_bg": "white",
    "text_fg": "black",
    "button_bg": "#4CAF50",
    "button_fg": "white",
    "label_bg": "#f0f0f0",
    "label_fg": "black"
}

# 加载主题配置
try:
    app_data_dir = os.path.expanduser("~\\.minecraft_archive_viewer")
    theme_path = os.path.join(app_data_dir, "data", "theme", "theme.json")

    with open(theme_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        print("正在加载的主题文件:", os.path.abspath("data/theme.json"))
        STYLE.update(config)
    logger.info(f"主题配置已从 JSON 加载: {config}")
except Exception as e:
    logger.warning(f"找不到主题文件，使用默认主题: {e}")

class MinecraftToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 存档查看器")
        self.root.geometry("1550x830")
        self.root.resizable(True, True)

        # 窗口背景色
        self.root.configure(bg=STYLE['bg'])

        # 标题栏
        title_frame = tk.Frame(root, bg=STYLE['button_bg'])
        self.title_label = tk.Label(
            title_frame,
            text="✨ Minecraft 存档查看器",
            fg=STYLE['button_fg'],
            bg=STYLE['button_bg'],
            font=("微软雅黑", 13)
        )
        self.title_label.pack(pady=5, padx=10, fill=tk.X)
        title_frame.pack(fill=tk.X)

        # 路径输入框
        path_frame = tk.Frame(root, bg=STYLE['bg'])
        self.path_label = tk.Label(
            path_frame,
            text="存档路径:",
            bg=STYLE['label_bg'],
            fg=STYLE['label_fg'],
            font=("微软雅黑", 10)
        )
        self.path_entry = tk.Entry(
            path_frame,
            bg=STYLE['entry_bg'],
            fg=STYLE['entry_fg'],
            font=("微软雅黑", 10)
        )
        self.path_label.pack(side=tk.LEFT, padx=5)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        path_frame.pack(pady=10, fill=tk.X)
        # 显示栏
        show_frame = tk.Frame(root, bg=STYLE['bg'])
        self.show_text = tk.Text(
            show_frame,
            bg=STYLE['text_bg'],
            fg=STYLE['text_fg'],
            state='disabled',  # 设置为只读
            font=("微软雅黑", 10)
        )
        self.show_text_scrollbar = tk.Scrollbar(show_frame)
        self.show_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.show_text.config(yscrollcommand=self.show_text_scrollbar.set)
        self.show_text_scrollbar.config(command=self.show_text.yview)
        self.show_text.pack(fill=tk.BOTH, expand=True)
        show_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 添加选择存档按钮
        self.select_world_btn = tk.Button(
            path_frame,
            text="选择存档",
            command=self.browse_world_path,
            font=("微软雅黑", 10),
            bg=STYLE['button_bg'],
            fg=STYLE['button_fg']
        )

        self.path_label.pack(side=tk.LEFT, padx=5)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.select_world_btn.pack(side=tk.RIGHT, padx=5)  # 放在右侧
        path_frame.pack(pady=10, fill=tk.X)

        # ===== 按钮区域 =====
        self.load_btn = tk.Button(
            root,
            text="加载存档",
            command=self.load_world_info,
            font=("微软雅黑", 12, "bold"),
            bg=STYLE['button_bg'],
            fg=STYLE['button_fg']
        )
        self.load_btn.pack(pady=10, fill=tk.X)

        self.export_btn = tk.Button(
            root,
            text="生成为 JSON",
            command=self.export_to_json,
            font=("微软雅黑", 12, "bold"),
            bg=STYLE['button_bg'],
            fg=STYLE['button_fg']
        )
        self.export_btn.pack(pady=5, fill=tk.X)

        # 主题编辑器
        self.edit_theme_btn = tk.Button(
            root,
            text="编辑主题",
            command=self.open_theme_editor,
            font=("微软雅黑", 12, "bold"),
            bg=STYLE['button_bg'],
            fg=STYLE['button_fg']
        )
        self.edit_theme_btn.pack(pady=5, fill=tk.X)

        # ===== 选择自定义主题按钮 =====
        self.select_custom_theme_btn = tk.Button(
            root,
            text="选择自定义主题",
            command=self.select_custom_theme,
            font=("微软雅黑", 12, "bold"),
            bg=STYLE['button_bg'],
            fg=STYLE['button_fg']
        )
        self.select_custom_theme_btn.pack(pady=5, fill=tk.X)

        # 存储数据
        self.world_info = None
        self.player_pos = None
        self.dimension = None
        self.inventory = []

    def select_custom_theme(self):
        """选择自定义主题文件并重启应用"""
        file_path = filedialog.askopenfilename(
            title="选择主题文件",
            filetypes=[("JSON 文件", "*.json")]
        )
        if not file_path:
            return

        try:
            # 使用用户本地路径作为目标路径（避免写入只读目录）
            app_data_dir = os.path.expanduser("~\\.minecraft_archive_viewer")
            dest_dir = os.path.join(app_data_dir, "data", "theme")
            dest_path = os.path.join(dest_dir, "theme.json")

            # 创建目标目录（如果不存在）
            os.makedirs(dest_dir, exist_ok=True)

            # 复制文件
            shutil.copy(file_path, dest_path)
            logger.info(f"主题文件已复制到: {dest_path}")

            # 弹出提示
            messagebox.showinfo("提示", "主题已设置成功！请重启程序以应用新主题。")

            # 重启程序（可选）
            # python = sys.executable
            # os.execl(python, python, *sys.argv)

        except Exception as e:
            logger.error(f"主题文件复制失败: {e}")
            messagebox.showerror("错误", f"无法复制主题文件: {e}")

    def reload_style(self):
        """从 data/theme/theme.json 中重新加载样式"""
        global STYLE
        theme_path = os.path.join("data", "theme", "theme.json")
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                new_style = json.load(f)
                STYLE.clear()
                STYLE.update(new_style)
                logger.info(f"成功加载新样式: {STYLE}")
        except Exception as e:
            logger.warning(f"加载新样式失败，使用当前样式继续运行: {e}")

    def choose_color(self, key, entry):
        """弹出色彩选择对话框"""
        color_code = colorchooser.askcolor(title=f"选择 {key} 颜色")[1]
        if color_code:
            entry.delete(0, tk.END)
            entry.insert(0, color_code)

    def save_and_apply_theme(self, editor_window):
        """保存并应用新主题"""
        global STYLE

        # 更新 STYLE 字典
        new_style = {key: entry.get() for key, entry in self.theme_fields.items()}

        # 检查是否是合法颜色格式（简单正则检查）
        import re
        hex_color_pattern = re.compile(r"^#([A-Fa-f0-9]{6})$")

        for key, value in new_style.items():
            if not hex_color_pattern.match(value):
                messagebox.showerror("错误", f"{key} 不是一个有效的十六进制颜色代码。")
                return

        # 关闭窗口
        editor_window.destroy()
        messagebox.showinfo("提示", "主题已更新！重启程序可恢复为保存的主题。")

    def save_as_json(self, editor_window):
        try:
            # 获取用户选择的保存路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON 文件", "*.json")],
                title="保存主题为 JSON"
            )
            if not file_path:
                return  # 用户取消

            # 收集当前输入框的值
            new_style = {key: entry.get() for key, entry in self.theme_fields.items()}

            # 写入 JSON 文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(new_style, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("成功", "主题已保存为 JSON 文件！")
            editor_window.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def open_theme_editor(self):
        """打开主题编辑器窗口"""
        translated_names = {
            "bg": "主窗口背景",
            "fg": "主窗口文字",
            "entry_bg": "输入框背景",
            "entry_fg": "输入框文字",
            "text_bg": "显示栏背景",
            "text_fg": "显示栏文字",
            "button_bg": "按钮背景",
            "button_fg": "按钮文字",
            "label_bg": "标签背景",
            "label_fg": "标签文字"
        }

        editor = tk.Toplevel(self.root)
        editor.title("主题编辑器")
        editor.geometry("600x488")
        editor.resizable(False, False)

        # 创建一个主框架并使其居中
        main_frame = tk.Frame(editor)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # 设置列宽自适应并居中
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)  # 输入框列更宽一点
        main_frame.grid_columnconfigure(2, weight=1)

        self.theme_fields = {}
        row = 0

        for key, value in STYLE.items():
            if key == "bg" or key == "fg" or key.endswith("_bg") or key.endswith("_fg"):
                # 使用翻译后的中文字段名
                label = tk.Label(
                    main_frame,
                    text=translated_names.get(key, key),  # ✅ 使用中文翻译
                    anchor="w",
                    bg=STYLE['bg'],
                    fg=STYLE['fg']
                )
                label.grid(row=row, column=0, sticky="ew", padx=5, pady=2)

                entry = tk.Entry(main_frame)
                entry.insert(0, value)
                entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)

                color_btn = tk.Button(
                    main_frame,
                    text="选择颜色",
                    command=lambda k=key, e=entry: self.choose_color(k, e),
                    bg=STYLE['button_bg'],
                    fg=STYLE['button_fg']
                )
                color_btn.grid(row=row, column=2, sticky="ew", padx=5, pady=2)

                self.theme_fields[key] = entry
                row += 1

        # 保存为 JSON 按钮
        save_btn = tk.Button(
            main_frame,
            text="保存为 JSON",
            command=lambda: self.save_as_json(editor),
            bg="#2196F3",
            fg="white"
        )
        save_btn.grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)

        # 恢复默认按钮
        reset_btn = tk.Button(
            main_frame,
            text="恢复默认",
            command=self.reset_to_default_theme,
            bg="#f44336",
            fg="white"
        )
        reset_btn.grid(row=row + 1, column=0, columnspan=3, sticky="ew", pady=5)

    def reset_to_default_theme(self):
        """恢复为默认主题"""
        confirm = messagebox.askyesno("确认", "确定要恢复为默认主题吗？")
        if confirm:
            default_style = {
                "bg": "#f0f0f0",
                "fg": "black",
                "entry_bg": "white",
                "entry_fg": "black",
                "text_bg": "white",
                "text_fg": "black",
                "button_bg": "#4CAF50",
                "button_fg": "white",
                "label_bg": "#f0f0f0",
                "label_fg": "black"
            }
            for key, entry in self.theme_fields.items():
                entry.delete(0, tk.END)
                entry.insert(0, default_style[key])

    def browse_world_path(self):
        """打开文件对话框选择存档路径"""
        world_path = filedialog.askdirectory(title="选择存档目录")
        if world_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, world_path)

    def load_world_info(self):
        """加载世界信息并显示"""
        world_path = self.path_entry.get().strip()
        if not world_path:
            logger.warning("未输入存档路径")
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

        # 构建输出内容
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
        if inventory_info:
            for item in inventory_info:
                slot = item.get('槽位', -1)
                name = item.get('物品ID', '未知').replace('minecraft:', '')
                count = item.get('数量') + 1
                nbt = item.get('NBT')
                formatted_nbt = format_nbt(nbt) if nbt else "无 NBT 数据"
                output += f"  槽位 {slot}: {name} ×{count}\n     └─ NBT: {formatted_nbt}\n"
        else:
            output += "  您的物品栏无内容\n"

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
            filetypes=[("JSON 文件", "*.json")],
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
    val = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
           (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
           (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
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
    elif hasattr(nbt_data, 'py_data'):
        return nbt_to_primitive(nbt_data.py_data, max_depth - 1)
    elif isinstance(nbt_data, dict):
        return {
            nbt_to_primitive(k, max_depth - 1): nbt_to_primitive(v, max_depth - 1)
            for k, v in nbt_data.items()
        }
    elif hasattr(nbt_data, '__iter__') and not isinstance(nbt_data, (str, bytes)):
        return [nbt_to_primitive(item, max_depth - 1) for item in nbt_data]
    else:
        return repr(nbt_data)

def format_nbt(nbt_data):
    """格式化显示 NBT 中的常用字段（如附魔）"""
    logger.debug(f"开始处理 NBT 数据: {nbt_data}")
    if not isinstance(nbt_data, dict):
        return "无 NBT 数据"

    result = []
    display = nbt_data.get('display', {})
    if 'Name' in display:
        result.append(f"名称: '{display['Name']}'")

    enchantments = nbt_data.get('Enchantments', [])
    if enchantments and isinstance(enchantments, list):
        enchantment_list = []
        enchant_name_map = \
        {
            'minecraft:protection': '保护',
            'minecraft:fire_protection': '火焰保护',
            'minecraft:feather_falling': '摔落保护',
            'minecraft:blast_protection': '爆炸保护',
            'minecraft:projectile_protection': '弹射物保护',
            'minecraft:respiration': '水下呼吸',
            'minecraft:aqua_affinity': '水下速掘',
            'minecraft:thorns': '荆棘',
            'minecraft:depth_strider': '深海探索者',
            'minecraft:frost_walker': '冰霜行者',
            'minecraft:binding_curse': '绑定诅咒',
            'minecraft:sharpness': '锋利',
            'minecraft:smite': '亡灵杀手',
            'minecraft:bane_of_arthropods': '节肢杀手',
            'minecraft:knockback': '击退',
            'minecraft:fire_aspect': '火焰附加',
            'minecraft:looting': '抢夺',
            'minecraft:sweeping': '横扫之刃',
            'minecraft:efficiency': '效率',
            'minecraft:silk_touch': '精准采集',
            'minecraft:unbreaking': '耐久',
            'minecraft:fortune': '时运',
            'minecraft:power': '力量',
            'minecraft:punch': '冲击',
            'minecraft:flame': '火矢',
            'minecraft:infinity': '无限',
            'minecraft:luck_of_the_sea': '海之眷顾',
            'minecraft:lure': '饵钓',
            'minecraft:loyalty': '忠诚',
            'minecraft:impaling': '穿刺',
            'minecraft:riptide': '激流',
            'minecraft:channeling': '引雷',
            'minecraft:multishot': '多重射击',
            'minecraft:quick_charge': '快速装填',
            'minecraft:piercing': '穿透',
            'minecraft:vanishing_curse': '消失诅咒',
        }
        for enchant in enchantments:
            if isinstance(enchant, dict):
                enchant_id = enchant.get('id', '未知')
                enchant_level = enchant.get('lvl', 0)
                enchant_id_str = str(enchant_id).lower().replace('minecraft:', '')
                enchant_name = enchant_name_map.get(f'minecraft:{enchant_id_str}', enchant_id_str)
                level_str = roman_numeral(int(enchant_level))
                enchantment_list.append(f"{enchant_name} {level_str}")
        if enchantment_list:
            result.append("附魔: " + ", ".join(enchantment_list))

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
    root.minsize(width=561, height=830)
    app = MinecraftToolGUI(root)
    logger.info("应用启动成功")
    root.mainloop()