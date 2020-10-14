import cv2
import glob
import re
import os



def size_half(im):
    imc = cv2.cv2.resize(im,None,fx = 0.5,fy = 0.5)
    cv2.cv2.waitKey(0)
    cv2.cv2.destroyAllWindows()
    return imc

def size_cut(img_path,screen):
    print(img_path)
    img = cv2.cv2.imread(img_path)
    if screen == 'half' :
        new_img = img[777:850,100:900]
    elif screen == 'full':
        new_img = img[730:850,300:1350]
    else:
        raise SyntaxError

    return new_img

def rename_all():
    origin_dir = "your Directory"
    img_paths = glob.glob(f'{origin_dir}/*.png')
    for img_path in img_paths:
        num = re.search(r'スクリーンショット\s[(](\d+)[)].png$',img_path).group(1)
        os.rename(img_path,f'{origin_dir}/scr/{num}.png')

#main
while True:
    boolern = input('rename? y or n: ')
    if boolern == 'y':
        rename_all()
        break
    elif boolern == 'n':
        break
    else:continue

output = input('filename: ')
screen = input('screen half or full: ')

d={} #for sort d[num] = img_path
imgs = glob.glob('path to pingFile')
for img in imgs:
    num = re.search(r'.+?(\d+).png',img).group(1)
    num = int(num)
    d[num] = img
#sort
img_list=[]
for num,img_path in sorted(d.items()):
    new_image = size_cut(img_path,screen)
    #temp
    #cv2.cv2.imwrite('temp.png',new_image)
    img_list.append(new_image)

#connect!
imc = cv2.cv2.vconcat(img_list)
imc = size_half(imc)
cv2.cv2.imwrite(f"{output}.png",imc)