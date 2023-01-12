from PIL import Image
import os

# def convert_image(filename):
#     im = Image.open(filename)
#     x, y = im.size
#     if y > 240:
#         im2 = im.crop((200 - x, 240 - y, x, y))
#     else:
#         im2 = im.crop((200 - x, 0, x, 240))
#     x2, y2 = im2.size
#     im3 = im2.crop((-((458 - x2) // 2), -((458 - y2) // 2), x2 + (458 - x2) // 2, y2 + (458 - y2) // 2))
#     tmp = filename.split('/')
#     tmp0 = tmp[0].split('\\')
#     print(tmp)
#     im3.save(f'C:/Users/Professional/PycharmProjects/2d_shooter/assets/player_sprites/{tmp0[0]}/{tmp0[1]}/{tmp[1][:-4]}' + '_reworked.png')
# os.chdir('C:/Users/Professional/Downloads/Top_Down_Survivor')
# for i in {'handgun', 'shotgun', 'rifle', 'knife'}:
#     for cdir, dirs, files in os.walk(f'{i}'):
#         # print(cdir)
#         for file in files:
#             convert_image(f'{cdir}/{file}')

os.chdir('assets/player_sprites')
for i in {'handgun', 'shotgun', 'rifle', 'knife'}:
    for cdir, dirs, files in os.walk(f'{i}'):
        # print(cdir)
        for file in files:
            file_split = file.split('_')
            file_split[2] = file_split[2].rjust(3, '0')
            os.rename(f'{cdir}/{file}', f'{cdir}/{"".join(file_split)}')

# im = Image.open('assets/player_sprites/handgun/shoot/survivor-shoot_handgun_0_reworked.png')
# im2 = im.resize((160, 160))
# pixels = im2.load()
# print(pixels[0, 0])
# im2.save('1.png')
