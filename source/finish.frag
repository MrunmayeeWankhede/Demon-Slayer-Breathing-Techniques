uniform vec4 uFinish; // time, style, intensity, unused
out vec4 fragColor;
void main(){
    vec2 uv=vUV.st;
    vec3 fx=texture(sTD2DInputs[0],uv).rgb;
    vec2 px=vec2(1./1280.,1./720.);
    vec3 glow=vec3(0);
    for(int x=-2;x<=2;x++) for(int y=-2;y<=2;y++)
        glow+=texture(sTD2DInputs[0],uv+vec2(x,y)*px*4.).rgb;
    fx=(fx+glow*.018)*uFinish.z;
    vec3 bg=vec3(.014,.021,.033);
    float vignette=1.-.35*length((uv-.5)*vec2(1.2,1.));
    bg*=vignette;
    // The stage ends before the controls and header.
    float stage=smoothstep(.19,.23,uv.y)*(1.-smoothstep(.77,.81,uv.y));
    vec3 col=bg+fx*stage;
    float grid=(1.-smoothstep(.0,.0015,abs(fract(uv.x*20.)-.5)/20.))+
               (1.-smoothstep(.0,.0015,abs(fract(uv.y*12.)-.5)/12.));
    col+=vec3(.013,.025,.033)*grid*stage;
    col=1.-exp(-col*1.12);
    fragColor=TDOutputSwizzle(vec4(col,1));
}
