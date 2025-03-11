from dlx import DLX
import random


def __add_num(dlx: DLX, i, v):
    r = i * 9 + v - 1
    x = i % 9
    y = i // 9
    g = (y // 3) * 3 + x // 3

    # 1-81 (x,y)中有数字
    dlx.dlx_add_node(r, i + 1)

    # 82-162 x行中有数字v
    dlx.dlx_add_node(r, x * 9 + v + 81)

    # 163-243 y列中有数字v
    dlx.dlx_add_node(r, y * 9 + v + 162)

    # 244-324 所在宫中有数字v
    dlx.dlx_add_node(r, g * 9 + v + 243)


def get_sudu_answer(question, maxans=0, answer=None):
    dlx = DLX(81 * 4)
    for i in range(81):
        if question[i]:
            __add_num(dlx, i, question[i])
        else:
            for v in range(9):
                __add_num(dlx, i, v + 1)

    ans_cnt = dlx.dlx_dance(maxans)
    if ans_cnt > 0 and answer != None:
        # for ans in dlx.all_ans:
        for rowid in dlx.all_ans[0]:
            v = rowid % 9 + 1
            answer[rowid // 9] = v

    return ans_cnt


class SUDU:

    def arr2str(arr):
        sret = ""
        for i in range(81):
            if i > 0 and i % 27 == 0:
                sret += "---+---+---\n"
            sret += str(arr[i])
            if (i + 1) % 9 == 0:
                sret += "\n"
            elif (i + 1) % 3 == 0:
                sret += "|"
        return sret

    def __init__(self):
        self.val = [0 for _ in range(81)]
        self.meb = []
        self.qus = [0 for _ in range(81)]
        self.ans = [0 for _ in range(81)]
        random.seed()

    def __standEnd(self):
        for y in range(9):
            for x in range(9):
                if y == 0:
                    self.ans[x] = x + 1
                elif y % 3 == 0:
                    self.ans[y * 9 + x] = self.ans[(y - 1) * 9 + (x + 4) % 9]
                else:
                    self.ans[y * 9 + x] = self.ans[(y - 1) * 9 + (x + 3) % 9]
        self.val = self.ans[:]

    def __randomEnd(self):
        tmp = [i + 1 for i in range(9)]
        for y in range(9):  # 随机生成\对角线三宫
            if y % 3 == 0:
                random.shuffle(tmp)
            for x in range(9):
                if y // 3 == x // 3:
                    self.val[y * 9 + x] = tmp[(y % 3) * 3 + x % 3]
                else:
                    self.val[y * 9 + x] = 0

        get_sudu_answer(self.val, 1, self.ans)  #  生成终盘

        for g in range(3):  # 列交换(在同一宫内)
            for i in range(3):
                y1 = random.randint(0, 2)
                y2 = random.randint(0, 2)
                if y1 == y2:
                    continue
                for x in range(9):
                    c1 = (g * 3 + y1) * 9 + x
                    c2 = (g * 3 + y2) * 9 + x
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]

        for g in range(3):  # 行交换(在同一宫内)
            for i in range(3):
                x1 = random.randint(0, 2)
                x2 = random.randint(0, 2)
                if x1 == x2:
                    continue
                for y in range(9):
                    c1 = y * 9 + g * 3 + x1
                    c2 = y * 9 + g * 3 + x2
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]

        for i in range(3):  # // 宫交换
            g1 = random.randint(0, 2)
            g2 = random.randint(0, 2)
            if g1 == g2:
                continue
            for y in range(9):  # 垂直
                for x in range(3):
                    c1 = y * 9 + g1 * 3 + x
                    c2 = y * 9 + g2 * 3 + x
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]

            for x in range(9):  # 水平
                for y in range(3):
                    c1 = (g1 * 3 + y) * 9 + x
                    c2 = (g2 * 3 + y) * 9 + x
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]

        random.shuffle(tmp)  # 数字随机替换
        for i in range(81):
            self.ans[i] = tmp[self.ans[i] - 1]

        # { // 矩阵变换 翻转 垂直 水平 \对角线 /对角线 // 旋转 90 180 270
        if random.randint(0, 1):  # 垂直
            for y in range(9):
                for x in range(4):
                    c1 = y * 9 + x
                    c2 = y * 9 + (8 - x)
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]
        if random.randint(0, 1):  # 水平
            for x in range(9):
                for y in range(4):
                    c1 = y * 9 + x
                    c2 = (8 - y) * 9 + x
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]
        if random.randint(0, 1):  # \对角线
            for y in range(9):
                for x in range(y + 1, 9):
                    c1 = y * 9 + x
                    c2 = x * 9 + y
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]
        if random.randint(0, 1):  # /对角线
            for y in range(9):
                for x in range(8 - y):
                    c1 = y * 9 + x
                    c2 = (8 - x) * 9 + 8 - y
                    self.ans[c1], self.ans[c2] = self.ans[c2], self.ans[c1]

        #     int buff[81];
        #     for (int r = rand() % 4; r > 0; r--) { // 旋转 90 180 270
        #         for (int y = 0; y < 9; y++)        // 旋转 (90 顺时针
        #             for (int x = 0; x < 9; x++)
        #                 buff[x * 9 + 8 - y] = answer[y * 9 + x];
        #         for (int i = 0; i < 81; i++)
        #             answer[i] = buff[i];

        self.val = self.ans[:]

    def __dig(self):
        total = 0
        while True:
            cnt = 0
            dig_idx = [i for i in range(81) if self.val[i]]
            random.shuffle(dig_idx)
            for i in range(len(dig_idx)):
                k = dig_idx[i]
                t = self.val[k]
                self.val[k] = 0
                if self.check_answer() == 1:
                    cnt += 1
                else:
                    self.val[k] = t

            if cnt:
                total = cnt
            else:
                break

        self.qus = self.val[:]
        get_sudu_answer(self.qus, 1, self.ans)
        return total

    def check_answer(self):  # 检查是否唯一解
        return get_sudu_answer(self.val, 2)

    def check_win(self):
        for i in range(81):
            if self.val[i] != self.ans[i]:
                return False
        return True

    def check_val(self, idx, v):  # 检查是否唯一可填数
        list_mbe = [i for i in self.get_row_cell(idx // 9) if self.check_meb(i, v)]
        if len(list_mbe) == 1:
            return True

        list_mbe = [i for i in self.get_col_cell(idx % 9) if self.check_meb(i, v)]
        if len(list_mbe) == 1:
            return True

        list_mbe = [i for i in self.get_blk_cell(idx) if self.check_meb(i, v)]
        if len(list_mbe) == 1:
            return True

        return False

    def check_meb(self, idx, v):
        return (self.meb[idx] & (1 << (v - 1))) != 0 if v else False

    def set_meb(self, idx, v):
        if v:
            self.meb[idx] |= 1 << (v - 1)

    def del_meb(self, idx, v):
        if v:
            self.meb[idx] &= ~(1 << (v - 1))

    def set_val(self, idx, v):
        if self.val[idx] == v:
            return
        elif self.val[idx] == 0:
            self.val[idx] = v
            self.meb[idx] = 0
            for i in self.get_link_cell(idx):
                self.del_meb(i, v)
        elif v == 0:
            for i in self.get_link_cell(idx):
                canbe = self.val[i] == 0
                if canbe:
                    for m in self.get_link_cell(i):
                        if m != idx and self.val[m] == self.val[idx]:
                            canbe = False
                            break
                if canbe:
                    self.set_meb(i, self.val[idx])
            self.val[idx] = v
            self.meb[idx] = 511
            for i in self.get_link_cell(idx):
                if self.val[i]:
                    self.del_meb(idx, self.val[i])

    def get_row_cell(self, r):
        return {r * 9 + i for i in range(9)}

    def get_col_cell(self, c):
        return {i * 9 + c for i in range(9)}

    def get_blk_cell(self, idx):
        gy = idx // 9 // 3 * 3
        gx = idx % 9 // 3 * 3
        return {(gy + i // 3) * 9 + (gx + i % 3) for i in range(9)}

    def get_link_cell(self, idx, include_self=False):
        cells = set.union(
            self.get_row_cell(idx // 9),
            self.get_col_cell(idx % 9),
            self.get_blk_cell(idx),
        )
        if not include_self:
            cells.remove(idx)
        return cells

    def reset_meb(self):
        self.meb = [0 if v else 511 for v in self.val]
        for idx in range(81):
            v = self.val[idx]
            for i in self.get_link_cell(idx):
                self.del_meb(i, v)

    def new_question(self, question):
        if get_sudu_answer(question, 2) > 1:
            return False

        self.val = question[:]
        self.qus = question[:]
        get_sudu_answer(self.val, 1, self.ans)
        self.reset_meb()
        ilen = 0
        for i in self.qus:
            if self.qus[i] == 0:
                ilen += 1
        return ilen

    def new(self):
        self.__randomEnd()
        cnt = self.__dig()
        self.reset_meb()
        return cnt


if __name__ == "__main__":
    sd = SUDU()
    sd.new()
    print("question:")
    print(SUDU.arr2str(sd.qus))
    print("answer:")
    print(print(SUDU.arr2str(sd.ans)))
    print("meybe:")
    print(print(SUDU.arr2str(sd.meb)))
