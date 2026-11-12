/** Verify getAuthCode() rejection boundaries with a controlled browser message interface. */
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const listeners=new Set(); let sent, timeout;
const parent={postMessage:(message,origin)=>{sent={message,origin};}};
const window={parent,addEventListener:(_,fn)=>listeners.add(fn),removeEventListener:(_,fn)=>listeners.delete(fn)};
const context=vm.createContext({window,URL,crypto:{randomUUID:()=> 'request-1'},setTimeout:fn=>{timeout=fn;return 1;},clearTimeout:()=>{}});
vm.runInContext(readFileSync('public/merchant-bridge.js','utf8').replace('export function','function'),context);
const bridge=vm.runInContext("createMerchantBridge({merchantOrigin:'https://merchant.test'})",context);
let resolved=false;
const pending=bridge.getAuthCode().then(value=>{resolved=true;return value;});
assert.equal(sent.origin,'https://merchant.test');
assert.deepEqual(JSON.parse(JSON.stringify(sent.message)),{type:'miniapp.authcode.request',request_id:'request-1'});
const data={type:'miniapp.authcode.response',request_id:'request-1',data:{authCode:'synthetic-test-code',expiresIn:300}};
for(const event of [
 {origin:'https://evil.test',source:parent,data},
 {origin:'https://merchant.test',source:{},data},
 {origin:'https://merchant.test',source:parent,data:{...data,request_id:'other'}},
 {origin:'https://merchant.test',source:parent,data:{...data,type:'miniapp.auth.response'}},
 {origin:'https://merchant.test',source:parent,data:{...data,data:{authCode:'x',expiresIn:'300'}}},
 {origin:'https://merchant.test',source:parent,data:{...data,data:{authCode:'x'.repeat(2049),expiresIn:300}}},
 {origin:'https://merchant.test',source:parent,data:{...data,data:{authCode:42,expiresIn:300}}},
 {origin:'https://merchant.test',source:parent,data:{...data,data:undefined,error:{code:7}}}
]) for(const listener of listeners) listener(event);
await Promise.resolve();assert.equal(resolved,false);assert.equal(listeners.size,1);
for(const listener of listeners)listener({origin:'https://merchant.test',source:parent,data});
const result=await pending;assert.equal(result.authCode,'synthetic-test-code');assert.equal(result.expiresIn,300);assert.equal(listeners.size,0);
const refused=bridge.getAuthCode();
for(const listener of listeners)listener({origin:'https://merchant.test',source:parent,data:{type:'miniapp.authcode.response',request_id:'request-1',error:{code:'UNAUTHENTICATED'}}});
await assert.rejects(refused,/UNAUTHENTICATED/);assert.equal(listeners.size,0);
const failure=bridge.getAuthCode();timeout();await assert.rejects(failure,/BRIDGE_TIMEOUT/);assert.equal(listeners.size,0);
window.parent=window;await assert.rejects(bridge.getAuthCode(),/CONTAINER_REQUIRED/);
console.log('SDK getAuthCode origin/source/request ID/schema, error, cleanup, timeout and standalone checks: PASS');
