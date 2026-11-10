/** Verify preference defaults, translations, storage boundaries and graceful fallback. */
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=readFileSync('public/ui-preferences.js','utf8');
function load(initial={},systemLight=false,blocked=false){
  const values=new Map(Object.entries(initial)),listeners={};
  const toggle=(preference,offValue,onValue)=>({dataset:{preference,offValue,onValue},attributes:{},events:{},
    setAttribute(name,value){this.attributes[name]=value;},addEventListener(name,fn){this.events[name]=fn;}});
  const welcome={dataset:{i18n:'welcome'}}, theme=toggle('theme','light','dark'),language=toggle('language','id','en');
  const document={documentElement:{dataset:{}},body:{dataset:{}},querySelector:()=>null,querySelectorAll:selector=>selector==='[data-i18n]'?[welcome]:selector==='[data-preference]'?[theme,language]:[],addEventListener:(name,fn)=>listeners[name]=fn};
  const window={dispatchEvent:()=>{},addEventListener:(name,fn)=>listeners[name]=fn};
  const localStorage={getItem:key=>{if(blocked)throw Error('blocked');return values.get(key)??null;},setItem:(key,value)=>{if(blocked)throw Error('blocked');values.set(key,value);}};
  vm.runInNewContext(source,{document,window,localStorage,matchMedia:()=>({matches:systemLight}),Event:class{}});
  return {ui:window.MerchantUI,document,values,welcome,listeners,theme,language};
}
const a=load({},true);assert.equal(a.document.documentElement.dataset.theme,'light');assert.equal(a.document.documentElement.lang,'id');
a.ui.apply();assert.equal(a.welcome.textContent,'Selamat datang.');
a.ui.set('language','en');assert.equal(a.document.documentElement.lang,'en');assert.equal(a.welcome.textContent,'Welcome back.');assert.equal(a.language.attributes['aria-checked'],'true');
a.ui.set('theme','dark');assert.equal(a.theme.attributes['aria-checked'],'true');assert.equal(a.values.get('mw.theme'),'dark');assert.equal(a.values.get('mw.language'),'en');assert.equal(a.values.size,2);
a.ui.set('theme','invalid');assert.equal(a.ui.state.theme,'dark');
const b=load(Object.fromEntries(a.values),true);assert.equal(b.ui.state.theme,'dark');assert.equal(b.ui.state.language,'en');
b.values.set('mw.theme','light');b.values.set('mw.language','id');b.listeners.storage({key:'mw.theme'});assert.equal(b.ui.state.theme,'light');assert.equal(b.ui.state.language,'id');
const c=load({'mw.theme':'invalid','mw.language':'invalid'});assert.equal(c.ui.state.theme,'dark');assert.equal(c.ui.state.language,'id');
const d=load({},false,true);d.ui.set('language','en');d.ui.set('theme','light');assert.equal(d.document.documentElement.lang,'en');assert.equal(d.document.documentElement.dataset.theme,'light');
console.log('Preferences: defaults, ID/EN, light/dark, persistence, invalid values, storage sync and blocked storage PASS');

// Use the actual click listeners, including repeated clicks and storage-driven state.
const e=load({},true);e.listeners.DOMContentLoaded();
assert.equal(e.theme.attributes['aria-checked'],'false');assert.equal(e.language.attributes['aria-checked'],'false');
e.theme.events.click();assert.equal(e.ui.state.theme,'dark');assert.equal(e.theme.attributes['aria-checked'],'true');
e.theme.events.click();assert.equal(e.ui.state.theme,'light');assert.equal(e.values.get('mw.theme'),'light');
e.language.events.click();assert.equal(e.ui.state.language,'en');assert.equal(e.language.attributes['aria-checked'],'true');
e.language.events.click();assert.equal(e.ui.state.language,'id');assert.equal(e.values.get('mw.language'),'id');
e.values.set('mw.language','en');e.listeners.storage({key:'mw.language'});assert.equal(e.language.attributes['aria-checked'],'true');
e.language.events.click();assert.equal(e.ui.state.language,'id');
const f=load({},false,true);f.listeners.DOMContentLoaded();f.theme.events.click();f.language.events.click();
assert.equal(f.theme.attributes['aria-checked'],'false');assert.equal(f.language.attributes['aria-checked'],'true');
console.log('Toggle click handlers, checked states, repeated clicks, storage sync and blocked storage PASS');
