#coding=utf-8
#!python
import wx
import os,time
import shutil
import cStringIO
from blockwindow import BlockWindow

class TestFrame(wx.Frame):
    def save(self, event):
        self.fileList = []
        tmp = self.name.GetValue()
        #self.fileList.append(tmp)
        self.fileList.append(("prossNum", self.prossNum.GetValue()))
        self.fileList.append(("timeNum", self.timeNum.GetValue()))
        self.fileList.append(("addr", self.addr.GetValue()))
        self.fileList.append(("port", self.port.GetValue()))
        self.fileList.append(("path", self.path.GetValue()))
        self.fileList.append(("param", self.param.GetValue()))

        PATH = os.getcwd()+'/'+tmp
        try:
            filetmp = open(PATH,'w')
            for tmp in self.fileList:
                filetmp.writelines(str('['+ tmp[0].capitalize() + ']\n'))
                filetmp.writelines(str(tmp[0]+'='+tmp[1]+'\n'))
                filetmp.writelines("\n")
        finally:
            if filetmp:
                filetmp.close()
        shutil.copy(PATH,os.getcwd()+"/file")
        self.Close(True)
        

    def load(self, event):
        print "load"
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "yougth test", (100,100), (400,300))  #不生效
        panel = wx.Panel(self)
        # First create the controls
        topLbl = wx.StaticText(panel, -1, "测试计划")#1 创建窗口部件
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        nameLbl = wx.StaticText(panel, -1, "名称:")
        self.name = wx.TextCtrl(panel, -1, "");
        addrLbl = wx.StaticText(panel, -1, "进程数:")
        addrLbl2 = wx.StaticText(panel, -1, "压测时间:")
        self.prossNum = wx.TextCtrl(panel, -1, "");
        self.timeNum = wx.TextCtrl(panel, -1, "");
        cstLbl = wx.StaticText(panel, -1, "addr, port:")
        self.addr  = wx.TextCtrl(panel, -1, "", size=(150,-1));
        self.port = wx.TextCtrl(panel, -1, "", size=(50,-1));
        pathLbl = wx.StaticText(panel, -1, "path:")
        self.path = wx.TextCtrl(panel, -1, "");
        paramLbl = wx.StaticText(panel, -1, "参数:")
        self.param = wx.TextCtrl(panel, -1, "");
        cancelBtn = wx.Button(panel, -1, "载入")
        cancelBtn.Bind(wx.EVT_BUTTON, self.load)
        
        saveBtn = wx.Button(panel, -1, "保存")
        saveBtn.Bind(wx.EVT_BUTTON, self.save)
        # Now do the layout.
        # mainSizer is the top-level one that manages everything
#2 垂直的sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(panel), 0,
                wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        # addrSizer is a grid that holds all of the address info
#3 地址列
        addrSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        addrSizer.AddGrowableCol(1)
        addrSizer.Add(nameLbl, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.name, 0, wx.EXPAND)
        addrSizer.Add(addrLbl, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.prossNum, 0, wx.EXPAND)
