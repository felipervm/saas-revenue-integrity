'use strict';
const payload = JSON.parse(document.getElementById('results').textContent);
const results = payload.results;
const bridge = results['01_arr_bridge'];
const billing = results['02_billing_distortion'];
const money = value => `CAD ${new Intl.NumberFormat('en-CA', {maximumFractionDigits: 0}).format(value || 0)}`;
const signed = value => `${value < 0 ? '−' : value > 0 ? '+' : ''}${money(Math.abs(value))}`;
const monthName = month => new Date(`${month}-15T12:00:00Z`).toLocaleString('en-CA', {month:'short', year:'numeric',timeZone:'UTC'}).toUpperCase();
const slider = document.getElementById('month-slider');
const setText = (id, text) => { document.getElementById(id).textContent = text; };
const chartMax = Math.ceil(Math.max(...billing.map(row => row.naive_annualized_invoices), ...bridge.map(row => row.closing_arr)) / 20000) * 20000;
const x = i => 65 + i * 900 / 11;
const y = value => 250 - value / chartMax * 225;
const svgNode = (tag, attrs, text) => {const node = document.createElementNS('http://www.w3.org/2000/svg',tag); Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,value)); if(text!==undefined)node.textContent=text;return node;};
const grid = document.getElementById('chart-grid');
for(let n=0;n<=chartMax;n+=40000){grid.append(svgNode('line',{x1:65,x2:965,y1:y(n),y2:y(n),stroke:'#dcdfe6','stroke-dasharray':'3 5'}),svgNode('text',{x:52,y:y(n)+4,'text-anchor':'end',fill:'#677083','font-size':13},n===0?'0':`${n/1000}k`));}
bridge.forEach((row,i)=>grid.append(svgNode('text',{x:x(i),y:280,'text-anchor':'middle',fill:'#677083','font-size':13},monthName(row.month).slice(0,3))));
document.getElementById('arr-path').setAttribute('d',bridge.map((row,i)=>`${i?'L':'M'}${x(i)},${y(row.closing_arr)}`).join(' '));
document.getElementById('invoice-path').setAttribute('d',billing.map((row,i)=>`${i?'L':'M'}${x(i)},${y(row.naive_annualized_invoices)}`).join(' '));
function draw(){
 const i=Number(slider.value),a=bridge[i],b=billing[i];
 setText('month-label',monthName(a.month)); slider.setAttribute('aria-valuetext',monthName(a.month));
 setText('arr',money(a.closing_arr));setText('invoices',money(b.naive_annualized_invoices));setText('difference',signed(b.invoice_vs_arr_delta));
 document.getElementById('previous-month').disabled=i===0;document.getElementById('next-month').disabled=i===11;
 const marker=document.getElementById('chart-selection');marker.replaceChildren(svgNode('line',{x1:x(i),x2:x(i),y1:15,y2:250,stroke:'#8d95a6','stroke-dasharray':'4 5'}),svgNode('circle',{cx:x(i),cy:y(a.closing_arr),r:7,fill:'#1762ff',stroke:'white','stroke-width':3}),svgNode('circle',{cx:x(i),cy:y(b.naive_annualized_invoices),r:6,fill:'#b86b28',stroke:'white','stroke-width':3}));
 document.getElementById('trend-description').textContent=`${monthName(a.month)}: contract ARR ${money(a.closing_arr)}, annualized invoices ${money(b.naive_annualized_invoices)}. All figures are synthetic.`;
 const parts=[['Opening',a.opening_arr],['New',a.new_arr],['Expansion',a.expansion_arr],['Contraction',-a.contraction_arr],['Churn',-a.churn_arr],['Closing',a.closing_arr]];
 const bridgeEl=document.getElementById('bridge');bridgeEl.replaceChildren();parts.forEach(([label,value])=>{const item=document.createElement('div');item.className='bridge-item';const name=document.createElement('span'),amount=document.createElement('strong');name.textContent=label;amount.textContent=money(value);item.append(name,amount);bridgeEl.append(item);});
 const nrr=results['04_retention'][i].monthly_net_revenue_retention_pct;setText('retention',nrr===null?'Not applicable':`${nrr.toFixed(2)}%`);
 const direction=b.invoice_vs_arr_delta<0?'understates':b.invoice_vs_arr_delta>0?'overstates':'matches';
 setText('insight',`${monthName(a.month)}: annualizing invoices ${direction} contract ARR${b.invoice_vs_arr_delta===0?'':` by ${money(Math.abs(b.invoice_vs_arr_delta))}`}. This is a metric-definition gap, not evidence of revenue lost or gained.`);
}
slider.addEventListener('input',draw);
document.getElementById('previous-month').addEventListener('click',()=>{slider.value=Math.max(0,Number(slider.value)-1);draw();});
document.getElementById('next-month').addEventListener('click',()=>{slider.value=Math.min(11,Number(slider.value)+1);draw();});
const heroData=billing[6];document.querySelector('[data-hero="arr"]').textContent=money(heroData.contract_arr);document.querySelector('[data-hero="invoice"]').textContent=money(heroData.naive_annualized_invoices);document.querySelector('.hero-gap').textContent=`${money(Math.abs(heroData.invoice_vs_arr_delta))} apart.`;
const growthButtons=[...document.querySelectorAll('[data-growth]')];
function showGrowth(index){
 const row=results['05_expansion_attribution'][index],cross=index===6;
 growthButtons.forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.growth)===index)));
 setText('growth-label',`${cross?'JULY / CROSS-SELL':'AUGUST / EXISTING-PRODUCT'} EXPANSION`);setText('growth-amount',money(row.identified_expansion_arr));
 setText('growth-title',cross?'New product. Same customer.':'Same product. More recurring value.');
 setText('growth-description',cross?'July’s expansion comes entirely from existing accounts adding a product. Calling those accounts “new customers” would misstate the growth story.':'August’s expansion comes entirely from higher recurring value on products the accounts already held. The model increases contractual MRR; it does not identify real-world willingness to pay.');
 setText('growth-question',cross?'Which existing customer segments are adopting an additional product?':'Which changes in seats, pricing or contract terms explain the increase? Validate the terms before assigning a cause.');
 const diagram=document.getElementById('growth-diagram');diagram.setAttribute('aria-label',cross?'Existing account adds a product':'Existing account has higher recurring value on an existing product');
 diagram.querySelector('.new-product').textContent=cross?'+ Product C':'Product A ↑ MRR';
 diagram.classList.toggle('existing-growth',!cross);
}
growthButtons.forEach(button=>button.addEventListener('click',()=>showGrowth(Number(button.dataset.growth))));
const quality=document.getElementById('quality-results');
[...results['03_quality_checks'],...results['06_semantic_controls']].forEach(check=>{const row=document.createElement('div');row.className='quality-row';const name=document.createElement('span'),status=document.createElement('span');name.textContent=check.check_name.replaceAll('_',' ');status.textContent=`${check.failures} failures`;status.className='status-pill';row.append(name,status);quality.append(row);});
const nav=document.getElementById('navigation'),toggle=document.querySelector('.nav-toggle');
function closeMenu(){nav.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','Open navigation');}
toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Close navigation':'Open navigation');nav.classList.toggle('is-open',open);});
nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeMenu));
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){closeMenu();toggle.focus();}});
const sections=[...document.querySelectorAll('main section[id]')];
if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){nav.querySelectorAll('a').forEach(link=>{if(link.hash===`#${entry.target.id}`)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});}});},{rootMargin:'-15% 0px -60% 0px'});sections.forEach(section=>observer.observe(section));}
draw();document.body.dataset.ready='revenue-v2';
