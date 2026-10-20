// TouchDesigner GLSL TOP pixel shader. No #version line; TD supplies it.
// Original stylized procedural effects; these are not anime animation assets.
uniform vec4 uHand;   // x, y, speed, active
uniform vec4 uOther;  // x, y, active, span
uniform vec4 uState;  // seconds, style 0..8, pose 0..3, width/height
uniform vec4 uAction; // pinch, span, trigger envelope, microphone amplitude
out vec4 fragColor;
const float TAU = 6.28318530718;
float line(float d, float w) { return exp(-abs(d)/max(w, .0005)); }
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) {
    vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
float fbm(vec2 p) { return .57*noise(p)+.28*noise(p*2.03)+.15*noise(p*4.09); }
float segment(vec2 p, vec2 a, vec2 b) {
    vec2 d=b-a; return length(p-a-d*clamp(dot(p-a,d)/max(dot(d,d),.00001),0.,1.));
}
void main() {
    vec2 uv=vUV.st, p=uv-uHand.xy;
    p.x*=uState.w;
    float t=uState.x, r=length(p), a=atan(p.y,p.x);
    int style=int(uState.y+.5), form=int(uState.z+.5);
    float span=uOther.z*uAction.y;
    float radius=.11+.22*span+.04*uHand.z;
    float width=.008+.01*uHand.z+.004*uAction.x;
    float burst=uAction.z;
    float wave=.026*sin(p.x*30.-t*5.);
    float slash=line(p.y-wave,width)*exp(-abs(p.x)*4.5);
    float ring=line(r-radius,width);
    float expand=line(r-(radius+.28*(1.-burst)),width)*burst;
    vec3 color=vec3(0);
    if(style==0) { // flame tongues, rising crown, protective flame wheel
        float n=fbm(p*18.-vec2(0,t*2.));
        float flame=line(p.x+.04*sin(p.y*24.-t*8.),.025+.025*n)
                    *exp(-max(p.y,0.)*6.)*smoothstep(-.09,0.,p.y);
        float v=form==1 ? slash*(.5+n) : form==2 ? flame+ring*.35 : ring*(.6+n)+expand;
        color=mix(vec3(1,.07,.005),vec3(1,.8,.06),n)*v*1.6;
    } else if(style==1) { // water ribbon, rotating wheel, quieter concentric field
        float v=form==1 ? slash+line(p.y-wave-.023,width*.45)*exp(-abs(p.x)*5.) :
            form==2 ? ring*(.65+.35*sin(a*7.-t*4.))+line(r-radius*.78,width*.5) :
            .35*line(sin(r*65.-t*.7),.11)*exp(-r*5.);
        color=vec3(.05,.6,1.)*v+vec3(.5,.85,1.)*pow(max(v,0.),3.)*.35;
    } else if(style==2) { // thin mist lane, moving band, enclosing fog
        float n=fbm(p*9.-vec2(t*.25,t*.08));
        float mask=form==1 ? exp(-abs(p.y)*18.-abs(p.x)*2.) :
            form==2 ? exp(-abs(p.y-.06*sin(p.x*10.+t))*10.-r*2.) : exp(-r*3.);
        color=vec3(.55,.8,.88)*n*mask*(.5+.6*burst);
    } else if(style==3) { // paired rocky orbit, rising stones, angular shell
        float v=0.;
        for(int i=0;i<10;i++) {
            float k=float(i), ang=k*TAU/10.+t*.4;
            vec2 c=vec2(cos(ang),sin(ang))*radius;
            if(form==2) c=vec2((hash(vec2(k,2))-.5)*.22,fract(k*.17+t*.3)*.5-.1);
            if(form==1) c=vec2(cos(ang),sin(ang))*radius*(.65+.35*mod(k,2.));
            vec2 q=abs(p-c); float d=max(q.x*.9+q.y*.45,q.y)-.017;
            v+=line(max(d,0.),.004)*.7;
        }
        if(form==3) v+=line(r-radius*(.9+.08*cos(a*6.)),.007);
        color=vec3(.68,.49,.28)*v+vec3(.8,.7,.45)*expand*.3;
    } else if(style==4) { // flowing whip, long loops, fan of pink arcs
        float v=0.;
        for(int i=0;i<5;i++) {
            float k=float(i);
            float d=p.y-.055*sin(p.x*(10.+k)+t*(2.+k*.15))-k*.015;
            if(form==2) d=r-radius*(1.+.25*sin(a*3.+t+k*.2));
            if(form==3) d=r-(.07+k*.035)+.035*sin(a*3.+t);
            v+=line(d,width*.45)*exp(-r*2.)*.5;
        }
        color=vec3(1.,.13,.5)*v+vec3(.8,.4,.7)*expand*.3;
    } else if(style==5) { // vortex, parallel claws, expanding spiral
        float spiral=sin(a*3.+r*38.-t*6.);
        float v=line(spiral,.08)*exp(-r*5.);
        if(form==2) v=(line(p.y-wave-.05,.006)+line(p.y-wave,.006)+line(p.y-wave+.05,.006))*exp(-abs(p.x)*4.);
        if(form==3) v*=.5+burst*1.5;
        color=vec3(.45,1.,.67)*(v+expand*.4);
    } else if(style==6) { // winding ribbon, twin fangs, enclosing coil
        float v=line(p.y-.065*sin(p.x*18.-t*4.),width)*exp(-abs(p.x)*3.);
        if(form==2) v=line(segment(p,vec2(-.08,.06),vec2(0,-.10)),.008)+line(segment(p,vec2(.08,.06),vec2(0,-.10)),.008);
        if(form==3) v=line(r-radius-.025*sin(a*3.-t*3.),.009);
        color=vec3(.65,.35,1.)*v;
    } else if(style==7) { // fluttering paired wings, needle, six-point motif
        float v=0.;
        for(int i=0;i<6;i++) {
            float k=float(i), ang=k*TAU/6.+t*.5;
            vec2 q=p-vec2(cos(ang),sin(ang))*radius;
            float flap=.006+.025*abs(sin(t*11.+k));
            if(form==1) v+=exp(-pow((abs(q.x)-flap)/.015,2.)-pow(q.y/.012,2.));
            else if(form==2) v+=line(segment(p,vec2(0),vec2(cos(ang),sin(ang))*(radius+.08)),.0025)*.45;
            else v+=line(length(q)-.025,.004);
        }
        color=vec3(.7,.22,1.)*(v+expand*.25);
    } else { // sound: connected string, rotating arcs, pulsing shock rings
        float v=line(sin(r*75.-t*(3.+uAction.w*6.)),.1)*exp(-r*5.);
        if(form==1 && uOther.z>.5) {
            vec2 end=uOther.xy-uHand.xy; end.x*=uState.w;
            v+=line(segment(p,vec2(0),end),.006);
        }
        if(form==2) v*=.55+.45*sin(a*6.-t*8.);
        if(form==3) v=v*.3+expand*2.;
        color=vec3(1.,.63,.15)*v*(.7+uAction.w*.7);
    }
    color*=uHand.w*(.55+.7*uHand.z);
    if(form==0) color=vec3(0);
    fragColor=TDOutputSwizzle(vec4(color,1.));
}
