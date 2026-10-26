const estado=document.getElementById('status');
const pin=document.getElementById('pin');
const liberar=document.getElementById('liberar');
const feedback=document.getElementById('feedback');
let liberada=false;
async function atualizar(){
  try{
    const resposta=await fetch('/api/status',{cache:'no-store'});
    const dados=await resposta.json();
    if(!resposta.ok||!dados.servidor_local)throw new Error();
    liberada=Boolean(dados.liberada);
    estado.textContent=liberada?'Uma votação está LIBERADA. Aguarde o eleitor finalizar.':'Urna bloqueada. Aguardando nova liberação.';
    liberar.disabled=liberada;
    estado.classList.remove('danger');
  }catch{
    estado.textContent='Servidor local desconectado. Abra o projeto pelo programa Iniciar_Urna.bat.';
    estado.classList.add('danger');
    liberar.disabled=true;
  }
}
document.getElementById('form').addEventListener('submit',async evento=>{
  evento.preventDefault();
  if(liberada)return;
  feedback.textContent='';
  liberar.disabled=true;
  try{
    const resposta=await fetch('/api/liberar',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pin:pin.value})
    });
    const dados=await resposta.json();
    if(!resposta.ok||!dados.ok)throw new Error(dados.erro||'Não foi possível liberar');
    pin.value='';
    feedback.textContent='Um voto liberado. Leve o eleitor até a urna.';
  }catch(erro){
    feedback.textContent=erro.message;
    feedback.classList.add('danger');
  }
  await atualizar();
});
atualizar();
setInterval(atualizar,2000);