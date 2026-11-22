'use strict';
const express=require('express');
const crypto=require('crypto');
const fs=require('fs');
const path=require('path');
const app=express();
app.use(express.json({limit:'2mb'}));
const PORT=process.env.PORT||3000;
const SITE_URL=(process.env.SITE_URL||'https://nvp105.onrender.com').replace(/\/$/,'');
const API_TOKEN=process.env.LINK4M_API_TOKEN;
const ADMIN_PASSWORD=process.env.ADMIN_PASSWORD;
const JWT_SECRET=process.env.JWT_SECRET;
const DATA_DIR=process.env.DATA_DIR||'/var/data';
const DB_FILE=path.join(DATA_DIR,'phong-data.json');
if(!API_TOKEN||!ADMIN_PASSWORD||!JWT_SECRET) console.warn('Missing LINK4M_API_TOKEN / ADMIN_PASSWORD / JWT_SECRET environment variables');
fs.mkdirSync(DATA_DIR,{recursive:true});
const empty={config:null,stats:{visits:0,success:0,failed:0,downloads:0,daily:{},items:{}},shortlinks:{}};
let db=empty;
try{db={...empty,...JSON.parse(fs.readFileSync(DB_FILE,'utf8'))};}catch{}
if(!db.adminPasswordHash && ADMIN_PASSWORD){const salt=crypto.randomBytes(16).toString('hex');const hash=crypto.scryptSync(ADMIN_PASSWORD,salt,64).toString('hex');db.adminPasswordHash={salt,hash};}
function persist(){const tmp=DB_FILE+'.tmp';fs.writeFileSync(tmp,JSON.stringify(db,null,2));fs.renameSync(tmp,DB_FILE)}
function sign(payload){const body=Buffer.from(JSON.stringify(payload)).toString('base64url');const sig=crypto.createHmac('sha256',JWT_SECRET).update(body).digest('base64url');return body+'.'+sig}
function auth(req,res,next){const token=(req.headers.authorization||'').replace(/^Bearer\s+/i,'');if(!token)return res.status(401).json({error:'Cần đăng nhập'});const [body,sig]=token.split('.');const expected=crypto.createHmac('sha256',JWT_SECRET||'').update(body||'').digest('base64url');if(!body||!sig||!crypto.timingSafeEqual(Buffer.from(sig),Buffer.from(expected)))return res.status(401).json({error:'Phiên đăng nhập không hợp lệ'});let p;try{p=JSON.parse(Buffer.from(body,'base64url').toString())}catch{}if(!p||p.exp<Date.now())return res.status(401).json({error:'Phiên đăng nhập đã hết hạn'});next()}
const validKey=k=>typeof k==='string'&&/^[a-z0-9_-]{1,50}$/.test(k);
function bump(field,key){db.stats[field]=(db.stats[field]||0)+1;const day=new Date().toISOString().slice(0,10);db.stats.daily[day]=(db.stats.daily[day]||0)+ (field==='visits'?1:0);if(key){db.stats.items[key]=db.stats.items[key]||{success:0,downloads:0};if(field==='success'||field==='downloads')db.stats.items[key][field]++}persist()}
app.get('/api/config',(req,res)=>res.json({config:db.config}));
app.get('/api/stats',(req,res)=>res.json({stats:db.stats}));
app.post('/api/visit',(req,res)=>{bump('visits');res.json({ok:true})});
app.post('/api/success',(req,res)=>{const {key}=req.body||{};if(!validKey(key))return res.status(400).json({error:'Key không hợp lệ'});bump('success',key);res.json({ok:true})});
app.post('/api/download',(req,res)=>{const {key}=req.body||{};if(!validKey(key))return res.status(400).json({error:'Key không hợp lệ'});bump('downloads',key);res.json({ok:true})});
app.post('/api/link4m/create',async(req,res)=>{
  try{
    if(!API_TOKEN)return res.status(503).json({error:'Chưa cấu hình LINK4M_API_TOKEN trên Render'});
    const {key}=req.body||{};if(!validKey(key))return res.status(400).json({error:'Key không hợp lệ'});
    const item=(db.config?.destinations||[]).find(x=>x.key===key);
    if(!item||!item.enabled||item.status!=='available')return res.status(404).json({error:'Mục tải không khả dụng'});
    const target=SITE_URL+'/#/return/'+encodeURIComponent(key);
    // Reuse cached Link4M URL only if the exact return destination has already been created.
    const cached=db.shortlinks[key];if(cached&&cached.target===target)return res.json({shortenedUrl:cached.url,cached:true});
    const endpoint=new URL('https://link4m.co/api-shorten/v2');endpoint.searchParams.set('api',API_TOKEN);endpoint.searchParams.set('url',target);
    const response=await fetch(endpoint,{signal:AbortSignal.timeout(15000)});if(!response.ok)throw new Error('Link4M HTTP '+response.status);
    const result=await response.json();if(result.status!=='success'||!/^https:\/\/link4m\.com\//i.test(result.shortenedUrl||''))return res.status(502).json({error:result.message||'Link4M không tạo được link'});
    db.shortlinks[key]={target,url:result.shortenedUrl,createdAt:new Date().toISOString()};persist();res.json({shortenedUrl:result.shortenedUrl});
  }catch(e){console.error('Link4M error',e);res.status(502).json({error:'Không kết nối được Link4M. Vui lòng thử lại.'})}
});
app.post('/api/admin/login',(req,res)=>{const pass=String(req.body?.password||'');const stored=db.adminPasswordHash;if(!stored)return res.status(503).json({error:'Chưa cấu hình ADMIN_PASSWORD trên Render'});const hash=crypto.scryptSync(pass,stored.salt,64);if(!crypto.timingSafeEqual(hash,Buffer.from(stored.hash,'hex')))return res.status(401).json({error:'Mật khẩu quản trị không chính xác'});res.json({token:sign({exp:Date.now()+8*60*60*1000,role:'admin'})})});
app.post('/api/admin/change-password',auth,(req,res)=>{const pass=String(req.body?.password||'');if(pass.length<12)return res.status(400).json({error:'Mật khẩu mới cần ít nhất 12 ký tự'});const salt=crypto.randomBytes(16).toString('hex');db.adminPasswordHash={salt,hash:crypto.scryptSync(pass,salt,64).toString('hex')};persist();res.json({ok:true})});
app.put('/api/admin/config',auth,(req,res)=>{const c=req.body?.config;if(!c||!Array.isArray(c.destinations)||!Array.isArray(c.playlist))return res.status(400).json({error:'Cấu hình không hợp lệ'});db.config=c;persist();res.json({ok:true})});
app.get('/api/admin/stats',auth,(req,res)=>res.json({stats:db.stats,shortlinks:db.shortlinks}));
app.use(express.static(path.join(__dirname)));
app.get('*',(req,res)=>res.sendFile(path.join(__dirname,'index.html')));
app.listen(PORT,()=>console.log('PHONG WEB server listening on '+PORT));
