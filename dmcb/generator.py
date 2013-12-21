# Package: dmcb
from io import BytesIO

from PIL import Image, ImageDraw

from dmcb import font, network, get_path, app, cache


# Parse the background texture
texture = Image.open(get_path('static/texture.png'))
texture = texture.resize((60,60))
texture = texture.point(lambda p: p * 0.17)

def _repeat(image, pattern):
    ''' Repeat the pattern over the image
    '''
    iw, ih = image.size
    pw, ph = pattern.size
    x = 0
    while x < iw:
        y = 0
        while y < ih:
            image.paste(pattern, (x, y))
            y += ph
        x += pw
    return image

@cache.memoize(timeout=app.config['TIMEOUT'])
def banner(name, adress, port=25565, mc_version='1.7'):
    assert mc_version == '1.7' or mc_version == '1.6'
        
    # Create the image, and past the texture on it
    image = Image.new('RGB', (660, 120))
    _repeat(image, texture)
    drawer = ImageDraw.Draw(image)
    
    # Render server name
    font.render((5,11), font.parse(name[:25]), image)
    # Render server adress
    if port != 25565:
        drawer.text((5,77), adress + ':' + str(port), fill=(42,42,42),
                    font=font.font_regular)
    else:
        drawer.text((5,77), adress, fill=(42,42,42), font=font.font_regular)
    
    # Render the info we need network access for
    try:
        # Fetch the info
        info = network.get_server_info(adress, port=port, version=mc_version)
        
        motd = info['description']
        if type(motd) == dict:
            motd = motd['text']
        if '\n' in motd:
            motd = motd.split('\n')[0]

        # Render the MOTD
        font.render((5,44), 
                    font.parse(motd),
                    image)
        
        # Render the player count
        players = font.parse('§7' + str(info['players']['online'])
                           + '§8/§7' + str(info['players']['max']))
        players_width = font.get_width(players)
        font.render((image.size[0]-10-players_width, 44), players, image)
        
        # Render the version
        version = font.parse('§7' + info['version']['name'])
        version_width = font.get_width(version)
        font.render((image.size[0]-55-version_width, 11), version, image)
        
        # Render the ping
        render_ping(drawer, (image.size[0]-47,7), parse_ping(info['ping']))
    except Exception as ex:
        font.render((5,44),font.parse("§4Can't reach server"), image)
        render_ping(drawer, (image.size[0]-47,7), -1)
    
    # Save the image to a BytesIO fake file and return it
    mem_file = BytesIO()
    image.save(mem_file, 'PNG')
    mem_file.seek(0)
    return mem_file

def render_ping(drawer, xy, ping):
    ''' Render the ping to the supplied Drawer object
    '''
    x, y = xy
    f85 = (85,85,85)
    f42 = (42,42,42)
    f85_255_85 = (85,255,85)
    f21_63_21 = (21,63,21)
    if (ping == 1):
        fills = [f21_63_21,f85_255_85,f42,f85,f42,f85,f42,f85,f42,f85]
    elif (ping == 2):
        fills = [f21_63_21,f85_255_85,f21_63_21,f85_255_85,f42,f85,f42,f85,
                 f42,f85]
    elif (ping == 3):
        fills = [f21_63_21,f85_255_85,f21_63_21,f85_255_85,f21_63_21,
                 f85_255_85,f42,f85,f42,f85]
    elif (ping == 4):
        fills = [f21_63_21,f85_255_85,f21_63_21,f85_255_85,f21_63_21,
                 f85_255_85,f21_63_21,f85_255_85,f42,f85]
    elif (ping == 5):
        fills = [f21_63_21,f85_255_85,f21_63_21,f85_255_85,f21_63_21,
                 f85_255_85,f21_63_21,f85_255_85,f21_63_21,f85_255_85]
    else:
        fills = [f42,f85,f42,f85,f42,f85,f42,f85,f42,f85]

    drawer.rectangle([(x+1*4-1, y+5*4), (x+2 *4-2, y+7*4-1)], fill=fills[0])
    drawer.rectangle([(x+0*4,   y+4*4), (x+1 *4-1, y+6*4-1)], fill=fills[1])
    drawer.rectangle([(x+3*4-1, y+4*4), (x+4 *4-2, y+7*4-1)], fill=fills[2])
    drawer.rectangle([(x+2*4,   y+3*4), (x+3 *4-1, y+6*4-1)], fill=fills[3])
    drawer.rectangle([(x+5*4-1, y+3*4), (x+6 *4-2, y+7*4-1)], fill=fills[4])
    drawer.rectangle([(x+4*4,   y+2*4), (x+5 *4-1, y+6*4-1)], fill=fills[5])
    drawer.rectangle([(x+7*4-1, y+2*4), (x+8 *4-2, y+7*4-1)], fill=fills[6])
    drawer.rectangle([(x+6*4,   y+1*4), (x+7 *4-1, y+6*4-1)], fill=fills[7])
    drawer.rectangle([(x+9*4-1, y+1*4), (x+10*4-2, y+7*4-1)], fill=fills[8])
    drawer.rectangle([(x+8*4,   y+0*4), (x+9 *4-1, y+6*4-1)], fill=fills[9])
    if(ping == -1):
        drawer.line([(x+4,y),(x+9*4-5,y+7*4-1)], fill=(170,0,0), width=3)
        drawer.line([(x+4,y+7*4-1),(x+9*4-5,y)], fill=(170,0,0), width=3)
    
def parse_ping(ping):
    ''' Parse a ping in ms to a format readable by render_ping
    '''
    if ping > 0 and ping < 150:
        return 5
    elif ping < 300:
        return 4
    elif ping < 600:
        return 3
    elif ping < 1000:
        return 2
    elif ping > 0:
        return 1
    else:
        return -1   
