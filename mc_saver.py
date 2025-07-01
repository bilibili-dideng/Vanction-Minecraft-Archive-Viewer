import nbtlib
import os


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