import torch
import genesis as gs

class EnvironmentPenalty: 
    def __init__(self, num_env=1, device="cuda"):
        self.num_envs = num_env
        self.device = device
        
    
        # シーン構築
        self.scene = gs.Scene(
            sim_options= gs.options.SimOptions(dt=0.01, substeps=2), # 本来は細かくした方がいいかもしれんが、メモリが足りない
            show_viewer=False,
        )

        self.plane = self.scene.add_entity(gs.morphs.Plane())
        self.robot = self.scene.add_entity(gs.morphs.URDF(
            file="urdf/go2/urdf/go2.urdf",
            pos=(0, 0, 0.5)))


        self.cam = self.scene.add_camera(
            res=(1280, 720),
            pos=(3.0, -3.0, 5), # カメラの配置位置 (x, y, z) 
            lookat=(0.0, 0.0, 0.5), # 注視点 (ロボットの少し上など) 
            fov=40, # 視野角 
            GUI=False, # GUIはオフ 
            )


        # 並列構築したい数を渡す
        self.scene.build(n_envs=self.num_envs)
        # ビルド後, 実態が生成
        self.initial_pos = self.robot.get_pos()
        self.initial_state = self.scene.get_state()
        # デフォルの関節角/PDゲインを設定
        self.n_dofs = self.robot.n_dofs
        self.default_dof_pos = torch.zeros((self.num_envs, self.n_dofs), device=self.device)
        self.robot.set_dofs_kp([20.0] * self.n_dofs)
        self.robot.set_dofs_kv([0.5] * self.n_dofs)

        # 観測・行動がもつ次元数の定義
        self.num_obs = self.n_dofs * 2 + 2
        self.num_actions = self.n_dofs # 関節角への指示　＝＝行動
        self.goal_pos = [20, 0, 0]


        # stepで学習やターゲットに使用したデータを格納する
        self.logs ={
            "target_pos": [],
            "rewards": [],
            "observation": [],
            "is_done": [] #終了判定
        }
        self.cfg = {
                    "num_envs": self.num_envs,
                    "device": self.device,
                    "default_position": self.default_dof_pos
                }
        return None

    def reset(self):
        self.scene.reset()
        return self._get_obs()
    
    def steps(self, actions):
        actions = actions.to(self.device)
        target_pos = self.default_dof_pos + actions
        self.robot.control_dofs_position(target_pos)
        
        
        # 物理時間を進める
        self.scene.step()

        # 観測/報酬決定
        obs = self._get_obs()
        rewards = self._compute_rewards()
        dones, fell = self._check_dones()

         # 転倒や目的を達成したepisodeは初期化
        if (dones.numel() > 0):
            self._reset_falling_robot(fell)

        # ここでlogging
        self._logging(target_pos, obs, rewards, dones)
        return obs, rewards, dones

    def _logging(self, target_pos, obs, rewards, dones):
        self.logs["target_pos"].append(target_pos)
        self.logs["observation"].append(obs)
        self.logs["rewards"].append(rewards)
        self.logs["is_done"].append(dones)
        return None

    def _reset_falling_robot(self,fall):#　転倒ロボの環境を初期化
        env_idx = torch.where(fall)[0] #転倒したロボット取得
        if len(env_idx) > 0:
            self.scene.reset(state = self.initial_state , envs_idx=env_idx)
        return None 

    def _get_obs(self): #現在のロボットの状態取得
        # ロボットの関節状態
        dofs_position = self.robot.get_dofs_position()
        dofs_velocity = self.robot.get_dofs_velocity()
        current_state = torch.cat([dofs_position, dofs_velocity], dim=-1).to(self.device)

        # イメージはこれ assert self.num_obj.shape == current_state.shape
        return current_state

    def _compute_rewards(self):
        """
        報酬：終了目標に近づく /　頭の位置を高くしている / goal していたら、bonus
        
        """
        robot_pos = self.robot.get_pos()
        # きめの問題だから、x方向に進んだかどうか？
        # 近づいたかを算出する
        reached_goal = robot_pos[:, 0] >= 20.0
        reward_goal = torch.where(reached_goal, 15, 0) # ゴールした場合のボーナス
        # 通常の報酬
        reward_fwd = self.robot.get_dofs_velocity()[:,0] * 2.0# 速度の方がいいらしい、腹落ち要件

        # +α: 転倒時に罰則を与えるわ => 逆転で頭をあげてられる＝＝姿勢を安定させる
        penelize_falling_idx = robot_pos[:, 2] < 0.35
        stable_posture = torch.where(penelize_falling_idx, -2, 0)
        return reward_fwd+reward_goal+stable_posture

    def _check_dones(self):
        # 全環境のロボット位置を取得 
        pos = self.robot.get_pos() 
        #1. X軸方向に20m到達・通過した判定 (Bool Tensor) 
        reached_goal = pos[:, 0] >= 20.0 
        # 2. 転倒判定（例: 胴体の高さが0.2m未満に低下） => 学習した結果が倒れた状態でばたばたになっている
        fell = pos[:, 2] < 0.35

        # todoこれはせt タイムアウト判定（例: 最大ステップ数を超過） #
        # timeout = self.episode_length_buf >= self.max_episode_length 
        # いずれかの条件を満たした環境を True (終了) にする 
        dones = reached_goal | fell 
        return dones, fell