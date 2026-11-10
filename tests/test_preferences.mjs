/** Verify preference defaults, translations, storage boundaries and graceful fallback. */
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=readFileSync('public/ui-preferences.js','utf8');
function load(initial={},systemLight=false,blocked=false){
  const values=new Map(Object.entries(initial)),listeners={};
  const welcome={dataset:{i18n:'welcome'}}, theme={dataset:{preference:'theme'}},language={dataset:{preference:'language'}};
  const document={documentElement:{dataset:{}},body:{dataset:{}},querySelector:()=>null,querySelectorAll:selector=>selector==='[data-i18n]'?[welcome]:selector==='[data-preference]'?[theme,language]:[],addEventListener:(name,fn)=>listeners[name]=fn};
  const window={dispatchEvent:()=>{},addEventListener:(name,fn)=>listeners[name]=fn};
  const localStorage={getItem:key=>{if(blocked)throw Error('blocked');return values.get(key)??null;},setItem:(key,value)=>{if(blocked)throw Error('blocked');values.set(key,value);}};
  vm.runInNewContext(source,{document,window,localStorage,matchMedia:()=>({matches:systemLight}),Event:class{}});
  return {ui:window.MerchantUI,document,values,welcome,listeners,theme,language};
}
const a=load({},true);assert.equal(a.document.documentElement.dataset.theme,'light');assert.equal(a.document.documentElement.lang,'id');
a.ui.apply();assert.equal(a.welcome.textContent,'Selamat datang.');
a.ui.set('language','en');assert.equal(a.document.documentElement.lang,'en');assert.equal(a.welcome.textContent,'Welcome back.');assert.equal(a.language.value,'en');
a.ui.set('theme','dark');assert.equal(a.theme.value,'dark');assert.equal(a.values.get('mw.theme'),'dark');assert.equal(a.values.get('mw.language'),'en');assert.equal(a.values.size,2);
a.ui.set('theme','invalid');assert.equal(a.ui.state.theme,'dark');
const b=load(Object.fromEntries(a.values),true);assert.equal(b.ui.state.theme,'dark');assert.equal(b.ui.state.language,'en');
b.values.set('mw.theme','light');b.values.set('mw.language','id');b.listeners.storage({key:'mw.theme'});assert.equal(b.ui.state.theme,'light');assert.equal(b.ui.state.language,'id');
const c=load({'mw.theme':'invalid','mw.language':'invalid'});assert.equal(c.ui.state.theme,'dark');assert.equal(c.ui.state.language,'id');
const d=load({},false,true);d.ui.set('language','en');d.ui.set('theme','light');assert.equal(d.document.documentElement.lang,'en');assert.equal(d.document.documentElement.dataset.theme,'light');
console.log('Preferences: defaults, ID/EN, light/dark, persistence, invalid values, storage sync and blocked storage PASS');
