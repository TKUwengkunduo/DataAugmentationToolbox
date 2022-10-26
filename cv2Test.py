import cv2IP

M = cv2IP.UI()
M.init_tk(seed=36)

while True:
    M.update()



# M = cv2IP.AlphaBlend()
img1 = M.read_img('./Puzzle/puzzle_1694.jpg')
img2 = M.read_img('./Mask/cat/cat_001.png')

# M.show_img('v', img1, 0)

_,_,_,Alpha = M.SplitAlpha(img2)
img = M.DoBlending(img2,img1,Alpha)
M.show_img('t', img, 0)

# img = M.Img_RandomAdd(img1, img2)
# M.show_img('t', img)



# Mask_list, num = M.ImportAllMask('H:/CV2_ws/Mask/')
# print(Mask_list, num)