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
