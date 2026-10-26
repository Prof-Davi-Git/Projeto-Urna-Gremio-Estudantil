// Urna simples: registro local no navegador, sem servidor Python nem banco.
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
const somTecla=new Audio('assets/bip-scanner.mp3');
const somFim=new Audio('assets/fim-som-da-urna.mp3');
somTecla.preload='auto';
somFim.preload='auto';
const CHAVE_VOTOS='urna_gremio_votos_v1';
let phase='typing',typed='',selected='';
let mensagemErro='';
let temporizadorRetorno=null;
let temporizadorSeguranca=null;

function tocarSomTecla(){
  try{
    somTecla.pause();
    somTecla.currentTime=0;
    const execucao=somTecla.play();
    if(execucao&&typeof execucao.catch==='function')execucao.catch(()=>{});
  }catch{
    // Falha de áudio não deve impedir a votação na interface.
  }
}
function reiniciarUrna(){
  clearTimeout(temporizadorRetorno);
  clearTimeout(temporizadorSeguranca);
  temporizadorRetorno=null;
  temporizadorSeguranca=null;
  phase='typing';
  typed='';
  selected='';
  render();
}
function agendarReinicio(espera=1400){
  if(phase!=='finished'||temporizadorRetorno!==null)return;
  clearTimeout(temporizadorSeguranca);
  temporizadorRetorno=setTimeout(reiniciarUrna,espera);
}
somFim.addEventListener('ended',()=>agendarReinicio(1400));
function finalizarVotacao(){
  phase='finished';
  render();
  // Enquanto FIM estiver na tela, nenhuma tecla pode iniciar outro voto.
  try{
    somFim.pause();
    somFim.currentTime=0;
    const execucao=somFim.play();
    if(execucao&&typeof execucao.catch==='function')execucao.catch(()=>agendarReinicio(1800));
  }catch{
    agendarReinicio(1800);
  }
  // Segurança caso o navegador não dispare o evento ended.
  temporizadorSeguranca=setTimeout(()=>agendarReinicio(0),6000);
}

// Salva a sequência dos votos neste navegador, neste mesmo endereço.
// O relatório pode ser consultado/exportado na página relatorio.html.
function salvarVoto(escolha){
  const bruto=localStorage.getItem(CHAVE_VOTOS);
  const votos=bruto===null?[]:JSON.parse(bruto);
  if(!Array.isArray(votos)||!votos.every(v=>v&&
      Number.isInteger(v.ordem)&&typeof v.escolha==='string')){
    throw new Error('O histórico local está inválido. Não foi adicionado nenhum voto.');
  }
  const numero=votos.length+1;
  votos.push({ordem:numero,escolha});
  localStorage.setItem(CHAVE_VOTOS,JSON.stringify(votos));
}
function registrarVoto(){
  if(phase!=='review'&&phase!=='error')return;
  const escolha=selected==='BRANCO'?'BRANCO':
    Object.prototype.hasOwnProperty.call(chapas,selected)?selected:'NULO';
  try{
    salvarVoto(escolha);
    mensagemErro='';
    finalizarVotacao();
  }catch(erro){
    mensagemErro=(erro&&erro.message)||'Não foi possível salvar neste navegador.';
    phase='error';
    render();
  }
}

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
    logo:'assets/chapa-13-logo-hd.avif',
    equipe:'assets/chapa-13-integrantes-hd.avif'
  },
  '33':{
    numero:'33',
    nome:'Ao Infinito e Além',
    logo:'assets/chapa-33-logo-hd.avif',
    equipe:'assets/chapa-33-integrantes-hd.avif'
  }
});
function render(){
  visor.classList.add('visible');
  if(phase==='error'){
    visor.innerHTML='<div><h1>VOTO NÃO SALVO</h1><p class="info" id="detalhe-erro"></p><p class="info">Não saia desta tela. Pressione CONFIRMA para tentar novamente.</p></div>';
    document.getElementById('detalhe-erro').textContent=mensagemErro;
  }else if(phase==='typing'){
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
    visor.innerHTML='<div><h1 class="fim-titulo">FIM</h1></div>';
  }
}
function press(key){
  if(phase==='error'){
    if(key==='CONFIRMA')registrarVoto();
    return;
  }
  if(phase!=='review'&&phase!=='typing')return;
  if(key==='CORRIGE'){
    tocarSomTecla();
    typed='';
    selected='';
    phase='typing';
    render();
    return;
  }
  if(key==='BRANCO'&&phase==='typing'){
    tocarSomTecla();
    selected='BRANCO';
    phase='review';
    render();
    return;
  }
  if(key==='CONFIRMA'){
    if(phase==='review'){
      registrarVoto();
    }else if(phase==='typing'&&typed.length===2){
      selected=typed;
      phase='review';
      render();
    }
    return;
  }
  if(/^\d$/.test(key)&&phase==='typing'&&typed.length<2){
    tocarSomTecla();
    typed+=key;
    if(typed.length===2){
      selected=typed;
      phase='review';
    }
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
