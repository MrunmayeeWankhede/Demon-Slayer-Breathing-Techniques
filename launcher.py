"""Breathing Studio controller installer/launcher. Run with Python 3.11 or 3.12."""
from pathlib import Path
import hashlib
import json
import os
import queue
import shutil
import ssl
import subprocess
import sys
import threading
import urllib.request
import venv
import zipfile

ROOT=Path(__file__).resolve().parent
ENV=ROOT/'.venv'
PYTHON=ENV/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
HAND_URL='https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
VOICE_URL='https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'


def download_context():
    # This launcher can run in system Python while certifi lives in our venv.
    # Ask that interpreter for its bundle without changing global certificates.
    result=subprocess.run(
        [str(PYTHON),'-c','import certifi; print(certifi.where())'],
        capture_output=True,text=True,encoding='utf-8',errors='replace',
        check=True,timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    bundle=Path(result.stdout.strip())
    if not bundle.is_file():
        raise RuntimeError('The installed certificate bundle could not be found. Retry installation.')
    context=ssl.create_default_context()
    context.load_verify_locations(cafile=str(bundle))
    return context


def download(url,path,log,expected_sha=None,context=None):
    path=Path(path)
    part=path.with_suffix(path.suffix+'.part')
    log('Downloading '+path.name+' ...')
    request=urllib.request.Request(url,headers={'User-Agent':'BreathingStudio/2.0'})
    digest=hashlib.sha256()
    if context is None:
        context=download_context()
    try:
        with urllib.request.urlopen(request,timeout=45,context=context) as response, part.open('wb') as output:
            while True:
                data=response.read(1024*512)
                if not data:
                    break
                output.write(data); digest.update(data)
        if expected_sha and digest.hexdigest()!=expected_sha:
            raise RuntimeError('Downloaded file checksum mismatch: '+path.name)
        part.replace(path)
    finally:
        part.unlink(missing_ok=True)


def extract_voice(archive,models):
    # Validate every archive path before extraction.
    models=Path(models).resolve()
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            dest=(models/member.filename).resolve()
            if models not in dest.parents:
                raise RuntimeError('Invalid path in model archive')
        z.extractall(models)


def prepare(log,run):
    if sys.version_info[:2] not in [(3,11),(3,12)]:
        raise RuntimeError('Please run this launcher using Python 3.11 or 3.12 from python.org.')
    if not PYTHON.exists():
        log('Creating a private Python environment...')
        venv.EnvBuilder(with_pip=True).create(ENV)
    marker=ENV/'breathing-installed.json'
    req_digest=hashlib.sha256((ROOT/'requirements.txt').read_bytes()).hexdigest()
    installed={}
    if marker.exists():
        try:
            installed=json.loads(marker.read_text())
        except (ValueError,OSError):
            pass
    if installed.get('requirements')!=req_digest:
        run([str(PYTHON),'-m','pip','install','--upgrade','pip'])
        run([str(PYTHON),'-m','pip','install','-r',str(ROOT/'requirements.txt')])
        run([str(PYTHON),'-c','import cv2, mediapipe, vosk; from pythonosc.udp_client import SimpleUDPClient; print("Core imports OK")'])
        marker.write_text(json.dumps({'requirements':req_digest}),encoding='utf-8')
    models=ROOT/'models'; models.mkdir(exist_ok=True)
    hashes=json.loads((ROOT/'model-checksums.json').read_text())
    context=download_context()
    hand=models/'hand_landmarker.task'
    if not hand.exists() or hashlib.sha256(hand.read_bytes()).hexdigest()!=hashes['hand_landmarker.task']:
        download(HAND_URL,hand,log,hashes['hand_landmarker.task'],context=context)
    voice=models/'vosk-model-small-en-us-0.15'
    complete=voice/'.download-complete'
    if not complete.exists():
        archive=models/'vosk-model-small-en-us-0.15.zip'
        download(VOICE_URL,archive,log,hashes[archive.name],context=context)
        extract_voice(archive,models)
        if not (voice/'am/final.mdl').is_file():
            raise RuntimeError('Speech model did not extract correctly.')
        complete.write_text('Downloaded and checksum verified.\n')
        archive.unlink()
    log('Ready. Models are local; camera and voice processing stay on this computer.')


def main():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print('This Python has no Tk window support. Install Python 3.11 or 3.12 from python.org.')
        raise SystemExit(1)
    root=tk.Tk()
    root.title('Breathing Studio — Controller')
    root.geometry('780x630')
    root.configure(bg='#101823')
    style=ttk.Style(); style.theme_use('clam')
    style.configure('TFrame',background='#101823')
    style.configure('TLabel',background='#101823',foreground='#dce6ef',font=('Arial',11))
    style.configure('Title.TLabel',font=('Arial',25,'bold'),foreground='#7fcaff')
    style.configure('TButton',font=('Arial',11),padding=9)
    style.configure('TCheckbutton',background='#101823',foreground='#dce6ef')
    body=ttk.Frame(root,padding=24); body.pack(fill='both',expand=True)
    ttk.Label(body,text='BREATHING STUDIO',style='Title.TLabel').pack(anchor='w')
    ttk.Label(body,text='Camera + voice controller for your TouchDesigner project.').pack(anchor='w',pady=(5,18))
    ttk.Label(body,text='First start installs dependencies and downloads about 50 MB of models.').pack(anchor='w')
    ttk.Label(body,text='In TouchDesigner, run INSTALL_IN_TOUCHDESIGNER.py once to build the interface.').pack(anchor='w',pady=(4,16))
    options=ttk.Frame(body); options.pack(fill='x')
    camera=tk.StringVar(value='0'); mic=tk.StringVar(value=''); hand=tk.StringVar(value='Right'); voice=tk.BooleanVar(value=True)
    config_path=ROOT/'controller-settings.json'
    try:
        config=json.loads(config_path.read_text())
        camera.set(str(config.get('camera',0))); mic.set(str(config.get('mic','')))
        hand.set(config.get('hand','Right')); voice.set(config.get('voice',True))
    except (OSError,ValueError):
        pass
    for col,(label,var,width) in enumerate([('Camera index',camera,8),('Microphone index (blank = default)',mic,12)]):
        ttk.Label(options,text=label).grid(row=0,column=col*2,sticky='w',padx=(0,8))
        ttk.Entry(options,textvariable=var,width=width).grid(row=1,column=col*2,sticky='w',pady=(4,10))
    ttk.Label(options,text='Controlling hand label').grid(row=0,column=4,sticky='w')
    ttk.Combobox(options,textvariable=hand,values=['Right','Left'],state='readonly',width=10).grid(row=1,column=4,sticky='w')
    ttk.Checkbutton(body,text='Enable voice commands',variable=voice).pack(anchor='w',pady=(0,12))
    buttons=ttk.Frame(body); buttons.pack(fill='x')
    status=tk.StringVar(value='Ready to install and start. Mouse demo works in TouchDesigner without this launcher.')
    ttk.Label(body,textvariable=status,wraplength=720).pack(anchor='w',pady=(12,8))
    output=tk.Text(body,height=14,bg='#080e16',fg='#a6bacd',font=('Courier',10),relief='flat',wrap='word')
    output.pack(fill='both',expand=True)
    events=queue.Queue(); state={'bridge':None,'install':None,'busy':False,'closing':False}
    log_file=(ROOT/'controller.log').open('a',encoding='utf-8',buffering=1)

    def log(message):
        events.put(('log',str(message)))

    def run(command):
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        proc=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf-8',errors='replace',creationflags=creationflags)
        state['install']=proc
        for line in proc.stdout:
            log(line.rstrip())
        code=proc.wait(); state['install']=None
        if code:
            raise RuntimeError(f'Command failed (exit {code}). See the log above.')

    def worker(settings,list_devices=False):
        try:
            prepare(log,run)
            if list_devices:
                run([str(PYTHON),str(ROOT/'bridge.py'),'--list-mics'])
                events.put(('status','Microphone devices are listed below. Enter an input-device index if needed.'))
                return
            log('Testing hand tracker before opening camera or microphone...')
            events.put(('status','Testing hand tracker...'))
            try:
                run([str(PYTHON),'-u',str(ROOT/'bridge.py'),'--self-test'])
            except RuntimeError as exc:
                raise RuntimeError('Hand tracker self-test failed before camera/microphone access. '
                                   'Copy the test log above for diagnosis. '+str(exc)) from exc
            config_path.write_text(json.dumps(settings,indent=2),encoding='utf-8')
            command=[str(PYTHON),'-u',str(ROOT/'bridge.py'),'--camera',str(settings['camera']),'--hand',settings['hand']]
            if settings['mic']!='': command+=['--mic',str(settings['mic'])]
            if not settings['voice']: command+=['--no-voice']
            proc=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                  text=True,encoding='utf-8',errors='replace')
            state['bridge']=proc
            events.put(('status','Controller starting. Allow camera/microphone access if your OS asks.'))
            for line in proc.stdout:
                log(line.rstrip())
            code=proc.wait(); state['bridge']=None
            events.put(('status','Controller stopped.' if code==0 else f'Controller exited (code {code}). See the error or crash trace in the log.'))
        except Exception as exc:
            log('ERROR: '+str(exc))
            events.put(('status','Could not start. See the error in the log.'))
        finally:
            events.put(('busy',False))

    def start(list_devices=False):
        if state['busy']: return
        try:
            settings={'camera':int(camera.get()),'mic':int(mic.get()) if mic.get().strip() else '',
                      'hand':hand.get(),'voice':voice.get()}
        except ValueError:
            messagebox.showerror('Device index','Camera and microphone indexes must be whole numbers.'); return
        state['busy']=True
        start_button.state(['disabled']); devices_button.state(['disabled'])
        status.set('Preparing the controller. The first installation can take several minutes.')
        threading.Thread(target=worker,args=(settings,list_devices),daemon=True).start()

    def stop():
        proc=state.get('bridge')
        if proc and proc.poll() is None:
            proc.terminate()
        elif state.get('install'):
            status.set('Installation is still running. Wait until it finishes before starting the controller.')

    start_button=ttk.Button(buttons,text='Install / Start controller',command=start); start_button.pack(side='left',padx=(0,8))
    ttk.Button(buttons,text='Stop',command=stop).pack(side='left',padx=(0,8))
    devices_button=ttk.Button(buttons,text='List microphones',command=lambda:start(True)); devices_button.pack(side='left')

    def poll():
        while True:
            try: kind,value=events.get_nowait()
            except queue.Empty: break
            if kind=='log':
                output.insert('end',value+'\n'); output.see('end'); log_file.write(value+'\n')
            elif kind=='status': status.set(value)
            else:
                state['busy']=value; start_button.state(['!disabled']); devices_button.state(['!disabled'])
        root.after(100,poll)

    def close():
        state['closing']=True
        for key in ['bridge','install']:
            proc=state.get(key)
            if proc and proc.poll() is None: proc.terminate()
        log_file.close(); root.destroy()
    root.protocol('WM_DELETE_WINDOW',close)
    poll(); root.mainloop()


if __name__=='__main__':
    main()
