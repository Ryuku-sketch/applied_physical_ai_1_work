# 研究開発-Phase
- 試しに行く
    - 先んじて,genesisを回す
    - genesisのサンプルコード回して環境構築回す
        - サンプルでドローンのやつ動くかだけ試す
        - 一旦ここ整理しておく
- モデリング部分何をどう学習させるかもそうだが....どうやったら歩くって学習するんだ？
    - ここ少し試行錯誤する
        - どうやったら？何をしたら？

# やりたいこと検討
1. GenesisっていうSimulation環境で何が出来るかイメージを作る
    - 何が出来て何が出来ないのか？
    - 壁や環境を作ることが出来るか？
    - ロボットが持つセンサーって何?
2. その理解を持ったうえで、「どんなタスクをするか考える」
    (構想)
    -> 歩かせるは出来るって書いてあるわ...
    -> 歩かせるだけじゃ「つまらない」
    -> 障害物を回避して歩く！とか少し難しい事したいよね
    -> 個人的に, RLのリスク考慮型モデルとか少し試してみたい-本で読んだやつ.
        -> これを問/タスクに変換する


# 学習した事
- Genesisについて
- Dockerについて
    - compose.yaml
    - dockerコマンドについて
        - パラメータ
        - 起動方法とかもまとめておかんと忘れるわ
        - hostからコンテナに対してコマンド実行が可能
    - bashとの接続について



# 環境開発-Phase
以下のコマンドで実施
(※: ai_roboticsディレクトリ配下で実施)
- 利用するDirectoryに応じて$(pwd)/の部分を変更
- ベース
    `docker run -p 6080:80 -v "$(pwd)/src:/home/desktop/dev" --gpus all ubuntu_base` 
- リソース制限
    `docker run -p 6080:80 -v "$(pwd)/src:/home/desktop/dev" --shm-size=5000m --gpus all ubuntu_base`
 - それを実行したのちに,↓をhost側で実行が必要
    `docker exec -u root -it <Container-id> chown -R desktop:desktop /home/desktop/app`
- 簡易版環境の話:
    `docker run --gpus all -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics -it -v "$(pwd)/src:/app" physical_ai_dev`
    `docker run -it -v "$(pwd)/src:/app" physical_ai_dev`

=> novncで仮想デスクトップ内で作業
- 構成イメージ
- Host => Docker-Container => Ubuntu => Python / Genesis / ROS2
- user -> rootに変更
    - 出来れば、中で開発が完結して欲しいが、これで無理だったら, 
    local開発 -> container でテスト・実行をする感じにする


TODO:
- STEPを切る
    - STEP1 INFRA
        - 開発環境構築
        - Docker：DevContainer x Ubuntuの仮想デスクトップ検証環境
    - STEP2 BASE-LINE
        - Genesisを使い, シミュレーションをが出来る
        - 学習をしてその先で, 学習が出来る
            [サンプルコード]{https://qiita.com/hEnka/items/cc5fd872eb0bf7cd3abc#genesis%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB}
        - 一旦で使ったやつをベースにdockerfile更新して終わり
    - STEP3 環境構築
        - ここまでやったら　終わり
        - ここの調査終わったら終わり
            - データのとり方=> 
        - 明日はここから
            -> 学習のやり方考える
            -> どんなタスク設定にするか？ => どんなおもろいことするか？
                -> どんな面白い楽しいこと入れ込むか？
            - RL回す
            - もう少し知りたいね. どうやるのか？何が必要かイメージが全然できてないわ
            - 一旦細かい部分は後でもっと知りに行くとして先に回す
            - こだわりたい部分や何ができるかとかは少し回す　→これは今後少し知りたい
            =>n何をするか一旦検討＝＞ご飯食べた後-自分の中に落とし込んで何がどう動いているか確認する
            =>どんなことができるかとか
            - ここからシステム組んで学習作る→モデルイメージを作った上で

    - STEP4 modeling
    - STEP5 4のIteration



