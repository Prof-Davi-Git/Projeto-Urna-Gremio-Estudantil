// ATENÇÃO: demonstração visual sem persistência, autenticação nem apuração.
// As posições são percentuais relativos à imagem original de 1536 x 1024.
const hotspots = [
['1',67.8,33.4,6.4,7.0],['2',76.0,33.4,6.5,7.0],['3',84.1,33.4,6.7,7.0],
['4',67.8,42.5,6.4,7.0],['5',76.0,42.5,6.5,7.0],['6',84.1,42.5,6.7,7.0],
['7',67.8,51.7,6.4,7.0],['8',76.0,51.7,6.5,7.0],['9',84.1,51.7,6.7,7.0],
['0',76.0,60.1,6.5,7.0],['BRANCO',65.0,68.1,8.5,9.4],
['CORRIGE',75.0,68.1,9.1,9.4],['CONFIRMA',85.2,68.1,9.4,9.4]
];
const layer=document.getElementById('hotspots'), visor=document.getElementById('visor');
let state='inicio',code='',selection='';
for(const [label,x,y,w,h] of hotspots){
 const el=document.createElement('button');el.type='button';el.className='hotspot';
 el.setAttribute('aria-label',label);el.title=label;Object.assign(el.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});
 el.addEventListener('click',()=>press(label));layer.append(el);
}
function show(){
 if(state==='inicio'){visor.classList.remove('visible');visor.innerHTML='';return}
 visor.classList.add('visible');
 if(state==='typing')visor.innerHTML='<div><small>VOTAÇÃO DO GRÊMIO ESTUDANTIL</small><h1>Digite o número da chapa</h1><div class="code">'+(code.padEnd(2,'_'))+'</div><p>Use CORRIGE para limpar.</p></div>';
 else if(state==='review')visor.innerHTML='<div><small>CONFIRA SUA ESCOLHA</small><h1>'+(selection==='BRANCO'?'VOTO EM BRANCO':'NÚMERO DA CHAPA')+'</h1><div class="code">'+(selection==='BRANCO'?'BRANCO':selection)+'</div><p>CONFIRMA para concluir a simulação<br>CORRIGE para alterar</p></div>';
 else visor.innerHTML='<div><h1>FIM</h1><p>Simulação concluída.</p><small>Nenhum voto foi gravado. Pressione CORRIGE para reiniciar.</small></div>';
}
function press(k){
 if(state==='inicio'){if(k==='CONFIRMA'){state='typing';show()}return}
 if(state==='done'){if(k==='CORRIGE'){state='inicio';code='';selection='';show()}return}
 if(k==='CORRIGE'){state='typing';code='';selection='';show();return}
 if(k==='BRANCO'&&state==='typing'){selection='BRANCO';state='review';show();return}
 if(k==='CONFIRMA'){if(state==='typing'&&code.length===2){selection=code;state='review';show()}else if(state==='review'){state='done';show()}return}
 if(/^\d$/.test(k)&&state==='typing'&&code.length<2){code+=k;show()}
}
document.addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey||e.repeat)return;if(/^\d$/.test(e.key)){e.preventDefault();press(e.key)}else if(e.key==='Enter'){e.preventDefault();press('CONFIRMA')}else if(e.key==='Backspace'){e.preventDefault();press('CORRIGE')}});
document.getElementById('full').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{alert('Use F11 para ativar a tela cheia.')}});
show();