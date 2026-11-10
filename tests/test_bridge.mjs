/** Verify SDK rejection boundaries with a controlled browser message interface. */
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
const pending=bridge.getAccessToken().then(value=>{resolved=true;return value;});
assert.equal(sent.origin,'https://merchant.test');
const data={type:'miniapp.auth.response',request_id:'request-1',data:{access_token:'synthetic-test',token_type:'Bearer',expires_in:300,merchant_code:'test'}};
for(const event of [
 {origin:'https://evil.test',source:parent,data},
 {origin:'https://merchant.test',source:{},data},
 {origin:'https://merchant.test',source:parent,data:{...data,request_id:'other'}},
 {origin:'https://merchant.test',source:parent,data:{...data,data:{access_token:'bad-shape'}}}
]) for(const listener of listeners) listener(event);
await Promise.resolve();assert.equal(resolved,false);
for(const listener of listeners)listener({origin:'https://merchant.test',source:parent,data});
assert.equal((await pending).access_token,'synthetic-test');assert.equal(listeners.size,0);
const failure=bridge.getAccessToken();timeout();await assert.rejects(failure,/BRIDGE_TIMEOUT/);assert.equal(listeners.size,0);
window.parent=window;await assert.rejects(bridge.getAccessToken(),/CONTAINER_REQUIRED/);
console.log('SDK origin/source/request ID/schema, cleanup, timeout and standalone checks: PASS');
