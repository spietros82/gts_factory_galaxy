import json,time,urllib.request
from dataclasses import dataclass
@dataclass(frozen=True)
class ModelRequest:
    task:str
    model:str
    messages:list
    schema:dict
@dataclass
class ModelResponse:
    raw:dict
    wall_seconds:float
    backend:str
    error:str=''
def ollama_payload(req):
    return {'model':req.model,'messages':req.messages,'format':req.schema,'stream':False,'think':False,'keep_alive':'30m',
            'options':{'temperature':0,'seed':42,'num_ctx':8192,'num_predict':512}}
class OllamaAdapter:
    def __init__(self,endpoint,timeout=120):self.endpoint=endpoint.rstrip('/');self.timeout=timeout
    def execute(self,req):
        payload=ollama_payload(req)
        start=time.perf_counter()
        try:
            request=urllib.request.Request(self.endpoint+'/api/chat',json.dumps(payload).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=self.timeout) as response:raw=json.load(response)
            return ModelResponse(raw,time.perf_counter()-start,'Ollama')
        except Exception as e:return ModelResponse({},time.perf_counter()-start,'Ollama',type(e).__name__+': '+str(e))
class FakeAdapter:
    def __init__(self,raw=None,error=''):self.raw=raw or {};self.error=error
    def execute(self,req):return ModelResponse(self.raw,0,'fake/test',self.error)
ASSIST_SCHEMA={'type':'object','properties':{'explanation':{'type':'string'},'next_check':{'type':'string'},'uncertainty':{'type':'string'},'evidence_ids':{'type':'array','items':{'type':'string'}},'procedure_ids':{'type':'array','items':{'type':'string'}}},'required':['explanation','next_check','uncertainty','evidence_ids','procedure_ids'],'additionalProperties':False}
VISION_SCHEMA={'type':'object','properties':{'cap_result':{'type':'string','enum':['present','missing','displaced','uncertain']},'observation':{'type':'string'}},'required':['cap_result','observation'],'additionalProperties':False}
def validate_response(task,response,allowed_evidence=(),allowed_procedures=()):
    if response.error:raise ValueError(response.error)
    raw=response.raw
    if raw.get('done') is not True or raw.get('done_reason') not in ['stop',None]:raise ValueError('Incomplete or truncated response')
    value=json.loads(raw.get('message',{}).get('content',''))
    schema=ASSIST_SCHEMA if task=='assistant' else VISION_SCHEMA
    if not isinstance(value,dict) or set(value)!=set(schema['required']):raise ValueError('Schema mismatch')
    for key,definition in schema['properties'].items():
        if definition['type']=='string' and not isinstance(value[key],str):raise ValueError('Invalid field type')
        if definition['type']=='array' and (not isinstance(value[key],list) or any(not isinstance(i,str) for i in value[key])):raise ValueError('Invalid reference list')
    if task=='assistant':
        if set(value['evidence_ids'])-set(allowed_evidence) or set(value['procedure_ids'])-set(allowed_procedures):raise ValueError('Unknown evidence/procedure reference')
    elif value['cap_result'] not in VISION_SCHEMA['properties']['cap_result']['enum']:raise ValueError('Unsupported result')
    return value
