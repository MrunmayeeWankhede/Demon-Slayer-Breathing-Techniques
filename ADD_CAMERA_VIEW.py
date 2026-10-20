# Breathing Studio camera-view add-on. Run inside your working TouchDesigner project.
import base64, json, zlib
ASSETS=json.loads(zlib.decompress(base64.b64decode('eJy1Vl1v2zYU/St36YMlR2EkJ007p9rQJQXWlyZY3eyhLgxZpmwiMqmRlC2l6H/fJSnJluMWw4bZgGXzXh6ee+4H/fUkTdZUJrM0yfN5kj4qUtQnYziZ2vfHVLJCw+TuHjqHMXDB57lIHxlfQlnkIlmAyECvKOSJpkoDGpMcHDJkEp/E4U05WxdCanSWNFkgwG6FrWn3o5R5zuZE0r9KxOuWebkuakgU8GLKp3xmMKiEGD4ITs3KlKd5ohT8YQ3jKQd8LWgGsxnjTM9mnqJ55jcG8zK/idKiQJSOFHm3oVx7/oFbE117XM+2pkolS4rGwZ8J00aaTMhOA0oX1yBxd2KDp6jbAtEWkAqupchzKsngANLR6fGa2G8eoiypjh0pIYoAFgldCx5PZEkD4HhoPPgNXfUKd91YDk6SwWFMDptYYibgnWQG+JlcL2CyYgq2Qj6i8AWVGOQa8yFgIsp0dUsVW3K0vL1/bytGkd3eNGeoKsbTzy6ZlyxfzERBcaN3YLuXoqp/T/gCBfK+fvP36G9XLKd4st7lkDA1UxTj2GNsIzXRUSslVhlBpYQWnKX7GTYvLeuDnfYgplcNeWJYeoOV1sX4/DwavSIhvqPxz2EYndtCHwT2DFHqOCRXvilWTHshuKJHoM2rSGrbQnHnSGySry5DGMLFlf2EU4j85/sZpgkJNRA+/BRDb9t3jpQJUxQekryk76QU0ht84rQqaGorcq9tQbEnOjhycMEqmivkzAuSSbGel1mGGWqIYD3quqAxGkvG9WsfI1KrpKAe8goMxQAujqC+gDvU9+YBpNhCCFhoplUwsdd2BGla6VLSvnUutBZr8mOKiTJ9xpalKFUiZVJ7zvp5PD6Lvhxh0u9377Bsggb9ezv3psHNbgKYZudW5EF/H61SimP2nX0wwY+k7X8YMj1o2z5bBPVCMnp5ENeBxzqpPMxgBOdwEcLZc3lwrWk53/fdXDYTRa1KvRBb7il7rdwVbZ8uczHHC6OZ524NS7ud70zZNjdTd0+Zxup42a53tmO3gjld8BshHv/F2QYGUGbDoT20GZs4b5KcbWhv4uwIuJnbEuuWe2d1RdYgu9/OJnjOuEl347QnBOBMfDbNUHfn+Tn8Am8gcihtxEYpSb1Bc+M7cJxX7ov/Q2dMpy4VOjcs20pkWUsSu4H+h7L0O+Ud3v4V3VJKRVF/MH8B3toWbkLt+tcw+AfbcBw8USmU1xtGz0ZWlzQcOVhBJwHgX6XCzB8ceMnS/EcqOTPXH2xoegnljbNew/k5IALliuk6wKLHaeWkCFpJXIgBZDkr2rUNlZqZK7Oecrw9HKg56UbkQl5P+UawBawTxj3/q+OGLiMoN/Hm0wOm63pv0WF+eojNL6/ckCroCJIt/ALkJfwKETlDUw1jMA9/B3DRAMTNxPXU5HZ0+54XpVaod9DC41xfzve3ZdXRLeGXoNw8c8bO2xqCF17o75MvKkc7InjDvg5JgF9ejULSOqHmHgoMVXw2uq7exPhxeup3y7VZrs1yjcu7ejDHnX6f3qk9swpqf1hUw0uyTxfDQq3whvTOzOzzsurUoA1JGL32h52wVdBE4w8jEo16gs6X8ZpVnnXAbZcBCUcRflxg6TXV0eHUO8inflZEboigMmfzpT80z6zqZGlrJZ7c3pUaI/u4ZU9POTWHXnq4N4h84/wNq/nb32fzx+4=')))
"""Add a clean camera + effects window to an existing Breathing Studio project."""

