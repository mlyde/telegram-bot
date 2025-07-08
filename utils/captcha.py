import logging
logger = logging.getLogger(__name__)
import random
import string
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

from core.static_config import static_config
font_path: str = static_config.get("font")
font_list: list = [
    ImageFont.truetype(font_path, 35),
    ImageFont.truetype(font_path, 40),
    ImageFont.truetype(font_path, 45)
]

def randomFormula(num_1_max = 69, num_2_max = 9):
    """随机产生数学公式"""
    a = random.randint(1, num_1_max)
    b = random.randint(1, num_2_max)
    operators = ['加', '减']  # 乘除法不易口算
    operator = random.choice(operators)

    # 结果
    match operator:
        case '加': result = a + b
        case '减': result = a - b

    return f"{a}{operator}{b}=", str(result)

def isSlim(char: str):
    """判断字符类型"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return True if char in chars else False

def randomColor(max_value: float = None):
    """随机颜色"""
    if max_value:   # 限制明度, 不要太接近白色
        h = random.random()             # 色相
        s = random.uniform(0, 1.0)      # 饱和度
        v = random.uniform(0, max_value)# 明度
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    else:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generateCaptcha():
    """生成验证码图片"""
    width, height = 180, 70
    img = Image.new('RGB', (width, height), (255, 255, 255))

    def getXY(width = width, height = height):
        """随机取一个点"""
        return (random.randint(0, width), random.randint(0, height))

    # 文字
    text, result = randomFormula()
    left = 0
    for ch in text:
        # 偏移和旋转
        x = left + random.randint(-4, 4)
        left += 30 if isSlim(ch) else 40
        y = random.randint(-8, 8)
        angle = random.randint(-20, 20)
        char_img = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        font = random.choice(font_list)
        char_draw.text((10, 10), ch, fill=randomColor(max_value=0.75), font=font)
        char_img = char_img.rotate(angle, expand=1)
        img.paste(char_img, (x, y), char_img)
    draw = ImageDraw.Draw(img)
    # 线条
    for _ in range(5):
        draw.line([getXY(), getXY()], fill=randomColor(), width=2)
    # 噪点
    for _ in range(50):
        draw.point(getXY(), fill=randomColor())
    # 模糊
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # 图片转为字节流
    with BytesIO() as byte_io:
        img.save(byte_io, format="PNG")
        byte_io.seek(0)
        image_bytes = byte_io.getvalue()# 不移动指针
        # image_bytes = byte_io.read()

    return image_bytes, result
