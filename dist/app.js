'use strict';
const root='https://lobotomycorporation.wiki.gg/wiki/';
const data=[
['O-03-03','一罪与百善','One Sin and Hundreds of Good Deeds','ZAYIN','骷髅与十字架','游戏第一天接触的异想体，是熟悉收容与工作流程的起点。','先熟悉员工指派、工作结果和资料解锁，再逐步接触更高风险的收容对象。'],
['O-03-60','碧蓝新星','Blue Star','ALEPH','收容高危实体','以蓝色心脏与众多腿部构成的形象出现，是高危险等级异想体。','安排工作或镇压前查阅完整管理须知，留意员工属性要求与精神伤害防护。'],
['O-06-20','一无所有','Nothing There','ALEPH','拟态收容对象','以模仿与变化为核心特征的高危异想体。','核对员工条件与防具，再安排工作；突破后暂停观察形态与攻击动作。'],
['O-02-56','惩戒鸟','Punishing Bird','TETH','黑森林相关','体型很小的鸟类异想体，其惩戒行为需要独立于普通镇压逻辑来理解。','不要把所有突破都当作必须立即攻击的目标，先阅读它对攻击行为的反应。'],
['T-01-68','亡蝶葬仪','Funeral of the Dead Butterflies','HE','棺木与蝴蝶','与棺木和蝴蝶意象相连的异想体。','查看管理须知中对不同属性的限制，不要仅凭员工总等级判断是否适合。'],
['O-01-04','憎恶女王','The Queen of Hatred','WAW','魔法少女','以魔法少女形象出现，状态变化是管理中的重要关注点。','关注状态提示与管理须知，避免连续安排工作却忽略其当前状态。'],
['O-02-40','大鸟','Big Bird','WAW','黑森林相关','携带灯笼、身上布满眼睛的鸟类异想体，与黑森林故事有关。','阅读突破与特殊行为说明，避免员工在突发事件中无目的地移动。'],
['O-02-62','审判鸟','Judgement Bird','WAW','黑森林相关','持有天平的长颈鸟类异想体，与审判意象有关。','留意特殊伤害与防具抗性，镇压前不要只比较员工生命值。'],
['F-01-57','小红帽雇佣兵','Little Red Riding Hooded Mercenary','WAW','童话相关','以持械雇佣兵形象出现，原型与小红帽故事相连。','使用特殊交互前核对目标与费用，并查阅与其他异想体的关联。'],
['F-02-58','又大又可能很坏的狼','Big and Will be Bad Wolf','WAW','童话相关','与狼和童话意象有关，与小红帽雇佣兵存在关联。','收容组合也会影响管理难度，阅读关联词条后再安排员工。'],
['T-01-02','焦化少女','Scorched Girl','TETH','燃烧意象','与燃烧、火柴和少女意象有关的异想体。','及时查看工作结果与计数器变化，突破时先保护脆弱员工。'],
['F-05-52','韦尔奇乐牌汽水','Opened Can of WellCheers','ZAYIN','自动售货机','以饮料售货机形象出现。低危险等级并不代表所有工作结果都安全。','即使面对 ZAYIN，也要解锁并阅读管理须知，避免把低风险误当成零风险。']
].map(([id,name,en,risk,tag,description,tip])=>({id,name,en,risk,tag,description,tip,url:root+en.replaceAll(' ','_')}));
const colors={ZAYIN:'#a3cb9f',TETH:'#bfc785',HE:'#e3b876',WAW:'#d99ed4',ALEPH:'#ef8d83'};
let query='',risk='ALL';
const main=document.querySelector('main');
function esc(s){return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')}
function title(k,h,p){return '<div class="eyebrow">'+k+'</div><h1>'+h+'</h1><p class="intro">'+p+'</p>'}
function footer(){return '<footer><span>脑叶公司 WIKI · 非官方粉丝项目</span><span>首版收录 '+data.length+' 个精选异想体 · 非全量图鉴</span></footer>'}
function source(url,label){return '<a class="source" href="'+url+'" target="_blank" rel="noopener noreferrer">'+label+' ↗</a>'}
function cards(){
const items=data.filter(a=>(risk==='ALL'||risk===a.risk)&&[a.id,a.name,a.en,a.tag].join(' ').toLowerCase().includes(query.trim().toLowerCase()));
document.querySelector('#count').textContent=items.length+' / '+data.length+' 份档案';
document.querySelector('#cards').innerHTML=items.length?items.map(a=>'<a class="card" href="#entry/'+a.id+'" aria-label="查看'+a.name+'档案"><div class="cardtop"><span class="code">'+a.id+'</span><span class="risk" style="color:'+colors[a.risk]+'">'+a.risk+'</span></div><h3>'+a.name+'</h3><div class="en">'+a.en+'</div><div class="cardbottom"><span>'+a.tag+'</span><span class="arrow">查看档案 ↗</span></div></a>').join(''):'<div class="empty"><h2>未找到匹配档案</h2><p class="intro">试试中文名、英文名或编号，例如「一罪」或「O-03-03」。</p><button class="chip" id="reset">清除筛选</button></div>';
document.querySelector('#reset')?.addEventListener('click',()=>{query='';risk='ALL';render()});
}
function render(){
const route=location.hash.slice(1)||'archive',key=route.startsWith('entry/')?'archive':route;
document.querySelectorAll('nav a').forEach(a=>{const active=a.hash==='#'+key;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
const name=({archive:'异想体档案',guide:'主管入门',mechanics:'工作与伤害',about:'关于与资料来源'})[key]||'档案';
document.querySelector('#breadcrumb').textContent=name;document.title=name+' · 脑叶公司 Wiki';
if(route==='archive'){
main.innerHTML='<div class="titleline"><div>'+title('ABNORMALITY DATABASE','异想体档案','每一次成功的收容，都始于充分的了解。')+'</div><div class="number">'+data.length+'</div></div><input class="search" type="search" aria-label="搜索异想体" placeholder="搜索名称、英文名或收容编号…" value="'+esc(query)+'"><div class="filters" aria-label="危险等级筛选">'+['ALL','ZAYIN','TETH','HE','WAW','ALEPH'].map(r=>'<button class="chip '+(r===risk?'selected':'')+'" data-risk="'+r+'" aria-pressed="'+(r===risk)+'">'+(r==='ALL'?'全部等级':r)+'</button>').join('')+'</div><div class="listhead"><span>收容对象 / INDEX</span><span id="count" role="status" aria-live="polite"></span></div><div class="cards" id="cards"></div><div class="notice">本区包含名称、危险等级与基础管理方向。首版为精选入门档案；精确数值、完整工作偏好与特殊条件请以游戏内资料和词条来源为准。</div>'+footer();
cards();document.querySelector('.search').addEventListener('input',e=>{query=e.target.value;cards()});
document.querySelectorAll('[data-risk]').forEach(b=>b.addEventListener('click',()=>{risk=b.dataset.risk;document.querySelectorAll('[data-risk]').forEach(x=>{x.classList.toggle('selected',x.dataset.risk===risk);x.setAttribute('aria-pressed',x.dataset.risk===risk)});cards()}));
}else if(route.startsWith('entry/')){
const a=data.find(x=>x.id===route.slice(6));
if(!a){main.innerHTML=title('404 / NOT FOUND','档案未收录','该编号不在首版档案中。')+'<a class="back" href="#archive">← 返回档案库</a>';return}
document.title=a.name+' · 脑叶公司 Wiki';
main.innerHTML='<article><a class="back" href="#archive">← 返回异想体档案</a><div class="articlehead">'+title(a.id,a.name,a.en)+'</div><div class="facts"><div><small>危险等级</small><strong style="color:'+colors[a.risk]+'">'+a.risk+'</strong></div><div><small>收容编号</small><strong>'+a.id+'</strong></div><div><small>档案主题</small><strong>'+a.tag+'</strong></div></div><section><h2>对象概览</h2><p>'+a.description+'</p></section><section><h2>管理阅读建议</h2><p>'+a.tip+'</p><div class="notice">这是入门阅读建议，不是完整操作配方。工作偏好会受到属性等级影响；派遣前请核对游戏内管理须知。</div></section><section><h2>延伸阅读</h2><p>'+source(a.url,'英文 Wiki：'+a.en)+'</p><p><a class="source" href="#mechanics">了解四种工作与四类伤害 →</a></p><p><a class="source" href="#guide">新任主管检查清单 →</a></p></section></article>'+footer();
}else if(route==='guide'){
main.innerHTML=title('MANAGER HANDBOOK','欢迎上任，主管。','先稳定完成一天，再追求更高的能源产量。')+'<div class="guidegrid">'+[
['01 / 准备','先读资料，再派员工','检查工作偏好、管理须知和员工属性。等级高不等于一定符合条件。'],
['02 / 工作','一次观察一个变量','确认员工状态，选择工作类型，观察结果。对陌生异想体不要同时派出多名关键员工冒险。'],
['03 / 预警','关注计数器与熔毁','逆卡巴拉计数器和熔毁是不同机制。看到警告时暂停，确认触发对象与处理时限。'],
['04 / 应急','先保人，再处理事件','暂停后检查突破位置、员工路线及装备抗性；不要让低抗性员工盲目加入镇压。']
].map(([n,h,p])=>'<section class="guidebox"><div class="eyebrow">'+n+'</div><h2>'+h+'</h2><p>'+p+'</p></section>').join('')+'</div><article><section><h2>开工前的三个问题</h2><ul><li>这名员工的属性，是否满足特殊要求？</li><li>防具对即将承受的伤害，是否有合适的抗性？</li><li>如果工作失败，我知道下一步该处理什么吗？</li></ul></section><p><a class="source" href="#mechanics">下一步：理解工作与伤害 →</a></p></article>'+footer();
}else if(route==='mechanics'){
main.innerHTML=title('OPERATIONS REFERENCE','工作与伤害','工作类型决定互动方式，伤害类型决定如何防护。')+'<article><section><h2>四种工作</h2><div class="tablewrap"><table><thead><tr><th>工作</th><th>对应成长属性</th><th>属性主要影响</th></tr></thead><tbody><tr><td>本能 Instinct</td><td>勇气 Fortitude</td><td>生命值上限</td></tr><tr><td>洞察 Insight</td><td>谨慎 Prudence</td><td>精神值上限</td></tr><tr><td>沟通 Attachment</td><td>自律 Temperance</td><td>工作成功率与速度</td></tr><tr><td>压迫 Repression</td><td>正义 Justice</td><td>移动与攻击速度</td></tr></tbody></table></div><p>工作偏好因异想体及员工属性等级而异。不要把某一种工作视为对所有对象都安全的通用答案。</p></section><section><h2>四类伤害</h2><div class="tablewrap"><table><thead><tr><th>类型</th><th>对员工的基础作用</th></tr></thead><tbody><tr><td>RED · 红伤</td><td>损伤生命值 HP</td></tr><tr><td>WHITE · 白伤</td><td>损伤精神值 SP</td></tr><tr><td>BLACK · 黑伤</td><td>同时损伤生命值与精神值</td></tr><tr><td>PALE · 蓝伤</td><td>按最大生命值比例造成伤害</td></tr></tbody></table></div><p>实际伤害还受装备抗性、等级修正与特殊机制影响。精神值耗尽会引发恐慌，不能只看生命条。</p></section><section><h2>风险等级</h2><p>ZAYIN → TETH → HE → WAW → ALEPH，表示总体危险等级由低到高。它不能取代管理须知。</p></section><section><h2>资料入口</h2><p>'+source(root+'Work','工作机制')+' · '+source(root+'Damage','伤害机制')+'</p></section></article>'+footer();
}else if(route==='about'){
main.innerHTML=title('ABOUT THIS ARCHIVE','关于这个档案库','面向中文玩家的非官方入门资料站。')+'<article><section><h2>收录范围</h2><p>当前版本包含 12 个精选异想体的基础档案、工作与伤害速查，以及主管入门建议。尚未收录全部异想体、完整剧情、核心抑制攻略、全部 E.G.O 数值或工作概率。</p><p>中文译名可能随本地化版本或社区习惯有所不同，可使用英文名与编号交叉检索。</p></section><section><h2>资料来源</h2><p>'+source('https://lobotomycorporation.wiki.gg/','Lobotomy Corporation Wiki')+'</p><p>'+source(root+'Abnormalities','异想体总目录')+'</p><p>各详情页附有对应英文词条入口。本站是基础概览，未逐项核验完整管理规则；精确数值与触发条件请优先核对当前游戏版本的管理须知。</p></section><section><h2>版权与维护</h2><p>《脑叶公司》及角色、名称和世界观的权利归 Project Moon 及相应权利人所有。本站为粉丝项目，与官方没有隶属关系。</p><p>本站为静态网页，无账号系统，内容通过源码更新，不提供在线协作编辑。</p></section></article>'+footer();
}else{main.innerHTML=title('404','页面不存在','请从导航选择档案或指南。')+'<a class="back" href="#archive">返回档案库</a>'}
}
window.addEventListener('hashchange',()=>{render();window.scrollTo(0,0);main.focus({preventScroll:true})});render();
