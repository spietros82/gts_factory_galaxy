Shader "Braemac/Stage3Glass" {
 Properties { _Color ("Glass tint", Color) = (0.34,0.17,0.05,0.20) }
 SubShader {
  Tags { "Queue"="Transparent" "RenderType"="Transparent" }
  ZWrite Off
  Blend SrcAlpha OneMinusSrcAlpha
  Pass {
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   fixed4 _Color;
   struct v2f { float4 vertex : SV_POSITION; };
   v2f vert(appdata_base v) { v2f o; o.vertex=UnityObjectToClipPos(v.vertex); return o; }
   fixed4 frag(v2f i) : SV_Target { return _Color; }
   ENDCG
  }
 }
}
