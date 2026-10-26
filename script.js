// Interação da urna escolar (sem registrar votos nesta etapa).
// Coordenadas em pixels da ARTE ORIGINAL 1536 x 1024.
// O CSS recorta a frente da máquina usando estas mesmas dimensões.
const crop={x:60,y:172,width:1430,height:651};
const buttons=[
  ['1',1041,340,99,76],['2',1168,340,99,76],['3',1291,340,99,76],
  ['4',1041,432,99,76],['5',1168,432,99,76],['6',1291,432,99,76],
  ['7',1041,524,99,77],['8',1168,524,99,77],['9',1291,524,99,77],
  ['0',1171,614,101,77],
  ['BRANCO',999,699,132,101],
  ['CORRIGE',1153,699,135,101],
  ['CONFIRMA',1310,699,146,101]
];
const visor=document.getElementById('visor');
const keypad=document.getElementById('teclado');
let phase='typing',typed='',selected='';
for(const [label,x,y,w,h] of buttons){
  const key=document.createElement('button');
  key.type='button';
  key.className='hotspot';
  key.setAttribute('aria-label',label);
  key.title=label;
  key.style.left=((x-crop.x)/crop.width*100)+'%';
  key.style.top=((y-crop.y)/crop.height*100)+'%';
  key.style.width=(w/crop.width*100)+'%';
  key.style.height=(h/crop.height*100)+'%';
  key.addEventListener('click',()=>press(label));
  keypad.appendChild(key);
}
// As imagens são arquivos locais do repositório, não endereços externos.
const chapas=Object.freeze({
  '13':{
    numero:'13',
    nome:'Menos Bullying mais Inclusão',
    logo:'assets/chapa-13-logo.webp',
    equipe:'assets/chapa-13-integrantes.webp'
  }
});
function render(){
  visor.classList.add('visible');
  if(phase==='typing'){
    visor.innerHTML='<div><p class="subtitle">VOTAÇÃO DO GRÊMIO ESTUDANTIL</p><h1>Digite o número da chapa</h1><div class="digits">'+typed.padEnd(2,'_')+'</div><p class="info">Use as teclas da urna.</p></div>';
  }else if(phase==='review'&&selected==='BRANCO'){
    visor.innerHTML='<div><p class="subtitle">CONFIRA SUA ESCOLHA</p><h1>VOTO EM BRANCO</h1><p class="info">CONFIRMA para concluir.<br>CORRIGE para voltar.</p></div>';
  }else if(phase==='review'&&chapas[selected]){
    const chapa=chapas[selected];
    // Todos os campos vêm da lista de chapas cadastradas, nunca do texto digitado pelo eleitor.
    visor.innerHTML=`<div class="chapa-view">
      <div class="chapa-heading">
        <p class="chapa-numero">CHAPA ${chapa.numero}</p>
        <h1>${chapa.nome}</h1>
      </div>
      <div class="chapa-media">
        <div class="chapa-figure"><img src="${chapa.logo}" alt="Logotipo da chapa ${chapa.nome}" loading="eager"></div>
        <div class="chapa-figure"><img src="${chapa.equipe}" alt="Foto dos integrantes da chapa ${chapa.nome}" loading="eager"></div>
      </div>
      <p class="chapa-instructions">CONFIRMA para concluir · CORRIGE para alterar</p>
    </div>`;
  }else if(phase==='review'){
    visor.innerHTML='<div><p class="subtitle">NÚMERO NÃO CADASTRADO</p><div class="digits">'+selected+'</div><h1>VOTO NULO</h1><p class="info">CONFIRMA para concluir.<br>CORRIGE para alterar.</p></div>';
  }else{
    visor.innerHTML='<div><h1>FIM</h1><p class="info">Esta versão ainda não registra votos.</p><p class="subtitle">Pressione CORRIGE para reiniciar.</p></div>';
  }
}
function press(key){
  if(phase==='finished'){
    if(key==='CORRIGE'){phase='typing';typed='';selected='';render()}
    return;
  }
  if(key==='CORRIGE'){
    typed='';selected='';phase='typing';render();return;
  }
  if(key==='BRANCO'&&phase==='typing'){
    selected='BRANCO';phase='review';render();return;
  }
  if(key==='CONFIRMA'){
    if(phase==='typing'&&typed.length===2){selected=typed;phase='review';render()}
    else if(phase==='review'){phase='finished';render()}
    return;
  }
  if(/^\d$/.test(key)&&phase==='typing'&&typed.length<2){
    typed+=key;
    if(typed.length===2){selected=typed;phase='review';}
    render();
  }
}
document.addEventListener('keydown',event=>{
  if(event.altKey||event.ctrlKey||event.metaKey||event.repeat)return;
  if(/^\d$/.test(event.key)){event.preventDefault();press(event.key)}
  else if(event.key==='Enter'){event.preventDefault();press('CONFIRMA')}
  else if(event.key==='Backspace'){event.preventDefault();press('CORRIGE')}
});
document.getElementById('tela-cheia').addEventListener('click',async()=>{
  try{
    if(document.fullscreenElement)await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  }catch{
    alert('Para exibir sem barras do navegador, use F11.');
  }
});
render();
