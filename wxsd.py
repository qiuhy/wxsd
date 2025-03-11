import wx
from sudu import SUDU
from icon import AppIcon


class MainFrm(wx.Frame):

    CELLSIZE = 42

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self.sudu = SUDU()
        self.on_init_face()
        self.on_init_data()

    def on_init_face(self):
        self.SetIcon(AppIcon.GetIcon())

        self.SetSize(self.FromDIP(wx.Size(640, 480)))

        sizer = wx.FlexGridSizer(2, 1, 0, 0)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(1)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(box)
        sizer.Add(panel, flag=wx.EXPAND | wx.ALL)
        btnText = ("新局", "答案", "导入", "导出")
        for i in range(len(btnText)):
            btn = wx.Button(panel, size=(self.CELLSIZE, self.CELLSIZE))
            btn.LabelText = btnText[i]
            btn.Bind(wx.EVT_BUTTON, lambda e, mark=i: self.on_btn_click(e, mark))
            box.Add(btn)

        box.AddSpacer(15)
        chk = wx.CheckBox(panel, wx.ID_ANY, "M")
        chk.Bind(wx.EVT_CHECKBOX, self.on_change_mode)
        box.Add(chk, flag=wx.EXPAND | wx.ALL)

        box.AddSpacer(15)
        for i in range(9):
            btn = wx.Button(panel, size=(self.CELLSIZE, self.CELLSIZE))
            btn.LabelText = str(i + 1)
            btn.Bind(wx.EVT_BUTTON, lambda e, mark=i + 11: self.on_btn_click(e, mark))
            box.Add(btn)

        panel2 = wx.Panel(self)
        panel2.BackgroundColour = wx.WHITE
        panel2.BackgroundStyle = wx.BG_STYLE_PAINT
        panel2.Bind(wx.EVT_MOUSE_EVENTS, self.on_DC_MouseEvent)
        panel2.Bind(wx.EVT_SIZE, self.on_resize)
        panel2.Bind(wx.EVT_PAINT, self.on_paint)

        sizer.Add(panel2, flag=wx.EXPAND | wx.ALL)

        # self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.SetSizer(sizer)
        self.Centre(wx.BOTH)

        self.client = panel2

    def on_init_data(self):
        self.curRow = None
        self.curCol = None
        self.sudu.new()
        self.selectNum = []
        self.selectCell = []

        self.cellMode = True
        self.selectMeb = {}

    def on_key_down(self, event: wx.KeyEvent):
        if self.curCol == None or self.curRow == None:
            return

        ch = event.GetUnicodeKey()
        if ch != wx.WXK_NONE:
            if ch >= 0x30 and ch <= 0x39:  # 0-9
                n = ch - 0x30
                if event.controlDown:
                    if n == 0:
                        return
                    self.on_switch_meb(n)
                elif event.HasAnyModifiers() == False:
                    idx = self.curRow * 9 + self.curCol
                    if self.sudu.qus[idx]:
                        return
                    self.on_set_value(idx, n)
        else:
            key = event.GetKeyCode()
            if key == wx.WXK_RETURN:
                pass

    def get_cell_index(self, pos):
        for r in range(9):
            for c in range(9):
                rt = self.get_cell_rect(c, r)
                if rt.Contains(pos):
                    return r * 9 + c
        return None

    def on_DC_MouseEvent(self, event: wx.MouseEvent):
        pos = event.GetPosition()
        idx = self.get_cell_index(pos)
        if idx == None:
            return
        if self.cellMode:
            if event.LeftDown():
                self.on_select_cell(idx, event.controlDown, event.shiftDown)
            elif event.LeftDClick():
                self.on_set_posable_val(idx)
            elif event.Dragging() and event.leftIsDown:
                self.on_select_cell(idx, False, True)
        elif event.LeftDown():
            for v in range(1, 10):
                rect = self.get_meb_rect(idx % 9, idx // 9, v)
                if rect.Contains(pos):
                    if self.selectMeb.get(idx):
                        del self.selectMeb[idx]
                    else:
                        self.selectMeb[idx] = v
                    self.on_draw_cell(wx.BufferedDC(wx.ClientDC(self.client)), idx)

    def on_switch_meb(self, v):
        dc = wx.BufferedDC(wx.ClientDC(self.client))
        for idx in self.selectCell:
            if self.sudu.val[idx] == 0:
                if self.sudu.check_meb(idx, v):
                    self.sudu.del_meb(idx, v)
                else:
                    self.sudu.set_meb(idx, v)
                self.on_draw_cell(dc, idx)

    def on_change_mode(self, event):
        self.cellMode = not event.IsChecked()

    def on_set_value(self, idx, v):
        self.sudu.set_val(idx, v)
        self.on_draw()
        if self.sudu.check_win():
            stip = "你赢了！\n 重新开始？"
            if wx.MessageBox(stip, self.Name, wx.OK | wx.CANCEL) == wx.CANCEL:
                return
            self.on_init_data()
            self.on_draw()

    def on_set_posable_val(self, idx):
        if self.sudu.val[idx]:
            return

        list_meb = [v for v in range(1, 10) if self.sudu.check_meb(idx, v)]
        if len(list_meb) == 1:
            return self.on_set_value(idx, list_meb[0])
        if len(self.selectNum):
            if self.sudu.check_val(idx, self.selectNum[0]):
                return self.on_set_value(idx, self.selectNum[0])
        # for i in range(9):
        #     if self.get_meb_rect(idx % 9, idx // 9, i + 1).Contains(pos):
        #         return self.on_set_value(idx, i + 1)

    def on_btn_click(self, event, mark):
        if mark == 0:
            self.on_init_data()
            self.on_draw()
        elif mark == 1:
            self.show_answer()
        elif mark == 2:
            self.on_import()
        elif mark == 3:
            self.on_export()

        elif mark > 10:
            self.on_select_num(mark - 10)

    def on_resize(self, event):
        sz = self.client.Size
        minsz = min(sz.Width, sz.Height)
        self.CELLSIZE = minsz // 10
        szGame = self.CELLSIZE * 9 + 24
        x = (sz.Width - szGame) // 2
        y = (sz.Height - szGame) // 2
        self.pt0 = wx.Point(x, y)
        self.on_draw()

    def on_paint(self, event):
        self.on_draw(wx.BufferedPaintDC(self.client))

    def show_answer(self):
        wx.MessageBox(self.sudu.arr2str(self.sudu.ans), self.Name)

    def on_import(self):
        cbd = wx.TheClipboard
        lstcopy = []
        if cbd.Open():
            data = wx.TextDataObject()
            if cbd.GetData(data):
                # .5.1.4..8......7..6....2..4..78...1...8...6...3...75..2..9....3..6......9..2.1.7.
                lstcopy = [int(c) if c.isdecimal() else 0 for c in data.GetText()]
            cbd.Close()
        if len(lstcopy) > 80:
            stip = "是否使用以下数据替换当前?\n" + SUDU.arr2str(lstcopy)
            if wx.MessageBox(stip, self.Name, wx.OK | wx.CANCEL) == wx.CANCEL:
                return
            self.sudu.new_question(lstcopy)
            self.on_draw()
        else:
            stip = "无效的数据格式！\n"
            wx.MessageBox(stip, self.Name)
        pass

    def on_export(self):
        cbd = wx.TheClipboard
        if cbd.Open():
            data = wx.TextDataObject(SUDU.arr2str(self.sudu.val))
            if not cbd.SetData(data):
                wx.MessageBox("导出到剪贴板失败！", self.Name)
            cbd.Close()
        pass

    def on_select_num(self, n):
        # if n in self.selectNum:
        #     self.selectNum.remove(n)
        # else:
        #     self.selectNum.append(n)
        self.selectNum = [n]
        self.on_draw()

    def on_select_cell(self, idx, ctrl=False, shift=False):
        if len(self.selectCell):
            if idx == self.curRow * 9 + self.curCol:
                return
        dc = wx.BufferedDC(wx.ClientDC(self.client))
        if ctrl:
            if idx in self.selectCell:
                self.selectCell.remove(idx)
            else:
                self.selectCell.append(idx)
            self.on_draw_cell(dc, idx)
        else:
            prvCell = self.selectCell[:]
            self.selectCell.clear()
            for i in prvCell:
                self.on_draw_cell(dc, i)
            selRow = idx // 9
            selCol = idx % 9
            if shift:
                beg_r = min(self.curRow, selRow)
                end_r = max(self.curRow, selRow)
                beg_c = min(self.curCol, selCol)
                end_c = max(self.curCol, selCol)

                for r in range(beg_r, end_r + 1):
                    for c in range(beg_c, end_c + 1):
                        self.selectCell.append(r * 9 + c)
            else:
                self.curCol = selCol
                self.curRow = selRow
                self.selectCell = [idx]

            for i in self.selectCell:
                self.on_draw_cell(dc, i)

    def on_draw(self, dc: wx.DC = None):
        if dc == None:
            dc = wx.BufferedDC(wx.ClientDC(self.client))
        pt = self.pt0
        szBorder = self.CELLSIZE * 9 + 24
        dc.Clear()

        dc.Pen = wx.Pen(wx.LIGHT_GREY, 1)
        for i in range(9):
            if i % 3 != 0:
                g = i // 3
                gap = i * (self.CELLSIZE + 2) + 1 + 2 * g
                dc.DrawLine(
                    pt.x + gap,
                    pt.y,
                    pt.x + gap,
                    pt.y + szBorder,
                )
                dc.DrawLine(
                    pt.x,
                    pt.y + gap,
                    pt.x + szBorder,
                    pt.y + gap,
                )

        dc.Pen = wx.Pen(wx.BLACK, 3)
        for i in range(4):
            gap = i * (3 * self.CELLSIZE + 8)
            dc.DrawLine(
                pt.x + gap,
                pt.y,
                pt.x + gap,
                pt.y + szBorder,
            )
            dc.DrawLine(
                pt.x,
                pt.y + gap,
                pt.x + szBorder,
                pt.y + gap,
            )

        for i in range(81):
            self.on_draw_cell(dc, i)

    def on_draw_cell(self, dc: wx.DC, idx):
        c = idx % 9
        r = idx // 9
        pt = self.get_cell_pt(c, r)
        dc.Pen = wx.TRANSPARENT_PEN
        dc.Brush = wx.WHITE_BRUSH

        # 背景
        for v in self.selectNum:
            if self.sudu.check_meb(idx, v):
                dc.Brush = wx.GREEN_BRUSH
                break
        dc.DrawRectangle(pt, wx.Size(self.CELLSIZE + 1, self.CELLSIZE + 1))

        # 焦点框
        if idx in self.selectCell:
            dc.Pen = wx.Pen(wx.YELLOW, 3)
            dc.Brush = wx.TRANSPARENT_BRUSH
            dc.DrawRectangle(pt.x + 1, pt.y + 1, self.CELLSIZE - 1, self.CELLSIZE - 1)

        if self.sudu.val[idx]:
            dc.Font = wx.Font(wx.FontInfo(self.CELLSIZE * 2 // 3))
            if self.sudu.qus[idx]:
                dc.TextForeground = wx.BLACK
            elif self.sudu.ans[idx] == self.sudu.val[idx]:
                dc.TextForeground = wx.BLUE
            else:
                dc.TextForeground = wx.RED
            dc.TextBackground = wx.TransparentColour
            rect = self.get_cell_rect(c, r)
            dc.DrawLabel(str(self.sudu.val[idx]), rect, wx.ALIGN_CENTRE)
        else:
            dc.Font = wx.Font(wx.FontInfo(self.CELLSIZE // 4))
            dc.TextForeground = wx.Colour(96, 96, 96)
            selMeb = self.selectMeb.get(idx)
            for i in range(9):
                if self.sudu.check_meb(idx, i + 1):
                    rect = self.get_meb_rect(c, r, i + 1)
                    if selMeb == i + 1:
                        dc.Pen = wx.TRANSPARENT_PEN
                        dc.Brush = wx.CYAN_BRUSH
                        dc.DrawRectangle(rect)
                        
                    dc.DrawLabel(str(i + 1), rect, wx.ALIGN_CENTRE)

    def get_cell_pt(self, c, r) -> wx.Point:
        return wx.Point(
            self.pt0.x + c * (self.CELLSIZE + 2) + 2 * (c // 3 + 1),
            self.pt0.y + r * (self.CELLSIZE + 2) + 2 * (r // 3 + 1),
        )

    def get_cell_rect(self, c, r) -> wx.Rect:
        return wx.Rect(self.get_cell_pt(c, r), wx.Size(self.CELLSIZE, self.CELLSIZE))

    def get_meb_rect(self, c, r, v) -> wx.Rect:
        idx = r * 9 + c
        if self.sudu.check_meb(idx, v):
            pt = self.get_cell_pt(c, r)
            size_meb = (self.CELLSIZE - 6) // 3
            x = pt.x + 3 + size_meb * ((v - 1) % 3)
            y = pt.y + 3 + size_meb * ((v - 1) // 3)
            return wx.Rect(x, y, size_meb, size_meb)
        return wx.Rect(0, 0, 0, 0)


if __name__ == "__main__":
    app = wx.App()
    frame = MainFrm(None, title="wxsd")
    frame.Show()
    app.MainLoop()
