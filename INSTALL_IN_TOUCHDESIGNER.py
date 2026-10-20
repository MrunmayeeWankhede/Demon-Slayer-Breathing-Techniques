# Breathing Studio v2: run inside TouchDesigner. Readable sources are in source/.
# Creates a new component and preserves existing project nodes.
import base64, json, zlib
ASSETS=json.loads(zlib.decompress(base64.b64decode('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')))
"""Self-contained build body. ASSETS is injected by the packaged installer."""
import traceback


def build():
    host = op('/project1') or op('/')
    existing = host.op('BreathingStudio')
    if existing is not None:
        if existing.fetch('breathing_studio_complete', False):
            existing.op('display').par.winopen.pulse()
            print('Breathing Studio is already built. Its window has been opened.')
            return existing
        raise RuntimeError('An operator named BreathingStudio already exists. Rename it before installing.')
    studio = host.create(containerCOMP, 'BreathingStudio')
    studio.store('breathing_studio_version','2.0')
    studio.nodeX, studio.nodeY = 400, 0

    def setting(node,name,value,required=True,expr=False):
        p = getattr(node.par,name,None)
        if p is None:
            if required:
                raise RuntimeError(f'{node.path}: missing parameter {name}. Use current Official TouchDesigner.')
            return
        if expr:
            p.expr = value
        else:
            p.val = value

    def menu(node,name,choices,required=True):
        p = getattr(node.par,name,None)
        if p is not None:
            for choice in choices:
                if choice in p.menuNames:
                    p.val = choice
                    return
                for i,label in enumerate(p.menuLabels):
                    if label.lower() == choice.lower():
                        p.val = p.menuNames[i]
                        return
        if required:
            raise RuntimeError(f'{node.path}: cannot select {name}: {choices}')

    def resolution(node,w=1280,h=720):
        menu(node,'outputresolution',['custom'],False)
        setting(node,'resolutionw',w)
        setting(node,'resolutionh',h)

    def create(kind,name,x,y,text=None):
        node=studio.create(kind,name)
        node.nodeX,node.nodeY=x,y
        if text is not None:
            node.text=text
        return node

    def connect(target,*sources):
        for i,source in enumerate(sources):
            target.inputConnectors[i].connect(source)

    def uniforms(node,items):
        # Current Official TouchDesigner uses named sequences.
        node.seq.vec.numBlocks=len(items)
        for i,(name,values) in enumerate(items):
            setting(node,f'vec{i}name',name)
            for c,value in zip('xyzw',values):
                setting(node,f'vec{i}value{c}',value,expr=isinstance(value,str))

    def label(name,text,x,y,w,h,size,color=(.9,.94,1),expr=False):
        texture=create(textTOP,name+'_text',-700,-600-len(studio.children)*8)
        resolution(texture,w,h)
        setting(texture,'text',text,expr=expr)
        menu(texture,'fontsizexunit',['pixels'],False)
        menu(texture,'fontsizeyunit',['pixels'],False)
        setting(texture,'fontsizex',size)
        setting(texture,'fontsizey',size,False)
        menu(texture,'fontautosize',['fitiffat','Auto-Fit if Too Large'],False)
        menu(texture,'alignx',['left'])
        menu(texture,'aligny',['center'])
        setting(texture,'bgalpha',0)
        for c,v in zip('rgb',color):
            setting(texture,'fontcolor'+c,v)
        panel=create(containerCOMP,name,-950,-600-len(studio.children)*8)
        for k,v in dict(x=x,y=y,w=w,h=h,bgalpha=0,top=texture.path).items():
            setting(panel,k,v)
        return panel

    def button(name,text,x,y,w,h,action,index=0):
        b=create(buttonCOMP,name,1000,-len(studio.children)*8)
        for k,v in dict(x=x,y=y,w=w,h=h,label=text,fontsize=15).items():
            setting(b,k,v)
        menu(b,'buttontype',['momentary'])
        menu(b,'scaletofit',['onlyshrink'],False)
        for channel,c in enumerate('rgb'):
            setting(b,'bgcolor'+c,f"op('control').module.button_color({action!r},{index},{channel})",expr=True)
        callback=create(panelexecuteDAT,name+'_click',1200,-len(studio.children)*8)
        setting(callback,'panels',b.path)
        setting(callback,'panelvalue','state')
        setting(callback,'offtoon',True)
        for k in ['whileon','ontooff','whileoff','valuechange']:
            setting(callback,k,False)
        callback.text=f"def onOffToOn(panelValue):\n    op('control').module.action({action!r}, {index})\n    return\n"
        return b

    try:
        for k,v in dict(w=1280,h=720,bgalpha=1).items():
            setting(studio,k,v)
        page=studio.appendCustomPage('Breathing')
        p=page.appendMenu('Style',label='Breathing style')[0]
        p.menuNames=[str(i) for i in range(9)]
        p.menuLabels=['Flame','Water','Mist','Stone','Love','Wind','Serpent','Insect','Sound']
        p.val=1
        p=page.appendMenu('Form',label='Demo form')[0]
        p.menuNames=['0','1','2']; p.menuLabels=['Pinch','Open palm','Fist']; p.val=0
        for name,value in [('Live',False),('Paused',False),('Trails',True)]:
            p=page.appendToggle(name)[0]; p.val=value
        p=page.appendFloat('Intensity')[0]; p.val=1.25; p.min=0; p.max=3; p.clampMin=True; p.clampMax=True

        control=create(textDAT,'control',-1000,350,ASSETS['control.py'])
        cb=create(textDAT,'osc_callbacks',-750,350,
            "def onReceiveOSC(dat, rowIndex, message, bytes, timeStamp, address, args, peer):\n    op('control').module.receive(address, args)\n    return\n")
        osc=create(oscinDAT,'input',-500,350)
        setting(osc,'active',False)
        setting(osc,'port',9000)
        setting(osc,'localaddress','127.0.0.1',False)
        menu(osc,'protocol',['msging'])
        setting(osc,'callbacks',cb.path)
        setting(osc,'maxlines',25,False)

        pixel=create(textDAT,'effect_pixel',-1000,100,ASSETS['effect.frag'])
        effect=create(glslTOP,'effect',-700,100)
        menu(effect,'mode',['vertexpixel'])
        menu(effect,'glslversion',['glsl450','glsl430','glsl330'],False)
        setting(effect,'pixeldat',pixel.path)
        resolution(effect)
        f=lambda k: f"op('control').module.value({k!r})"
        uniforms(effect,[('uHand',[f('x'),f('y'),f('speed'),f('active')]),
            ('uOther',[f('otherx'),f('othery'),f('otheractive'),f('span')]),
            ('uState',['absTime.seconds',f('style'),f('form'),1280/720]),
            ('uAction',[f('pinch'),f('span'),f('burst'),f('audio')])])

        seed=create(constantTOP,'seed',-700,-100); resolution(seed)
        for c in 'rgb': setting(seed,'color'+c,0)
        feedback=create(feedbackTOP,'feedback',-450,-100); connect(feedback,seed)
        decay=create(constantTOP,'decay',-450,-300); resolution(decay)
        for c in 'rgb': setting(decay,'color'+c,"op('control').module.fade()",expr=True)
        fade=create(multiplyTOP,'fade',-200,-100); connect(fade,feedback,decay)
        mix=create(compositeTOP,'trails',50,100); connect(mix,effect,fade)
        menu(mix,'operand',['maximum'])
        setting(feedback,'top',mix.path)
        setting(feedback,'reset',0)
        finish_pixel=create(textDAT,'finish_pixel',50,-150,ASSETS['finish.frag'])
        finish=create(glslTOP,'finish',300,100); connect(finish,mix)
        menu(finish,'mode',['vertexpixel'])
        menu(finish,'glslversion',['glsl450','glsl430','glsl330'],False)
        setting(finish,'pixeldat',finish_pixel.path); resolution(finish)
        uniforms(finish,[('uFinish',['absTime.seconds',f('style'),'parent().par.Intensity',0])])
        out=create(nullTOP,'OUT',550,100); connect(out,finish)
        setting(studio,'top',out.path)
        menu(studio,'topfill',['off','Stretch'],False)

        stage=create(containerCOMP,'stage',600,-200)
        for k,v in dict(x=24,y=165,w=1232,h=385,bgalpha=0).items():
            setting(stage,k,v)
        label('brand','B R E A T H I N G   S T U D I O',32,670,690,24,16,(.56,.65,.73))
        label('style_title',"op('control').module.title()",32,609,1216,54,42,expr=True)
        label('form_title',"op('control').module.form_title()",34,575,1210,32,23,(.65,.76,.85),True)
        label('status',"op('control').module.status()",34,138,1210,26,16,(.58,.69,.76),True)
        for i,name in enumerate(['FLAME','WATER','MIST','STONE','LOVE','WIND','SERPENT','INSECT','SOUND']):
            button('style_'+str(i),name,32+i*136,82,128,40,'style',i)
        for i,name in enumerate(['PINCH','OPEN PALM','FIST']):
            b=button('form_'+str(i),name,32+i*146,28,138,38,'form',i)
            setting(b,'enable','not parent().par.Live',expr=True)
        button('demo','Mouse demo',492,28,142,38,'demo')
        button('live','Camera + voice',642,28,166,38,'live')
        b=button('pause','Pause',816,28,126,38,'pause')
        setting(b,'label',"'Resume' if parent().par.Paused else 'Pause'",expr=True)
        b=button('trail_toggle','Trails',950,28,126,38,'trails')
        setting(b,'label',"'Trails: on' if parent().par.Trails else 'Trails: off'",expr=True)
        button('save','Save project',1084,28,164,38,'save')

        display=create(windowCOMP,'display',800,250)
        setting(display,'winop',studio.path)
        setting(display,'title','Breathing Studio')
        setting(display,'interact',True)
        setting(display,'borders',True,False)
        menu(display,'size',['automatic'])
        menu(display,'dpiscaling',['native'],False)
        setting(display,'winw',1280,False); setting(display,'winh',720,False)
        startup=create(executeDAT,'startup',800,450,
            "def onStart():\n    op('control').store('received', -1000)\n    op('control').store('cache_frame', -1)\n    op('control').store('state', {})\n    op('display').par.winopen.pulse()\n    return\n")
        setting(startup,'start',True)
        for trigger in ['create','exit','framestart','frameend','playstatechange','devicechange']:
            setting(startup,trigger,False,False)
        for name,node in [('effect_compile',effect),('finish_compile',finish)]:
            info=create(infoDAT,name,300,-350 if name.startswith('effect') else -450)
            setting(info,'op',node.path)
        notes=create(textDAT,'READ_ME',-1000,-100,
            'Breathing Studio v2\nMouse demo works without Python.\nUse launcher.py for camera + voice.\nSave project with the button.\nOpen display with its Open as Separate Window pulse.\nShader errors: effect_compile / finish_compile DATs.\n')
        setting(osc,'active',True)
        feedback.par.resetpulse.pulse()
        display.par.winopen.pulse()
        studio.store('breathing_studio_complete',True)
        print('Breathing Studio created at '+studio.path+'. Use Save project to create your .toe.')
        return studio
    except Exception:
        studio.store('build_error',traceback.format_exc())
        print(traceback.format_exc())
        print('The partial component is preserved for diagnosis. Rename it before trying another installer.')
        raise


build()
