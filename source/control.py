"""TouchDesigner module. Runtime globals me, op, parent, absTime are provided by TD."""
import math
import time

STYLES = ['Flame','Water','Mist','Stone','Love','Wind','Serpent','Insect','Sound']
COLORS = [(1,.28,.08),(.12,.66,1),(.57,.8,.85),(.74,.55,.34),(1,.25,.6),(.5,1,.7),(.7,.45,1),(.82,.4,1),(1,.72,.28)]
FORMS = [
 ['Unknowing Fire','Rising Scorching Sun','Blooming Flame Undulation'],
 ['Water Surface Slash','Water Wheel','Dead Calm'],
 ['Low Clouds, Distant Haze','Shifting Flow Slash','Obscuring Clouds'],
 ['Serpentinite Bipolar','Upper Smash','Stone Skin'],
 ['Shivers of First Love','Love Pangs','Catlove Shower'],
 ['Dust Whirlwind Cutter','Claws-Purifying Wind','Rising Dust Storm'],
 ['Winding Serpent Slash','Venom Fangs of the Narrow Head','Coil Choke'],
 ['Butterfly Dance: Caprice','Bee Sting Dance: True Flutter','Dragonfly Dance: Compound Eye Hexagon'],
 ['String Performance','Constant Resounding Slashes','Roar'],
]
KEYS = ['seq','style','form','x','y','speed','pinch','active','otherx','othery','otheractive','span','event','audio','enabled','command','session']


def reset_trails():
    node = op('feedback')
    if node is not None:
        node.par.resetpulse.pulse()


def receive(address, args):
    if address == '/voice' and args:
        me.store('voice', str(args[0]))
        return
    if address != '/state' or len(args) != len(KEYS):
        return
    try:
        v = [float(x) for x in args]
    except (ValueError, TypeError):
        return
    if not all(math.isfinite(x) for x in v):
        return
    d = dict(zip(KEYS,v))
    if not (d['style'].is_integer() and 0 <= d['style'] <= 8 and d['form'].is_integer() and 0 <= d['form'] <= 3):
        return
    now = time.monotonic()
    old = me.fetch('state', {})
    same_session = d['session'] == old.get('session')
    if same_session and d['seq'] <= old.get('seq', -1):
        return
    if me.fetch('autoconnect', True):
        parent().par.Live = True
    if d['command'] != old.get('command') or not same_session:
        parent().par.Style = int(d['style'])
        parent().par.Paused = not bool(d['enabled'])
        reset_trails()
    if d['event'] != old.get('event') or not same_session:
        me.store('trigger_time', now)
    me.store('state', d)
    me.store('received', now)
    me.store('cache_frame', -1)


def snapshot():
    frame = absTime.frame
    if me.fetch('cache_frame',-1) == frame:
        return me.fetch('cache')
    now, t = time.monotonic(), absTime.seconds
    live = bool(parent().par.Live.eval())
    style = int(parent().par.Style.eval())
    if live:
        s = dict(me.fetch('state',{}))
        online = now-me.fetch('received',-1000) < .5
        if not online:
            s.update(active=0,otheractive=0,audio=0,speed=0,form=0)
        s['online'] = int(online)
    else:
        stage = op('stage')
        hover = bool(stage.panel.inside)
        x = (24+1232*float(stage.panel.u))/1280 if hover else .5+.19*math.cos(t*.7)
        y = (165+385*float(stage.panel.v))/720 if hover else .5+.16*math.sin(t*.9)
        s = dict(x=x,y=y,speed=.45,pinch=.7,active=1,otherx=.3,othery=.5,
                 otheractive=1,span=.35,audio=.08,form=int(parent().par.Form.eval())+1,online=0)
    s.update(style=style,live=int(live))
    s['active'] = int(bool(s.get('active',0)) and not parent().par.Paused.eval())
    age = now-me.fetch('trigger_time',-1000)
    s['burst'] = max(0,1-age/.7)
    s['x'] = min(max(s.get('x',.5),0),1)
    s['y'] = min(max(s.get('y',.5),0),1)
    me.store('cache_frame',frame)
    me.store('cache',s)
    return s


def value(key, default=0):
    return snapshot().get(key, default)


def action(name, index=0):
    if name == 'style':
        parent().par.Style = index
    elif name == 'form':
        parent().par.Form = index
    elif name == 'demo':
        parent().par.Live = False
        parent().par.Paused = False
        me.store('autoconnect', False)
    elif name == 'live':
        parent().par.Live = True
        parent().par.Paused = False
        me.store('autoconnect', True)
    elif name == 'pause':
        parent().par.Paused = not parent().par.Paused.eval()
    elif name == 'trails':
        parent().par.Trails = not parent().par.Trails.eval()
    elif name == 'save':
        target = ui.chooseFile(load=False,fileTypes=['.toe'],title='Save Breathing Studio')
        if target:
            if not target.lower().endswith('.toe'):
                target += '.toe'
            project.save(target)
        return
    me.store('cache_frame',-1)
    me.store('trigger_time',time.monotonic())
    reset_trails()


def title():
    return STYLES[int(value('style'))].upper()+' BREATHING'


def form_title():
    f = int(value('form'))
    return FORMS[int(value('style'))][f-1] if f else 'Show a pinch, open palm, or fist'


def status():
    s = snapshot()
    if not s['live']:
        return 'MOUSE DEMO  /  Move inside the stage. Choose a form below.'
    if not s['online']:
        return 'WAITING FOR CAMERA  /  Open the controller launcher and press Start.'
    if parent().par.Paused.eval():
        return 'PAUSED  /  Say start or click Resume.'
    return 'LIVE  /  Say a style. Pinch, open palm, or fist to change form.'


def button_color(kind,index,channel):
    _ = absTime.frame
    selected = (kind == 'style' and int(parent().par.Style.eval()) == index) or (kind == 'form' and int(value('form')) == index+1)
    c = COLORS[int(parent().par.Style.eval())][channel]
    return .08+c*.20 if selected else .055


def fade():
    if not parent().par.Trails.eval():
        return 0
    if int(value('style')) == 1 and int(value('form')) == 3:
        return .5
    return .91
