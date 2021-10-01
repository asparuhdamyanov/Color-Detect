import cv2, numpy as np, glob, re, os
SCRIPT_DIR = os.path.join(os.path.dirname(__file__))

color_dict_HSV = {
    'pink': [[0, 40, 50], [7, 172, 255], 'ee6893'],
    'red': [[0, 172, 50], [7, 255, 255], 'f34638'],
    'orange': [[7, 40, 50], [22, 255, 255], 'ff6318'],
    'yellow': [[22, 40, 50], [33, 255, 255], 'ffda27'],
    'chartreuse': [[33, 40, 50], [40, 255, 255], 'd1d951'],
    'grass green': [[40, 40, 50], [77, 255, 255], '2fb14b'],
    'teal': [[77, 40, 50], [98, 255, 255], '26a5a9'],
    'azure': [[98, 40, 50], [125, 255, 255], '0980fb'],
    'purple': [[125, 40, 50], [162, 255, 255], 'a826b2'],
    'pink2': [[162, 40, 50], [172, 255, 255], 'ee6893'],
    'pink3': [[172, 40, 50], [180, 172, 255], 'ee6893'],
    'red2': [[172, 172, 50], [180, 255, 255], 'f34638'],
}

re_pink = re.compile(r'^pink.+$')

def get_dominant_colors(orig_image, num_of_colors=3):

    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2HSV)

    result = {}
    multiColor = False
    noColor = False
    numOfColors = 0
    text = 'None'
    color_mask = np.zeros(image.shape[:2])

    for color, (lower, upper, hex) in color_dict_HSV.items():
        mask = cv2.inRange(image, np.array(lower), np.array(upper))
        color_mask += mask
        percentage = (mask>0).mean()
        result[color] = percentage

    result['red'] += result.pop('red2')  
    result['pink'] += sum(map(result.pop, filter(re_pink.match, list(result))))
    
    result = list(result.items())
    result.sort(key=lambda x: x[1], reverse=True)

    # relative to the highest
    result_relative = [(color, per/result[0][1]) for color, per in result]

    # relative to the previous
    # result_relative = []
    # for index, (color, percentage) in enumerate(result):
    #     if index == 0:
    #         result_relative.append((color, percentage/percentage))
    #     else:
    #         result_relative.append((color, percentage/result[index-1][1]))

    color_mask *= 255
    color_mask = color_mask.clip(0, 255).astype("uint8")
    color_mask = cv2.bitwise_and(orig_image, orig_image, mask=color_mask)

    # display mask
    # if color_mask.shape[0] > 1000:
    #     color_mask = cv2.resize(color_mask, (int(color_mask.shape[1]/2.5), int(color_mask.shape[0]/2.5)))
    # cv2.imshow('test', color_mask)
    # cv2.waitKey(0)

    if result[0][1] < 0.011:
        noColor = True
    else:
        if result_relative[1][1] < 0.5:
            numOfColors = 1
        elif result_relative[2][1] < 0.4:
            numOfColors = 2
        elif result_relative[3][1] < 0.3:
            numOfColors = 3
        else:
            multiColor = True


    # if result[0][1] < 0.01:
    #     noColor = True
    # else:
    #     if result[0][1] / result[1][1] > 10:
    #         numOfColors = 1
    #     elif result[1][1] / result[2][1] > 5:
    #         numOfColors = 2
    #     elif result[2][1] / result[3][1] > 1.5:
    #         numOfColors = 3
    #     else:
    #         multiColor = True
    
    print('='*6,'RESULT', '='*6)
    if noColor:
        print(text:='No dominant colors found')
    elif multiColor:
        print(text:='Found more than 3 dominant colors')
    elif numOfColors < num_of_colors:
        print(text:=f'Found only {numOfColors} dominant color' + ('s' if numOfColors > 1 else ''))
    elif numOfColors == num_of_colors:
        print(text:=f'Found exactly {numOfColors} dominant color' + ('s' if numOfColors > 1 else '')) 
    else:
        print(text:=f'Found more dominant colors than specified')

    for color, percentage in result:
            print(f'{color:12}', f'{percentage:.2%}')

    # for color, percentage in result_relative:
    #         print(f'{color:12}', f'{percentage:.2%}')
    
    return result, noColor, multiColor, numOfColors, text

if __name__ == '__main__': 
    for imagePath in glob.glob(os.path.join(SCRIPT_DIR, 'color_images', '*.jpg')):
        image = cv2.imread(imagePath)
        print('\n', imagePath)
        get_dominant_colors(image)