def add_camera_view():
    host = op('/project1') or op('/')
    studio = host.op('BreathingStudio')
    if studio is None or not studio.fetch('breathing_studio_complete', False):
        raise RuntimeError('Open your working Breathing Studio project first, then run this add-on.')
    for name in ('trails', 'control', 'display'):
        if studio.op(name) is None:
            raise RuntimeError('Required Breathing Studio node missing: ' + name)

    def node(kind, name, x, y, text=None):
        result = studio.op(name) or studio.create(kind, name)
        result.nodeX, result.nodeY = x, y
        if text is not None:
            result.text = text
        return result

    def setting(n, name, value, expr=False, required=True):
        p = getattr(n.par, name, None)
        if p is None:
            if required:
                raise RuntimeError(f'{n.path}: missing parameter {name}. Copy this error for diagnosis.')
            return
        if expr:
            p.expr = value
        else:
            p.val = value

    def menu(n, name, choices, required=True):
        p = getattr(n.par, name, None)
        if p is not None:
            for choice in choices:
                for key, label in zip(p.menuNames, p.menuLabels):
                    if choice.lower() in (key.lower(), label.lower()):
                        p.val = key
                        return
        if required:
            raise RuntimeError(f'{n.path}: unsupported menu {name}. Copy this error for diagnosis.')

    def resolution(n, w, h):
        menu(n, 'outputresolution', ['custom'], required=False)
        setting(n, 'resolutionw', w)
        setting(n, 'resolutionh', h)

    if getattr(studio.par, 'Camerabg', None) is None:
        page = studio.appendCustomPage('Camera view')
        page.appendToggle('Camerabg', label='Show camera video')[0].val = True
        page.appendToggle('Cameraflipy', label='Flip camera vertically')[0].val = False

    previous = studio.op('capture_callbacks')
    if previous is not None:
        previous.module.shutdown(studio.op('capture_camera'))
    cb = node(textDAT, 'capture_callbacks', -700, -900, ASSETS['camera_callbacks.py'])
    camera = node(scriptTOP, 'capture_camera', -400, -900)
    setting(camera, 'callbacks', cb.path)
    camera.store('camera_online', False)
    camera.store('camera_status', 'Waiting for camera feed; restart the updated controller.')

    pixel = node(textDAT, 'capture_pixel', -400, -1100, ASSETS['capture.frag'])
    render = node(glslTOP, 'capture_render', -100, -900)
    render.inputConnectors[0].connect(studio.op('trails'))
    render.inputConnectors[1].connect(camera)
    menu(render, 'mode', ['vertexpixel'])
    menu(render, 'glslversion', ['glsl450', 'glsl430', 'glsl330'], required=False)
    setting(render, 'pixeldat', pixel.path)
    resolution(render, 1280, 720)
    render.seq.vec.numBlocks = 1
    setting(render, 'vec0name', 'uCapture')
    for c, expression in zip('xyzw', ['parent().par.Intensity', 'parent().par.Camerabg',
            "int(op('capture_camera').fetch('camera_online', False))", 'parent().par.Cameraflipy']):
        setting(render, 'vec0value' + c, expression, expr=True)
    out = node(nullTOP, 'CAPTURE_OUT', 150, -900)
    out.inputConnectors[0].connect(render)
    info = node(infoDAT, 'capture_compile', -100, -1100)
    setting(info, 'op', render.path)
    window = node(windowCOMP, 'capture_window', 400, -900)
    setting(window, 'winop', out.path)
    setting(window, 'title', 'Breathing Studio - Camera + effects')
    setting(window, 'borders', True, required=False)
    menu(window, 'size', ['automatic'])
    menu(window, 'dpiscaling', ['native'], required=False)

    # Force the Script TOP to upload on the main thread; networking stays in its worker.
    tick = node(executeDAT, 'capture_tick', 400, -1100,
        "def onFrameStart(frame):\n    op('capture_camera').cook(force=True)\n    return\n"
        "def onStart():\n    op('capture_callbacks').module.shutdown(op('capture_camera'))\n    return\n"
        "def onExit():\n    op('capture_callbacks').module.shutdown(op('capture_camera'))\n    return\n")
    for name in ('framestart', 'start', 'exit'):
        setting(tick, name, True)
    for name in ('create', 'frameend', 'playstatechange', 'devicechange'):
        setting(tick, name, False, required=False)

    def button(name, text, x, width, command):
        b = node(buttonCOMP, name, 700, -900 - x)
        for key, value in dict(x=x, y=665, w=width, h=34, label=text, fontsize=14).items():
            setting(b, key, value)
        menu(b, 'buttontype', ['momentary'])
        callback = node(panelexecuteDAT, name + '_click', 900, -900 - x,
            'def onOffToOn(panelValue):\n    ' + command + '\n    return\n')
        setting(callback, 'panels', b.path)
        setting(callback, 'panelvalue', 'state')
        setting(callback, 'offtoon', True)
        for trigger in ('whileon', 'ontooff', 'whileoff', 'valuechange'):
            setting(callback, trigger, False)
        return b

    button('capture_open', 'Camera view', 850, 170, "op('capture_window').par.winopen.pulse()")
    toggle = button('capture_toggle', 'Video: on', 1030, 180,
                    'parent().par.Camerabg = not parent().par.Camerabg.eval()')
    setting(toggle, 'label', "'Video: on' if parent().par.Camerabg else 'Video: off'", expr=True)
    text = node(textTOP, 'capture_status_text', 700, -1150)
    resolution(text, 470, 22)
    setting(text, 'text', "op('capture_camera').fetch('camera_status', 'Waiting for camera feed')", expr=True)
    setting(text, 'bgalpha', 0)
    menu(text, 'fontsizexunit', ['pixels'], required=False)
    menu(text, 'fontsizeyunit', ['pixels'], required=False)
    setting(text, 'fontsizex', 13)
    setting(text, 'fontsizey', 13, required=False)
    menu(text, 'alignx', ['left'])
    status = node(containerCOMP, 'capture_status', 700, -1250)
    for key, value in dict(x=778, y=638, w=470, h=22, bgalpha=0, top=text.path).items():
        setting(status, key, value)

    studio.store('camera_view_version', '1.0')
    camera.cook(force=True)
    studio.op('display').par.winopen.pulse()
    window.par.winopen.pulse()
    print('Camera view added. Restart the updated controller, select Camera + voice, and save your .toe.')
    print('Record the separate Camera + effects window with Shift-Command-5 on Mac.')
    return studio


add_camera_view()
