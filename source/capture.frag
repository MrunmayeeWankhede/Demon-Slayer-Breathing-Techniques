uniform vec4 uCapture; // intensity, show camera, camera online, flip camera vertically
out vec4 fragColor;
void main(){
    vec2 uv=vUV.st;
    vec2 cameraUV=vec2(uv.x, uCapture.w > .5 ? 1.-uv.y : uv.y);
    vec3 camera=texture(sTD2DInputs[1],cameraUV).rgb;
    vec3 fx=texture(sTD2DInputs[0],uv).rgb;
    vec3 glow=vec3(0);
    vec2 px=vec2(1./1280.,1./720.);
    for(int x=-2;x<=2;x++) for(int y=-2;y<=2;y++)
        glow+=texture(sTD2DInputs[0],uv+vec2(x,y)*px*4.).rgb;
    fx=1.-exp(-max((fx+glow*.018)*uCapture.x,vec3(0))*1.12);
    vec3 bg=mix(vec3(.014,.021,.033),camera,uCapture.y*uCapture.z);
    vec3 col=1.-(1.-bg)*(1.-fx);
    fragColor=TDOutputSwizzle(vec4(col,1));
}
