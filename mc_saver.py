# mc_saver.py

import os
from tkinter import messagebox
import nbtlib


def nbt_to_primitive(nbt_data, max_depth=32):
    """安全将 NBT 数据转换为 Python 原生类型"""
    if max_depth <= 0:
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


class MinecraftSaver:
    def __init__(self, world_path):
            self.world_path = world_path
            self.level_dat = self._load_level_dat()
    def _load_level_dat(self):
            level_path = os.path.join(self.world_path, "level.dat")
            return nbtlib.load(level_path)

    def get_world_info(self):
        data = self.level_dat['Data']
        player = data.get('Player', {})
        return {
            "世界名称": str(data.get('LevelName', "未知")),
            "游戏模式": self.get_game_mode(player),
            "出生点": {
                "x": int(data.get('SpawnX', 0)),
                "y": int(data.get('SpawnY', 0)),
                "z": int(data.get('SpawnZ', 0))
            },
            "世界时间": int(data.get('Time', 0)),
            "最后保存时间": int(data.get('LastPlayed', 0)),
            "世界难度": self.get_difficulty(data)
        }

    def get_player_position(self):
        try:
            pos = self.level_dat['Data']['Player']['Pos']
            return {
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2])
            }
        except Exception:
            return {"x": 0.0, "y": 0.0, "z": 0.0}

    def get_dimension(self):
        try:
            dimension = self.level_dat['Data']['Player'].get('Dimension', 'minecraft:overworld')
            dimension_map = {
                'minecraft:overworld': '主世界',
                'overworld': '主世界',
                'minecraft:the_nether': '下界',
                'nether': '下界',
                'minecraft:the_end': '末地',
                'end': '末地'
            }
            return dimension_map.get(str(dimension), f"未知维度({dimension})")
        except Exception:
            return "无法读取维度"

    def get_player_inventory(self):
        """获取玩家背包信息"""
        try:
            inventory_nbt = self.level_dat['Data']['Player'].get('Inventory', [])
            inventory = []
            for item in inventory_nbt:
                if 'id' not in item:
                    continue
                inventory.append({
                    "槽位": int(item.get('Slot', -1)),
                    "物品ID": str(item['id']),
                    "数量": int(item.get('Count', 0)),
                    "NBT": item.get('tag', None)
                })
            return inventory
        except Exception as e:
            print("读取背包失败:", e)
            return []

    def get_game_mode(self, player):
        game_type = int(player.get('playerGameType', 0))
        mode_map = {
            0: "生存模式",
            1: "创造模式",
            2: "冒险模式",
            3: "旁观者模式"
        }
        return mode_map.get(game_type, "未知模式")

    def get_difficulty(self, data):
        difficulty = int(data.get('Difficulty', 0))
        difficulty_map = {
            0: "和平",
            1: "简单",
            2: "普通",
            3: "困难"
        }
        return difficulty_map.get(difficulty, "未知难度")