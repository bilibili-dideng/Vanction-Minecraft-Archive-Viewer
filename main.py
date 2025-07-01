import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, END, simpledialog
from mc_saver import MinecraftSaver
from datetime import datetime, timezone

# 主题配置
# 默认主题（不要修改）
DEFAULT_THEMES = {
    'light': {
        'bg': '#f0f0f0',
        'fg': 'black',
        'entry_bg': 'white',
        'text_bg': 'white',
        'text_fg': 'black',
        'button_bg': '#4CAF50',
        'button_fg': 'white',
        'label_bg': '#f0f0f0'
    },
    'dark': {
        'bg': '#2d2d2d',
        'fg': 'white',
        'entry_bg': '#1e1e1e',
        'text_bg': '#1e1e1e',
        'text_fg': 'white',
        'button_bg': '#3a3a3a',
        'button_fg': 'white',
        'label_bg': '#2d2d2d'
    },
    'redstone': {
        'bg': '#2b0f0f',
        'fg': 'white',
        'entry_bg': '#4a1d1d',
        'text_bg': '#4a1d1d',
        'text_fg': 'white',
        'button_bg': '#8B0000',
        'button_fg': 'white',
        'label_bg': '#2b0f0f'
    },
    'nether': {
        'bg': '#1c1c2e',
        'fg': 'white',
        'entry_bg': '#2e2e4a',
        'text_bg': '#2e2e4a',
        'text_fg': 'white',
        'button_bg': '#cc6600',
        'button_fg': 'white',
        'label_bg': '#1c1c2e'
    },
    'end': {
        'bg': '#2d003a',
        'fg': 'white',
        'entry_bg': '#4a2a5a',
        'text_bg': '#4a2a5a',
        'text_fg': 'white',
        'button_bg': '#6a0dad',
        'button_fg': 'white',
        'label_bg': '#2d003a'
    }
}

# 可变的主题池，包含默认 + 自定义主题
THEMES = DEFAULT_THEMES.copy()

DEFAULT_FONT = ("微软雅黑", 10)
BIG_FONT = ("微软雅黑", 12, "bold")


class MinecraftToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 存档查看器")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)
        # 初始化主题
        self.current_theme = self.load_theme()

        # 标题栏
        title_frame = tk.Frame(root, bg=THEMES[self.current_theme]['button_bg'])
        self.title_label = tk.Label(
            title_frame,
            text="✨ Minecraft 存档查看器",
            fg=THEMES[self.current_theme]['button_fg'],
            bg=THEMES[self.current_theme]['button_bg'],
            font=BIG_FONT
        )
        self.title_label.pack(pady=5, padx=10, fill=tk.X)
        title_frame.pack(fill=tk.X)
        # 存档路径输入框
        path_frame = tk.Frame(root, bg=THEMES[self.current_theme]['bg'])
        self.path_label = tk.Label(path_frame, text="存档路径:", font=DEFAULT_FONT,
                                   bg=THEMES[self.current_theme]['label_bg'], fg=THEMES[self.current_theme]['fg'])
        self.path_entry = tk.Entry(path_frame, width=50, font=DEFAULT_FONT, bg=THEMES[self.current_theme]['entry_bg'],
                                   fg=THEMES[self.current_theme]['fg'])
        self.browse_btn = tk.Button(
            path_frame,
            text="选择路径",
            command=self.browse_path,
            font=DEFAULT_FONT,
            bg=THEMES[self.current_theme]['button_bg'],
            fg=THEMES[self.current_theme]['button_fg']
        )
        self.path_label.pack(side=tk.LEFT, padx=5)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        path_frame.pack(pady=10, fill=tk.X)
        # 显示区域
        show_frame = tk.Frame(root, bg=THEMES[self.current_theme]['bg'])
        self.show_text = tk.Text(
            show_frame,
            wrap=tk.WORD,
            height=15,
            width=70,
            font=DEFAULT_FONT,
            bg=THEMES[self.current_theme]['text_bg'],
            fg=THEMES[self.current_theme]['text_fg']
        )
        self.show_text_scrollbar = tk.Scrollbar(show_frame, command=self.show_text.yview)
        self.show_text.config(yscrollcommand=self.show_text_scrollbar.set)
        self.show_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        show_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        # 加载按钮
        self.load_btn = tk.Button(
            root,
            text="加载存档",
            command=self.load_world_info,
            font=BIG_FONT,
            bg=THEMES[self.current_theme]['button_bg'],
            fg=THEMES[self.current_theme]['button_fg']
        )
        self.load_btn.pack(pady=10, fill=tk.X)
        # 导出 JSON 按钮
        self.export_btn = tk.Button(
            root,
            text="生成为 JSON",
            command=self.export_to_json,
            font=BIG_FONT,
            bg=THEMES[self.current_theme]['button_bg'],
            fg=THEMES[self.current_theme]['button_fg']
        )
        self.export_btn.pack(pady=5, fill=tk.X)
        # 添加主题编辑器按钮
        self.edit_theme_btn = tk.Button(
            root,
            text="编辑主题",
            command=lambda: ThemeEditor(root, self),
            font=BIG_FONT,
            bg=THEMES[self.current_theme]['button_bg'],
            fg=THEMES[self.current_theme]['button_fg']
        )
        self.edit_theme_btn.pack(pady=5, fill=tk.X)
        # 主题下拉菜单
        self.theme_var = tk.StringVar(root)
        self.theme_var.set(self.current_theme)  # 默认选中当前主题
        theme_options = list(THEMES.keys())
        self.theme_menu = tk.OptionMenu(
            root, self.theme_var, *theme_options, command=self.change_theme
        )
        self.theme_menu.pack(pady=5, fill=tk.X)
        # 存储当前世界信息
        self.world_info = None
        self.player_pos = None
        # 应用初始主题
        self.apply_theme(self.current_theme)

    def load_theme(self):
        """从 theme.json 加载主题和所有主题配置"""
        try:
            with open("theme.json", "r") as f:
                data = json.load(f)
                custom_themes = data.get("themes", {})
                current_theme = data.get("theme", "light")

                # 合并默认主题 + 自定义主题，防止默认主题丢失
                THEMES.clear()
                THEMES.update(DEFAULT_THEMES)
                THEMES.update(custom_themes)

                return current_theme
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或解析失败，恢复默认主题
            THEMES.clear()
            THEMES.update(DEFAULT_THEMES)
            return "light"
    def save_theme(self, theme):
        """保存主题和所有主题配置到 theme.json"""
        with open("theme.json", "w") as f:
            json.dump({
                "theme": theme,
                "themes": THEMES
            }, f, indent=4)

    def change_theme(self, theme_name):
        """根据用户选择应用主题"""
        if theme_name not in THEMES:
            return
        self.apply_theme(theme_name)
        messagebox.showinfo("提示","请重启应用以刷新主题")

    def apply_theme(self, theme_name):
        """应用指定主题"""
        theme = THEMES[theme_name]
        # 更新窗口背景
        self.root.configure(bg=theme['bg'])
        # 更新标题栏
        self.title_label.config(bg=theme['button_bg'], fg=theme['button_fg'])
        # 更新标签
        self.path_label.config(bg=theme['label_bg'], fg=theme['fg'])
        # 更新滚动条（可选）
        self.show_text_scrollbar.config(
            bg=theme['bg'],
            activebackground=theme['button_bg'],
            troughcolor=theme['bg']
        )
        # 更新 OptionMenu 样式
        self.theme_menu.config(
            bg=theme['button_bg'],  # 背景色
            fg=theme['button_fg'],  # 前景色
            activebackground=theme['button_bg'],  # 激活时的背景色
            activeforeground=theme['button_fg']  # 激活时的前景色

        )
        # 更新下拉菜单的样式
        menu = self.theme_menu["menu"]
        menu.config(
            bg=theme['button_bg'],  # 下拉菜单的背景色
            fg=theme['button_fg'],  # 下拉菜单的文字颜色
            activebackground=theme['button_bg'],  # 选中项的背景色
            activeforeground=theme['button_fg']  # 选中项的文字颜色
        )
        # 更新按钮文字
        self.current_theme = theme_name
        self.save_theme(theme_name)

    def browse_path(self):
        """打开文件对话框选择存档路径"""
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def load_world_info(self):
        """加载并显示世界信息"""
        world_path = self.path_entry.get().strip()
        if not world_path:
            messagebox.showerror("错误", "请输入存档路径！")
            return
        try:
            saver = MinecraftSaver(world_path)
            self.world_info = saver.get_world_info()
            self.player_pos = saver.get_player_position()
        except FileNotFoundError:
            messagebox.showerror("错误", "找不到 level.dat 文件！")
            return
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误：{e}")
            return
        # 转换 NBT 数据为原生类型
        world_info = nbt_to_primitive(self.world_info)
        player_pos = nbt_to_primitive(self.player_pos)
        # 格式化输出
        output = f"✨ 世界名称：{world_info.get('世界名称', '未知')}\n"
        output += "🌍 世界信息：\n"
        output += f"  游戏模式：{world_info.get('游戏模式', '未知')}\n"
        output += f"  出生点坐标：X={world_info['出生点']['x']}, Y={world_info['出生点']['y']}, Z={world_info['出生点']['z']}\n"
        output += f"  世界时间：{format_minecraft_time(world_info.get('世界时间', 0))}（游戏内）\n"
        output += f"  最后保存时间：{format_real_time(world_info.get('最后保存时间', 0))}\n"
        output += f"  世界难度：{world_info.get('世界难度', '未知')}\n"
        output += "游戏角色坐标：\n"
        output += f"  X={player_pos['x']:.2f}, Y={player_pos['y']:.2f}, Z={player_pos['z']:.2f}"
        # 清空并插入新内容
        self.show_text.config(state='normal')
        self.show_text.delete(1.0, END)
        self.show_text.insert(END, output)
        self.show_text.config(state='disabled')

    def export_to_json(self):
        """导出为 JSON 文件"""
        if not hasattr(self, 'world_info') or not self.world_info:
            messagebox.showwarning("警告", "请先加载存档后再导出 JSON")
            return
        # 弹出保存对话框
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="保存为 JSON 文件"
        )
        if not file_path:
            return  # 用户取消保存
        try:
            export_data = {
                "世界信息": self.world_info,
                "玩家位置": self.player_pos
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", f"数据已保存至：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出 JSON 时发生错误：{e}")


def format_minecraft_time(tick):
    """将 tick 转换为游戏时间"""
    try:
        tick = int(tick)
        days = tick // 24000
        remaining = tick % 24000
        hours = remaining // 1000
        minutes = (remaining % 1000) * 60 // 1000
        return f"{days} 天 {hours} 小时 {minutes} 分钟"
    except:
        return "未知时间"


def format_real_time(timestamp_ms):
    """将毫秒时间戳转换为现实时间"""
    try:
        timestamp = int(timestamp_ms) / 1000
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    except:
        return "时间解析失败"


def nbt_to_primitive(nbt_data):
    """将 NBT 数据转换为原生类型"""
    if isinstance(nbt_data, (int, float, str)):
        return nbt_data
    elif isinstance(nbt_data, dict):
        return {k: nbt_to_primitive(v) for k, v in nbt_data.items()}
    elif hasattr(nbt_data, '__len__'):
        return [nbt_to_primitive(item) for item in nbt_data]
    elif 'nbtlib' in str(type(nbt_data)):
        return int(nbt_data)
    else:
        return repr(nbt_data)

# ====== 主题编辑器模块 ======
class ThemeEditor:
    def __init__(self, parent, gui):
        self.parent = parent
        self.gui = gui
        self.editor_window = tk.Toplevel(parent)
        self.editor_window.title("主题编辑器")
        self.editor_window.geometry("500x600")
        self.editor_window.resizable(False, False)

        # 当前编辑的主题数据
        self.current_theme_data = THEMES[gui.current_theme].copy()

        # 主题名称输入
        name_frame = tk.Frame(self.editor_window)
        tk.Label(name_frame, text="主题名称:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=gui.current_theme)
        self.name_entry = tk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name_frame.pack(fill=tk.X, padx=10, pady=5)

        # 颜色选项
        self.color_vars = {}
        color_options = [
            ('背景', 'bg'),
            ('文字', 'fg'),
            ('输入框背景', 'entry_bg'),
            ('文本区域背景', 'text_bg'),
            ('文本文字', 'text_fg'),
            ('按钮背景', 'button_bg'),
            ('按钮文字', 'button_fg'),
            ('标签背景', 'label_bg')
        ]

        for label, key in color_options:
            frame = tk.Frame(self.editor_window)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar(value=self.current_theme_data[key])
            entry = tk.Entry(frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="选择颜色", command=lambda v=var: self.choose_color(v)).pack(side=tk.LEFT)
            frame.pack(fill=tk.X, padx=10, pady=2)
            self.color_vars[key] = var

        # 按钮区域
        btn_frame = tk.Frame(self.editor_window)
        tk.Button(btn_frame, text="保存主题", command=self.save_theme).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="加载主题", command=self.load_theme).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="删除主题", command=self.delete_theme).pack(side=tk.LEFT, expand=True, fill=tk.X)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

    def delete_theme(self):
        """删除当前选择的主题"""
        theme_name = self.name_var.get().strip()
        if not theme_name:
            messagebox.showerror("错误", "请输入有效的主题名称！")
            return

        # 判断是否为内置主题
        built_in_themes = ['light', 'dark', 'redstone', 'nether', 'end']
        if theme_name in built_in_themes:
            messagebox.showwarning("警告", f"「{theme_name}」是内置主题，不能删除！")
            return

        if theme_name not in THEMES:
            messagebox.showwarning("警告", f"未找到主题：{theme_name}")
            return

        # 确认删除
        confirm = messagebox.askyesno("确认删除", f"确定要删除主题 '{theme_name}' 吗？")
        if not confirm:
            return

        del THEMES[theme_name]
        self.save_all_themes()  # 保存更新后的主题列表
        messagebox.showinfo("成功", f"主题 '{theme_name}' 已删除。")

        # 自动切换到 light 主题
        self.gui.apply_theme("light")
        self.update_theme_menu()

        # 关闭窗口或刷新界面
        self.editor_window.destroy()
    def choose_color(self, var):
        """选择颜色"""
        from tkinter import colorchooser
        color_code = colorchooser.askcolor(title="选择颜色")[1]
        if color_code:
            var.set(color_code)

    def save_all_themes(self):
        """将所有主题保存到 theme.json"""
        with open("theme.json", "w") as f:
            json.dump({
                "theme": self.gui.current_theme,
                "themes": THEMES
            }, f, indent=4)

    def save_theme(self):
        """保存当前设置为主题"""
        theme_name = self.name_var.get().strip()
        if not theme_name:
            messagebox.showerror("错误", "请输入主题名称！")
            return

        built_in_themes = list(DEFAULT_THEMES.keys())
        if theme_name in built_in_themes:
            messagebox.showwarning("警告", f"「{theme_name}」是内置主题，不能覆盖！请换一个名字保存。")
            return

        new_colors = {key: var.get() for key, var in self.color_vars.items()}
        THEMES[theme_name] = new_colors
        self.gui.apply_theme(theme_name)
        self.gui.save_theme(theme_name)  # 保存到 theme.json
        messagebox.showinfo("成功", f"主题 '{theme_name}' 已保存并应用！")
        self.update_theme_menu()


    def load_theme(self):
        """从现有主题中选择一个加载"""
        theme_list = list(THEMES.keys())
        selected = simpledialog.askstring("加载主题", "请选择要加载的主题名:\n" + ", ".join(theme_list))
        if selected and selected in THEMES:
            self.current_theme_data = THEMES[selected].copy()
            for key, var in self.color_vars.items():
                var.set(self.current_theme_data[key])
            self.name_var.set(selected)

    def update_theme_menu(self):
        """更新主界面的主题下拉菜单"""
        menu = self.gui.theme_menu["menu"]
        menu.delete(0, "end")
        for theme in THEMES:
            menu.add_command(
                label=theme,
                command=lambda t=theme: self.gui.change_theme(t)
            )
        messagebox.showinfo("提示","请重启应用以刷新主题")
if __name__ == "__main__":
    root = tk.Tk()
    # 设置图标（可选）
    icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icons", "mc_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    root.minsize(width=561,height=633)
    # 启动 GUI
    app = MinecraftToolGUI(root)
    root.mainloop()