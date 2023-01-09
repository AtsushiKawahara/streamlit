import pyxel
import collections
import random
import copy

# 画面推移用の定数
SCENE_TITLE = 0 # タイトル画面
SCENE_PLAY = 1 # ゲーム画面
SCENE_COUNTDOWN = 2 # カウントダウン画面
SCENE_RESULT = 3 # 結果画面

# 難易度の定数
EASY = 0
NORMAL = 1
HARD = 2

class App:
    def __init__(self):
        pyxel.init(160, 128, title="Pyxel Jump")
        pyxel.load("assets/sum_game.pyxres")
        self.score = 0
        self.player_x = 72
        self.player_y = -16
        self.player_dy = 0
        self.is_alive = True
        self.far_cloud = [(-10, 75), (40, 65), (90, 60)]
        self.near_cloud = [(10, 25), (70, 35), (120, 15)]
        self.floor = [(i * 60, pyxel.rndi(8, 104), True) for i in range(4)]
        self.fruit = [
            # (i * 60, pyxel.rndi(0, 104), pyxel.rndi(0, 2), True) for i in range(4)
            (i * 10, pyxel.rndi(0, 104), pyxel.rndi(0, 2), True) for i in range(20)
        ]
        pyxel.playm(0, loop=True)
        self.random_w_block_list = self.rand_ints_nodup(0, 130, 10, 7)

        # ゲーム難易度選択変数
        self.difficulty = NORMAL

        # 画面推移変数
        self.scene = SCENE_TITLE

        # 結果画面のメニュー選択
        self.scene_result_select_menu = SCENE_TITLE

        self.w_block_0 = self.random_w_block_list[0]
        self.w_block_1 = self.random_w_block_list[1]
        self.w_block_2 = self.random_w_block_list[2]
        self.w_block_3 = self.random_w_block_list[3]
        self.w_block_4 = self.random_w_block_list[4]
        self.w_block_5 = self.random_w_block_list[5]
        self.w_block_6 = self.random_w_block_list[6]
        self.yazirusi_position = 1
        self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}

        # カウントダウン用
        self.countdown_game_start = 90  # カウントダウン用(1秒間に30フレーム減る。3秒カウントダウンしたいから90)
        self.countdown_game_time = 150  # カウントダウン用(1秒間に30フレーム減る。60秒カウントダウンしたいから1800)

        # pop_num(question_listから取り除く値:初期値0)
        self.pop_num = 0

        # block move info
        self.block_move_x_1 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0
        self.block_move_y_6 = 0

        # text move info
        self.text_move_x_1 = 0
        self.text_move_x_2 = 0
        self.text_move_x_3 = 0
        self.text_move_x_4 = 0
        self.text_move_x_5 = 0
        self.text_move_y_0 = 0
        self.text_move_y_1 = 0
        self.text_move_y_2 = 0
        self.text_move_y_3 = 0
        self.text_move_y_4 = 0
        self.text_move_y_5 = 0
        self.text_move_y_6 = 0

        # block is_move
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False

        # block_is_draw
        self.is_block_draw_0 = True
        self.is_block_draw_1 = True
        self.is_block_draw_2 = True
        self.is_block_draw_3 = True
        self.is_block_draw_4 = True
        self.is_block_draw_5 = True
        self.is_block_draw_6 = True

        # beem is_draw
        self.is_beem_draw_0 = False
        self.is_beem_draw_1 = False
        self.is_beem_draw_2 = False
        self.is_beem_draw_3 = False
        self.is_beem_draw_4 = False
        self.is_beem_draw_5 = False
        self.is_beem_draw_6 = False

        # ブロックが落下しきったときにもろもろupdateするための信号
        self.is_update_all = False

        # ブロックが１つになったときの表示時間確保用変数(この変数が定数を超えると表示を終了)
        self.block_count_1_wait_time = 0

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            pyxel.quit()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        if self.scene == SCENE_PLAY:
            self.update_play_scene()
        if self.scene == SCENE_COUNTDOWN:
            self.update_countdown_scene()
        if self.scene == SCENE_RESULT:
            self.update_result_scene()

    def update_result_scene(self):
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if self.scene_result_select_menu == SCENE_TITLE:
                pass
            if self.scene_result_select_menu == SCENE_PLAY:
                self.scene_result_select_menu = SCENE_TITLE
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if self.scene_result_select_menu == SCENE_TITLE:
                self.scene_result_select_menu = SCENE_PLAY
            if self.scene_result_select_menu == SCENE_PLAY:
                pass
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            pyxel.play(3, 9)
            self.scene = self.scene_result_select_menu  # 現在選択中のメニュー画面へ推移
            self.score = 0
            self.countdown_game_time = 150
            self.question_list, self.yazirusi_position_list, self.quesution_dict, self.answer = self.question_create(element_count=7)
            self.block_count = len(self.question_list)

    def update_countdown_scene(self):
        self.countdown_game_start -= 1
        if self.countdown_game_start == 0:
            self.scene = SCENE_PLAY

    def update_title_scene(self):
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
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            pyxel.play(3, 9)
            self.scene = SCENE_COUNTDOWN
            self.score = 0
            self.countdown_game_time = 150
            self.question_list, self.yazirusi_position_list, self.quesution_dict, self.answer = self.question_create(element_count=7)
            self.block_count = len(self.question_list)

    def update_play_scene(self):
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            self.update_block_retry()
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.move_yazirusi(is_up=True)
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.move_yazirusi(is_up=False)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.update_block_and_beem()
        if pyxel.btnp(pyxel.KEY_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.scene = SCENE_TITLE
            self.update_block_retry()
        if self.countdown_game_time == 0:
            self.scene = SCENE_RESULT

        # 変数が変更によるブロック・数字の動きを計算
        self.move_calculate()

    def update_block_retry(self):
        self.random_w_block_list = self.rand_ints_nodup(0, 130, 10, 7)
        self.question_list, self.yazirusi_position_list, self.quesution_dict, self.answer = self.question_create(element_count=7)
        self.w_block_0 = self.random_w_block_list[0]
        self.w_block_1 = self.random_w_block_list[1]
        self.w_block_2 = self.random_w_block_list[2]
        self.w_block_3 = self.random_w_block_list[3]
        self.w_block_4 = self.random_w_block_list[4]
        self.w_block_5 = self.random_w_block_list[5]
        self.w_block_6 = self.random_w_block_list[6]
        self.block_count = len(self.question_list)
        self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}
        self.yazirusi_position = 1
        self.countdown_game_start = 90  # カウントダウン用(1秒間に30フレーム減る。3秒カウントダウンしたいから90)

        # block move info
        self.block_move_x_1 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0
        self.block_move_y_6 = 0

        # text move info
        self.text_move_x_1 = 0
        self.text_move_x_2 = 0
        self.text_move_x_3 = 0
        self.text_move_x_4 = 0
        self.text_move_x_5 = 0
        self.text_move_y_0 = 0
        self.text_move_y_1 = 0
        self.text_move_y_2 = 0
        self.text_move_y_3 = 0
        self.text_move_y_4 = 0
        self.text_move_y_5 = 0
        self.text_move_y_6 = 0

        # block is_move
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False

        # block_is_draw
        self.is_block_draw_0 = True
        self.is_block_draw_1 = True
        self.is_block_draw_2 = True
        self.is_block_draw_3 = True
        self.is_block_draw_4 = True
        self.is_block_draw_5 = True
        self.is_block_draw_6 = True

        # beem is_draw
        self.is_beem_draw_0 = False
        self.is_beem_draw_1 = False
        self.is_beem_draw_2 = False
        self.is_beem_draw_3 = False
        self.is_beem_draw_4 = False
        self.is_beem_draw_5 = False
        self.is_beem_draw_6 = False

        # ブロックが１つになったときの表示時間確保用変数(この変数が定数を超えると表示を終了)
        self.block_count_1_wait_time = 0

    def update_block_and_beem(self):
        if (self.is_block_move_0 or
            self.is_block_move_1 or
            self.is_block_move_2 or
            self.is_block_move_3 or
            self.is_block_move_4 or
            self.is_block_move_5 or
                self.is_block_move_6):
            # ブロックが落下している途中は、ビームがでる処理のみ行う
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
                self.is_block_move_1 = True
                self.is_beem_draw_1 = True
                self.pop_num = 1
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
        if block_count == 7:
            self.yazirusi_position_dict = {1: 21, 2: 32, 3: 43, 4: 54, 5: 65}
        if block_count == 5:
            if self.yazirusi_position == 1 or self.yazirusi_position == 2:
                self.yazirusi_position = 3
            self.yazirusi_position_dict = {3: 43, 4: 54, 5: 65}
        if block_count == 3:
            if self.yazirusi_position == 3 or self.yazirusi_position == 4:
                self.yazirusi_position = 5
            self.yazirusi_position_dict = {5: 65}
        if block_count == 1:
            self.yazirusi_position = 6
            self.yazirusi_position_dict = {6: 76}

    def update_question_list(self, question_list, block_num_list, w_block_list, pop_num):
        # self.question_list, self.yazirusi_position_list, self.yazirusi_position_dict, self.random_w_block_list = self.update_question_list(self.question_list, self.yazirusi_position_list, self.random_w_block_list, pop_num=self.yazirusi_position)
        # def update_question_list(question_list, block_num_list, pop_num):

        # memo-----------------------------------------------------------------
        # question_list = [2, 1, 9, 8, 6, 9, 4]
        # question_list
        # block_num_list = [0, 1, 2, 3, 4, 5, 6]
        # w_block_list = [100, 90, 40, 30, 110, 50, 60]
        # pop_num = 1
        # question_list
        # block_num_list
        # block_num_dict
        # w_block_list
        # memo-----------------------------------------------------------------

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
        # pop_num_raight
        pop_num_left = pop_num  # 取り除いた値の右の要素の順番
        # pop_num_left
        sum_num = question_list[pop_num_raight] + question_list[pop_num_left]
        # sum_num
        # print(f"sum_num_raight:{question_list[pop_num_raight]}")
        # print(f"sum_num_raight:{question_list[pop_num_left]}")
        # print(f"sum_num:{sum_num}")

        # 取り除いた要素の両側の要素を取り除く
        question_list.pop(pop_num_raight)
        question_list.pop(pop_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している
        # block_num_list.pop(pop_num_raight)
        block_num_list.pop(pop_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している

        question_list.insert(pop_num - 1, sum_num)  # -1: 位置の調整(固定)

        block_num_dict = {key: value for key, value in zip(block_num_list, question_list)}
        # print(f"question_list(合計値挿入):{question_list}")

        return question_list, block_num_list, block_num_dict, w_block_list

    def update_block(self):
        # ブロックの数が減ったことによるブロックの配置変更(block数5でも稼働するようにリセットするのが目的
        if self.block_count == 5:
            # block_is_draw
            self.is_block_draw_0 = False
            self.is_block_draw_1 = False
            self.is_block_draw_2 = True
            self.is_block_draw_3 = True
            self.is_block_draw_4 = True
            self.is_block_draw_5 = True
            self.is_block_draw_6 = True

            self.w_block_2 = self.random_w_block_list[0]
            self.w_block_3 = self.random_w_block_list[1]
            self.w_block_4 = self.random_w_block_list[2]
            self.w_block_5 = self.random_w_block_list[3]
            self.w_block_6 = self.random_w_block_list[4]
        elif self.block_count == 3:
            # block_is_draw
            self.is_block_draw_0 = False
            self.is_block_draw_1 = False
            self.is_block_draw_2 = False
            self.is_block_draw_3 = False
            self.is_block_draw_4 = True
            self.is_block_draw_5 = True
            self.is_block_draw_6 = True
            self.w_block_4 = self.random_w_block_list[0]
            self.w_block_5 = self.random_w_block_list[1]
            self.w_block_6 = self.random_w_block_list[2]

        self.block_move_y_0 = 0
        self.block_move_y_1 = 0
        self.block_move_y_2 = 0
        self.block_move_y_3 = 0
        self.block_move_y_4 = 0
        self.block_move_y_5 = 0
        self.block_move_y_6 = 0
        self.block_move_x_2 = 0
        self.block_move_x_3 = 0
        self.block_move_x_4 = 0
        self.block_move_x_5 = 0
        self.block_move_x_6 = 0
        self.is_block_move_0 = False
        self.is_block_move_1 = False
        self.is_block_move_2 = False
        self.is_block_move_3 = False
        self.is_block_move_4 = False
        self.is_block_move_5 = False
        self.is_block_move_6 = False
        self.is_update_all = False

    def move_calculate(self):
        """
        シグナルからブロック・数字の動く量を計算する
        動きが完了したあとに、ブロック数が減ることによる変数のリセットも行う(self.is_update_allによる)
        """
        # ゲーム残り時間の計算
        self.countdown_game_time -= 1

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
                # self.block_move_y_2 = 0
                self.text_move_x_3 = 0
                self.text_move_y_2 = 0
                self.is_block_move_3 = False
                self.is_block_draw_2 = False
                self.is_block_draw_3 = False
                self.is_update_all = True
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
        if self.is_update_all:
            print("is_update_all_start")
            # print(f"yazirusi_position{self.yazirusi_position_list}")
            print(f"yazirusi_position{self.yazirusi_position}")
            print(self.yazirusi_position)
            print(self.question_list)
            self.question_list, self.yazirusi_position_list, self.yazirusi_position_dict, self.random_w_block_list = self.update_question_list(self.question_list, self.yazirusi_position_list, self.random_w_block_list, pop_num=self.pop_num)
            self.block_count = len(self.question_list)
            self.update_yazirusi(block_count=len(self.question_list))
            print(self.question_list)
            self.update_block()

    def move_yazirusi(self, is_up):
        if is_up:
            self.yazirusi_position -= 1
            if self.yazirusi_position < min(self.yazirusi_position_dict):
                self.yazirusi_position = min(self.yazirusi_position_dict)
        if is_up is False:
            self.yazirusi_position += 1
            if self.yazirusi_position > 5:  # ５はブロックの一番下(6)から1つ上の(5)を設定している
                self.yazirusi_position = 5
                if len(self.question_list) == 1:
                    self.yazirusi_position = 6

    def question_create(self, element_count):
        # def question_create(element_count):
        # element_count = 7  # 必ず奇数とすること

        remove_time = int((element_count - 1)/2)

        # 難易度によって発生する整数の範囲を変えるための辞書
        max_number_dict = {HARD:100, NORMAL:10, EASY:3}
        max_number = max_number_dict[self.difficulty]

        # 難易度で指定した範囲の整数を格納したlistを作成(長さはelement_countにより設定)
        random_list = [random.randint(1, max_number) for _ in range(element_count)]
        random_list_base = copy.copy(random_list)
        yazirusi_position_list = list(range(7))  # 矢印のポジション管理のリストを作成(random_listと一緒に管理する)
        # print(f"random_list(開始状態):{random_list}")

        # # key:self.yazirusi_position, value:question_list →blockの位置管理に使用
        random_list_base_dict = {key: value for key, value in zip(yazirusi_position_list, random_list_base)}

        for i in range(remove_time):
            # print(f"試行回数:{i + 1}")
            # print(f"random_list(開始状態):{random_list}")

            # 取り除く要素を指定(一番上と下は取り除かない)
            pop_num = random.randint(1, element_count - 2)
            # print(f"pop_num:{pop_num}")

            # ランダムに指定した要素を取り除く
            random_list.pop(pop_num)

            # 取り除いた要素の両隣の要素を合計する
            sum_num_raight = pop_num - 1  # 取り除いた値の左の要素の順番
            sum_num_left = pop_num  # 取り除いた値の右の要素の順番
            sum_num = random_list[sum_num_raight] + random_list[sum_num_left]
            # print(f"sum_num_raight:{random_list[sum_num_raight]}")
            # print(f"sum_num_raight:{random_list[sum_num_left]}")
            # print(f"sum_num:{sum_num}")

            # 取り除いた要素の両側の要素を取り除く
            random_list.pop(sum_num_raight)
            random_list.pop(sum_num_left - 1)  # 1行上の要素の削除で１つ順番がズレるため-1している

            random_list.insert(pop_num - 1, sum_num)  # -1: 位置の調整(固定)
            # print(f"random_list(合計値挿入):{random_list}")

            element_count = len(random_list)
            # print(f"element_count:{element_count}")

        return random_list_base, yazirusi_position_list, random_list_base_dict, random_list[0]

    def rand_ints_nodup(self, a, b, c, k):
        """
        重複なしのリストの作成
        params:
        a, b, c(int): a ~ b の間(間隔c)でk個選択する
        """
        # 重複なしリストの作成
        ns = []
        while len(ns) < k:
            n = random.randrange(a, b, c)
            if not n in ns:
                ns.append(n)
        return ns

    def draw(self):
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
        if 60 < self.countdown_game_start < 90:
            pyxel.blt(70, 50, 1, 40, 64, 16, 16, 0)  # カウントダウン(3)
        if 30 < self.countdown_game_start <= 60:
            pyxel.blt(70, 50, 1, 56, 64, 16, 16, 0)  # カウントダウン(2)
        if self.countdown_game_start <= 30:
            pyxel.blt(70, 50, 1, 72, 64, 16, 16, 0)  # カウントダウン(1)

    def draw_result_scene(self):
        if self.difficulty == HARD:
            pyxel.text(58, 30, "level hard", 7)
        elif self.difficulty == NORMAL:
            pyxel.text(58, 30, "level normal", 7)
        elif self.difficulty == EASY:
            pyxel.text(58, 30, "level easy", 7)
        if self.score >= 50:
            pyxel.text(55, 40, f"your score {self.score}", pyxel.frame_count % 16)
        elif self.score >= 30:
            pyxel.text(55, 40, f"your score {self.score}", 10)
        elif self.score >= 0:
            pyxel.text(55, 40, f"your score {self.score}", 10)
        else:
            pyxel.text(55, 40, f"your score {self.score}", 12)
        if self.scene_result_select_menu == SCENE_TITLE:
            pyxel.text(62, 80, "main menu", pyxel.frame_count % 16)
            pyxel.text(62, 100, "  retry  ", 7)
        if self.scene_result_select_menu == SCENE_PLAY:
            pyxel.text(62, 80, "main menu", 7)
            pyxel.text(62, 100, "  retry  ", pyxel.frame_count % 16)

    def draw_title_scene(self):
        pyxel.text(55, 60, "please select", 7)
        pyxel.blt(32, 30, 1, 40, 48, 64, 16, 0)  # タイトル(PLUS)
        pyxel.blt(100, 30, 1, 104, (pyxel.frame_count % 7)*16, 16, 16, 0)  # タイトル(N)
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
        # memo------------------------------------------------------------------
        # 00 08 * * 6 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_am_8_00.sh
        # 30 9-16 * * 6 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_9to16_30min_interval.sh
        # 00 10-16 * * 6 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_9to16_30min_interval.sh
        # 30 9-16 * * 7 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_9to16_30min_interval.sh
        # 00 10-16 * * 7 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_9to16_30min_interval.sh
        # 00 09 * * 6 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_am_9_00.sh
        # 00 09 * * 7 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/shell_script/every_satruday_and_sunday_am_9_00.sh
        # memo------------------------------------------------------------------

        # memo------------------------------------------------------------------
        # collections.OrderedDict([('k1', 1), ('k2', 2), ('k3', 3)])
        # collections.OrderedDict([])
        # question_list, yazirusi_position_list, block_num_dict, answer = question_create(element_count=7)
        # question_list
        # yazirusi_position_list
        # block_num_dict
        # question_list_, block_num_list_, block_num_dict_ = update_question_list(question_list, yazirusi_position_list, pop_num=3)
        # question_list_
        # block_num_list_
        # block_num_dict_
        # question_list_dict = {0: self.block_move_x_0
        #                       1: self.block_move_x_1,
        #                       2: self.block_move_x_2,
        #                       3: self.block_move_x_3,
        #                       4: self.block_move_x_4,
        #                       5: self.block_move_x_5,
        #                       6: self.block_move_x_6,
        #                       }
        # memo------------------------------------------------------------------

        # text and block move info

        # memo------------------------------------------------------------------
        # yazirusi_position = 1
        # block_position_x_dict
        # block_position_y_dict
        # yazirusi_position_dict
        # yazirusi_position_dict[yazirusi_position]
        # question_list
        # block_num_list
        # block_num_dict
        # block_position_x_dict[yazirusi_position] -= 1
        # memo------------------------------------------------------------------

        # Draw_countdown
        pyxel.text(121, 8, "time", 1)
        pyxel.text(122, 8, "time", 7)
        pyxel.text(129, 16, str(self.countdown_game_time // 30), 1)
        pyxel.text(130, 16, str(self.countdown_game_time // 30), 7)

        # Draw score
        pyxel.text(121, 32, "SCORE", 1)
        pyxel.text(122, 32, "SCORE", 7)
        # s = f"SCORE {self.score:>4}"
        pyxel.text(129, 40, str(self.score), 1)
        pyxel.text(130, 40, str(self.score), 7)
        # pyxel.blt(118, 6, 1, 40, 0, 27, 17, 0)  # 枠

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
            pyxel.blt(16                      , 76 + self.block_move_y_6, 1, 0, self.w_block_6, 40, 10)

        if self.block_count == 7:
            # Draw text
            pyxel.text(35                      , 13 + self.text_move_y_0, str(self.question_list[0]), 1)
            pyxel.text(36                      , 13 + self.text_move_y_0, str(self.question_list[0]), 7)
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
            pyxel.text(35                      , 79 + self.text_move_y_6, str(self.question_list[6]), 1)
            pyxel.text(36                      , 79 + self.text_move_y_6, str(self.question_list[6]), 7)
        elif self.block_count == 5:
            # Draw text
            # pyxel.text(35                      , 13 + self.block_move_y_0, str(self.question_list[0]), 1)
            # pyxel.text(36                      , 13 + self.block_move_y_0, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 7)
            pyxel.text(35 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 1)
            pyxel.text(36 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 7)
            pyxel.text(35 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 1)
            pyxel.text(36 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 7)
            pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[2]), 1)
            pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[2]), 7)
            pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[3]), 1)
            pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[3]), 7)
            pyxel.text(35                     , 79 + self.text_move_y_6, str(self.question_list[4]), 1)
            pyxel.text(36                     , 79 + self.text_move_y_6, str(self.question_list[4]), 7)
        elif self.block_count == 3:
            # Draw text
            # pyxel.text(35                      , 13 + self.block_move_y_0, str(self.question_list[0]), 1)
            # pyxel.text(36                      , 13 + self.block_move_y_0, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 7)
            # pyxel.text(35 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 1)
            # pyxel.text(36 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 7)
            pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 1)
            pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 7)
            pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 1)
            pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 7)
            pyxel.text(35                     , 79 + self.text_move_y_6, str(self.question_list[2]), 1)
            pyxel.text(36                     , 79 + self.text_move_y_6, str(self.question_list[2]), 7)
        elif self.block_count == 1:
            # Draw text
            # pyxel.text(35                      , 13 + self.block_move_y_0, str(self.question_list[0]), 1)
            # pyxel.text(36                      , 13 + self.block_move_y_0, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.block_move_x_1, 24 + self.block_move_y_1, str(self.question_list[1]), 7)
            # pyxel.text(35 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 1)
            # pyxel.text(36 + self.text_move_x_2, 35 + self.text_move_y_2, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.text_move_x_3, 46 + self.text_move_y_3, str(self.question_list[1]), 7)
            # pyxel.text(35 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 1)
            # pyxel.text(36 + self.text_move_x_4, 57 + self.text_move_y_4, str(self.question_list[0]), 7)
            # pyxel.text(35 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 1)
            # pyxel.text(36 + self.text_move_x_5, 68 + self.text_move_y_5, str(self.question_list[1]), 7)
            pyxel.text(35                     , 79 + self.text_move_y_6, str(self.question_list[0]), 1)
            pyxel.text(36                     , 79 + self.text_move_y_6, str(self.question_list[0]), 7)
            self.block_count_1_wait_time += 1
            if self.question_list[0] == self.answer and self.block_count_1_wait_time == 1:
                pyxel.play(3, 8)
                self.score += 10
            elif self.question_list[0] != self.answer and self.block_count_1_wait_time == 1:
                pyxel.play(3, 6)
                self.score -= 10
            if self.block_count_1_wait_time > 20:
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
        # pyxel.blt(90, 65, 1, 55, 120, 18, 22, 1)  # 波動２
        # pyxel.blt(90, 65, 1, 87, 120, 16, 22, 1)  # 波動３
        pyxel.blt(98, 61, 1, 108, 120, 19, 22, 1)  # 波動３

        # Draw yazirusi
        yazirusi_y = self.yazirusi_position_dict[self.yazirusi_position]

        pyxel.blt(60, yazirusi_y, 1, 40, 32, 10, 10, 0)


App()