#4 带有空白空间的行
        #addrSizer.Add((10,10)) # some empty space
        addrSizer.Add(addrLbl2, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.timeNum, 0, wx.EXPAND)
        addrSizer.Add(cstLbl, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        # the city, state, zip fields are in a sub-sizer
#5 水平嵌套
        cstSizer = wx.BoxSizer(wx.HORIZONTAL)
        cstSizer.Add(self.addr, 1)
        cstSizer.Add(self.port, 0, wx.EXPAND)
        addrSizer.Add(cstSizer, 0, wx.EXPAND)
#6 电话和电子邮箱
        addrSizer.Add(pathLbl, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.path, 0, wx.EXPAND)
        addrSizer.Add(paramLbl, 0,
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.param, 0, wx.EXPAND)
        # now add the addrSizer to the mainSizer
#7 添加Flex sizer
        mainSizer.Add(addrSizer, 0, wx.EXPAND|wx.ALL, 10)
        # The buttons sizer will put them in a row with resizeable
        # gaps between and on either side of the buttons
#8 按钮行
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add((20,20), 1)
        btnSizer.Add(cancelBtn)
        btnSizer.Add((20,20), 1)
        btnSizer.Add(saveBtn)
        btnSizer.Add((20,20), 1)
        mainSizer.Add(btnSizer, 0, wx.EXPAND|wx.BOTTOM, 10)
        panel.SetSizer(mainSizer)
        # Fit the frame to the needs of the sizer.  The frame will
        # automatically resize the panel as needed.  Also prevent the
        # frame from getting smaller than this size.
        mainSizer.Fit(self)  #调整到合适的大小
        mainSizer.SetSizeHints(self)
    def OnExit():
        print "exit"

class MainFrame(wx.Frame):
    def __init__(self):
        self.cnt = 0
        wx.Frame.__init__(self, None, -1, "Main", size=(820,670))
        panel = wx.Panel(self)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        lable = ["start.png", "stop.png", "statue.png", "clear.png"]
        for tmp in lable:
            #img1 = wx.Image(tmp, wx.BITMAP_TYPE_ANY)
            #width = img1.GetWidth()
            #height = img1.GetHeight()
            #pps = img1.Scale(width/3, height/3)
            data = open(tmp, "rb").read()
            stream = cStringIO.StringIO(data)
            bmp = wx.BitmapFromImage(wx.ImageFromStream(stream))
            self.button = wx.BitmapButton(panel, -1, bmp, pos=(10,20))
            #bw = BlockWindow(self, label=tmp, size=(75,30))
            topsizer.Add(self.button,flag = wx.EXPAND)
        mainsizer.Add(topsizer, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        mainsizer.Add((-1, 5))
        mainsizer.Add(wx.StaticLine(panel), 0,
                wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        mainsizer.Add((-1, 120))
        lable = ["Label","Total", "Success", "Fail", "Average", "Query/s"]
        value = ["总体", "0", "0", "0","0.000000","0.000000"]
        lablesizer = wx.BoxSizer(wx.HORIZONTAL)
        valuesizer = wx.BoxSizer(wx.HORIZONTAL)
        viewsizer = wx.BoxSizer(wx.VERTICAL)
        for tmp in lable:
            lableButt = wx.Button(panel, -1, tmp, size= (120,30))
            #bw = BlockWindow(self, label=tmp, size=(75,ss30)) #panel会覆盖底层的panel
            lablesizer.Add(lableButt, flag = wx.EXPAND)
        for tmp in value:
            valueButt = wx.Button(panel, -1, tmp, size=(120,30))
            #bw = BlockWindow(self, label=tmp, size=(75,30))
            valuesizer.Add(valueButt, flag = wx.EXPAND)
        '''
        yougth = "This is an example of static text"
        while True:
            self.cnt = self.cnt + 1
            ps = yougth + str(self.cnt)
            wx.StaticText(panel, -1, ps, (400, 10))
            time.sleep(2)
        '''
        self.Butt = wx.Button(panel, -1, "wode", size= (120,30))
        self.Bind(wx.EVT_BUTTON, self.Onclick)
        
        #richLabel = wx.StaticText(panel, -1, "Rich Text")
        self.richText = wx.TextCtrl(panel, -1, 
                "If supported by the native control, this is reversed, and this is a different font.",
                size=(200, 100), style=wx.TE_MULTILINE|wx.TE_RICH2) #创建丰富文本控件
        self.richText.SetInsertionPoint(0)
        self.richText.SetStyle(44, 52, wx.TextAttr("white", "black")) #设置文本样式
        points = self.richText.GetFont().GetPointSize() 
        f = wx.Font(points + 3, wx.ROMAN, wx.ITALIC, wx.BOLD, True) #创建一个字体
        self.richText.SetStyle(68, 82, wx.TextAttr("blue", wx.NullColour, f)) #用新字体设置样式
        
        viewsizer.Add(lablesizer, 0, wx.EXPAND|wx.TOP, 1)
        viewsizer.Add(valuesizer, 0, wx.EXPAND|wx.TOP, 1) #边框周围像素
        mainsizer.Add(viewsizer, 0, wx.EXPAND|wx.BOTTOM, 1)
        mainsizer.Add(self.Butt, 0 ,wx.EXPAND|wx.BOTTOM, 1)
        mainsizer.Add((-1, 230))
        mainsizer.Add(self.richText, 0, wx.EXPAND|wx.BOTTOM, 1)
        panel.SetSizer(mainsizer) 

        #mainsizer.Fit(self)
        #mainsizer.SetSizeHints(self)

    def Onclick(self , event):
        while(self.cnt<5):
            self.cnt = self.cnt + 1
            self.Butt.SetLabel(str(self.cnt))
            time.sleep(0.5)
        self.richText.SetLabel("i am yougth")
        
        
        
        

if __name__ == '__main__':
    app = wx.PySimpleApp()
    #TestFrame().Show()
    #app.MainLoop()
    MainFrame().Show()
    app.MainLoop()
