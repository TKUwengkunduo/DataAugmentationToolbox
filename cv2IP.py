from msilib.schema import Class
import cv2
import numpy as np
import random as rand
import os
import tkinter as tk
from PIL import ImageTk, Image

class BaseIP:
    @staticmethod
    def __inti__():
        pass
    
    @staticmethod
    def read_img(Path:str):
        img = cv2.imread(Path, cv2.IMREAD_UNCHANGED)
        return img

    @staticmethod
    def show_img(WindowsName:str, img, wait=int, mode=cv2.WINDOW_AUTOSIZE):
        '''
            顯示影像\n\n
                WindowsName :   視窗名稱\n
                img     :   顯示的圖片\n
                wait    :   顯示暫停秒數(0代表無限暫停)\n
                mode    :   cv2.WINDOW_AUTOSIZE(預設) / cv2.WINDOW_NORMAL / WINDOW_OPENGL\n
        '''
        cv2.namedWindow(WindowsName, mode)
        cv2.imshow(WindowsName, img)
        cv2.waitKey(wait)

    @staticmethod
    def save_img(FileName:str, img):
        '''
            儲存影像
        '''
        cv2.imwrite(FileName, img)

    @staticmethod
    def close():
        '''
            關閉所有視窗
        '''
        cv2.destroyAllWindows()


class AlphaBlend(BaseIP):
    @classmethod
    def __init__(self):
        self.Mask_list = []
        self.Puzzle_list = []

    @classmethod
    def ImportAllMask(self, Path):  #讀入所有前景
        self.Mask_list = []
        FileList = os.walk(Path)
        for root, dirs, files in FileList:
            for file in files:
                self.Mask_list.append(root+'/'+file)
        return self.Mask_list, len(self.Mask_list)
    
    @classmethod
    def ImportAllPuzzle(self, Path):    #讀入所有背景
        self.Puzzle_list = []
        FileList = os.walk(Path)
        for root, dirs, files in FileList:
            for file in files:
                self.Puzzle_list.append(root+'/'+file)
        return self.Puzzle_list, len(self.Puzzle_list)
    
    @classmethod
    def PrintAllMask(self):
        print(self.Mask_list)

    @staticmethod
    def SplitAlpha(img):
        b, g, r, Alpha = cv2.split(img)
        return b, g, r, Alpha
    
    @classmethod
    def DoBlending(self, Foreground, Background, Alpha):
        if type(Foreground)==str:
            Path = self.Mask_list[rand.randint(0,len(self.Mask_list)-1)]
            Foreground=cv2.imread(Path, cv2.IMREAD_UNCHANGED)
        b, g, r, _ = cv2.split(Foreground)
        Foreground = cv2.merge((b, g, r))
        foreground = Foreground.astype(float)
        Alpha = cv2.merge((Alpha, Alpha, Alpha))
        alpha = Alpha.astype(float)/255
        foreground = cv2.multiply(alpha, foreground)
        foreground = foreground.astype("uint8")

        rows_h, cols_h = Background.shape[:2]
        rows_l, cols_l = foreground.shape[:2]
        rows = rand.randint(0,rows_h-rows_l)
        cols = rand.randint(0,cols_h-cols_l)
        roi = Background[rows:rows+rows_l, cols:cols+cols_l]
        cimg = cv2.add(roi, foreground)
        # cimg = cv2.addWeighted(roi, 0.8, img2, 0.2, 0)
        Background[rows:rows+rows_l, cols:cols+cols_l] = cimg

        return Background
    
    @staticmethod
    def Img_Add(img1, img2):
        img2 = cv2.resize(img2, (1280,720))
        cimg = cv2.addWeighted(img1, 0.8, img2, 0.2, 0)
        return cimg

    @staticmethod
    def Img_RandomAdd(img1, img2):
        rows_h, cols_h = img1.shape[:2]
        rows_l, cols_l = img2.shape[:2]
        rows = rand.randint(0,rows_h-rows_l)
        cols = rand.randint(0,cols_h-cols_l)
        roi = img1[rows:rows+rows_l, cols:cols+cols_l]
        cimg = cv2.add(roi, img2)
        # cimg = cv2.addWeighted(roi, 0.8, img2, 0.2, 0)
        img1[rows:rows+rows_l, cols:cols+cols_l] = cimg
        return img1


