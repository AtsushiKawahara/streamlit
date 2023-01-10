import pyxel
import collections
import random
import copy

# 画面推移用の定数
SCENE_TITLE = 0  # タイトル画面
SCENE_PLAY = 1  # ゲーム画面
SCENE_COUNTDOWN = 2  # カウントダウン画面
SCENE_RESULT = 3  # 結果画面

# 難易度の定数
EASY = 0
NORMAL = 1
HARD = 2


class App:
    def __init__(self):
        # ゲーム画面サイズの設定
        pyxel.init(160, 128, title="Pyxel Jump")

        # イラストファイルの読み込み
        pyxel.load("assets/sum_game.pyxres")
        self.score = 0

        # サウンドの再生
        pyxel.playm(0, loop=True)

        # ゲーム難易度選択変数
        self.difficulty = NORMAL

        # 画面推移変数
        self.scene = SCENE_TITLE

        # 結果画面のメニュー選択
        self.scene_result_select_menu = SCENE_TITLE

        # ブロックの色をランダムに決定(被り色なし)
        self.random_w_block_list = self.rand_ints_nodup(0, 130, 10, 7)
        self.w_block_0 = self.random_w_block_list[0]  # 0番目のブロックの色(以下同様)
        self.w_block_1 = self.random_w_block_list[1]
        self.w_block_2 = self.random_w_block_list[2]
        self.w_block_3 = self.random_w_block_list[3]
        self.w_block_4 = self.random_w_block_list[4]
        self.w_block_5 = self.random_w_block_list[5]
        self.w_block_6 = self.random_w_block_list[6]  # 6番上のブロックの色

        # 矢印の位置
        self.yazirusi_position = 1  # この変数で矢印の位置を管理
        self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}  # key: 矢印のポジション, value: 矢印のx座標

        # カウントダウン用
        self.countdown_game_start = 90  # ゲーム開始カウントダウン用(1秒間に30フレーム減る。3秒カウントダウンしたいから90)
        self.countdown_game_time = 150  # ゲームプレイ時間カウントダウン用(1秒間に30フレーム減る。60秒カウントダウンしたいから1800)
        self.countdown_next_question_wait_time = 20  # 次の問題に移行するまでの待機時間カウントダウン用(1秒間に30フレーム減る。0.6秒カウントダウンしたいから20)

        # question_listから取り除く値: 初期値0
        self.pop_num = 0

        # ブロックの動き(x軸)を管理する変数
        # x: 最上段・最下段(x_0, x_6)は動かないため変数なし
        self.block_move_x_1 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        # ブロックの動き(y軸)を管理する変数
        # y: 最下段(y_6)は動かないため変数なし
        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0

        # ブロック文字の動き(x軸)を管理する変数
        # x: 最上段・最下段(x_0, x_6)は動かないため変数なし
        self.text_move_x_1 = 0
        self.text_move_x_2 = 0
        self.text_move_x_3 = 0
        self.text_move_x_4 = 0
        self.text_move_x_5 = 0
        # ブロック文字の動き(y軸)を管理する変数
        # y: 最下段(y_6)は動かないため変数なし
        self.text_move_y_0 = 0
        self.text_move_y_1 = 0
        self.text_move_y_2 = 0
        self.text_move_y_3 = 0
        self.text_move_y_4 = 0
        self.text_move_y_5 = 0

        # ブロックを動かすかを判定する変数(Trueになると動く)
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False

        # ブロックを描写するかを判定する変数(Trueになると描写する)
        # ブロック合体した後に消す用
        self.is_block_draw_0 = True
        self.is_block_draw_1 = True
        self.is_block_draw_2 = True
        self.is_block_draw_3 = True
        self.is_block_draw_4 = True
        self.is_block_draw_5 = True
        self.is_block_draw_6 = True

        # ビームを描写するかを判定する変数(Trueになると描写する)
        self.is_beem_draw_0 = False
        self.is_beem_draw_1 = False
        self.is_beem_draw_2 = False
        self.is_beem_draw_3 = False
        self.is_beem_draw_4 = False
        self.is_beem_draw_5 = False
        self.is_beem_draw_6 = False

        # ブロックが落下したときにブロック座標情報等を更新するため変数
        self.is_update_all = False

        pyxel.run(self.update, self.draw)

    def update(self):
        """
        ボタン押下によって処理を行うメソッドを選択
        シーン(SCENE)によって処理を分岐
        """
        # ゲーム終了処理(全SCENE共通)
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # タイトル画面の処理
        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        # プレイ画面の処理
        if self.scene == SCENE_PLAY:
            self.update_play_scene()
        # カウントダウン画面の処理
        if self.scene == SCENE_COUNTDOWN:
            self.update_countdown_scene()
        # 結果画面の処理
        if self.scene == SCENE_RESULT:
            self.update_result_scene()

    def update_result_scene(self):
        """
        結果表示画面の処理
        - メインメニュー・リトライを選択
        """
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if self.scene_result_select_menu == SCENE_TITLE:
                pass
            if self.scene_result_select_menu == SCENE_COUNTDOWN:
                self.scene_result_select_menu = SCENE_TITLE  # タイトル画面へ
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if self.scene_result_select_menu == SCENE_TITLE:
                self.scene_result_select_menu = SCENE_COUNTDOWN  # カウントダウン画面へ
            if self.scene_result_select_menu == SCENE_COUNTDOWN:
                pass
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            pyxel.play(3, 9)
            self.countdown_game_start = 90  # ゲーム開始カウントダウン変数を初期化
            self.scene = self.scene_result_select_menu  # 上の行で選択中のメニュー画面へ推移

    def update_countdown_scene(self):
        """
        カウントダウン画面の処理
        - 3秒カウントダウンしてゲーム画面へ移行
        """
        self.countdown_game_start -= 1
        # カウントダウンが０になったらゲームを開始する
        if self.countdown_game_start == 0:
            self.scene = SCENE_PLAY  # プレイ画面へ
            # スコア・プレイ時間をリセット
            self.score = 0
            self.countdown_game_time = 150
            # 問題の再作成
            self.update_block_retry()  # 問題の再作成
            self.block_count = len(self.question_list)

    def update_title_scene(self):
        """
        タイトル画面の処理
        - 難易度を選択
        """
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if self.difficulty == HARD:
                pass
            if self.difficulty == NORMAL or self.difficulty == EASY:
                self.difficulty += 1  # 1つ難易度をup
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if self.difficulty == EASY:
                pass
            if self.difficulty == HARD or self.difficulty == NORMAL:
                self.difficulty -= 1  # 1つ難易度をdown
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            pyxel.play(3, 9)
            self.countdown_game_start = 90  # ゲーム開始カウントダウン変数を初期化
            self.scene = SCENE_COUNTDOWN  # カウントダウン画面へ


    def update_play_scene(self):
        """
        プレイ画面の処理
        - 問題の再作成
        - 矢印の位置変更(上・下)
        - ブロック(飛ばす・落とす)・ビーム発射
        - タイトル画面へ移行
        """
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.update_block_retry()  # 問題の再作成
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.move_yazirusi(is_up=True)  # 矢印を上に移動
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.move_yazirusi(is_up=False)  # 矢印を下に移動
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.update_block_and_beem()  # ビーム発射・ブロックはじく・落ちる
        if pyxel.btnp(pyxel.KEY_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.scene = SCENE_TITLE  # タイトル画面へ
        if self.countdown_game_time == 0:
            self.scene = SCENE_RESULT

        # 変数が変更によるブロック・数字の動きを計算
        self.move_calculate()

    def update_block_retry(self):
        """
        問題を再作成する
        変数も同時にリセット
        """

        # ブロックの色をランダムに決定(被り色なし)
        self.random_w_block_list = self.rand_ints_nodup(0, 130, 10, 7)
        self.w_block_0 = self.random_w_block_list[0]  # 0番目のブロックの色(以下同様)
        self.w_block_1 = self.random_w_block_list[1]
        self.w_block_2 = self.random_w_block_list[2]
        self.w_block_3 = self.random_w_block_list[3]
        self.w_block_4 = self.random_w_block_list[4]
        self.w_block_5 = self.random_w_block_list[5]
        self.w_block_6 = self.random_w_block_list[6]  # 6番上のブロックの色

        # 問題を再作成
        self.question_list, self.yazirusi_position_list, self.quesution_dict, self.answer = self.question_create(element_count=7)
        self.block_count = len(self.question_list)

        # 矢印の位置
        self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}
        self.yazirusi_position = 1

        # カウントダウン用
        self.countdown_next_question_wait_time = 20  # 次の問題に移行するまでの待機時間カウントダウン用(1秒間に30フレーム減る。0.6秒カウントダウンしたいから20)

        # ブロックの動き(x軸)を管理する変数
        # x: 最上段・最下段(x_0, x_6)は動かないため変数なし
        self.block_move_x_1 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        # ブロックの動き(y軸)を管理する変数
        # y: 最下段(y_6)は動かないため変数なし
        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0

        # ブロック文字の動き(x軸)を管理する変数
        # x: 最上段・最下段(x_0, x_6)は動かないため変数なし
        self.text_move_x_1 = 0
        self.text_move_x_2 = 0
        self.text_move_x_3 = 0
        self.text_move_x_4 = 0
        self.text_move_x_5 = 0
        # ブロック文字の動き(y軸)を管理する変数
        # y: 最下段(y_6)は動かないため変数なし
        self.text_move_y_0 = 0
        self.text_move_y_1 = 0
        self.text_move_y_2 = 0
        self.text_move_y_3 = 0
        self.text_move_y_4 = 0
        self.text_move_y_5 = 0

        # ブロックを動かすかを判定する変数(Trueになると動く)
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False

        # ブロックを描写するかを判定する変数(Trueになると描写する)
        # ブロック合体した後に消す用
        self.is_block_draw_0 = True
        self.is_block_draw_1 = True
        self.is_block_draw_2 = True
        self.is_block_draw_3 = True
        self.is_block_draw_4 = True
        self.is_block_draw_5 = True
        self.is_block_draw_6 = True

        # ビームを描写するかを判定する変数(Trueになると描写する)
        self.is_beem_draw_0 = False
        self.is_beem_draw_1 = False
        self.is_beem_draw_2 = False
        self.is_beem_draw_3 = False
        self.is_beem_draw_4 = False
        self.is_beem_draw_5 = False
        self.is_beem_draw_6 = False

    def update_block_and_beem(self):
        """
        取り除くブロックが選択された場合の処理
        - ブロック・ビームを動かす信号をTrueにする
        - 選択された矢印の位置で判定
        """
        # ブロックが落下している途中は、ビームがでる処理のみ行う
        if (self.is_block_move_0 or
            self.is_block_move_1 or
            self.is_block_move_2 or
            self.is_block_move_3 or
            self.is_block_move_4 or
            self.is_block_move_5 or
                self.is_block_move_6):
            if self.yazirusi_position == 1:
                self.is_beem_draw_1 = True
                pyxel.play(3, 7)
            if self.yazirusi_position == 2:
                self.is_beem_draw_2 = True
                pyxel.play(3, 7)
            if self.yazirusi_position == 3:
                self.is_beem_draw_3 = True
                pyxel.play(3, 7)
            if self.yazirusi_position == 4:
                self.is_beem_draw_4 = True
                pyxel.play(3, 7)
            if self.yazirusi_position == 5:
                self.is_beem_draw_5 = True
                pyxel.play(3, 7)
        else:
            if self.yazirusi_position == 1:
                self.is_block_move_1 = True  # ブロックを動かす(以下同様)
                self.is_beem_draw_1 = True  # ビームを描写する(以下同様)
                self.pop_num = 1  # 1番目のブロックを取り除く(以下同様)
                pyxel.play(3, 7)
            if self.yazirusi_position == 2:
                self.is_block_move_2 = True
                self.is_beem_draw_2 = True
                self.pop_num = 2
                pyxel.play(3, 7)
            if self.yazirusi_position == 3:
                self.is_block_move_3 = True
                self.is_beem_draw_3 = True
                self.pop_num = 3
                pyxel.play(3, 7)
            if self.yazirusi_position == 4:
                self.is_block_move_4 = True
                self.is_beem_draw_4 = True
                self.pop_num = 4
                pyxel.play(3, 7)
            if self.yazirusi_position == 5:
                self.is_block_move_5 = True
                self.is_beem_draw_5 = True
                self.pop_num = 5
                pyxel.play(3, 7)

    def update_yazirusi(self, block_count):
        """
        ブロック数が減ったときの矢印の可動域の更新(減少)
        """
        if block_count == 7:
            self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}  # 1番目~5番目のブロック選択できる
        if block_count == 5:
            if self.yazirusi_position == 1 or self.yazirusi_position == 2:
                self.yazirusi_position = 3
            self.yazirusi_position_dict = {3: 43, 4: 54, 5: 65}  # 3番目~5番目のブロック選択できる
        if block_count == 3:
            if self.yazirusi_position == 3 or self.yazirusi_position == 4:
                self.yazirusi_position = 5
            self.yazirusi_position_dict = {5: 65}  # 5番目のブロック選択できる
        if block_count == 1:
            self.yazirusi_position = 6
            self.yazirusi_position_dict = {6: 76}  # 6番目のブロック選択できる

    def update_question_list(self, question_list, block_num_list, w_block_list, pop_num):
        """
        問題を更新
        - pop_numで指定した番号のブロックを削除・問題更新
        """

        # question_listのlen数が5であれば調整のため-2する(3であれば-4する)
        if len(question_list) == 5:
            pop_num = pop_num - 2
        elif len(question_list) == 3:
            pop_num = pop_num - 4

        # pop_numに指定した要素を取り除く
        question_list.pop(pop_num)
        block_num_list.pop(pop_num)
        w_block_list.pop(pop_num)
        w_block_list.pop(pop_num - 1)

        # 取り除いた要素の両隣の要素を合計する
        pop_num_raight = pop_num - 1  # 取り除いた値の左の要素の順番
        pop_num_left = pop_num  # 取り除いた値の右の要素の順番
        sum_num = question_list[pop_num_raight] + question_list[pop_num_left]

        # 取り除いた要素の両側の要素を取り除く
        question_list.pop(pop_num_raight)
        question_list.pop(pop_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している
        block_num_list.pop(pop_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している

        question_list.insert(pop_num - 1, sum_num)  # -1: 位置の調整(固定)

        block_num_dict = {key: value for key, value in zip(block_num_list, question_list)}

        return question_list, block_num_list, block_num_dict, w_block_list

    def update_block(self):
        """
        ブロックの数が減ったことによるブロックの配置変更
        - 落ちてきたブロック番号の更新
        - 重なったブロックを削除
        - 落ちる処理を止める
        - 落ちる信号をリセット
        """
        if self.block_count == 5:
            # ブロックを描写するかを判定する変数(Trueになると描写する)
            # ブロック合体した後に消す用
            self.is_block_draw_0 = False
            self.is_block_draw_1 = False
            self.is_block_draw_2 = True
            self.is_block_draw_3 = True
            self.is_block_draw_4 = True
            self.is_block_draw_5 = True
            self.is_block_draw_6 = True

            # ブロックの色を更新
            self.w_block_2 = self.random_w_block_list[0]
            self.w_block_3 = self.random_w_block_list[1]
            self.w_block_4 = self.random_w_block_list[2]
            self.w_block_5 = self.random_w_block_list[3]
            self.w_block_6 = self.random_w_block_list[4]
        elif self.block_count == 3:
            # ブロックを描写するかを判定する変数(Trueになると描写する)
            # ブロック合体した後に消す用
            self.is_block_draw_0 = False
            self.is_block_draw_1 = False
            self.is_block_draw_2 = False
            self.is_block_draw_3 = False
            self.is_block_draw_4 = True
            self.is_block_draw_5 = True
            self.is_block_draw_6 = True

            # ブロックの色を更新
            self.w_block_4 = self.random_w_block_list[0]
            self.w_block_5 = self.random_w_block_list[1]
            self.w_block_6 = self.random_w_block_list[2]

        # 共通処理
        # ブロックの動く信号をFalseに
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False
        self.is_update_all = False

        # ブロックの動きを止める
        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        self.block_move_x_6 = 0

    def move_calculate(self):
        """
        シグナルからブロック・数字の動く量を計算する
        動きが完了したあとに、ブロック数が減ることによる変数のリセットも行う(self.is_update_allによる)
        """
        # ゲーム残り時間の計算
        self.countdown_game_time -= 1

        # 1番目のブロックが選択されたとき
        if self.is_block_move_1:
            if -56 < self.block_move_x_1:
                self.block_move_x_1 -= 2
                self.text_move_x_1 -= 2
            if self.block_move_y_0 < 22:
                self.block_move_y_0 += 1
                self.text_move_y_0 += 1
            else:
                self.block_move_x_1 = 0
                self.text_move_x_1 = 0
                self.is_block_move_1 = False
                self.is_block_draw_0 = False
                self.is_block_draw_1 = False
                self.is_update_all = True
        # 2番目のブロックが選択されたとき
        if self.is_block_move_2:
            if -56 < self.block_move_x_2:
                self.block_move_x_2 -= 5
                self.text_move_x_2 -= 5
            if self.block_move_y_0 < 22:
                self.block_move_y_0 += 1
                self.block_move_y_1 += 1
                self.text_move_y_0 += 1
                self.text_move_y_1 += 1
            if self.block_move_y_0 == 22:
                self.block_move_x_2 = 0
                self.text_move_x_2 = 0
                self.is_block_move_2 = False
                self.is_block_draw_1 = False
                self.is_block_draw_2 = False
                self.is_update_all = True
        # 3番目のブロックが選択されたとき
        if self.is_block_move_3:
            if -56 < self.block_move_x_3:
                self.block_move_x_3 -= 5
                self.text_move_x_3 -= 5
            if self.block_move_y_0 < 22:
                self.block_move_y_0 += 1
                self.block_move_y_1 += 1
                self.block_move_y_2 += 1
                self.text_move_y_0 += 1
                self.text_move_y_1 += 1
                self.text_move_y_2 += 1
            if self.block_move_y_0 == 22:
                self.block_move_x_3 = 0
                self.text_move_x_3 = 0
                self.text_move_y_2 = 0
                self.is_block_move_3 = False
                self.is_block_draw_2 = False
                self.is_block_draw_3 = False
                self.is_update_all = True
        # 4番目のブロックが選択されたとき
        if self.is_block_move_4:
            if -56 < self.block_move_x_4:
                self.block_move_x_4 -= 5
                self.text_move_x_4 -= 5
            if self.block_move_y_0 < 22:
                self.block_move_y_0 += 1
                self.block_move_y_1 += 1
                self.block_move_y_2 += 1
                self.block_move_y_3 += 1
                self.text_move_y_0 += 1
                self.text_move_y_1 += 1
                self.text_move_y_2 += 1
                self.text_move_y_3 += 1
            if self.block_move_y_0 == 22:
                self.block_move_x_4 = 0
                self.block_move_y_3 = 0
                self.text_move_x_4 = 0
                self.text_move_y_2 = 0
                self.text_move_y_3 = 0
                self.is_block_move_4 = False
                self.is_block_draw_3 = False
                self.is_block_draw_4 = False
                self.is_update_all = True
        # 5番目のブロックが選択されたとき
        if self.is_block_move_5:
            if -56 < self.block_move_x_5:
                self.block_move_x_5 -= 5
                self.text_move_x_5 -= 5
            if self.block_move_y_0 < 22:
                self.block_move_y_0 += 1
                self.block_move_y_1 += 1
                self.block_move_y_2 += 1
                self.block_move_y_3 += 1
                self.block_move_y_4 += 1
                self.text_move_y_0 += 1
                self.text_move_y_1 += 1
                self.text_move_y_2 += 1
                self.text_move_y_3 += 1
                self.text_move_y_4 += 1
            if self.block_move_y_0 == 22:
                self.block_move_x_5 = 0
                self.block_move_y_4 = 0
                self.text_move_x_5 = 0
                self.text_move_y_2 = 0
                self.text_move_y_3 = 0
                self.text_move_y_4 = 0
                self.is_block_move_5 = False
                self.is_block_draw_4 = False
                self.is_block_draw_5 = False
                self.is_update_all = True

        # ブロック数が減ったときの処理
        if self.is_update_all:
            self.question_list, self.yazirusi_position_list, self.yazirusi_position_dict, self.random_w_block_list = self.update_question_list(self.question_list, self.yazirusi_position_list, self.random_w_block_list, pop_num=self.pop_num)
            self.block_count = len(self.question_list)
            self.update_yazirusi(block_count=len(self.question_list))
            self.update_block()

    def move_yazirusi(self, is_up):
        """
        ボタンが押された時に矢印を動かす
        """
        if is_up:
            self.yazirusi_position -= 1
            # 上限を設定
            if self.yazirusi_position < min(self.yazirusi_position_dict):
                self.yazirusi_position = min(self.yazirusi_position_dict)
        if is_up is False:
            self.yazirusi_position += 1
            # 下限を設定
            if self.yazirusi_position > 5:  # ５はブロックの一番下(6)から1つ上の(5)を設定している
                self.yazirusi_position = 5
                # ブロックが１つになったときのみ
                if len(self.question_list) == 1:
                    self.yazirusi_position = 6

    def question_create(self, element_count):
        """
        問題・答えの作成
        params:
        element_count(int): ブロックの数(必ず奇数とすること→最後に1つにならない)
        """

        remove_time = int((element_count - 1)/2)

        # 難易度によって発生する整数の範囲を変えるための辞書
        max_number_dict = {HARD: 100, NORMAL: 10, EASY: 3}
        max_number = max_number_dict[self.difficulty]

        # 難易度で指定した範囲の整数を格納したlistを作成(長さはelement_countにより設定)
        random_list = [random.randint(1, max_number) for _ in range(element_count)]
        random_list_base = copy.copy(random_list)
        yazirusi_position_list = list(range(element_count))  # 矢印のポジション管理のリストを作成(random_listと一緒に管理する)

        # key:self.yazirusi_position, value:question_list →blockの位置管理に使用
        random_list_base_dict = {key: value for key, value in zip(yazirusi_position_list, random_list_base)}

        for i in range(remove_time):

            # 取り除く要素を指定(一番上と下は取り除かない)
            pop_num = random.randint(1, element_count - 2)

            # ランダムに指定した要素を取り除く
            random_list.pop(pop_num)

            # 取り除いた要素の両隣の要素を合計する
            sum_num_raight = pop_num - 1  # 取り除いた値の左の要素の順番
            sum_num_left = pop_num  # 取り除いた値の右の要素の順番
            sum_num = random_list[sum_num_raight] + random_list[sum_num_left]

            # 取り除いた要素の両側の要素を取り除く
            random_list.pop(sum_num_raight)
            random_list.pop(sum_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している

            random_list.insert(pop_num - 1, sum_num)  # -1: 位置の調整(固定)

            element_count = len(random_list)

        return random_list_base, yazirusi_position_list, random_list_base_dict, random_list[0]

    def rand_ints_nodup(self, a, b, c, k):
        """
        重複なしのリストの作成
        params:
        a, b, c(int): a ~ b の間(間隔c)でk個選択する
        """
        ns = []
        while len(ns) < k:
            n = random.randrange(a, b, c)
            if not n in ns:
                ns.append(n)
        return ns

    def draw(self):
        """
        シーン(SCENE)によって描写処理を分岐
        """
        pyxel.cls(0)  # 黒色(0)のカラースクリーン

        # 描画の画面分岐
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_COUNTDOWN:
            self.draw_countdown_scene()
        elif self.scene == SCENE_RESULT:
            self.draw_result_scene()

    def draw_countdown_scene(self):
        """
        カウントダウン画面の描写処理
        """
        if 60 < self.countdown_game_start < 90:
            pyxel.blt(70, 50, 1, 40, 64, 16, 16, 0)  # カウントダウン(3)
        if 30 < self.countdown_game_start <= 60:
            pyxel.blt(70, 50, 1, 56, 64, 16, 16, 0)  # カウントダウン(2)
        if self.countdown_game_start <= 30:
            pyxel.blt(70, 50, 1, 72, 64, 16, 16, 0)  # カウントダウン(1)

    def draw_result_scene(self):
        """
        結果画面の描写処理
        """
        # 選択している難易度
        if self.difficulty == HARD:
            pyxel.text(58, 30, "level hard", 7)
        elif self.difficulty == NORMAL:
            pyxel.text(58, 30, "level normal", 7)
        elif self.difficulty == EASY:
            pyxel.text(58, 30, "level easy", 7)

        # スコア(スコアによって表示する色を設定)
        if self.score >= 50:
            pyxel.text(55, 40, f"your score {self.score}", pyxel.frame_count % 16)
        elif self.score >= 30:
            pyxel.text(55, 40, f"your score {self.score}", 10)
        elif self.score >= 0:
            pyxel.text(55, 40, f"your score {self.score}", 10)
        else:
            pyxel.text(55, 40, f"your score {self.score}", 12)

        # 選択中のmenuをカラフルに表示
        if self.scene_result_select_menu == SCENE_TITLE:
            pyxel.text(62, 80, "main menu", pyxel.frame_count % 16)
            pyxel.text(62, 100, "  retry  ", 7)
        if self.scene_result_select_menu == SCENE_COUNTDOWN:
            pyxel.text(62, 80, "main menu", 7)
            pyxel.text(62, 100, "  retry  ", pyxel.frame_count % 16)

    def draw_title_scene(self):
        """
        タイトル画面の描写処理
        """
        pyxel.text(55, 60, "please select", 7)
        pyxel.blt(32, 30, 1, 40, 48, 64, 16, 0)  # タイトル(PLUS)
        pyxel.blt(100, 30, 1, 104, (pyxel.frame_count % 7)*16, 16, 16, 0)  # タイトル(N)

        # 選択中の難易度をカラフルに表示
        if self.difficulty == EASY:
            pyxel.text(70, 80, "hard", 7)
            pyxel.text(70, 90, "normal", 7)
            pyxel.text(70, 100, "easy", pyxel.frame_count % 16)
        if self.difficulty == NORMAL:
            pyxel.text(70, 80, "hard", 7)
            pyxel.text(70, 90, "normal", pyxel.frame_count % 16)
            pyxel.text(70, 100, "easy", 7)
        if self.difficulty == HARD:
            pyxel.text(70, 80, "hard", pyxel.frame_count % 16)
            pyxel.text(70, 90, "normal", 7)
            pyxel.text(70, 100, "easy", 7)

    def draw_play_scene(self):
        """
        プレイ画面の描写処理
        """

        # Draw_countdown
        pyxel.text(121, 8, "time", 1)
        pyxel.text(122, 8, "time", 7)
        pyxel.text(129, 16, str(self.countdown_game_time // 30), 1)
        pyxel.text(130, 16, str(self.countdown_game_time // 30), 7)

        # Draw score
        pyxel.text(121, 32, "SCORE", 1)
        pyxel.text(122, 32, "SCORE", 7)
        pyxel.text(129, 40, str(self.score), 1)
        pyxel.text(130, 40, str(self.score), 7)

        # Draw answer
        pyxel.text(119, 56, "ANSWER", 1)
        pyxel.text(120, 56, "ANSWER", 7)
        pyxel.text(129, 64, str(self.answer), 1)
        pyxel.text(130, 64, str(self.answer), 7)
        pyxel.blt(118, 54, 1, 40, 0, 27, 17, 0)  # 枠

        # Draw block
        if self.is_block_draw_0:
            pyxel.blt(16                      , 10 + self.block_move_y_0, 1, 0, self.w_block_0, 40, 10)
        if self.block_move_x_1 > -56 and self.is_block_draw_1:
            pyxel.blt(16 + self.block_move_x_1, 21 + self.block_move_y_1, 1, 0, self.w_block_1, 40, 10)
        if self.block_move_x_2 > -56 and self.is_block_draw_2:
            pyxel.blt(16 + self.block_move_x_2, 32 + self.block_move_y_2, 1, 0, self.w_block_2, 40, 10)
        if self.block_move_x_3 > -56 and self.is_block_draw_3:
            pyxel.blt(16 + self.block_move_x_3, 43 + self.block_move_y_3, 1, 0, self.w_block_3, 40, 10)
        if self.block_move_x_4 > -56 and self.is_block_draw_4:
            pyxel.blt(16 + self.block_move_x_4, 54 + self.block_move_y_4, 1, 0, self.w_block_4, 40, 10)
        if self.block_move_x_5 > -56 and self.is_block_draw_5:
            pyxel.blt(16 + self.block_move_x_5, 65 + self.block_move_y_5, 1, 0, self.w_block_5, 40, 10)
        if self.is_block_draw_6:
            pyxel.blt(16                      , 76                      , 1, 0, self.w_block_6, 40, 10)

        # Draw text
        if self.block_count == 7:
            pyxel.text(35                     , 13 + self.text_move_y_0, str(self.question_list[0]), 1)
            pyxel.text(36                     , 13 + self.text_move_y_0, str(self.question_list[0]), 7)
            pyxel.text(35 + self.text_move_x_1, 24 + self.text_move_y_1, str(self.question_list[1]), 1)
            pyxel.text(36 + self.text_move_x_1, 24 + self.text_move_y_1, str(self.question_list[1]), 7)
            pyxel.text(35 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[2]), 1)
            pyxel.text(36 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[2]), 7)
            pyxel.text(35 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[3]), 1)
            pyxel.text(36 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[3]), 7)
            pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[4]), 1)
            pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[4]), 7)
            pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[5]), 1)
            pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[5]), 7)
            pyxel.text(35                     , 79                     , str(self.question_list[6]), 1)
            pyxel.text(36                     , 79                     , str(self.question_list[6]), 7)
        elif self.block_count == 5:
            pyxel.text(35 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 1)
            pyxel.text(36 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 7)
            pyxel.text(35 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 1)
            pyxel.text(36 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 7)
            pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[2]), 1)
            pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[2]), 7)
            pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[3]), 1)
            pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[3]), 7)
            pyxel.text(35                     , 79                     , str(self.question_list[4]), 1)
            pyxel.text(36                     , 79                     , str(self.question_list[4]), 7)
        elif self.block_count == 3:
            pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 1)
            pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 7)
            pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 1)
            pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 7)
            pyxel.text(35                     , 79                     , str(self.question_list[2]), 1)
            pyxel.text(36                     , 79                     , str(self.question_list[2]), 7)
        elif self.block_count == 1:
            pyxel.text(35                     , 79                       , str(self.question_list[0]), 1)
            pyxel.text(36                     , 79                       , str(self.question_list[0]), 7)
            # 正解
            if self.question_list[0] == self.answer and self.countdown_next_question_wait_time == 19:
                pyxel.play(3, 8)
                self.score += 10
            # 不正解
            elif self.question_list[0] != self.answer and self.countdown_next_question_wait_time == 19:
                pyxel.play(3, 6)
                self.score -= 10
            # ブロックが１つの間のカウントダウン(この間は描写)
            self.countdown_next_question_wait_time -= 1
            # カウントダウンが０になると次の問題に移行
            if self.countdown_next_question_wait_time == 0:
                self.update_block_retry()

        # Draw beem
        if self.is_beem_draw_1:
            pyxel.blt(56, 22, 1, 136, 0, 42, 57, 0)  # block1波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_1 = False
        if self.is_beem_draw_2:
            pyxel.blt(56, 33, 1, 136, 138, 42, 56, 0)  # block2波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_2 = False
        if self.is_beem_draw_3:
            pyxel.blt(56, 44, 1, 136, 200, 42, 44, 0)  # block3波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_3 = False
        if self.is_beem_draw_4:
            pyxel.blt(56, 56, 1, 192, 0, 42, 26, 0)  # block4波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_4 = False
        if self.is_beem_draw_5:
            pyxel.blt(56, 66, 1, 192, 36, 42, 15, 0)  # block5波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_5 = False
        if self.is_beem_draw_6:
            pyxel.blt(56, 73, 1, 192, 59, 42, 12, 0)  # block6波動
            if self.block_move_y_0 > 3:
                self.is_beem_draw_6 = False

        # Draw human
        pyxel.blt(98, 61, 1, 108, 120, 19, 22, 1)

        # Draw yazirusi
        yazirusi_y = self.yazirusi_position_dict[self.yazirusi_position]
        pyxel.blt(60, yazirusi_y, 1, 40, 32, 10, 10, 0)


App()
