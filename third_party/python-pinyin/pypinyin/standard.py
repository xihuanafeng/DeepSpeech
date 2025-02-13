"""
处理汉语拼音方案中的一些特殊情况
汉语拼音方案:
* https://zh.wiktionary.org/wiki/%E9%99%84%E5%BD%95:%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3%E6%96%B9%E6%A1%88
* http://www.moe.edu.cn/s78/A19/yxs_left/moe_810/s230/195802/t19580201_186000.html

“知、蚩、诗、日、资、雌、思”等七个音节的韵母用i，即：知、蚩、诗、日、资、雌、思等字拼作zhi，chi，shi，ri，zi，ci，si。
韵母ㄦ写成er，用作韵尾的时候写成r。例如：“儿童”拼作ertong，“花儿”拼作huar。
i行的韵母，前面没有声母的时候，写成yi(衣)，ya(呀)，ye(耶)，yao(腰)，you(忧)，yan(烟)，yin(因)，yang(央)，ying(英)，yong(雍)。
u行的韵母，前面没有声母的时候，写成wu(乌)，wa(蛙)，wo(窝)，wai(歪)，wei(威)，wan(弯)，wen(温)，wang(汪)，weng(翁)。
ü行的韵母，前面没有声母的时候，写成yu(迂)，yue(约)，yuan(冤)，yun(晕)；ü上两点省略。
ü行的韵跟声母j，q，x拼的时候，写成ju(居)，qu(区)，xu(虚)，ü上两点也省略；但是跟声母n，l拼的时候，仍然写成nü(女)，lü(吕)。
iou，uei，uen前面加声母的时候，写成iu，ui，un。例如niu(牛)，gui(归)，lun(论)。
在给汉字注音的时候，为了使拼式简短，ng可以省作ŋ。
"""
import re
from typing import Text

# u -> ü
UV_MAP = {
    'u': 'ü',
    'ū': 'ǖ',
    'ú': 'ǘ',
    'ǔ': 'ǚ',
    'ù': 'ǜ',
}
U_TONES = set(UV_MAP.keys())
# ü行的韵跟声母j，q，x拼的时候，写成ju(居)，qu(区)，xu(虚)
UV_RE = re.compile(
    r'^(j|q|x)({tones})(.*)$'.format(tones='|'.join(UV_MAP.keys())))

I_TONES = set(['i', 'ī', 'í', 'ǐ', 'ì'])

# iu -> iou
IU_MAP = {
    'iu': 'iou',
    'iū': 'ioū',
    'iú': 'ioú',
    'iǔ': 'ioǔ',
    'iù': 'ioù',
}
IU_TONES = set(IU_MAP.keys())
IU_RE = re.compile(r'^([a-z]+)({tones})$'.format(tones='|'.join(IU_TONES)))

# ui -> uei
UI_MAP = {
    'ui': 'uei',
    'uī': 'ueī',
    'uí': 'ueí',
    'uǐ': 'ueǐ',
    'uì': 'ueì',
}
UI_TONES = set(UI_MAP.keys())
UI_RE = re.compile(r'([a-z]+)({tones})$'.format(tones='|'.join(UI_TONES)))

# un -> uen
UN_MAP = {
    'un': 'uen',
    'ūn': 'ūen',
    'ún': 'úen',
    'ǔn': 'ǔen',
    'ùn': 'ùen',
}
UN_TONES = set(UN_MAP.keys())
UN_RE = re.compile(r'([a-z]+)({tones})$'.format(tones='|'.join(UN_TONES)))


def convert_zero_consonant(pinyin: Text) -> Text:
    """零声母转换，还原原始的韵母
    i行的韵母，前面没有声母的时候，写成yi(衣)，ya(呀)，ye(耶)，yao(腰)，
        you(忧)，yan(烟)，yin(因)，yang(央)，ying(英)，yong(雍)。
    u行的韵母，前面没有声母的时候，写成wu(乌)，wa(蛙)，wo(窝)，wai(歪)，
        wei(威)，wan(弯)，wen(温)，wang(汪)，weng(翁)。
    ü行的韵母，前面没有声母的时候，写成yu(迂)，yue(约)，yuan(冤)，
        yun(晕)；ü上两点省略。
    """
    # y: yu -> v, yi -> i, y -> i
    if pinyin.startswith('y'):
        # 去除 y 后的拼音
        no_y_py = pinyin[1:]
        first_char = no_y_py[0] if len(no_y_py) > 0 else None

        # yu -> ü: yue -> üe
        if first_char in U_TONES:
            pinyin = UV_MAP[first_char] + pinyin[2:]
        # yi -> i: yi -> i
        elif first_char in I_TONES:
            pinyin = no_y_py
        # y -> i: ya -> ia
        else:
            pinyin = 'i' + no_y_py
        return pinyin

    # w: wu -> u, w -> u
    if pinyin.startswith('w'):
        # 去除 w 后的拼音
        no_w_py = pinyin[1:]
        first_char = no_w_py[0] if len(no_w_py) > 0 else None

        # wu -> u: wu -> u
        if first_char in U_TONES:
            pinyin = pinyin[1:]
        # w -> u: wa -> ua
        else:
            pinyin = 'u' + pinyin[1:]
        return pinyin

    return pinyin


def convert_uv(pinyin: Text) -> Text:
    """ü 转换，还原原始的韵母
    ü行的韵跟声母j，q，x拼的时候，写成ju(居)，qu(区)，xu(虚)，ü上两点也省略；
    但是跟声母n，l拼的时候，仍然写成nü(女)，lü(吕)。
    """
    return UV_RE.sub(
        lambda m: ''.join((m.group(1), UV_MAP[m.group(2)], m.group(3))), pinyin)


def convert_iou(pinyin: Text) -> Text:
    """iou 转换，还原原始的韵母
    iou，uei，uen前面加声母的时候，写成iu，ui，un。
        例如niu(牛)，gui(归)，lun(论)。
    """
    return IU_RE.sub(lambda m: m.group(1) + IU_MAP[m.group(2)], pinyin)


def convert_uei(pinyin: Text) -> Text:
    """uei 转换，还原原始的韵母
    iou，uei，uen前面加声母的时候，写成iu，ui，un。
        例如niu(牛)，gui(归)，lun(论)。
    """
    return UI_RE.sub(lambda m: m.group(1) + UI_MAP[m.group(2)], pinyin)


def convert_uen(pinyin: Text) -> Text:
    """uen 转换，还原原始的韵母
    iou，uei，uen前面加声母的时候，写成iu，ui，un。
        例如niu(牛)，gui(归)，lun(论)。
    """
    return UN_RE.sub(lambda m: m.group(1) + UN_MAP[m.group(2)], pinyin)


def convert_finals(pinyin: Text) -> Text:
    """还原原始的韵母"""
    # i,u,ü 行的韵母，前面没有声母的时候
    pinyin = convert_zero_consonant(pinyin)
    # ü行的韵跟声母j，q，x拼的时候
    pinyin = convert_uv(pinyin)
    # iou，uei，uen前面加声母的时候
    pinyin = convert_iou(pinyin)
    pinyin = convert_uei(pinyin)
    pinyin = convert_uen(pinyin)
    return pinyin