class UI(AlphaBlend):
    win = tk.Tk()   #建立根視窗
    win.title("Control Window") #視窗名稱
    win.resizable(0,0)  #大小調整(0=False,1=True)
    win.config(bg="gray")    #顏色
    win.attributes("-topmost",0) #置頂(0=False,1=True)

    img_num = int(1)
    Alpha_pct = tk.IntVar()
    Now_Mask = 0

    @classmethod
    def __inti__(self):
        self.img_num = int(1)
        # self.win = tk.Tk()  #建立根視窗
    
    @classmethod
    def update(self):   #刷新頁面
        self.win.update()

    @classmethod
    def Scan_AllPuzzle(self):   #印出所有背景
        path = str(self.bge.get())
        self.ImportAllPuzzle(path)

    @classmethod
    def Scan_AllMask(self): #印出所有前景
        path = str(self.fge.get())
        self.ImportAllMask(path)

    @classmethod
    def Update_Img(self, img):  #更新圖片
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((480,270),Image.ANTIALIAS)
        TKImg = ImageTk.PhotoImage(img)
        self.show.config(image = TKImg)
        self.show.image=TKImg

    @classmethod
    def Get_Img(self, Puzzle_num=0, Mask_num='rand'):   #取得影像
        if Puzzle_num=='rand':
            Path = self.Puzzle_list[rand.randint(0,len(self.Puzzle_list)-1)]
            PuzzleImg = self.read_img(Path)
        else:
            PuzzleImg = self.read_img(self.Puzzle_list[Puzzle_num])
        if Mask_num=='rand':
            Path = self.Mask_list[rand.randint(0,len(self.Mask_list)-1)]
            self.Now_Mask = self.read_img(Path)
        elif Mask_num=='no':
            pass
        else:
            self.Now_Mask = self.read_img(self.Mask_list[Mask_num])
        return PuzzleImg, self.Now_Mask

    @classmethod
    def Next_Pic(self): #下一張
        if(len(self.Mask_list)==0 or len(self.Puzzle_list)==0):
            self.Scan_AllPuzzle()
            self.Scan_AllMask()
        elif self.img_num<len(self.Puzzle_list):
            self.img_num+=1
        else:
            pass
        PuzzleImg, MaskImg = self.Get_Img(self.img_num, 'rand')
        _,_,_,Alpha = self.SplitAlpha(MaskImg)
        Alpha = self.Alpha_fade(Alpha)
        img = self.DoBlending(MaskImg,PuzzleImg,Alpha)
        self.Update_Img(img)
    
    @classmethod
    def Back_Pic(self): #上一張
        if(len(self.Mask_list)==0 or len(self.Puzzle_list)==0):
            self.Scan_AllPuzzle()
            self.Scan_AllMask()
        elif self.img_num>0:
            self.img_num-=1
        else:
            pass
        PuzzleImg, MaskImg = self.Get_Img(self.img_num, 'rand')
        _,_,_,Alpha = self.SplitAlpha(MaskImg)
        Alpha = self.Alpha_fade(Alpha)
        img = self.DoBlending(MaskImg,PuzzleImg,Alpha)
        self.Update_Img(img)

    @classmethod
    def Start(self):
        for i in range(0,len(self.Puzzle_list)-1):
            PuzzleImg, MaskImg = self.Get_Img(i, 'rand')
            _,_,_,Alpha = self.SplitAlpha(MaskImg)
            Alpha = self.Alpha_fade(Alpha)
            img = self.DoBlending(MaskImg,PuzzleImg,Alpha)
            # print(str(self.Puzzle_list[i]).split(str(self.bge.get())))
            Path = str(self.sve.get())+str(self.Puzzle_list[i]).split(str(self.bge.get()))[1].split('.jpg')[0]+'_A.jpg'
            print(Path)
            self.save_img(Path, img)

    @classmethod
    def Get_Scale(self):
        PuzzleImg, MaskImg = self.Get_Img(self.img_num, 'no')
        _,_,_,Alpha = self.SplitAlpha(self.Now_Mask)
        Alpha = self.Alpha_fade(Alpha)
        img = self.DoBlending(self.Now_Mask,PuzzleImg,Alpha)
        self.Update_Img(img)

    @classmethod
    def Alpha_fade(self, Alpha):
        for i in range(len(Alpha)):
            for j in range(len(Alpha[0])):
                Alpha[i][j] = Alpha[i][j]*(self.Alpha_pct.get()/100)
        return Alpha
    
    @classmethod
    def init_tk(self, seed=36):
        # 設定種子碼
        rand.seed(seed)

        #Entry
        self.bge = tk.Entry(width=40)   #建立輸入框
        self.fge = tk.Entry(width=40)
        self.sve = tk.Entry(width=40)
        self.bge.insert(0,"./Puzzle")   #設定預設輸入
        self.fge.insert(0,"./Mask")
        self.sve.insert(0,"./Save")
        self.bge.grid(row=2,column=1)   #放置輸入框
        self.fge.grid(row=3,column=1)
        self.sve.grid(row=4,column=1)
        
        #Label for Image
        img = Image.open("./Puzzle/puzzle_0174.jpg")
        img = img.resize((480,270),Image.ANTIALIAS)
        tk_img = ImageTk.PhotoImage(img)
        self.show = tk.Label(image=tk_img,width=480,height=270)
        self.show.grid(row=0,column=0,columnspan=3)#,rowspan=4

        #Label
        bgl = tk.Label(bg="gray",fg="black",text="背景路徑",font="微軟正黑體 12")
        fgl = tk.Label(bg="gray",fg="black",text="前景路徑",font="微軟正黑體 12")
        svl = tk.Label(bg="gray",fg="black",text="儲存路徑",font="微軟正黑體 12")
        bgl.grid(row=2,column=0)
        fgl.grid(row=3,column=0)
        svl.grid(row=4,column=0)
        Alpha_l = tk.Label(bg="gray",fg="black",text="Alpha(%)",font="Times 12")
        Alpha_l.grid(row=5,column=0)

        #Scale
        self.Alpha_s = tk.Scale(bg="gray",length=280,orient=tk.HORIZONTAL,to=100, variable=self.Alpha_pct)
        self.Alpha_s.grid(row=5,column=1)

        #LastButton
        Back_btn = tk.Button(bg="gray",width=14,text="<Last")
        Back_btn.config(command=self.Back_Pic)
        Back_btn.grid(row=1,column=0)

        #RefreshButton
        Start_btn = tk.Button(bg="gray",width=40,text="Start")
        Start_btn.config(command=self.Start)
        Start_btn.grid(row=1,column=1)

        #NextButton
        Next_btn = tk.Button(bg="gray",width=14,text="Next>")
        Next_btn.config(command=self.Next_Pic)
        Next_btn.grid(row=1,column=2)

        #Button for Entry
        Entry_btn1 = tk.Button(bg="gray",width=14,text="Enter")
        Entry_btn1.config(command=self.Scan_AllPuzzle)
        Entry_btn1.grid(row=2,column=2)
        Entry_btn2 = tk.Button(bg="gray",width=14,text="Enter")
        Entry_btn2.config(command=self.Scan_AllMask)
        Entry_btn2.grid(row=3,column=2)
        # Entry_btn3 = tk.Button(bg="gray",width=10,text="Enter")
        # Entry_btn3.config(command=self.Scan_AllPuzzle)
        # Entry_btn3.grid(row=2,column=5)

        #Button for Scale
        Alpha_btn = tk.Button(bg="gray",width=14,height=2,text="Refresh")
        Alpha_btn.config(command=self.Get_Scale)
        Alpha_btn.grid(row=5,column=2)

    # win.mainloop() #常駐頁面
