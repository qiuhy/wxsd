# 十字交叉双向循环链表 Dance Link
class DLX_NODE:
    def __init__(self):
        self.row = 0
        self.col = 0
        self.Lt = 0
        self.Rt = 0
        self.Up = 0
        self.Dn = 0


class DLX:
    def __init__(self, maxcol):
        # 包括 H + C
        self.node = [DLX_NODE() for _ in range(maxcol + 1)]
        self.lcnt = [0 for _ in range(maxcol + 1)]  # 每col列元素个数
        self.hrow = {}  # 每行第一个元素 rowid:nodeidex
        self.all_ans = []
        self.ans = []

        for i in range(maxcol + 1):
            self.node[i].Lt = i - 1
            self.node[i].Rt = i + 1
            self.node[i].Up = i
            self.node[i].Dn = i
            self.lcnt[i] = 0

        self.node[0].Lt = maxcol
        self.node[maxcol].Rt = 0

    def dlx_add_node(self, r, c):
        # 修改该结点所在列链
        n = DLX_NODE()
        idx = len(self.node)

        n.row = r
        n.col = c
        n.Up = self.node[c].Up
        n.Dn = c

        self.node[n.Up].Dn = idx
        self.node[c].Up = idx

        # 修改该结点所在行链
        if self.hrow.get(r) == None:
            n.Lt = idx
            n.Rt = idx
            self.hrow[r] = idx
        else:
            n.Lt = self.node[self.hrow[r]].Lt
            n.Rt = self.hrow[r]
            self.node[n.Lt].Rt = idx
            self.node[n.Rt].Lt = idx

        self.node.append(n)
        self.lcnt[c] += 1

    def __remove_col(self, c):  #  删除列元素所在列链及其中元素所对应行
        i = self.node[c].Dn
        while i != c:
            # 枚举列链中元素
            j = self.node[i].Rt
            while j != i:
                # 枚举列链中元素所对应行链中元素并删除
                self.node[self.node[j].Dn].Up = self.node[j].Up
                self.node[self.node[j].Up].Dn = self.node[j].Dn
                self.lcnt[self.node[j].col] -= 1
                j = self.node[j].Rt
            i = self.node[i].Dn

        # 删除列链（仅需删除列元素即可删除整个列链）
        self.node[self.node[c].Lt].Rt = self.node[c].Rt
        self.node[self.node[c].Rt].Lt = self.node[c].Lt

    def __resume_col(self, c):  # 恢复列元素所在列链及其中元素所对应行
        # 恢复列链（仅需恢复列元素即可恢复整个列链）
        self.node[self.node[c].Lt].Rt = c
        self.node[self.node[c].Rt].Lt = c
        i = self.node[c].Dn
        while i != c:
            # 枚举列链中元素
            j = self.node[i].Rt
            while j != i:
                # 枚举列链中元素所对应行链中元素并恢复
                self.node[self.node[j].Dn].Up = j
                self.node[self.node[j].Up].Dn = j
                self.lcnt[self.node[j].col] += 1
                j = self.node[j].Rt
            i = self.node[i].Dn

    def dlx_dance(self, maxans=0):
        # maxans 表示要搜索的答案的个数
        col = self.node[0].Rt
        if col == 0:
            # 如果head.right==head，说明有解，输出答案
            self.all_ans.append(self.ans[:])
            return 1

        i = self.node[0].Rt
        while i:
            # 提速（寻找元素最少的列）
            if self.lcnt[i] < self.lcnt[col]:
                col = i
            i = self.node[i].Rt

        self.__remove_col(col)
        i = self.node[col].Dn
        while i != col:
            self.ans.append(self.node[i].row)
            j = self.node[i].Rt
            while j != i:  # 删除选择行链元素所在列链
                self.__remove_col(self.node[j].col)
                j = self.node[j].Rt

            self.dlx_dance(maxans)
            if maxans > 0:
                if len(self.all_ans) >= maxans:
                    return len(self.all_ans)
            self.ans.pop()

            j = self.node[i].Rt
            while j != i:  # 恢复选择行链元素所在列链
                self.__resume_col(self.node[j].col)
                j = self.node[j].Rt

            i = self.node[i].Dn

        self.__resume_col(col)  # 恢复列链
        return len(self.all_ans)


if __name__ == "__main__":
    test = [[1, 4, 7], [1, 4], [4, 5, 7], [3, 5, 6], [2, 3, 6, 7], [2, 7]]
    dlx = DLX(7)
    for i in range(len(test)):
        for v in test[i]:
            dlx.dlx_add_node(i, v)

    print("answer count:", dlx.dlx_dance())
    # 1,3,5
    print(dlx.all_ans)
