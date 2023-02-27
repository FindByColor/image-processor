import io
import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from PIL import Image, ImageFilter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

chart_font = { 
    'color': '#999999', 
    'fontfamily': 'monospace', 
    'fontsize': 190, 
    'fontweight': 'bold'
}

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

def color_chart(colors, cropped_image):
    #chart background
    fig, ax = plt.subplots(figsize=(136,112),dpi=10)
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    fig.set_facecolor('None')
    plt.margins(0)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    plt.close(fig)

    # Annotate Text
    list_color = list(colors['hex'])
    list_percent = [int(i) for i in list(colors["occurrence"])]
    text_c = [c + ' ' + str(round(p*100/sum(list_percent),1)) +'%' for c, p in zip(list_color, list_percent)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(180,70), dpi = 10)

    #donut plot
    wedges, text = ax1.pie(list_percent, counterclock=False, labels= text_c, labeldistance= 1.05, colors = list_color, startangle=180, textprops={ 'fontsize': 150, 'color': '#999999', 'fontfamily': 'monospace' })
    plt.setp(wedges, width=0.3)

    #add image in the center of donut plot
    img = cropped_image
    img.thumbnail((600, 600), Image.ANTIALIAS)

    alpha = img.split()[-1]
    alpha_blur = alpha.filter(ImageFilter.BoxBlur(10))

    product = Image.new(mode="RGBA", size=(alpha_blur.size[0] + 20, alpha_blur.size[1] + 20))
    shadow = Image.new(mode="RGBA", size=alpha_blur.size)
    shadow.putalpha(alpha_blur)

    product.paste(shadow, (10, 10), shadow)
    product.paste(shadow, (10, 10), shadow)
    product.paste(shadow, (10, 10), shadow)
    product.paste(shadow, (10, 10), shadow)

    product.paste(img, (10, 10), img)

    imagebox = OffsetImage(product, zoom=5)
    ab = AnnotationBbox(imagebox, (0, 0.1), frameon=False)
    ax1.add_artist(ab)

    # Color Palette
    x_posi, y_posi, y_posi2 = 40, -156, -156
    for c in list_color:
        if list_color.index(c) < math.ceil(len(list_color) / 2):
            y_posi += 180
            rect = patches.Rectangle((x_posi, y_posi), 360, 160, facecolor = c)
            ax2.add_patch(rect)
            ax2.text(x = x_posi+400, y = y_posi+100, s = c, fontdict=chart_font)
        else:
            y_posi2 += 180
            rect = patches.Rectangle((x_posi + 675, y_posi2), 360, 160, facecolor = c)
            ax2.add_artist(rect)
            ax2.text(x = x_posi+1075, y = y_posi2+100, s = c, fontdict=chart_font)

    fig.set_facecolor('None')
    ax2.axis('off')
    plt.imshow(Image.open(buf))
    plt.margins(0)
    
    plt.tight_layout()
    chart = plt.gcf()
    buf.close()

    img = fig2img(chart)
    img = img.crop(img.getbbox())

    return img
